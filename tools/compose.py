#!/usr/bin/env python3
"""Scene compositor: background + camera + character pose clips + overlays + voiceover -> MP4.

usage: compose.py SHOTS.json OUT.mp4 [--start S] [--end E] [--size 1920x1080] [--fps 30]

SHOTS.json:
{
 "audio": "vo.mp3",
 "clips": {"name": "dir with f00000.png... + meta.json (from tools/xflrender/render_pose.py)"},
 "shots": [
   {"t0": 0, "t1": 7, "bg": "bg.jpg",
    "cam": [[x, y, w], [x, y, w]],          # BG-pixel crop rect (16:9) at shot start / end, eased
    "actors": [
      {"x": 1280, "y": 1100, "h": 520,       # feet anchor + figure height, in BG pixels
       "x1": 1500, "y1": 1150, "h1": 600,    # optional end position (walking / depth)
       "talk": "raja_talk", "idle": "raja_idle", "speaking": [[21.8, 27.4]],
       "flip": false, "hold_idle_frame": 0}
    ],
    "overlays": [{"png": "title.png", "t0": 1, "t1": 6, "x": 0.5, "y": 0.2, "w": 0.6}],
    "fade_in": 0.5, "fade_out": 0.5}
 ]
}
Idle clips loop; if an actor has no idle clip, the talk clip is held on `hold_idle_frame`.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Clip:
    def __init__(self, d):
        self.dir = d; self.meta = json.load(open(os.path.join(d, 'meta.json')))
        self.n = self.meta['frames']; self.cache = {}
        vx, vy, vw, vh = self.meta['view']; s = self.meta['scale']; x0, y0, x1, y1 = self.meta['bbox']
        self.foot = (((x0 + x1) / 2 - vx) * s, (y1 - vy) * s)        # feet anchor in image px
        self.fig_h = (y1 - y0) * s                                      # figure height in image px

    def frame(self, i):
        i %= self.n
        if i not in self.cache:
            if len(self.cache) > 40: self.cache.clear()
            self.cache[i] = Image.open(os.path.join(self.dir, 'f%05d.png' % i)).convert('RGBA')
        return self.cache[i]


class BG:
    cache = {}

    @classmethod
    def get(cls, path):
        if path not in cls.cache:
            im = Image.open(path).convert('RGB')
            if im.width > 3840: im = im.resize((3840, round(im.height * 3840 / im.width)), Image.LANCZOS)
            cls.cache[path] = im
        return cls.cache[path]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shots'); ap.add_argument('out'); ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float); ap.add_argument('--size', default='1920x1080'); ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    spec = json.load(open(a.shots)); base = os.path.dirname(os.path.abspath(a.shots))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    W, H = (int(v) for v in a.size.split('x')); fps = a.fps
    clips = {k: Clip(P(v)) for k, v in spec['clips'].items()}
    shots = spec['shots']; end = a.end if a.end is not None else shots[-1]['t1']
    overlays_cache = {}
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                           '-r', str(fps), '-i', '-', '-ss', str(a.start), '-t', str(end - a.start), '-i', P(spec['audio']),
                           '-filter_complex', '[1:a]afade=t=out:st=%f:d=1[a]' % max(0, end - a.start - 1),
                           '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a.out],
                          stdin=subprocess.PIPE)
    nfr = int(round((end - a.start) * fps))
    for fi in range(nfr):
        t = a.start + fi / fps
        sh = next((s for s in shots if s['t0'] <= t < s['t1']), shots[-1])
        u = ease((t - sh['t0']) / max(1e-6, sh['t1'] - sh['t0']))
        bg = BG.get(P(sh['bg']))
        c0, c1 = sh['cam']
        cx = c0[0] + (c1[0] - c0[0]) * u; cy = c0[1] + (c1[1] - c0[1]) * u; cw = c0[2] + (c1[2] - c0[2]) * u
        ch = cw * H / W; k = W / cw
        frame = bg.resize((W, H), Image.BICUBIC, box=(cx, cy, cx + cw, cy + ch)).convert('RGBA')
        actors = sorted(sh.get('actors', []), key=lambda ac: ac.get('z', ac['y']))
        for ac in actors:
            sp = next((iv for iv in ac.get('speaking', []) if iv[0] <= t < iv[1]), None)
            speaking = sp is not None
            local = int(round((t - sh['t0']) * fps)) + ac.get('offset', 0)
            if speaking or not ac.get('idle'):
                clip = clips[ac['talk']]
                img = clip.frame(int(round((t - sp[0]) * fps)) if speaking else ac.get('hold_idle_frame', 0))
            else:
                clip = clips[ac['idle']]; img = clip.frame(local)
            mu = ease((t - sh['t0'] - ac.get('move_t0', 0)) / max(1e-6, ac.get('move_dur', sh['t1'] - sh['t0']))) if 'x1' in ac else 0
            ax = ac['x'] + (ac.get('x1', ac['x']) - ac['x']) * mu
            ay = ac['y'] + (ac.get('y1', ac['y']) - ac['y']) * mu
            ah = ac['h'] + (ac.get('h1', ac['h']) - ac['h']) * mu
            s = ah * k / clip.fig_h
            iw, ih = max(1, int(img.width * s)), max(1, int(img.height * s))
            im = img.resize((iw, ih), Image.BICUBIC)
            fx, fy = clip.foot
            if ac.get('flip'):
                im = im.transpose(Image.FLIP_LEFT_RIGHT); fx = img.width - fx
            px = int((ax - cx) * k - fx * s); py = int((ay - cy) * k - fy * s)
            if px > W or py > H or px + iw < 0 or py + ih < 0: continue
            frame.alpha_composite(im, (max(0, px), max(0, py)), (max(0, -px), max(0, -py)))
        for ov in sh.get('overlays', []):
            if not (ov['t0'] <= t < ov['t1']): continue
            if ov['png'] not in overlays_cache: overlays_cache[ov['png']] = Image.open(P(ov['png'])).convert('RGBA')
            o = overlays_cache[ov['png']]; ow = int(W * ov['w']); oh = int(o.height * ow / o.width)
            o2 = o.resize((ow, oh), Image.LANCZOS)
            al = min(1, (t - ov['t0']) / 0.6, (ov['t1'] - t) / 0.6)
            if al < 1:
                o2 = o2.copy(); o2.putalpha(o2.getchannel('A').point(lambda v: int(v * al)))
            frame.alpha_composite(o2, (int(W * ov['x'] - ow / 2), int(H * ov['y'] - oh / 2)))
        rgb = np.asarray(frame.convert('RGB'), dtype=np.float32)
        fade = 1.0
        if sh.get('fade_in'): fade = min(fade, (t - sh['t0']) / sh['fade_in'])
        if sh.get('fade_out'): fade = min(fade, (sh['t1'] - t) / sh['fade_out'])
        if fade < 1: rgb *= max(0.0, fade)
        ff.stdin.write(rgb.astype(np.uint8).tobytes())
        if fi % 150 == 0: print('frame', fi, '/', nfr, flush=True)
    ff.stdin.close(); ff.wait()
    print('wrote', a.out)


if __name__ == '__main__':
    main()

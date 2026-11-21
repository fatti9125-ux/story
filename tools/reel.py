#!/usr/bin/env python3
"""Vertical Instagram Reel compositor (dark cinematic history style).

usage: reel.py SPEC.json OUT.mp4 [--start S] [--end E] [--still T OUT.png]

SPEC.json:
{ "size": [1080, 1920], "fps": 30, "vo": "vo.wav", "vo_timing": "vo_timing.json",
  "clips": {name: dir},                       # from tools/xflrender/render_pose.py
  "shots": [ {"t0", "t1", "bg": path | "black", "card": "TEXT" (black shots),
              "cam": [[x, y, w], [x, y, w]],  # BG-pixel crop, height = w*H/W, eased
              "actors": [...same schema as compose.py...],
              "fx": {"night": 0..1, "fire": 0..1, "embers": n, "smoke": 0..1,
                     "blur_in": sec, "shake": px, "desat": 0..1, "dim_actors": 0..1}} ] }
Captions come from vo_timing (one line each) and are hidden on black-card shots.
Music + SFX are synthesized (drone, wind, boom on cuts, fire crackle) and mixed under the VO.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import Clip, BG, ease

FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'


def noise_tex(w, h, seed=1):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for cell in (256, 128, 64, 32):
        g = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 2 * cell, h + 2 * cell), Image.BICUBIC),
                                np.float32)[cell:cell + h, cell:cell + w] / 255
        tot += amp; amp *= 0.5
    acc /= tot
    return np.clip((acc - 0.35) / 0.4, 0, 1)


def text_img(text, size, maxw, stroke=10):
    f = ImageFont.truetype(FONT, size)
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    lh = int(size * 1.08); W = int(maxw + 2 * stroke + 40); H = lh * len(lines) + 2 * stroke + 30
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for i, l in enumerate(lines):
        x = (W - f.getlength(l)) / 2; y = stroke + 10 + i * lh
        ds.text((x + 4, y + 8), l, font=f, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
        d.text((x, y), l, font=f, fill=(255, 255, 255, 255), stroke_width=stroke // 2, stroke_fill=(20, 20, 20, 255))
    sh = sh.filter(ImageFilter.GaussianBlur(8)); sh.alpha_composite(im)
    return sh


def music(dur, sr, cuts, fire_spans):
    t = np.arange(int(dur * sr)) / sr
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t)
    drone = sum(a * np.sin(2 * np.pi * f * t + p) for f, a, p in ((36.7, 0.5, 0), (55.0, 0.35, 1), (73.4, 0.25, 2), (110, 0.08, 0.5)))
    drone *= trem
    rng = np.random.default_rng(3)
    wind = np.convolve(rng.standard_normal(len(t)), np.ones(400) / 400, 'same') * 3.0 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    out = 0.22 * drone + 0.10 * wind
    for c in cuts:   # sub boom on each cut
        i = int(c * sr); n = int(1.2 * sr)
        if i >= len(t): continue
        tt = np.arange(min(n, len(t) - i)) / sr
        out[i:i + len(tt)] += 0.55 * np.sin(2 * np.pi * (48 - 18 * tt) * tt) * np.exp(-tt * 4.0)
    for a, b, g in fire_spans:  # crackle
        i0, i1 = int(a * sr), min(len(t), int(b * sr))
        cr = (rng.random(i1 - i0) < 0.0025) * rng.standard_normal(i1 - i0) * 0.5
        cr = np.convolve(cr, np.exp(-np.arange(60) / 8), 'same')
        rumble = np.convolve(rng.standard_normal(i1 - i0), np.ones(800) / 800, 'same') * 4
        out[i0:i1] += g * (0.25 * cr + 0.12 * rumble)
    return np.clip(out, -1, 1).astype(np.float32)


class Reel:
    def __init__(self, spec_path):
        self.spec = json.load(open(spec_path)); self.base = os.path.dirname(os.path.abspath(spec_path))
        P = self.P = lambda p: p if os.path.isabs(p) else os.path.join(self.base, p)
        self.W, self.H = self.spec.get('size', [1080, 1920]); self.fps = self.spec.get('fps', 30)
        self.clips = {k: Clip(P(v)) for k, v in self.spec['clips'].items()}
        self.shots = self.spec['shots']; self.timing = json.load(open(P(self.spec['vo_timing'])))
        self.smoke = noise_tex(self.W // 2, self.H, 7)
        yy = np.linspace(0, 1, self.H)[:, None]; xx = np.linspace(-1, 1, self.W)[None, :]
        self.vign = np.clip(1 - 0.55 * (xx ** 2 + ((yy - 0.5) * 2) ** 2) ** 1.2, 0.25, 1).astype(np.float32)[..., None]
        self.firegrad = (np.clip((yy - 0.35) / 0.65, 0, 1) ** 1.6).astype(np.float32) * np.ones((1, self.W), np.float32)
        self.horizon = np.exp(-((yy - 0.42) / 0.13) ** 2).astype(np.float32) * np.ones((1, self.W), np.float32)
        self.skydark = (np.clip(1 - yy / 0.45, 0, 1) ** 1.2).astype(np.float32)[..., None] * np.ones((1, self.W, 1), np.float32)
        rng = np.random.default_rng(11); n = 160
        self.emb = dict(x=rng.random(n) * self.W, y=rng.random(n) * self.H, v=60 + rng.random(n) * 220,
                        r=1.5 + rng.random(n) * 4.5, ph=rng.random(n) * 6.28, sw=10 + rng.random(n) * 40)
        self.capcache = {}; self.cardcache = {}

    def caption_at(self, t):
        for x in self.timing:
            if x['t0'] - 0.05 <= t < x['t1'] + 0.25: return x
        return None

    def frame(self, t):
        W, H, fps = self.W, self.H, self.fps
        sh = next((s for s in self.shots if s['t0'] <= t < s['t1']), self.shots[-1])
        fx = sh.get('fx', {}); lt = t - sh['t0']; u = ease(lt / max(1e-6, sh['t1'] - sh['t0']))
        if sh.get('bg') == 'black':
            img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
            key = sh['card']
            if key not in self.cardcache: self.cardcache[key] = text_img(key.upper(), 92, W * 0.78, 12)
            c = self.cardcache[key]; s = 1.0 + 0.04 * min(1, lt / 0.25)
            c2 = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
            a = min(1, lt / 0.15)
            if a < 1: c2 = c2.copy(); c2.putalpha(c2.getchannel('A').point(lambda v: int(v * a)))
            img.alpha_composite(c2, (int(W / 2 - c2.width / 2), int(H * 0.47 - c2.height / 2)))
            return np.asarray(img.convert('RGB'))
        bg = BG.get(self.P(sh['bg']), 0)
        (x0, y0, w0), (x1, y1, w1) = sh['cam']
        cx = x0 + (x1 - x0) * u; cy = y0 + (y1 - y0) * u; cw = w0 + (w1 - w0) * u; ch = cw * H / W; k = W / cw
        if fx.get('shake'):
            a = fx['shake'] / k; cx += a * math.sin(t * 37) ; cy += a * math.cos(t * 29)
        if ch > bg.height: cw = bg.height * W / H; ch = bg.height; k = W / cw
        cw = min(cw, bg.width); cx = max(0, min(cx, bg.width - cw)); cy = max(0, min(cy, bg.height - ch))
        frame = bg.resize((W, H), Image.BICUBIC, box=(cx, cy, cx + cw, cy + ch)).convert('RGBA')
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for ac in sorted(sh.get('actors', []), key=lambda a: a.get('z', a['y'])):
            clip = self.clips[ac.get('idle') or ac['talk']]
            img = clip.frame(int(round(lt * fps)) + ac.get('offset', 0))
            mu = ease((lt - ac.get('move_t0', 0)) / max(1e-6, ac.get('move_dur', sh['t1'] - sh['t0']))) if 'x1' in ac else 0
            ax = ac['x'] + (ac.get('x1', ac['x']) - ac['x']) * mu; ay = ac['y'] + (ac.get('y1', ac['y']) - ac['y']) * mu
            ah = ac['h'] + (ac.get('h1', ac['h']) - ac['h']) * mu
            s = ah * k / clip.fig_h; iw, ih = max(1, int(img.width * s)), max(1, int(img.height * s))
            im = img.resize((iw, ih), Image.BICUBIC); fxp, fyp = clip.foot
            if ac.get('flip'): im = im.transpose(Image.FLIP_LEFT_RIGHT); fxp = img.width - fxp
            px = int((ax - cx) * k - fxp * s); py = int((ay - cy) * k - fyp * s)
            if px > W or py > H or px + iw < 0 or py + ih < 0: continue
            layer.alpha_composite(im, (max(0, px), max(0, py)), (max(0, -px), max(0, -py)))
        if fx.get('dim_actors'):
            a = np.asarray(layer).astype(np.float32); a[..., :3] *= 1 - fx['dim_actors']; layer = Image.fromarray(a.astype(np.uint8))
        frame.alpha_composite(layer)
        if fx.get('blur_in') and lt < fx['blur_in']:
            frame = frame.filter(ImageFilter.GaussianBlur(28 * (1 - lt / fx['blur_in']) ** 2))
        f = np.asarray(frame.convert('RGB'), np.float32) / 255
        # ---- grade: night + teal/orange + contrast
        night = fx.get('night', 0.4)
        L = (0.3 * f[..., 0] + 0.59 * f[..., 1] + 0.11 * f[..., 2])[..., None]
        if fx.get('desat'): f = f * (1 - fx['desat']) + L * fx['desat']
        cool = f * np.array([0.36, 0.52, 0.72], np.float32)
        f = f * (1 - night) + cool * night
        f = f * (1 - night * 0.55 * self.skydark)          # darken the sky / top of frame
        f = np.clip((f - 0.5) * 1.12 + 0.5, 0, 1)
        L = (0.3 * f[..., 0] + 0.59 * f[..., 1] + 0.11 * f[..., 2])[..., None]
        f = f + (1 - L) * np.array([-0.02, 0.025, 0.04], np.float32) + L * L * np.array([0.06, 0.02, -0.03], np.float32)
        fire = fx.get('fire', 0)
        if fire:
            fl = 0.8 + 0.12 * math.sin(t * 13) + 0.08 * math.sin(t * 31 + 1)
            g = (self.horizon * 0.9 + self.firegrad * 0.6)[..., None] * fire * fl
            f = 1 - (1 - f) * (1 - np.clip(g * np.array([1.0, 0.42, 0.08], np.float32) * (0.5 + 0.8 * f) * 1.5, 0, 1))  # screen
        burn = fx.get('burn', 0)
        if burn:
            L = (0.3 * f[..., 0] + 0.59 * f[..., 1] + 0.11 * f[..., 2])[..., None]
            m = burn * np.clip(self.skydark * 1.6, 0, 1)
            f = f * (1 - m) + m * (L * np.array([1.9, 0.75, 0.3], np.float32) + np.array([0.18, 0.04, 0.0], np.float32))
        sm = fx.get('smoke', 0)
        if sm:
            off = int(t * 40) % self.H
            tex = np.roll(self.smoke, -off, axis=0)
            tex = np.asarray(Image.fromarray((tex * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
            f = f * (1 - sm * 0.55 * tex) + sm * 0.55 * tex * np.array([0.22, 0.25, 0.28], np.float32)
        f = f * self.vign
        out = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
        ne = fx.get('embers', 0)
        if ne:
            el = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(el); e = self.emb
            for i in range(min(ne, len(e['x']))):
                y = (e['y'][i] - t * e['v'][i]) % (H + 40) - 20
                x = (e['x'][i] + e['sw'][i] * math.sin(t * 1.7 + e['ph'][i])) % W
                r = e['r'][i]; a = int(160 + 95 * math.sin(t * 6 + e['ph'][i]))
                d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 160 + int(60 * (r < 3)), 60, max(0, min(255, a))))
            glow = el.filter(ImageFilter.GaussianBlur(5)); out.alpha_composite(glow); out.alpha_composite(el)
        # ---- caption
        cap = self.caption_at(t)
        if cap:
            key = cap.get('caption') or cap['text'].rstrip('.!?,')
            if key not in self.capcache: self.capcache[key] = text_img(key.upper(), 68, W * 0.82, 10)
            c = self.capcache[key]; ct = t - cap['t0']; s = 0.92 + 0.08 * min(1, max(0, ct) / 0.12)
            c2 = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
            out.alpha_composite(c2, (int(W / 2 - c2.width / 2), int(H * 0.66 - c2.height / 2)))
        return np.asarray(out.convert('RGB'))

    def render(self, out, start=0, end=None):
        W, H, fps = self.W, self.H, self.fps
        end = end if end is not None else self.shots[-1]['t1']
        cuts = [s['t0'] for s in self.shots if s['t0'] > 0]
        fire_spans = [(s['t0'], s['t1'], s.get('fx', {}).get('fire', 0)) for s in self.shots if s.get('fx', {}).get('fire')]
        sr = 48000; mus = music(end + 1, sr, cuts, fire_spans)
        mp = out + '.music.wav'
        import soundfile as sf
        sf.write(mp, mus, sr)
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(fps), '-i', '-',
                               '-ss', str(start), '-i', self.P(self.spec['vo']), '-ss', str(start), '-i', mp,
                               '-filter_complex', '[1:a]aresample=48000,volume=1.0[v];[2:a]volume=0.35[m];[v][m]amix=inputs=2:duration=first:normalize=0,'
                               'loudnorm=I=-14:TP=-1.5:LRA=9[a]',
                               '-map', '0:v', '-map', '[a]', '-t', str(end - start), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                               '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
        n = int(round((end - start) * fps))
        for i in range(n):
            ff.stdin.write(self.frame(start + i / fps).tobytes())
            if i % 150 == 0: print('frame', i, '/', n, flush=True)
        ff.stdin.close(); ff.wait(); os.remove(mp)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('out')
    ap.add_argument('--start', type=float, default=0); ap.add_argument('--end', type=float)
    ap.add_argument('--stills', help='comma list of times; writes OUT as a contact sheet instead of video')
    a = ap.parse_args(); r = Reel(a.spec)
    if a.stills:
        ts = [float(x) for x in a.stills.split(',')]; ims = [Image.fromarray(r.frame(t)).resize((270, 480)) for t in ts]
        g = Image.new('RGB', (270 * min(8, len(ims)), 480 * ((len(ims) + 7) // 8)))
        for i, im in enumerate(ims): g.paste(im, ((i % 8) * 270, (i // 8) * 480))
        g.save(a.out); return
    r.render(a.out, a.start, a.end)


if __name__ == '__main__':
    main()

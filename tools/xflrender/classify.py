#!/usr/bin/env python3
"""Classify each pose of a character as TALK / IDLE / MOVE and find its full-motion bbox.

Renders every pose at low resolution for up to N frames, measures how often the head
region changes (mouth swaps every few frames = talk; rare changes = blinks = idle) and how
much the body moves, and records the union bbox over all frames (so gesturing arms are
never cropped later). Updates POSES_JSON in place with: kind, head_rate, body_rate, ubbox.

usage: classify.py XFL_DIR POSES_JSON [--frames 90]
"""
import argparse, json, os, sys, io
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xfl import XFL
from poses import pose_list, render_pose_svg
from PIL import Image


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('xfl'); ap.add_argument('poses'); ap.add_argument('--frames', type=int, default=90)
    a = ap.parse_args()
    doc = XFL(a.xfl); tl, poses = pose_list(doc); meta = json.load(open(a.poses))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium'), args=['--no-sandbox'])
        for k, ps in enumerate(poses):
            if not meta[k].get('bbox'): continue
            x0, y0, x1, y1 = meta[k]['bbox']; w, h = x1 - x0, y1 - y0
            view = (x0 - w, y0 - 0.25 * h, 3 * w, 1.5 * h)          # generous canvas to catch reaching arms
            sc = 360 / view[3]; W, H = int(view[2] * sc), 360
            pg = br.new_page(viewport={'width': W, 'height': H})
            n = min(a.frames, ps['length']); prev = None; head = []; body = []; ub = None
            hy = int((0.25 * h + 0.22 * h) * sc)                      # head band: top 22% of figure
            for f in range(n):
                s = render_pose_svg(doc, tl, ps['layer'], ps['element'], f, view, (W, H))
                pg.set_content('<body style="margin:0;background:transparent">' + s + '</body>')
                im = Image.open(io.BytesIO(pg.screenshot(omit_background=True))).convert('RGBA')
                bb = im.getbbox()
                if bb: ub = bb if ub is None else (min(ub[0], bb[0]), min(ub[1], bb[1]), max(ub[2], bb[2]), max(ub[3], bb[3]))
                arr = np.asarray(im).astype(np.int16)
                if prev is not None:
                    d = np.abs(arr - prev).max(2) > 30
                    head.append(d[:hy].mean() > 0.0004); body.append(d[hy:].mean())
                prev = arr
            pg.close()
            hr = float(np.mean(head)) if head else 0; brt = float(np.mean(body)) if body else 0
            kind = 'MOVE' if brt > 0.01 else ('TALK' if hr > 0.30 else 'IDLE')
            meta[k].update(kind=kind, head_rate=round(hr, 3), body_rate=round(brt, 4),
                           ubbox=[view[0] + ub[0] / sc, view[1] + ub[1] / sc, view[0] + ub[2] / sc, view[1] + ub[3] / sc] if ub else meta[k]['bbox'])
            print(k, kind, 'head', round(hr, 2), 'body', round(brt, 4), flush=True)
        br.close()
    json.dump(meta, open(a.poses, 'w'), indent=1)


if __name__ == '__main__':
    main()

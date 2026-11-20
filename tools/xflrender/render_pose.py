#!/usr/bin/env python3
"""Render one pose clip (an element on a character file's main timeline) to a transparent PNG sequence.

usage: render_pose.py XFL_DIR POSES_JSON POSE_INDEX OUTDIR [--frames N] [--scale S] [--pad P]
Writes OUTDIR/f00000.png ... and OUTDIR/meta.json (stage bbox, scale, frame count) so the
compositor can place the clip in stage coordinates (feet / anchor stay consistent).
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xfl import XFL
from poses import pose_list, render_pose_svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('xfl'); ap.add_argument('poses'); ap.add_argument('index', type=int); ap.add_argument('out')
    ap.add_argument('--frames', type=int, default=300); ap.add_argument('--scale', type=float, default=4.0)
    ap.add_argument('--pad', type=float, default=0.12)
    a = ap.parse_args()
    doc = XFL(a.xfl); tl, poses = pose_list(doc)
    meta_in = json.load(open(a.poses))[a.index]
    ps = poses[a.index]
    x0, y0, x1, y1 = meta_in['bbox']; w, h = x1 - x0, y1 - y0
    px, py = w * a.pad, h * a.pad
    view = (x0 - px, y0 - py, w + 2 * px, h + 2 * py)
    W, H = int(view[2] * a.scale), int(view[3] * a.scale)
    n = min(a.frames, ps['length'])
    os.makedirs(a.out, exist_ok=True)
    page = os.path.join(os.path.abspath(a.out), '_page.html')
    open(page, 'w').write('<html><body style="margin:0;background:transparent"><div id="c"></div></body></html>')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium'), args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': W, 'height': H}); pg.goto('file://' + page)
        for f in range(n):
            s = render_pose_svg(doc, tl, ps['layer'], ps['element'], f, view, (W, H))
            pg.evaluate('s => { document.getElementById("c").innerHTML = s; }', s)
            pg.screenshot(path=os.path.join(a.out, 'f%05d.png' % f), omit_background=True,
                          clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        br.close()
    json.dump(dict(view=view, scale=a.scale, frames=n, size=[W, H], bbox=meta_in['bbox'], symbol=ps['symbol']),
              open(os.path.join(a.out, 'meta.json'), 'w'), indent=1)
    print('rendered', n, 'frames', W, 'x', H)


if __name__ == '__main__':
    main()

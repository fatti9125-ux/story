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
    ap.add_argument('--pad', type=float, default=0.04)
    ap.add_argument('--mute', action='store_true', help='mouth locked closed')
    ap.add_argument('--still', action='store_true', help='hold body on frame 0, eyes/loops keep running (implies --mute)')
    a = ap.parse_args()
    doc = XFL(a.xfl); tl, poses = pose_list(doc)
    meta_in = json.load(open(a.poses))[a.index]
    ps = poses[a.index]
    doc.mute = a.mute or a.still
    bx = [meta_in['bbox']] + ([meta_in['ubbox']] if meta_in.get('ubbox') else [])
    x0, y0 = min(b[0] for b in bx), min(b[1] for b in bx); x1, y1 = max(b[2] for b in bx), max(b[3] for b in bx)
    w, h = x1 - x0, y1 - y0
    px, py = w * 0.45 + h * 0.15, h * 0.12          # wide canvas; trimmed to real union after rendering
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
            if a.still: doc.gclock = f
            s = render_pose_svg(doc, tl, ps['layer'], ps['element'], 0 if a.still else f, view, (W, H))
            pg.evaluate('s => { document.getElementById("c").innerHTML = s; }', s)
            pg.screenshot(path=os.path.join(a.out, 'f%05d.png' % f), omit_background=True,
                          clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        br.close()
    # trim every frame to the union of all frames' alpha boxes (nothing can be cut off)
    from PIL import Image
    files = [os.path.join(a.out, 'f%05d.png' % f) for f in range(n)]
    ub = None
    for fn in files:
        bb = Image.open(fn).getbbox()
        if bb: ub = bb if ub is None else (min(ub[0], bb[0]), min(ub[1], bb[1]), max(ub[2], bb[2]), max(ub[3], bb[3]))
    edge = ub and (ub[0] == 0 or ub[1] == 0 or ub[2] == W or ub[3] == H)
    if ub:
        m = 6; ub = (max(0, ub[0] - m), max(0, ub[1] - m), min(W, ub[2] + m), min(H, ub[3] + m))
        for fn in files: Image.open(fn).crop(ub).save(fn)
        view = (view[0] + ub[0] / a.scale, view[1] + ub[1] / a.scale, (ub[2] - ub[0]) / a.scale, (ub[3] - ub[1]) / a.scale)
        W, H = ub[2] - ub[0], ub[3] - ub[1]
    if edge: print('WARNING: content touches the render canvas edge')
    json.dump(dict(view=view, scale=a.scale, frames=n, size=[W, H], bbox=meta_in['bbox'], symbol=ps['symbol']),
              open(os.path.join(a.out, 'meta.json'), 'w'), indent=1)
    print('rendered', n, 'frames', W, 'x', H)


if __name__ == '__main__':
    main()

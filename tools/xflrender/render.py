#!/usr/bin/env python3
"""Render frames of an XFL timeline to transparent PNGs with headless Chromium.

usage: render.py XFL_DIR TIMELINE START END OUTDIR [--view x,y,w,h] [--size WxH]
                 [--bg #RRGGBB] [--no-hidden] [--step N] [--svg]
Frames are 0-based, END exclusive. XFL_DIR is an extracted .fla (see tools/fla_extract.py).
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xfl import XFL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('xfl'); ap.add_argument('timeline'); ap.add_argument('start', type=int); ap.add_argument('end', type=int)
    ap.add_argument('out'); ap.add_argument('--view'); ap.add_argument('--size'); ap.add_argument('--bg')
    ap.add_argument('--no-hidden', action='store_true'); ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--svg', action='store_true', help='also keep the SVG files')
    a = ap.parse_args()
    doc = XFL(a.xfl, include_hidden=not a.no_hidden)
    view = tuple(float(v) for v in a.view.split(',')) if a.view else (0, 0, doc.width, doc.height)
    W, H = (int(v) for v in a.size.split('x')) if a.size else (int(view[2]), int(view[3]))
    os.makedirs(a.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium'), args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': W, 'height': H})
        blank = os.path.join(os.path.abspath(a.out), '_page.html')
        open(blank, 'w').write('<html><body style="margin:0;background:transparent"><div id="c"></div></body></html>')
        pg.goto('file://' + blank)
        for f in range(a.start, a.end, a.step):
            s = doc.svg(a.timeline, f, W, H, view, a.bg)
            if a.svg:
                open(os.path.join(a.out, 'f%05d.svg' % f), 'w').write(s)
            pg.evaluate('s => { document.getElementById("c").innerHTML = s; }', s)
            pg.screenshot(path=os.path.join(a.out, 'f%05d.png' % f), omit_background=True,
                          clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        br.close()


if __name__ == '__main__':
    main()

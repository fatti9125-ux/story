#!/usr/bin/env python3
"""List and preview every pose clip on a character file's main timeline.

Each layer of the main timeline in these character packs holds one pre-animated pose
(talk, idle, walk, sit ...). This renders each pose's first frame on its own, records its
on-stage bounding box and length, and writes a labelled contact sheet + poses.json.

usage: poses.py XFL_DIR OUTDIR
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xfl import XFL, kids, strip, mat_of
from PIL import Image, ImageDraw


def pose_list(doc):
    tl = next(iter(doc.scenes.values()))
    out = []
    for li, (L, frames) in enumerate(tl.layers):
        if L.get('layerType') in ('guide', 'folder', 'mask', 'camera') or L.get('name') == 'Camera': continue
        for F in frames[:1]:
            for ei, el in enumerate(kids(F, 'elements')):
                if strip(el.tag) == 'DOMSymbolInstance' and el.get('libraryItemName') in doc.items:
                    name = el.get('libraryItemName')
                    out.append(dict(layer=li, element=ei, layer_name=L.get('name'), symbol=name,
                                    length=doc.timeline(name).length, matrix=mat_of(el),
                                    loop=el.get('loop', 'loop'), first=int(el.get('firstFrame', 0))))
    return tl, out


def render_pose_svg(doc, tl, li, ei, frame, view, size):
    """Render one element (pose instance) of a main-timeline layer at a given frame."""
    doc.reset_defs()
    fi, F = tl.frame_at(li, 0)
    el = kids(F, 'elements')[ei]
    body = doc.render_element(el, frame)
    defs = ''.join(doc.defs[k] for k in doc.def_order)
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" '
            'viewBox="%g %g %g %g"><defs>%s</defs>%s</svg>' % (size[0], size[1], *view, defs, body))


def main():
    xd, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    doc = XFL(xd)
    tl, poses = pose_list(doc)
    from playwright.sync_api import sync_playwright
    W, H = 1920, 1080
    page_file = os.path.join(os.path.abspath(out), '_page.html')
    open(page_file, 'w').write('<html><body style="margin:0;background:transparent"><div id="c"></div></body></html>')
    tiles = []
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=os.environ.get('CHROMIUM', '/opt/pw-browsers/chromium'), args=['--no-sandbox'])
        pg = br.new_page(viewport={'width': W, 'height': H}); pg.goto('file://' + page_file)
        for k, ps in enumerate(poses):
            s = render_pose_svg(doc, tl, ps['layer'], ps['element'], 0, (0, 0, doc.width, doc.height), (W, H))
            pg.evaluate('s => { document.getElementById("c").innerHTML = s; }', s)
            fn = os.path.join(out, 'pose%02d.png' % k)
            pg.screenshot(path=fn, omit_background=True, clip={'x': 0, 'y': 0, 'width': W, 'height': H})
            im = Image.open(fn); bb = im.getbbox()
            ps['bbox'] = [v * doc.width / W if i % 2 == 0 else v * doc.height / H for i, v in enumerate(bb)] if bb else None
            # mouth activity: does anything change in the head region over the first 30 frames?
            tiles.append((k, im.crop(bb) if bb else im))
        br.close()
    cols = 6; tw, th = 300, 420
    sheet = Image.new('RGB', (cols * tw, ((len(tiles) + cols - 1) // cols) * th), 'white'); d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(tiles):
        im = im.copy(); im.thumbnail((tw - 10, th - 40))
        x, y = (i % cols) * tw, (i // cols) * th
        bg = Image.new('RGB', im.size, 'white'); bg.paste(im, (0, 0), im)
        sheet.paste(bg, (x + 5, y + 35))
        ps = poses[k]
        d.text((x + 5, y + 3), 'pose %d  L%d.%d  %df' % (k, ps['layer'], ps['element'], ps['length']), fill='black')
        d.text((x + 5, y + 17), ps['symbol'][-30:], fill='gray')
    sheet.save(os.path.join(out, 'poses_sheet.png'))
    for ps in poses: ps['matrix'] = list(ps['matrix'])
    json.dump(poses, open(os.path.join(out, 'poses.json'), 'w'), indent=1)
    print(len(poses), 'poses')


if __name__ == '__main__':
    main()

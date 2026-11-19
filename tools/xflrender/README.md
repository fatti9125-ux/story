# xflrender

Renders Adobe Animate `.fla` files (XFL) frame-by-frame to transparent PNG without Animate.

```bash
python3 -I tools/fla_extract.py "assets/characters/fla/young man 2.fla" /tmp/xfl/young_man_2
python3 -I tools/xflrender/render.py /tmp/xfl/young_man_2 "Scene 1" 0 240 /tmp/out --size 1920x1080
```

Supports shapes (edge format), solid/linear/radial/bitmap fills, strokes, groups, graphic
and movie-clip symbols (loop / play once / single frame), classic motion tweens with eases,
shape tweens (when edge structure matches), colour effects, masks, guide/folder layers,
and Animate `.dat` bitmaps (lossless ARGB and JPEG). Rasterised with headless Chromium
(`pip install playwright`; uses `/opt/pw-browsers/chromium`).

Verified on all 21 characters in `assets/characters/fla` against their preview images.

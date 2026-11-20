"""Render Adobe Animate XFL timelines to SVG, frame by frame.

Own implementation for the story pipeline. Supports: shapes (edge format, solid /
linear / radial fills, solid strokes), groups, graphic & movie-clip symbol
instances (loop / play once / single frame, firstFrame, lastFrame), classic motion
tweens (Flash-style matrix decomposition around the transformation point, eases),
shape tweens (number interpolation when edge structure matches, else hold), colour
effects (alpha, brightness, tint, advanced), mask layers, guide / folder layers.
Coordinates: edges are twips (/20); matrices are pixels.
"""
import math, re, os, html
import xml.etree.ElementTree as ET

NS = '{http://ns.adobe.com/xfl/2008/}'


def strip(tag):
    return tag[len(NS):] if tag.startswith(NS) else tag


def kids(el, name):
    c = el.find(NS + name)
    return list(c) if c is not None else []


# ---------------------------------------------------------------- numbers / edges
TOK = re.compile(r"[!|/\[\]]|(?<!S)-?\d+(?:\.\d+)?|#[A-Z0-9]+\.[A-Z0-9]+")


def num(s):
    if s[0] == '#':
        a, b = s[1:].split('.')
        v = int.from_bytes(bytes.fromhex('{:>06}{:<02}'.format(a, b)), 'big', signed=True)
        return v / 256 / 20
    return float(s) / 20


def parse_edges(s):
    """Yield point lists: [p0, p1, (ctrl,), p2, ...]; tuple marks a quad control."""
    toks = TOK.findall(s)
    i = 0; cur = None; last = None
    while i < len(toks):
        t = toks[i]
        if t == '!':
            p = (num(toks[i + 1]), num(toks[i + 2])); i += 3
            if cur is None or p != last:
                if cur and len(cur) > 1: yield cur
                cur = [p]
            last = p
        elif t in '|/':
            p = (num(toks[i + 1]), num(toks[i + 2])); i += 3
            cur.append(p); last = p
        elif t in '[]':
            c = (num(toks[i + 1]), num(toks[i + 2])); p = (num(toks[i + 3]), num(toks[i + 4])); i += 5
            cur.append((c,)); cur.append(p); last = p
        else:
            i += 1
    if cur and len(cur) > 1: yield cur


def key(p):
    return (round(p[0], 2), round(p[1], 2))


def pl_to_d(pl):
    out = ['M%.2f %.2f' % pl[0]]
    i = 1
    while i < len(pl):
        p = pl[i]
        if isinstance(p, tuple) and len(p) == 1:
            c = p[0]; q = pl[i + 1]
            out.append('Q%.2f %.2f %.2f %.2f' % (c[0], c[1], q[0], q[1])); i += 2
        else:
            out.append('L%.2f %.2f' % p); i += 1
    return ''.join(out)


def join_fills(segs):
    """Join point lists (fill on left) into closed loops; return SVG d string."""
    loops = []; graph = {}
    for pl in segs:
        if key(pl[0]) == key(pl[-1]):
            loops.append(pl); continue
        graph.setdefault(key(pl[0]), []).append(pl)
    while graph:
        k0 = next(iter(graph)); pl = graph[k0].pop()
        if not graph[k0]: del graph[k0]
        path = list(pl); guard = 0
        while key(path[-1]) != key(path[0]) and guard < 10000:
            guard += 1
            nxt = graph.get(key(path[-1]))
            if not nxt: break
            seg = nxt.pop()
            if not nxt: del graph[key(path[-1])]
            path.extend(seg[1:])
        loops.append(path)
    return ''.join(pl_to_d(p) + 'Z' for p in loops)


# ---------------------------------------------------------------- matrices
I = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mat_of(el):
    m = el.find(NS + 'matrix')
    if m is None: return I
    m = m.find(NS + 'Matrix')
    if m is None: return I
    g = lambda k, d: float(m.get(k, d))
    return (g('a', 1), g('b', 0), g('c', 0), g('d', 1), g('tx', 0), g('ty', 0))


def mmul(m, n):  # m then n applied after? returns m*n (apply n first, then m)
    a, b, c, d, e, f = m; A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def tpoint(el):
    p = el.find(NS + 'transformationPoint')
    if p is None: return (0.0, 0.0)
    p = p.find(NS + 'Point')
    return (float(p.get('x', 0)), float(p.get('y', 0)))


def lerp_angle(a, b, t):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * t


def tween_matrix(m0, m1, p0, p1, t):
    def dec(m):
        a, b, c, d, _, _ = m
        return math.hypot(a, b), math.hypot(c, d), math.atan2(b, a), math.atan2(-c, d)
    sx0, sy0, ry0, rx0 = dec(m0); sx1, sy1, ry1, rx1 = dec(m1)
    sx = sx0 + (sx1 - sx0) * t; sy = sy0 + (sy1 - sy0) * t
    ry = lerp_angle(ry0, ry1, t); rx = lerp_angle(rx0, rx1, t)
    a, b, c, d = sx * math.cos(ry), sx * math.sin(ry), -sy * math.sin(rx), sy * math.cos(rx)
    w0 = (m0[0] * p0[0] + m0[2] * p0[1] + m0[4], m0[1] * p0[0] + m0[3] * p0[1] + m0[5])
    w1 = (m1[0] * p1[0] + m1[2] * p1[1] + m1[4], m1[1] * p1[0] + m1[3] * p1[1] + m1[5])
    wx = w0[0] + (w1[0] - w0[0]) * t; wy = w0[1] + (w1[1] - w0[1]) * t
    px = p0[0] + (p1[0] - p0[0]) * t; py = p0[1] + (p1[1] - p0[1]) * t
    return (a, b, c, d, wx - (a * px + c * py), wy - (b * px + d * py))


def ease(t, acc):
    a = acc / 100.0
    return t + a * t * (1 - t)


# ---------------------------------------------------------------- colour effects
def color_of(el):
    """Return (mult(r,g,b,a), off(r,g,b,a)) with offsets in 0..1, or None."""
    c = el.find(NS + 'color')
    if c is None: return None
    c = c.find(NS + 'Color')
    if c is None: return None
    g = lambda k, d=0.0: float(c.get(k, d))
    if 'brightness' in c.attrib:
        br = g('brightness')
        if br < 0: return ((1 + br,) * 3 + (1,), (0, 0, 0, 0))
        return ((1 - br,) * 3 + (1,), (br, br, br, 0))
    if 'tintMultiplier' in c.attrib or 'tintColor' in c.attrib:
        tm = g('tintMultiplier'); tc = c.get('tintColor', '#000000')
        r, gg, b = (int(tc[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return ((1 - tm,) * 3 + (1,), (tm * r, tm * gg, tm * b, 0))
    mult = (g('redMultiplier', 1), g('greenMultiplier', 1), g('blueMultiplier', 1), g('alphaMultiplier', 1))
    off = (g('redOffset') / 255, g('greenOffset') / 255, g('blueOffset') / 255, g('alphaOffset') / 255)
    return (mult, off)


ID_CT = ((1, 1, 1, 1), (0, 0, 0, 0))


def ct_mul(outer, inner):
    if outer is None: return inner
    if inner is None: return outer
    (m1, o1), (m2, o2) = outer, inner
    return (tuple(m1[i] * m2[i] for i in range(4)), tuple(m1[i] * o2[i] + o1[i] for i in range(4)))


def ct_lerp(c0, c1, t):
    c0 = c0 or ID_CT; c1 = c1 or ID_CT
    return (tuple(c0[0][i] + (c1[0][i] - c0[0][i]) * t for i in range(4)),
            tuple(c0[1][i] + (c1[1][i] - c0[1][i]) * t for i in range(4)))


# ---------------------------------------------------------------- styles
def rgba(color, alpha):
    return color or '#000000', float(alpha if alpha is not None else 1)


def fmtm(m):
    return 'matrix(%.5f %.5f %.5f %.5f %.3f %.3f)' % m


# ---------------------------------------------------------------- bitmaps
def decode_dat(src, out):
    """Animate bin/*.dat: raw JPEG, or 0x0503 lossless ARGB (premultiplied) in zlib chunks."""
    import struct, zlib, io
    from PIL import Image
    b = open(src, 'rb').read()
    if b[:2] == b'\xff\xd8':
        Image.open(io.BytesIO(b)).save(out); return
    if b[:2] != b'\x03\x05': return
    _, rowb, w, h = struct.unpack('<HHHH', b[:8])
    has_alpha, compressed = b[24], b[25]
    pos = 26; chunks = []
    if compressed:
        while pos + 2 <= len(b):
            n = struct.unpack('<H', b[pos:pos + 2])[0]; pos += 2
            if n == 0: break
            chunks.append(b[pos:pos + n]); pos += n
        raw = zlib.decompress(b''.join(chunks))
    else:
        raw = b[pos:]
    import numpy as np
    a = np.frombuffer(raw[:rowb * h], np.uint8).reshape(h, rowb)[:, :w * 4].reshape(h, w, 4).astype(np.float32)
    A, R, G, B = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    if has_alpha:
        k = np.where(A > 0, 255.0 / np.maximum(A, 1), 0)
        R, G, B = np.clip(R * k, 0, 255), np.clip(G * k, 0, 255), np.clip(B * k, 0, 255)
    else:
        A = np.full_like(A, 255)
    Image.fromarray(np.stack([R, G, B, A], -1).astype(np.uint8), 'RGBA').save(out)


# ---------------------------------------------------------------- document
class Timeline:
    def __init__(self, el):
        self.name = el.get('name')
        self.layers = []
        for L in kids(el, 'layers'):
            frames = []
            for F in kids(L, 'frames'):
                frames.append(F)
            self.layers.append((L, frames))
        self.length = max([int(F.get('index')) + int(F.get('duration', 1)) for _, fr in self.layers for F in fr] or [1])

    def frame_at(self, li, f):
        frames = self.layers[li][1]
        lo, hi = 0, len(frames) - 1
        res = None
        while lo <= hi:
            mid = (lo + hi) // 2
            if int(frames[mid].get('index')) <= f:
                res = mid; lo = mid + 1
            else:
                hi = mid - 1
        if res is None: return None, None
        F = frames[res]
        if f >= int(F.get('index')) + int(F.get('duration', 1)): return None, None
        return res, F


class XFL:
    def __init__(self, root, include_hidden=True):
        self.root = root; self.include_hidden = include_hidden
        self.doc = ET.parse(os.path.join(root, 'DOMDocument.xml')).getroot()
        self.width = float(self.doc.get('width', 550)); self.height = float(self.doc.get('height', 400))
        self.fps = float(self.doc.get('frameRate', 24))
        self.scenes = {T.get('name'): Timeline(T) for T in kids(self.doc, 'timelines')}
        self.items = {}  # name -> path
        for inc in kids(self.doc, 'symbols'):
            href = inc.get('href')
            self.items[href[:-4]] = os.path.join(root, 'LIBRARY', href)
        self.bitmaps = {}  # name -> (dat path, w, h)
        for b in kids(self.doc, 'media'):
            if strip(b.tag) == 'DOMBitmapItem' and b.get('bitmapDataHRef'):
                self.bitmaps[b.get('name')] = (os.path.join(root, 'bin', b.get('bitmapDataHRef')),
                                               float(b.get('frameRight', 0)) / 20, float(b.get('frameBottom', 0)) / 20)
        self._bmp_url = {}
        self.mute = False      # lock mouth ('lip') symbols to frame 0
        self.gclock = None     # 'still' mode: nested looping symbols follow this clock
        self._depth = 0
        self._tl = {}
        self.defs = {}; self.def_order = []; self._shape_cache = {}; self._grad = 0; self._filters = {}

    def timeline(self, name):
        if name in self.scenes: return self.scenes[name]
        if name not in self._tl:
            el = ET.parse(self.items[name]).getroot()
            self._tl[name] = Timeline(el.find(NS + 'timeline').find(NS + 'DOMTimeline'))
        return self._tl[name]

    # ------------------------------------------------ frame sequencing
    def reset_defs(self):
        self.defs = {}; self.def_order = []; self._filters = {}

    def child_frame(self, inst, offset, length):
        first = int(inst.get('firstFrame', 0)); loop = inst.get('loop', 'loop')
        last = inst.get('lastFrame')
        if strip(inst.tag) == 'DOMSymbolInstance' and inst.get('symbolType') == 'movie clip':
            return offset % length
        if loop == 'single frame': return min(first, length - 1)
        if last is not None:
            last = int(last); n = abs(last - first) + 1
        else:
            n = length - first if loop in ('play once', 'loop') else length
        if loop == 'play once': return min(first + offset, length - 1) if last is None else min(first + offset, last)
        if loop == 'play once reverse': return max(first - offset, 0)
        if loop == 'loop reverse': return (first - offset) % length
        # loop
        if last is not None: return first + offset % n
        return (first + offset) % length

    # ------------------------------------------------ rendering
    def render(self, timeline_name, frame):
        """Return full-stage SVG body (without <svg> wrapper) and defs for one frame."""
        self.reset_defs()
        body = self.render_timeline(self.timeline(timeline_name), frame)
        return body

    def svg(self, timeline_name, frame, width=None, height=None, view=None, bg=None):
        body = self.render(timeline_name, frame)
        vx, vy, vw, vh = view or (0, 0, self.width, self.height)
        w = width or vw; h = height or vh
        defs = ''.join(self.defs[k] for k in self.def_order)
        bgr = '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (vx, vy, vw, vh, bg) if bg else ''
        return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                'width="%d" height="%d" viewBox="%g %g %g %g"><defs>%s</defs>%s%s</svg>' % (w, h, vx, vy, vw, vh, defs, bgr, body))

    def render_timeline(self, tl, f):
        out = []
        layers = tl.layers
        types = [L.get('layerType', 'normal') for L, _ in layers]
        # layers listed top-first; render bottom-first
        n = len(layers); i = n - 1
        rendered = {}
        for li in range(n - 1, -1, -1):
            L, _ = layers[li]
            lt = types[li]
            if lt in ('guide', 'folder'): continue
            if not self.include_hidden and L.get('visible') == 'false': continue
            pi = L.get('parentLayerIndex')
            if pi is not None and types[int(pi)] == 'mask':
                continue  # drawn inside its mask group
            if lt == 'mask':
                masked = []
                for lj in range(n - 1, li, -1):
                    Lj, _ = layers[lj]
                    pj = Lj.get('parentLayerIndex')
                    if pj is not None and int(pj) == li and types[lj] not in ('guide', 'folder'):
                        if not self.include_hidden and Lj.get('visible') == 'false': continue
                        masked.append(self.render_layer(tl, lj, f))
                mbody = self.render_layer(tl, li, f)
                content = ''.join(masked)
                if not content: continue
                if not mbody:
                    continue
                mid = 'm%d' % len(self.def_order)
                self._add_def(mid, '<mask id="%s" maskUnits="userSpaceOnUse" x="-100000" y="-100000" width="200000" height="200000">'
                                   '<g filter="url(#%s)">%s</g></mask>' % (mid, self._white_filter(), mbody))
                out.append('<g mask="url(#%s)">%s</g>' % (mid, content))
                continue
            out.append(self.render_layer(tl, li, f))
        return ''.join(out)

    def _add_def(self, k, s):
        if k not in self.defs:
            self.defs[k] = s; self.def_order.append(k)

    def _white_filter(self):
        k = 'fw'
        self._add_def(k, '<filter id="fw" x="-100000" y="-100000" width="200000" height="200000" filterUnits="userSpaceOnUse" '
                         'color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 255 0"/></filter>')
        return k

    def render_layer(self, tl, li, f):
        fi, F = tl.frame_at(li, f)
        if F is None: return ''
        els = kids(F, 'elements')
        if not els: return ''
        start = int(F.get('index')); dur = int(F.get('duration', 1)); off = f - start
        tw = F.get('tweenType')
        nxt = None
        if tw and off > 0:
            frames = tl.layers[li][1]
            if fi + 1 < len(frames) and int(frames[fi + 1].get('index')) == start + dur:
                nxt = frames[fi + 1]
        t = ease(off / dur, float(F.get('acceleration', 0))) if nxt is not None else 0.0
        out = []
        nels = kids(nxt, 'elements') if nxt is not None else []
        for k, el in enumerate(els):
            el1 = None
            if nxt is not None and tw == 'motion' and k < len(nels) and strip(nels[k].tag) == strip(el.tag) \
                    and nels[k].get('libraryItemName') == el.get('libraryItemName'):
                el1 = nels[k]
            if nxt is not None and tw == 'shape' and strip(el.tag) == 'DOMShape' and k < len(nels):
                out.append(self.render_shape(el, I, None, other=nels[k], t=t)); continue
            out.append(self.render_element(el, off, el1, t))
        return ''.join(out)

    def render_element(self, el, off, el1=None, t=0.0):
        tag = strip(el.tag)
        m = mat_of(el)
        if tag == 'DOMShape':
            return self.render_shape(el, m)
        if tag == 'DOMGroup':
            # A group's own <matrix> duplicates the members' transforms (members carry
            # their own matrices), so it must NOT be applied again.
            return ''.join(self.render_element(c, off) for c in kids(el, 'members'))
        if tag == 'DOMSymbolInstance':
            ct = color_of(el)
            if el1 is not None:
                m = tween_matrix(m, mat_of(el1), tpoint(el), tpoint(el1), t)
                ct = ct_lerp(ct, color_of(el1), t) if (ct or color_of(el1)) else None
            name = el.get('libraryItemName')
            if name not in self.items: return ''
            tl = self.timeline(name)
            if self.gclock is not None and self._depth >= 1 and el.get('loop', 'loop') == 'loop':
                off = self.gclock
            cf = self.child_frame(el, off, tl.length)
            if self.mute and re.search('lip', name.split('/')[-1], re.I):
                cf = 0
            sid = self.symbol_def(name, cf)
            if sid is None: return ''
            node = '<use xlink:href="#%s" transform="%s"/>' % (sid, fmtm(m))
            return self.wrap_color(node, ct)
        if tag == 'DOMBitmapInstance':
            b = self.bitmap(el.get('libraryItemName'))
            if not b: return ''
            url, w, h = b
            return '<image href="%s" width="%g" height="%g" transform="%s" preserveAspectRatio="none"/>' % (url, w, h, fmtm(m))
        return ''

    def wrap_color(self, node, ct):
        if ct is None: return node
        mult, off = ct
        if mult[:3] == (1, 1, 1) and off == (0, 0, 0, 0):
            if mult[3] >= 0.999: return node
            return '<g opacity="%.4f">%s</g>' % (max(0.0, mult[3]), node)
        k = 'c' + '_'.join('%.3f' % v for v in mult + off)
        if k not in self._filters:
            fid = 'f%d' % len(self._filters); self._filters[k] = fid
            v = '%.4f 0 0 0 %.4f 0 %.4f 0 0 %.4f 0 0 %.4f 0 %.4f 0 0 0 %.4f %.4f' % (
                mult[0], off[0], mult[1], off[1], mult[2], off[2], mult[3], off[3])
            self._add_def(fid, '<filter id="%s" x="-100000" y="-100000" width="200000" height="200000" filterUnits="userSpaceOnUse" '
                               'color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="%s"/></filter>' % (fid, v))
        return '<g filter="url(#%s)">%s</g>' % (self._filters[k], node)

    def symbol_def(self, name, frame):
        sid = 's%x_%d_%s' % (abs(hash(name)) & 0xffffffff, frame, '' if self.gclock is None else self.gclock)
        if sid in self.defs: return sid
        self.defs[sid] = None  # recursion guard
        self._depth += 1
        try:
            body = self.render_timeline(self.timeline(name), frame)
        finally:
            self._depth -= 1
        self.defs[sid] = '<g id="%s">%s</g>' % (sid, body)
        self.def_order.append(sid)
        return sid

    # ------------------------------------------------ shapes
    def fill_attr(self, fs, prefix='fill'):
        """fs: FillStyle child element (SolidColor / gradient). Returns attribute string."""
        tag = strip(fs.tag)
        if tag == 'SolidColor':
            col, a = rgba(fs.get('color'), fs.get('alpha'))
            return '%s="%s"%s' % (prefix, col, (' %s-opacity="%.3f"' % (prefix, a)) if a < 1 else '')
        if tag in ('LinearGradient', 'RadialGradient'):
            self._grad += 1; gid = 'g%d' % self._grad
            m = mat_of(fs)
            stops = ''.join('<stop offset="%.4f" stop-color="%s" stop-opacity="%.3f"/>' % (
                float(e.get('ratio', 0)), e.get('color', '#000000'), float(e.get('alpha', 1)))
                for e in fs if strip(e.tag) == 'GradientEntry')
            spread = {'reflect': 'reflect', 'repeat': 'repeat'}.get(fs.get('spreadMethod'), 'pad')
            if tag == 'LinearGradient':
                g = '<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="-819.2" y1="0" x2="819.2" y2="0" spreadMethod="%s" gradientTransform="%s">%s</linearGradient>' % (gid, spread, fmtm(m), stops)
            else:
                fr = float(fs.get('focalPointRatio', 0))
                g = '<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="819.2" fx="%.2f" fy="0" spreadMethod="%s" gradientTransform="%s">%s</radialGradient>' % (gid, fr * 819.2, spread, fmtm(m), stops)
            self._add_def(gid, g)
            return '%s="url(#%s)"' % (prefix, gid)
        if tag == 'BitmapFill':
            b = self.bitmap(fs.get('bitmapPath'))
            if not b: return '%s="none"' % prefix
            url, w, h = b
            m = mat_of(fs); m = (m[0] / 20, m[1] / 20, m[2] / 20, m[3] / 20, m[4], m[5])
            self._grad += 1; gid = 'g%d' % self._grad
            self._add_def(gid, '<pattern id="%s" patternUnits="userSpaceOnUse" width="%g" height="%g" patternTransform="%s">'
                               '<image href="%s" width="%g" height="%g" preserveAspectRatio="none"/></pattern>' % (gid, w, h, fmtm(m), url, w, h))
            return '%s="url(#%s)"' % (prefix, gid)
        return '%s="#000000"' % prefix

    def bitmap(self, name):
        """Decode a library bitmap (.dat) to a cached PNG; return (file url, w, h)."""
        if name in self._bmp_url: return self._bmp_url[name]
        info = self.bitmaps.get(name); res = None
        if info and os.path.exists(info[0]):
            cache = os.path.join(self.root, '.bmpcache'); os.makedirs(cache, exist_ok=True)
            out = os.path.join(cache, '%x.png' % (abs(hash(info[0])) & 0xffffffff))
            if not os.path.exists(out):
                decode_dat(info[0], out)
            if os.path.exists(out):
                from PIL import Image
                w, h = Image.open(out).size
                res = ('file://' + out.replace(' ', '%20'), w if not info[1] else info[1], h if not info[2] else info[2])
        self._bmp_url[name] = res
        return res

    def render_shape(self, el, m, _unused=None, other=None, t=0.0):
        ck = (id(el), id(other), round(t, 3))
        if other is None and ck in self._shape_cache:
            body = self._shape_cache[ck]
        else:
            body = self._shape_body(el, other, t)
            if other is None: self._shape_cache[ck] = body
        # gradient defs must exist in this frame's defs too
        if other is None:
            for gid, g in self._shape_grads.get(id(el), []):
                self._add_def(gid, g)
        if m != I: return '<g transform="%s">%s</g>' % (fmtm(m), body)
        return body

    _shape_grads = {}

    def _shape_body(self, el, other, t):
        fills = {f.get('index'): list(f)[0] for f in kids(el, 'fills') if len(list(f))}
        strokes = {s.get('index'): list(s)[0] for s in kids(el, 'strokes') if len(list(s))}
        edges = [e for e in kids(el, 'edges') if e.get('edges')]
        if other is not None:
            oedges = [e for e in kids(other, 'edges') if e.get('edges')]
            if len(oedges) == len(edges):
                new = []
                ok = True
                for e0, e1 in zip(edges, oedges):
                    t0 = TOK.findall(e0.get('edges')); t1 = TOK.findall(e1.get('edges'))
                    if len(t0) != len(t1) or any((a in '!|/[]') != (b in '!|/[]') for a, b in zip(t0, t1)):
                        ok = False; break
                    merged = []
                    for a, b in zip(t0, t1):
                        if a in '!|/[]': merged.append(a)
                        else: merged.append('%.2f' % ((num(a) + (num(b) - num(a)) * t) * 20))
                    e = ET.Element(NS + 'Edge', dict(e0.attrib)); e.set('edges', ' '.join(merged)); new.append(e)
                if ok: edges = new
        fill_segs = {}; stroke_segs = {}
        for e in edges:
            f0, f1, st = e.get('fillStyle0'), e.get('fillStyle1'), e.get('strokeStyle')
            for pl in parse_edges(e.get('edges')):
                if f0: fill_segs.setdefault(f0, []).append(pl)
                if f1: fill_segs.setdefault(f1, []).append(pl[::-1])
                if st: stroke_segs.setdefault(st, []).append(pl)
        before = len(self.def_order)
        out = []
        for idx in sorted(fill_segs, key=lambda x: int(x)):
            if idx not in fills: continue
            d = join_fills(fill_segs[idx])
            out.append('<path d="%s" %s fill-rule="nonzero"/>' % (d, self.fill_attr(fills[idx])))
        for idx in sorted(stroke_segs, key=lambda x: int(x)):
            s = strokes.get(idx)
            if s is None: continue
            w = float(s.get('weight', 1))
            fill = s.find(NS + 'fill')
            fc = list(fill)[0] if fill is not None and len(list(fill)) else None
            attr = self.fill_attr(fc, 'stroke') if fc is not None else 'stroke="#000000"'
            caps = {'none': 'butt', 'square': 'square'}.get(s.get('caps'), 'round')
            joins = {'miter': 'miter', 'bevel': 'bevel'}.get(s.get('joints'), 'round')
            d = ''.join(pl_to_d(pl) for pl in stroke_segs[idx])
            out.append('<path d="%s" fill="none" %s stroke-width="%.2f" stroke-linecap="%s" stroke-linejoin="%s"/>' % (
                d, attr, max(w, 0.1), caps, joins))
        self._shape_grads[id(el)] = [(k, self.defs[k]) for k in self.def_order[before:]]
        return ''.join(out)

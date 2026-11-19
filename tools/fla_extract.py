#!/usr/bin/env python3
"""Extract an Adobe Animate .fla (XFL-in-zip) even when its central directory is broken.
Walks local file headers (PK\\x03\\x04) directly. Usage: fla_extract.py file.fla outdir"""
import sys, struct, zlib, os
data = open(sys.argv[1], 'rb').read(); out = sys.argv[2]; pos = 0; n = 0
while True:
    pos = data.find(b'PK\x03\x04', pos)
    if pos < 0: break
    (ver, flag, method, _, _, crc, csize, usize, nlen, xlen) = struct.unpack('<HHHHHIIIHH', data[pos+4:pos+30])
    name = data[pos+30:pos+30+nlen].decode('utf-8', 'replace'); start = pos+30+nlen+xlen
    if method == 8:
        d = zlib.decompressobj(-15)
        body = d.decompress(data[start:start+csize] if csize and not flag & 8 else data[start:])
        end = start + (csize if csize and not flag & 8 else len(data[start:]) - len(d.unused_data))
    else:
        if flag & 8 and not csize:  # stored with data descriptor: find next header
            nxt = data.find(b'PK\x03\x04', start); end = nxt if nxt > 0 else len(data)
            body = data[start:end]
        else:
            body = data[start:start+csize]; end = start + csize
    safe = os.path.normpath(name).lstrip('/')
    if safe.startswith('..'): pos = end; continue
    if not name.endswith('/'):
        p = os.path.join(out, safe); os.makedirs(os.path.dirname(p) or out, exist_ok=True)
        open(p, 'wb').write(body); n += 1
    pos = max(end, pos+4)
print(f"extracted {n} files")

# PVRT decode/encode (ARGB4444/1555/565, twiddled / VQ / paletted-free subset)
import struct, numpy as np
def detw(n):
    # morton index -> (x,y) for square n: bit0 -> y, bit1 -> x
    idx = np.arange(n * n); x = np.zeros_like(idx); y = np.zeros_like(idx)
    for b in range(int(np.log2(n))):
        y |= ((idx >> (2 * b)) & 1) << b
        x |= ((idx >> (2 * b + 1)) & 1) << b
    return x, y
def px2rgba(v, fmt):
    v = v.astype(np.uint32)
    if fmt == 2:   a, r, g, b = (v >> 12) & 15, (v >> 8) & 15, (v >> 4) & 15, v & 15; return np.stack([r*17, g*17, b*17, a*17], -1).astype(np.uint8)
    if fmt == 0:   a, r, g, b = (v >> 15) & 1, (v >> 10) & 31, (v >> 5) & 31, v & 31; return np.stack([r*255//31, g*255//31, b*255//31, a*255], -1).astype(np.uint8)
    if fmt == 1:   r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31; return np.stack([r*255//31, g*255//63, b*255//31, np.full_like(r, 255)], -1).astype(np.uint8)
def rgba2px(img, fmt):
    i = img.astype(np.uint32)
    if fmt == 2: return (((i[..., 3] >> 4) << 12) | ((i[..., 0] >> 4) << 8) | ((i[..., 1] >> 4) << 4) | (i[..., 2] >> 4)).astype(np.uint16)
    if fmt == 0: return (((i[..., 3] >> 7) << 15) | ((i[..., 0] >> 3) << 10) | ((i[..., 1] >> 3) << 5) | (i[..., 2] >> 3)).astype(np.uint16)
    if fmt == 1: return (((i[..., 0] >> 3) << 11) | ((i[..., 1] >> 2) << 5) | (i[..., 2] >> 3)).astype(np.uint16)
def header(b):
    p = b.find(b'PVRT')
    ln, fmt, typ, w, h = struct.unpack_from('<IBBxxHH', b, p + 4)
    return p, fmt, typ, w, h
def decode(b):
    p, fmt, typ, w, h = header(b); d = b[p + 16:]
    if typ == 3:  # VQ twiddled
        cb = np.frombuffer(d[:2048], '<u2').reshape(256, 4)
        n = w // 2; ix = np.frombuffer(d[2048:2048 + n * n], 'u1')
        x, y = detw(n); px = np.zeros((h, w), np.uint16)
        c = cb[ix]
        px[y * 2, x * 2] = c[:, 0]; px[y * 2 + 1, x * 2] = c[:, 1]; px[y * 2, x * 2 + 1] = c[:, 2]; px[y * 2 + 1, x * 2 + 1] = c[:, 3]
    elif typ == 1:
        v = np.frombuffer(d[:w * h * 2], '<u2'); x, y = detw(w); px = np.zeros((h, w), np.uint16); px[y, x] = v
    elif typ == 9:
        px = np.frombuffer(d[:w * h * 2], '<u2').reshape(h, w)
    else: raise ValueError('type %d' % typ)
    return px2rgba(px, fmt), fmt, typ

# AHF archive: 'AHFF', ver(2), count, hdr_end; entries: off,size,unk, name\0 padded to 4
import struct
def parse(b):
    assert b[:4] == b'AHFF', b[:4]
    ver, cnt, hs = struct.unpack_from('<III', b, 4)
    out = []; p = 0x10
    for i in range(cnt):
        off, size, unk = struct.unpack_from('<III', b, p)
        e = b.index(b'\0', p + 12)
        name = b[p + 12:e].decode('latin1')
        out.append(dict(i=i, off=off, size=size, unk=unk, name=name, ent=p))
        p = (e + 4) & ~3
    return out
def items(b):
    return [(e['name'], b[e['off']:e['off'] + e['size']], e['unk']) for e in parse(b)]
def build(its, ver=2):
    # its: list of (name, data, unk) ; data may be shared object identity for dedupe (same bytes -> same offset if dedupe)
    ent = bytearray()
    offs = []
    for name, data, unk in its:
        offs.append(len(ent))
        nm = name.encode('latin1') + b'\0'
        nm += b'\0' * ((-len(nm)) % 4)
        ent += b'\0' * 12 + nm
    tab_off = 0x10 + len(ent)
    dstart = tab_off + 4 * len(its); dstart += (-dstart) % 8
    out = bytearray(dstart)
    out[:16] = b'AHFF' + struct.pack('<III', ver, len(its), tab_off - 16)
    out[16:16 + len(ent)] = ent
    struct.pack_into('<%dI' % len(its), out, tab_off, *offs)
    seen = {}
    for (name, data, unk), o in zip(its, offs):
        key = bytes(data)
        if False and key in seen:  # original archives never share data; game processes entries in place
            pos = seen[key]
        else:
            pos = len(out); out += data; out += b'\0' * ((-len(out)) % 8); seen[key] = pos
        struct.pack_into('<III', out, 0x10 + o, pos, len(data), unk)
    return bytes(out)

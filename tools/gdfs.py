# GD-ROM (redump cue/bin) ISO9660 reader / in-place writer with EDC/ECC
import os, struct, sys
BASE = os.path.dirname(os.path.abspath(__file__)) + '/..'
NAME = 'Headhunter (Europe) (En,Fr,De,Es) (Disc %d) (Track %d).bin'
DISC = 1
T3_LBA = 45000

def track_layout(folder=BASE):
    return [(T3_LBA, 3, os.path.getsize(os.path.join(folder, NAME % (DISC, 3))) // 2352)]

class Disc:
    def __init__(self, folder=BASE, mode='rb', disc=None, path=None):
        global DISC
        if disc: DISC = disc
        self.layout = track_layout(folder)
        self.f = {n: open(path or os.path.join(folder, NAME % (DISC, n)), mode) for _, n, _ in self.layout}
    def loc(self, lba):
        for start, n, cnt in self.layout:
            if start <= lba < start + cnt:
                return n, (lba - start) * 2352
        raise ValueError('lba %d' % lba)
    def read_sector(self, lba):
        n, off = self.loc(lba); f = self.f[n]; f.seek(off); return f.read(2352)[16:16+2048]
    def read(self, lba, size):
        out = bytearray()
        for i in range((size + 2047) // 2048):
            out += self.read_sector(lba + i)
        return bytes(out[:size])
    def write_sector(self, lba, data2048):
        n, off = self.loc(lba); f = self.f[n]; f.seek(off); raw = bytearray(f.read(2352))
        if raw[16:16+2048] == bytes(data2048): return
        raw[16:16+2048] = data2048
        encode_mode1(raw, lba)
        f.seek(off); f.write(raw)
    def write(self, lba, data):
        data = bytes(data)
        for i in range(0, len(data), 2048):
            chunk = data[i:i+2048]
            if len(chunk) < 2048:
                chunk = chunk + self.read_sector(lba + i // 2048)[len(chunk):]
            self.write_sector(lba + i // 2048, chunk)
    def files(self):
        pvd = self.read_sector(T3_LBA + 16)
        rlba, rsize = struct.unpack_from('<I', pvd, 156 + 2)[0], struct.unpack_from('<I', pvd, 156 + 10)[0]
        out = {}
        def walk(lba, size, path):
            data = self.read(lba, size); p = 0
            while p < len(data):
                ln = data[p]
                if ln == 0:
                    p = (p // 2048 + 1) * 2048; continue
                elba, esz = struct.unpack_from('<I', data, p + 2)[0], struct.unpack_from('<I', data, p + 10)[0]
                fl = data[p + 25]; nl = data[p + 32]; nm = data[p + 33:p + 33 + nl]
                if nm not in (b'\0', b'\1'):
                    name = nm.decode('latin1').split(';')[0]
                    full = path + '/' + name
                    if fl & 2: walk(elba, esz, full)
                    else: out[full.lstrip('/')] = (elba, esz, lba, p)  # dir-record location
                p += ln
        walk(rlba, rsize, '')
        return out

# ---- EDC / ECC ----
EDC = []
for i in range(256):
    e = i
    for _ in range(8): e = (e >> 1) ^ (0xD8018001 if e & 1 else 0)
    EDC.append(e)
EF = [0]*256; EB = [0]*256
for i in range(256):
    j = (i << 1) ^ (0x11D if i & 0x80 else 0); EF[i] = j; EB[i ^ j] = i
def edc(b):
    e = 0
    for x in b: e = (e >> 8) ^ EDC[(e ^ x) & 0xFF]
    return e
def _ecc(sec, maj_cnt, min_cnt, maj_mult, min_inc, dst):
    size = maj_cnt * min_cnt
    for major in range(maj_cnt):
        index = (major >> 1) * maj_mult + (major & 1); a = b = 0
        for _ in range(min_cnt):
            t = sec[12 + index]; index += min_inc
            if index >= size: index -= size
            a ^= t; b ^= t; a = EF[a]
        a = EB[EF[a] ^ b]
        sec[dst + major] = a; sec[dst + major + maj_cnt] = a ^ b
def encode_mode1(sec, lba):
    sec[0:12] = b'\x00' + b'\xff'*10 + b'\x00'
    m = lba + 150
    bcd = lambda v: (v // 10) * 16 + v % 10
    sec[12] = bcd(m // 4500); sec[13] = bcd(m // 75 % 60); sec[14] = bcd(m % 75); sec[15] = 1
    struct.pack_into('<I', sec, 2064, edc(sec[0:2064]))
    sec[2068:2076] = b'\0'*8
    _ecc(sec, 86, 24, 2, 86, 2076)
    _ecc(sec, 52, 43, 86, 88, 2248)

if __name__ == '__main__':
    d = Disc(disc=int(sys.argv[1]) if len(sys.argv)>1 else 1)
    for k, v in sorted(d.files().items(), key=lambda x: x[1][0]): print('%8d %10d %s' % (v[0], v[1], k))

# ---- replace a file's content (in place if it fits, else relocate to free LBA) ----
def put(d, path, data, free, fs=None):
    fs = fs or d.files()
    lba, size, dlba, p = fs[path]
    need = (len(data) + 2047) // 2048
    if need <= (size + 2047) // 2048:
        nl = lba
    else:
        nl = free[0]; free[0] += need + 1
    pad = data + b'\0' * ((-len(data)) % 2048)
    d.write(nl, pad)
    sec = dlba + p // 2048; o = p % 2048
    s = bytearray(d.read_sector(sec))
    struct.pack_into('<I', s, o + 2, nl); struct.pack_into('>I', s, o + 6, nl)
    struct.pack_into('<I', s, o + 10, len(data)); struct.pack_into('>I', s, o + 14, len(data))
    d.write_sector(sec, bytes(s))
    fs[path] = (nl, len(data), dlba, p)
    return nl

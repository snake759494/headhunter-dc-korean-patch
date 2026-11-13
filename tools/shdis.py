# usage: dis.py file start end  (file offsets, hex). annotates pc-relative literals
import sys, struct, capstone as C
BASE = 0x8C010000
md = C.Cs(C.CS_ARCH_SH, C.CS_MODE_SH4 | C.CS_MODE_SHFPU | C.CS_MODE_LITTLE_ENDIAN)
def run(d, s, e, out=print):
    for o in range(s, e, 2):
        ins = list(md.disasm(d[o:o + 2], BASE + o))
        op = struct.unpack_from('<H', d, o)[0]
        txt = (ins[0].mnemonic + ' ' + ins[0].op_str) if ins else '.word 0x%04x' % op
        t = op >> 12; note = ''
        if t in (0xD, 0x9):
            pc = BASE + o; i8 = op & 0xff
            a = ((pc & ~3) + 4 + i8 * 4) if t == 0xD else (pc + 4 + i8 * 2)
            oo = a - BASE
            if 0 <= oo < len(d):
                v = struct.unpack_from('<I' if t == 0xD else '<h', d, oo)[0]; note = '  ; =%#x' % (v & 0xffffffff)
                vo = v - BASE
                if t == 0xD and 0 <= vo < len(d):
                    sbytes = d[vo:vo + 40].split(b'\0')[0]
                    if len(sbytes) >= 3 and all(32 <= c < 127 for c in sbytes): note += ' "%s"' % sbytes.decode()
        out('%08x %06x: %s%s' % (BASE + o, o, txt, note))
if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); run(d, int(sys.argv[2], 16), int(sys.argv[3], 16))

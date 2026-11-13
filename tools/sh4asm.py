# minimal SH4 assembler (subset) - two pass, labels, literals
import re,struct
R=lambda s:int(s.lower().lstrip('r'))
def FR(s): s=s.lower(); assert s.startswith('fr'); return int(s[2:])
def isreg(s): return re.fullmatch(r'r(1[0-5]|[0-9])',s.lower()) is not None
class Asm:
    def __init__(s,org): s.org=org
    def assemble(s,src,syms=None):
        lines=[]
        for l in src.split('\n'):
            l=l.split(';')[0].strip()
            if not l: continue
            while True:
                m=re.match(r'^([A-Za-z_.][\w.]*):\s*(.*)$',l)
                if not m: break
                lines.append(('label',m.group(1))); l=m.group(2).strip()
            if l: lines.append(('ins',l))
        s.syms=dict(syms or {})
        for p in (0,1):
            pc=s.org; out=bytearray()
            for k,v in lines:
                if k=='label':
                    if p==0: assert v not in s.syms,v; s.syms[v]=pc
                    continue
                b=s.one(v,pc,p); out+=b; pc+=len(b)
        return bytes(out)
    def val(s,e,p):
        e=e.strip()
        try: return int(eval(e,{},s.syms))
        except NameError:
            if p==0: return 0
            raise
    def one(s,t,pc,p):
        m=re.match(r'^(\S+)\s*(.*)$',t); op=m.group(1).lower(); a=m.group(2)
        args=[x.strip() for x in re.split(r',(?![^(]*\))',a)] if a else []
        W=lambda x:struct.pack('<H',x&0xffff)
        if op=='.long': return b''.join(struct.pack('<I',s.val(x,p)&0xffffffff) for x in args)
        if op=='.word': return b''.join(struct.pack('<H',s.val(x,p)&0xffff) for x in args)
        if op=='.byte': return bytes(s.val(x,p)&0xff for x in args)
        if op=='.float': return b''.join(struct.pack('<f',float(eval(x,{},s.syms))) for x in args)
        if op=='.ascii': return eval(a).encode('latin1')
        if op=='.align':
            n=int(args[0]); k=(-pc)%n
            return (b'\x09\x00'*(k//2)) if k%2==0 else b'\0'*k
        if op=='.space': return b'\0'*int(args[0])
        if op in('nop',): return W(0x0009)
        if op=='rts': return W(0x000b)
        def imm(x): return s.val(x[1:],p)
        def pcrel(lab,size):
            tgt=s.val(lab,p)
            if size==4: d=(tgt-((pc&~3)+4))
            else: d=tgt-(pc+4)
            if p:
                assert d%size==0 and 0<=d//size<256,(t,hex(pc),d)
            return (d//size)&0xff
        if op in('bt','bf','bt/s','bf/s'):
            tgt=s.val(args[0],p); d=(tgt-(pc+4))//2
            if p: assert -128<=d<128,t
            c={'bt':0x89,'bf':0x8b,'bt/s':0x8d,'bf/s':0x8f}[op]
            return W(c<<8|(d&0xff))
        if op in('bra','bsr'):
            tgt=s.val(args[0],p); d=(tgt-(pc+4))//2
            if p: assert -2048<=d<2048
            return W((0xa000 if op=='bra' else 0xb000)|(d&0xfff))
        if op in('jsr','jmp'):
            n=R(args[0][1:]); return W(0x4000|n<<8|(0x0b if op=='jsr' else 0x2b))
        two={'add':0x300c,'sub':0x3008,'cmp/eq':0x3000,'cmp/hs':0x3002,'cmp/ge':0x3003,'cmp/hi':0x3006,'cmp/gt':0x3007,
             'and':0x2009,'or':0x200b,'tst':0x2008,'xor':0x200a,'mul.l':0x0007,'extu.b':0x600c,'extu.w':0x600d,'exts.b':0x600e,'exts.w':0x600f,'neg':0x600b,'not':0x6007}
        if op in two and len(args)==2 and isreg(args[0]) and isreg(args[1]):
            return W(two[op]|R(args[1])<<8|R(args[0])<<4)
        one_={'shll':0x4000,'shlr':0x4001,'shll2':0x4008,'shlr2':0x4009,'shll8':0x4018,'shlr8':0x4019,'shll16':0x4028,'shlr16':0x4029,'dt':0x4010}
        if op in one_: return W(one_[op]|R(args[0])<<8)
        if op=='add' and args[0][0]=='#': return W(0x7000|R(args[1])<<8|(imm(args[0])&0xff))
        if op=='cmp/eq' and args[0][0]=='#': return W(0x8800|(imm(args[0])&0xff))
        if op=='and' and args[0][0]=='#': return W(0xc900|(imm(args[0])&0xff))
        if op=='tst' and args[0][0]=='#': return W(0xc800|(imm(args[0])&0xff))
        if op=='sts' and args[0].lower()=='macl': return W(0x001a|R(args[1])<<8)
        if op=='sts' and args[0].lower()=='fpul': return W(0x005a|R(args[1])<<8)
        if op=='sts' and args[0].lower()=='pr': return W(0x002a|R(args[1])<<8)
        if op=='lds' and args[1].lower()=='fpul': return W(0x405a|R(args[0])<<8)
        if op=='sts.l' and args[0].lower()=='pr': return W(0x4022|R(args[1][2:])<<8)
        if op=='lds.l' and args[1].lower()=='pr': return W(0x4026|R(args[0][1:-1])<<8)
        if op=='float': return W(0xf02d|FR(args[1])<<8)
        if op=='ftrc': return W(0xf03d|FR(args[0])<<8)
        fp={'fadd':0,'fsub':1,'fmul':2,'fdiv':3,'fmov':0xc}
        if op in fp and args[0].lower().startswith('fr') and args[1].lower().startswith('fr'):
            return W(0xf000|FR(args[1])<<8|FR(args[0])<<4|fp[op])
        if op in('fmov.s','fmov'):
            if args[0].startswith('@'): return W(0xf008|FR(args[1])<<8|R(args[0][1:])<<4)
            return W(0xf00a|R(args[1][1:])<<8|FR(args[0])<<4)
        if op=='mova':
            return W(0xc700|pcrel(args[0],4))
        if op in('mov','mov.b','mov.w','mov.l'):
            sz={'mov':None,'mov.b':0,'mov.w':1,'mov.l':2}[op]
            a0,a1=args
            if op=='mov' and a0[0]=='#': return W(0xe000|R(a1)<<8|(imm(a0)&0xff))
            if op=='mov' and isreg(a0) and isreg(a1): return W(0x6003|R(a1)<<8|R(a0)<<4)
            m0=re.fullmatch(r'@\(([^,]+),\s*(\w+)\)',a0); m1=re.fullmatch(r'@\(([^,]+),\s*(\w+)\)',a1)
            if not a0.startswith('@') and not a1.startswith('@') and not isreg(a0):
                # mov.l label,Rn  (pc relative literal)
                if sz==2: return W(0xd000|R(a1)<<8|pcrel(a0,4))
                if sz==1: return W(0x9000|R(a1)<<8|pcrel(a0,2))
            if m0 and m0.group(1).lower()=='r0':
                return W(0x000c|R(a1)<<8|R(m0.group(2))<<4|sz)
            if m1 and m1.group(1).lower()=='r0':
                return W(0x0004|R(m1.group(2))<<8|R(a0)<<4|sz)
            if m0:
                d=s.val(m0.group(1),p); m=R(m0.group(2))
                if sz==2: assert d%4==0 and d<64; return W(0x5000|R(a1)<<8|m<<4|d//4)
                assert a1.lower()=='r0'
                return W((0x8400 if sz==0 else 0x8500)|m<<4|(d>>sz))
            if m1:
                d=s.val(m1.group(1),p); n=R(m1.group(2))
                if sz==2: assert d%4==0 and d<64; return W(0x1000|n<<8|R(a0)<<4|d//4)
                assert a0.lower()=='r0'
                return W((0x8000 if sz==0 else 0x8100)|n<<4|(d>>sz))
            if a0.startswith('@-'): raise Exception(t)
            if a1.startswith('@-'): return W(0x2004|R(a1[2:])<<8|R(a0)<<4|sz)
            if a0.startswith('@') and a0.endswith('+'): return W(0x6004|R(a1)<<8|R(a0[1:-1])<<4|sz)
            if a0.startswith('@'): return W(0x6000|R(a1)<<8|R(a0[1:])<<4|sz)
            if a1.startswith('@'): return W(0x2000|R(a1[1:])<<8|R(a0)<<4|sz)
        raise Exception('unknown: '+t)

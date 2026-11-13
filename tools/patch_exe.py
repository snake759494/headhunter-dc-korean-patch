# patch 1ST_READ.BIN for Korean 2-byte glyphs (lead 0x80-0x9F, trail 0x80-0x9F|0xE0-0xFD; k=lead*62+t)
import sys,os,struct
sys.path.insert(0,os.path.dirname(__file__))
from sh4asm import Asm
BASE=0x8c010000
CAVE=0x8c0e7f84; CAVE_END=0x8c0e83e4
TD=int(os.environ.get('TD',512)); CS=int(os.environ.get('CS',20)); COLS=TD//CS; PER=COLS*COLS; ADV=CS*15//16
HA=ADV*128//CS
SITES=[ # name, site, resume, p_off, font_off, tex_off, rebuild
 ('A',0x8c0e867e,0x8c0e868a,8,36,32,0x8c0e8510),
 ('B',0x8c0e8f9a,0x8c0e8fac,0x94,32,28,0x8c0e8e2c),
 ('C',0x8c0e939c,0x8c0e93ae,0x98,36,32,0x8c0e922a),
 ('D',0x8c0e97c4,0x8c0e97d6,0x98,36,32,0x8c0e9652),
 ('E',0x8c0ea43e,0x8c0ea450,0x98,32,28,0x8c0ea2d0),
]
NPAGES=2
def texw():
    t='''TEXW:
  sts.l pr,@-r15
  mov.l r4,@-r15
  mov.l T_292C,r0
  jsr @r0
  nop
  mov.l r0,@-r15
'''
    for i in range(NPAGES):
        t+=f'''  mov.l @(4,r15),r4
  mova S_K{i},r0
  mov r0,r5
  mov.l T_292C,r0
  jsr @r0
  nop
  mov.l T_KTEX,r1
  mov.w r0,@({2*i},r1)
'''
    return t+'''  mov.l @r15+,r0
  add #4,r15
  lds.l @r15+,pr
  rts
  nop
'''
def kstr():
    return ''.join(f'S_K{i}: .ascii "KOR{i}"\n  .byte 0\n  .align 4\n' for i in range(NPAGES))
def src():
    s=f'''
KGET:
  mov.l @r5,r3
  mov.b @r3,r0
  extu.b r0,r0
  mov #0,r2
  mov r0,r6
  add #-128,r6
  mov #32,r7
  cmp/hs r7,r6
  bt notk
  mov.b @(1,r3),r0
  extu.b r0,r0
  add #-128,r0
  mov #32,r7
  cmp/hs r7,r0
  bf tok
  add #-96,r0
  mov #30,r7
  cmp/hs r7,r0
  bt notk
  add #32,r0
tok:
  mov #62,r7
  mul.l r7,r6
  sts macl,r6
  add r0,r6
  mov.w W_PER,r7
  mov.l T_KTEX,r1
pl:
  cmp/hs r7,r6
  bf t0
  sub r7,r6
  bra pl
  add #2,r1
t0:
  mov.w @r1,r1
  extu.w r1,r1
  mov #0,r7
  mov #{COLS},r3
cl:
  cmp/hs r3,r6
  bf cd
  sub r3,r6
  bra cl
  add #1,r7
cd:
  mova F_K,r0
  fmov.s @r0,fr5
  lds r6,fpul
  float fpul,fr0
  fmul fr5,fr0
  lds r7,fpul
  float fpul,fr1
  fmul fr5,fr1
  fmov fr1,fr3
  fadd fr5,fr3
  mov.w W_HALF,r0
  mov.b @(r0,r4),r6
  add r6,r6
  mov.w W_SP,r0
  mov.b @(r0,r4),r7
  add r7,r6
  mov.w W_W7F,r0
  mov.b r6,@(r0,r4)
  lds r6,fpul
  float fpul,fr2
  fmul fr5,fr2
  mov.w W_H,r0
  mov.b @(r0,r4),r7
  extu.b r7,r7
  lds r7,fpul
  float fpul,fr4
  fdiv fr4,fr2
  fadd fr0,fr2
  mov.w W_UV,r7
  add r4,r7
  fmov.s fr0,@r7
  add #4,r7
  fmov.s fr1,@r7
  add #4,r7
  fmov.s fr2,@r7
  add #4,r7
  fmov.s fr1,@r7
  add #4,r7
  fmov.s fr2,@r7
  add #4,r7
  fmov.s fr3,@r7
  add #4,r7
  fmov.s fr0,@r7
  add #4,r7
  fmov.s fr3,@r7
  mov #1,r2
  rts
  mov #127,r0
notk:
  mov.l @r5,r3
  mov.b @r3,r0
  extu.b r0,r0
  mov.w W_TEX,r1
  add r4,r1
  mov.w @r1,r1
  rts
  extu.w r1,r1

  .align 4
W_PER: .word {PER}
W_HALF: .word {0x202a+0x80}
W_SP: .word 0x212b
W_W7F: .word {0x202a+0x7f}
W_H: .word 0x212a
W_UV: .word {4+0x7f*32}
W_TEX: .word 0x2008
  .align 4
A_KTEX: .long KTEX
F_K: .float {CS/TD}

FIXW:
  mov.w X_H,r0
  mov.b @(r0,r4),r1
  extu.b r1,r1
  mov #{HA},r2
  mul.l r2,r1
  sts macl,r1
  add #127,r1
  add #1,r1
  shlr8 r1
  mov.w X_HALF,r0
  add r4,r0
  mov #32,r2
fl:
  mov.b r1,@r0
  dt r2
  bf/s fl
  add #1,r0
  mov r0,r5
  mov.w X_CASE,r0
  mov.b @(r0,r4),r2
  mov r5,r0
  mov #3,r5
  extu.b r2,r2
  cmp/eq r5,r2
  bt nc
  mov #64,r2
  bra fl2
  add #32,r0
nc:
  add #64,r0
  mov #30,r2
fl2:
  mov.b r1,@r0
  dt r2
  bf/s fl2
  add #1,r0
  mov.l @(4,r15),r2
  mov.l r4,@r2
  mov #1,r0
  add #12,r15
  lds.l @r15+,pr
  rts
  nop
X_H: .word 0x212a
X_CASE: .word 0x212c
X_HALF: .word {0x202a+0x80}

''' + texw() + '''
  .align 4
T_KTEX: .long KTEX
T_292C: .long 0x8c0c292c
KTEX: .word 0,0,0,0,0,0,0,0
LANGD: .long 0
''' + kstr() + ''''''
    for n,site,res,po,fo,to,rb in SITES:
        s+=f'''
ST_{n}:
  mov.l @({fo},r15),r4
  mov.w P_{n},r5
  add r15,r5
  mov.l AK_{n},r3
  jsr @r3
  nop
  mov r0,r6
  mov #{to},r0
  mov.w @(r0,r15),r3
  extu.w r3,r3
  cmp/eq r1,r3
  bt SM_{n}
  mov.w r1,@(r0,r15)
  mov.l RB_{n},r0
  jmp @r0
  nop
SM_{n}:
  mov.l @r5,r3
  add r2,r3
  add #1,r3
  mov.l r3,@r5
  mov r6,r0
  mov.b r0,@(7,r15)
  mov.l RS_{n},r0
  jmp @r0
  nop
P_{n}: .word {po}
  .align 4
RB_{n}: .long {rb}
RS_{n}: .long {res}
AK_{n}: .long KGET
'''
    return s
def jstub(org,target,pre=''):
    # mov.l lit,r0; jmp @r0; nop; align; lit
    return Asm(org).assemble(pre+f'''
  mov.l L,r0
  jmp @r0
  nop
  .align 4
L: .long {target}
''')
def patch(exe,npages=2):
    global NPAGES; NPAGES=npages
    exe=bytearray(exe)
    a=Asm(CAVE); code=a.assemble(src()); sy=a.syms
    assert CAVE+len(code)<=CAVE_END,(hex(len(code)))
    o=CAVE-BASE; exe[o:o+len(code)]=code
    for n,site,res,po,fo,to,rb in SITES:
        b=jstub(site,sy['ST_'+n]); assert site+len(b)<=res
        exe[site-BASE:site-BASE+len(b)]=b
    b=jstub(0x8c0e99e4,sy['FIXW'],'  mov.l @r15,r4\n'); assert len(b)<=0x10
    exe[0x8c0e99e4-BASE:0x8c0e99e4-BASE+len(b)]=b
    # CreateFont texture call literal -> TEXW
    # force language slot = 1 (German column/folder carries Korean); redirect all writers to a dummy word
    LANG=0x8c152470
    for lit in (0x8c029f74,0x8c07b708,0x8c0ee808):
        assert struct.unpack_from('<I',exe,lit-BASE)[0]==LANG
        struct.pack_into('<I',exe,lit-BASE,sy['LANGD'])
    struct.pack_into('<I',exe,LANG-BASE,int(os.environ.get('LANGSLOT',1)))
    if os.environ.get('NOTEXW'): return bytes(exe),len(code)
    o=0x8c0e7a7c-BASE; assert struct.unpack_from('<I',exe,o)[0]==0x8c0c292c
    struct.pack_into('<I',exe,o,sy['TEXW'])
    return bytes(exe),len(code)
if __name__=='__main__':
    d=os.path.join(os.path.dirname(__file__),'..')
    e,n=patch(open(os.path.join(d,'orig','1ST_READ.BIN'),'rb').read())
    os.makedirs(os.path.join(d,'build'),exist_ok=True)
    open(os.path.join(d,'build','1ST_READ.BIN'),'wb').write(e); print('code',n,'bytes')

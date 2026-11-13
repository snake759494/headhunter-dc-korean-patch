# build Korean-patched discs: python build.py [disc...]
import sys,os,shutil,struct
sys.path.insert(0,os.path.dirname(__file__))
import gdfs,ahf,patch_exe,kfont,title_tex,loc_tex
import kotext  # transform(name, bytes) -> str|None ; order_chars(texts)
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
ROOT=W
NAME='Headhunter (Europe) (En,Fr,De,Es) (Disc %d) (Track %d)'
FREE_LBA=50000
# level display names stored in map data (no CSV location row): (pattern, korean)
BINNAMES=[]  # NOTE: map-internal names (e.g. 'Docks' in S69_DN) double as lookup keys; patching them crashes the level
STRICT=not os.environ.get('LOOSE')
def enc(s,cmap):
    out=bytearray()
    for ch in s.replace(chr(0x20ac),'E'):
        o=ord(ch)
        if o<0x80 or (not STRICT and o<0x100) or (0xc0<=o<0xe0) or o in (0xa7,0xaa,0xba): out.append(o)
        elif ch in cmap: out+=kfont.code(cmap[ch])
        elif o<0x100:
            import unicodedata; a=unicodedata.normalize('NFD',ch)[0]
            out.append(ord(a) if ord(a)<0x80 else 39)
        else: raise ValueError('unmapped char %r in %r'%(ch,s[:80]))
    return bytes(out)
def scan(disc):
    """yield (kind, path, entryname, data) for every text-bearing item"""
    d=gdfs.Disc(disc=disc); fs=d.files()
    for path,(lba,size,_,_) in sorted(fs.items()):
        if path.upper().endswith('.AHF'):
            b=d.read(lba,size)
            for e in ahf.parse(b): yield 'ahf',path,e['name'],b[e['off']:e['off']+e['size']]
        elif path.upper().startswith('HEADHUNTER/'):
            yield 'iso',path,path.replace('/','\\'),d.read(lba,size)
    for f in d.f.values(): f.close()
def collect(discs):
    res={}
    for disc in discs:
        for kind,path,name,data in scan(disc):
            if (name.upper(),data) in res: continue
            t=kotext.transform(name,data)
            if t is not None: res[(name.upper(),data)]=t
    return res
def build_disc(disc,T,cmap,kor_pvrs,exe):
    src=os.path.join(ROOT,NAME%(disc,3)+'.bin'); dst=os.path.join(ROOT,NAME%(disc,3)+' [KR].bin')
    print('copy',disc,flush=True); shutil.copyfile(src,dst)
    d=gdfs.Disc(disc=disc,mode='r+b',path=dst); fs=d.files(); free=[FREE_LBA]
    if not os.environ.get('NOEXE'): gdfs.put(d,'1ST_READ.BIN',exe,free,fs)
    for path in sorted(fs):
        lba,size,_,_=fs[path]
        if os.environ.get('VERB'): print('>',path,flush=True)
        if path.upper().endswith('.AHF'):
            b=d.read(lba,size); ch=False; new=[]
            for nm,data,unk in ahf.items(b):
                t=T.get((nm.upper(),data))
                if t is not None: data=enc(t,cmap); ch=True
                elif 'TITLE_LOCALTEXT' in nm.upper(): data=title_tex.make(data)[0]; ch=True
                elif loc_tex.target(nm): data=loc_tex.make(nm,data)[0]; ch=True
                for pat,ko in BINNAMES:
                    if pat in data:
                        k=enc(ko,cmap); assert len(k)<=5
                        data=data.replace(pat,b'\x00'+k.ljust(7,b'\x00')+pat[9:]); ch=True
                new.append((nm,data,unk))
            if path.upper().endswith('HEADHUNTER.AHF'):
                for i,p in enumerate(kor_pvrs): new.append(('HEADHUNTER\\TEXTURE\\FONTS\\KOR%d.PVR'%i,p,0)); ch=True
            if ch:
                nb=ahf.build(new); nl=gdfs.put(d,path,nb,free,fs)
                if nl!=lba or len(nb)>size: print(' ',path,size,'->',len(nb),'@',nl,flush=True)
        elif path.upper().startswith('HEADHUNTER/'):
            data=d.read(lba,size); t=T.get((path.replace('/','\\').upper(),data))
            if t is not None: gdfs.put(d,path,enc(t,cmap),free,fs)
    for f in d.f.values(): f.close()
    cue=open(os.path.join(ROOT,'Headhunter (Europe) (En,Fr,De,Es) (Disc %d).cue'%disc),encoding='latin1').read()
    cue=cue.replace(NAME%(disc,3)+'.bin',NAME%(disc,3)+' [KR].bin')
    open(os.path.join(ROOT,'Headhunter (Europe) (En,Fr,De,Es) (Disc %d) [KR].cue'%disc),'w',encoding='latin1',newline='').write(cue)
def main(discs):
    T=collect([1,2])
    if kotext.MISSING:
        open(os.path.join(W,'missing.txt'),'w',encoding='utf8').write(chr(10).join(r+chr(9)+kotext.key(e) for (r,e) in kotext.MISSING))
        print('MISSING translations:',len(kotext.MISSING),'(see missing.txt)')
        if STRICT: raise SystemExit(1)
    chars=kotext.order_chars(T.values())
    cmap={c:i for i,c in enumerate(chars)}
    print('texts',len(T),'glyphs',len(chars),flush=True)
    pvrs,_=kfont.build(chars)
    exe,_=patch_exe.patch(open(os.path.join(W,'orig','1ST_READ.BIN'),'rb').read(),len(pvrs))
    for disc in discs: build_disc(disc,T,cmap,pvrs,exe)
if __name__=='__main__':
    main([int(x) for x in sys.argv[1:]] or [1,2])

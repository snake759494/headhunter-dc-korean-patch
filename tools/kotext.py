# translation provider: rebuild Korean LOCALE text files from tr/*.json translation memory
import os,json,glob,re,hashlib
from collections import Counter
import segs
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
BS=chr(92)
LANGS=('ENGLISH','GERMAN','FRENCH','SPANISH','ITALIAN')
_TM=None; _G=None; _EN=None; _F=None
MISSING=Counter()
def _load():
    global _TM,_G,_EN,_F
    if _TM is not None: return
    _TM={}; _G={}
    for p in glob.glob(os.path.join(W,'tr','*.json')):
        d=json.load(open(p,encoding='utf8'))
        m={s['h']:s['ko'] for s in d['segs'] if s['ko'].strip()}  # key = SHA-1(English source)[:16]
        _TM[d['rel'].upper()]=m
        for k,v in m.items(): _G.setdefault(k,v)
    j=json.load(open(os.path.join(W,'text_index.json')))
    _EN={}
    for fn,info in j.items():
        r=relname(info['name'])
        if r and (fn.startswith('ENGLISH__') or not any(fn.startswith(l+'__') for l in LANGS)):
            _EN[r.upper()]=open(os.path.join(W,'text_en',fn),'rb').read()
    _F=json.load(open(os.path.join(W,'fonts.json')))
def relname(name):
    parts=name.replace('/',BS).split(BS)
    if 'LOCALE' not in [p.upper() for p in parts]: return None
    i=[p.upper() for p in parts].index('LOCALE'); rest=parts[i+1:]
    if rest and rest[0].upper() in LANGS: rest=rest[1:]
    return BS.join(rest)
def key(en): return hashlib.sha1(en.encode('utf8')).hexdigest()[:16]
def tr(rel,en):
    m=_TM.get(rel.upper(),{}); h=key(en)
    if h in m: return m[h]
    if h in _G: return _G[h]
    MISSING[(rel,en)]+=1
    return en
# ---- width model (pixels at font's native size) ----
from patch_exe import HA
def width(s,font='Font_Small'):
    f=_F[font]; h=f['h']; sp=f['sp']; half=(h*HA+128)>>8; w=0
    for c in s:
        if '가'<=c<='힣': w+=2*half+2*sp
        else:
            o=ord(c) if ord(c)<256 else 32
            w+=f['w'][o]+sp
    return w
def wrap(text,maxw,indent='',font='Font_Small'):
    words=text.split(' '); lines=[]; cur=''
    for wd in words:
        t=(cur+' '+wd) if cur else wd
        pre=indent if lines else ''
        if cur and width(pre+t,font)>maxw: lines.append(cur); cur=wd
        else: cur=t
    if cur: lines.append(cur)
    return [ (indent if i else '')+l for i,l in enumerate(lines)]
def _txt(rel,data):
    k=segs.kind(rel); t=segs.dec(data)
    if k=='sub':
        out=[]; enmax=0
        for p,x in segs.split_sub(t):
            for l in x.split('\n'): enmax=max(enmax,width(l))
        for p,x in segs.split_sub(t):
            if not x.strip(): out.append(p+x); continue
            ko=tr(rel,x)
            lines=[]
            for l in ko.split('\n'):
                l=l.strip()
                if width(l)>enmax*1.02: lines+=wrap(l,enmax)
                else: lines.append(l)
            out.append(p+'\r\n'.join(lines))
        return '\r\n'.join(out)
    if k=='wrap':
        enmax=max(width(l) for l in t.split('\r\n'))
        out=[]
        for b in segs.split_wrap(t):
            if b is None: out.append(''); continue
            for _,ind,ls in b:
                en=' '.join(ls); ko=tr(rel,en)
                m=re.match(r'^(\d+\)\s*)',ko)
                hang=' '*ind if ind else ('   ' if m else '')
                out+=wrap(ko,enmax,hang)
        # split_wrap emits None for each blank line; blocks are not separated otherwise
        return '\r\n'.join(out)
    out=[]
    for l in t.split('\r\n'):
        out.append(tr(rel,l) if l.strip() else l)
    return '\r\n'.join(out)
def _csv(rel,data):
    t=segs.dec(data); out=[]
    for l in t.split('\r\n'):
        s=l.strip(); q=s.startswith('"')
        cols=s.strip('"').split(';')
        if len(cols)<2: out.append(l); continue
        en=cols[0] if q else cols[1]
        if not en.strip(): out.append(l); continue
        ko=tr(rel,en)
        if q:
            for i in range(1,min(4,len(cols))): cols[i]=ko
            out.append('"'+';'.join(cols)+'"')
        else:
            for i in range(1,min(5,len(cols))): cols[i]=ko
            out.append(';'.join(cols))
    for key,ko in EXTRA.get(rel.upper(),[]):
        out.insert(len(out)-1 if out and not out[-1].strip() else len(out),';'.join([key]+[ko]*4)+';;')
    return '\r\n'.join(out)
# the game looks up a level's script location name (in its .ASB) as a key in the level CSV;
# these levels lack that row, so append one (appended at the end so row indices stay the same)
EXTRA={'S69_DN.CSV':[('Docks','부두')],'SXX_FA_NIGHT.CSV':[('North District','노스 지구')]}
def transform(name,data):
    _load()
    rel=relname(name)
    if not rel: return None
    u=rel.upper()
    if u.endswith('.CSV'):
        if not data.strip(): return None
        return _tail(_csv(rel,data),data)
    if u.endswith('.TXT'):
        src=_EN.get(u)
        if src is None or not src.strip(): return None
        return _tail(_txt(rel,src),src)
    return None
def _tail(t,src):
    # keep the source's trailing line break(s): the game's parsers expect them
    n=len(src)-len(src.rstrip(b'\r\n'))
    return t.rstrip('\r\n')+src[len(src)-n:].decode('latin1') if n else t
def order_chars(texts):
    c=Counter()
    for v in texts:
        for ch in v:
            if '가'<=ch<='힣': c[ch]+=1
    return [ch for ch,_ in c.most_common()]

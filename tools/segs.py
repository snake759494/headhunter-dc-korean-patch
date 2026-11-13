# shared segmentation rules for translation extraction / application
import re
REWRAP_FILES={'FILE_DEFEATED_GREYWOLF.TXT','FILE_INTRODUCTION.TXT','FILE_PALMERA_MALL_INFO.TXT',
              'FILE_PROJECTMODINFO.TXT','FILE_PROJ_MILLENIUM.TXT'}
QUOTED_CSV={'STRING_COLLECTION.CSV','INVENTORY.CSV','DATABASE_CAPTIONS.CSV'}
def dec(b): return b.decode('cp1252',errors='replace') if isinstance(b,bytes) else b
def kind(rel):
    r=rel.upper()
    if r.endswith('.CSV'): return 'csv'
    if r.startswith('SUBTITLE\\'): return 'sub'
    base=r.split('\\')[-1]
    if base in REWRAP_FILES or base.startswith('OBJECTIVE_'): return 'wrap'
    return 'line'
def split_sub(t):
    """-> list of (prefix, text) ; prefix like ';00:13;'"""
    out=[]; cur=None
    for l in t.split('\r\n'):
        m=re.match(r'^(;[^;]*;)(.*)$',l)
        if m:
            cur=[m.group(1),[m.group(2)]]; out.append(cur)
        elif cur is not None: cur[1].append(l)
        else: out.append(['',[l]])
    return [(p,'\n'.join(x).rstrip()) for p,x in out]
def split_wrap(t):
    """-> list of blocks; block = list of items (indent, text)"""
    blocks=[];cur=[]
    for l in t.split('\r\n'):
        if not l.strip():
            if cur: blocks.append(cur); cur=[]
            blocks.append(None); continue
        ind=len(l)-len(l.lstrip(' '))
        if cur and ind>0 and cur[-1][0]==0 and not re.match(r'^\s*\d+\)',l):
            cur[-1][2].append(l.strip()); cur[-1][1]=max(cur[-1][1],ind)
        elif cur and ind==0 and not re.match(r'^\d+\)',l) and not re.match(r'^\d+\)',cur[-1][2][0]) :
            cur[-1][2].append(l.strip())
        else:
            cur.append([0,ind if ind else 0,[l.strip()]])
    if cur: blocks.append(cur)
    return blocks
def segments(rel,data):
    """English segments (unicode) in file order"""
    t=dec(data); k=kind(rel)
    if k=='csv':
        out=[]
        for l in t.split('\r\n'):
            q=l.strip().startswith('"')
            cols=l.strip().strip('"').split(';')
            if len(cols)<2: continue
            en=cols[0] if q else cols[1]
            if en.strip(): out.append(en)
        return out
    if k=='sub': return [x for p,x in split_sub(t) if x.strip()]
    if k=='wrap':
        out=[]
        for b in split_wrap(t):
            if b:
                for it in b: out.append(' '.join(it[2]))
        return out
    return [l for l in t.split('\r\n') if l.strip()]

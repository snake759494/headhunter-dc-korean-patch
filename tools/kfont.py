# render Korean glyph textures (1024x1024 ARGB4444 VQ) for the 2-byte code scheme
from paths import fontpath
import sys,os,struct,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__))
import pvr
from patch_exe import CS,COLS,PER,ADV,TD
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
FONT=fontpath('NanumSquareNeo-cBd.ttf')
GRAY=(0xcc,0xcc,0xcc)
def code(k):
    l,t=divmod(k,62); assert l<32
    return bytes([0x80+l,0x80+t if t<32 else 0xc0+t])
def render(chars,size=None):
    size=size or round(CS*0.84)
    f=ImageFont.truetype(FONT,size)
    pages=[]
    for pg in range((len(chars)+PER-1)//PER or 1):
        im=Image.new('L',(TD,TD),0); d=ImageDraw.Draw(im)
        for i,ch in enumerate(chars[pg*PER:(pg+1)*PER]):
            col,row=i%COLS,i//COLS
            x0,y0=col*CS,row*CS
            bb=d.textbbox((0,0),ch,font=f)
            w=bb[2]-bb[0]
            # center horizontally in ADV, vertically by font metrics
            asc,desc=f.getmetrics()
            x=x0+(ADV-w)/2-bb[0]; y=y0+(CS-(asc+desc))/2-1
            d.text((x,y),ch,font=f,fill=255)
        pages.append(np.array(im))
    return pages
def kmeans(X,k=256,it=12,seed=1):
    rng=np.random.default_rng(seed)
    U,cnt=np.unique(X,axis=0,return_counts=True)
    if len(U)<=k:
        C=np.zeros((k,X.shape[1]),np.float32); C[:len(U)]=U; return C
    # weighted kmeans on unique vectors
    C=U[rng.choice(len(U),k,replace=False,p=cnt/cnt.sum())].astype(np.float32)
    Uf=U.astype(np.float32); w=cnt.astype(np.float32)
    for _ in range(it):
        d=((Uf[:,None,:]-C[None,:,:])**2).sum(-1); a=d.argmin(1)
        for j in range(k):
            m=a==j
            if m.any(): C[j]=(Uf[m]*w[m,None]).sum(0)/w[m].sum()
    return C
def vq(alpha):
    # alpha: 1024x1024 uint8 -> PVR VQ bytes (ARGB4444, twiddled VQ)
    n=alpha.shape[0]//2
    a4=(alpha.astype(np.int32)+8)//17
    a4=np.clip(a4,0,15)
    x,y=pvr.detw(n)
    blk=np.stack([a4[y*2,x*2],a4[y*2+1,x*2],a4[y*2,x*2+1],a4[y*2+1,x*2+1]],-1)
    C=kmeans(blk)
    Cq=np.clip(np.rint(C),0,15).astype(np.int32)
    # assign in chunks
    idx=np.empty(len(blk),np.uint8)
    for s in range(0,len(blk),65536):
        d=((blk[s:s+65536,None,:]-Cq[None])**2).sum(-1); idx[s:s+65536]=d.argmin(1)
    r,g,b=[c>>4 for c in GRAY]
    cb=(Cq<<12)|(r<<8)|(g<<4)|b
    cb=cb.astype('<u2').tobytes()
    body=cb+idx.tobytes()
    hdr=b'PVRT'+struct.pack('<IBBxxHH',len(body)+8,2,3,alpha.shape[1],alpha.shape[0])
    return hdr+body
def build(chars):
    pages=render(chars)
    out=[vq(p) for p in pages]
    if len(out)<1: out.append(vq(np.zeros((8,8),np.uint8)))
    return out,pages
if __name__=='__main__':
    chars=sys.argv[1]
    t,p=build(chars)
    for i,(b,pg) in enumerate(zip(t,p)):
        open(f'KOR{i}.PVR','wb').write(b)
        img,_,_=pvr.decode(b); Image.fromarray(img[:256,:512]).save(f'view/kor{i}.png')

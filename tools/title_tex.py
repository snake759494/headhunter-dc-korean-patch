# Korean replacement for TITLE_LOCALTEXT.PVR (German "START-TASTE DRUECKEN" band)
from paths import fontpath
import os,sys,struct,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import pvr,kfont
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
TEXT='START 버튼을 누르세요'
Y0,Y1=41,62      # German first band
Y2,Y3,X3=63,86,48  # German continuation band (cleared)
# this game stores fmt 5 ("PAL4") textures with plain ARGB1555 VQ codebooks
FMAP={5:0,6:0}
def fmt_of(b):
    p=b.find(b'PVRT'); f=b[p+8]; return FMAP.get(f,f)
def decode(b):
    x=bytearray(b); p=x.find(b'PVRT'); x[p+8]=fmt_of(b)
    img,_,_=pvr.decode(bytes(x)); return img
def encode(b,img):
    p=b.find(b'PVRT'); w,h=struct.unpack_from('<HH',b,p+12); f=fmt_of(b)
    q=pvr.px2rgba(pvr.rgba2px(img,f),f).astype(np.int32)   # snap to the target format first
    n=w//2; x,y=pvr.detw(n)
    blk=np.stack([q[y*2,x*2],q[y*2+1,x*2],q[y*2,x*2+1],q[y*2+1,x*2+1]],1).reshape(len(x),16)
    C=np.clip(np.rint(kfont.kmeans(blk)),0,255).astype(np.uint8)
    Cf=C.astype(np.int32); idx=np.empty(len(blk),np.uint8)
    for s in range(0,len(blk),8192):
        d=((blk[s:s+8192,None,:]-Cf[None])**2).sum(-1); idx[s:s+8192]=d.argmin(1)
    cb=pvr.rgba2px(C.reshape(256,4,4),f)
    body=cb.astype('<u2').tobytes()+idx.tobytes()
    return b[:p+16]+body+b[p+16+len(body):]
def make(b):
    img=decode(b).copy()
    band=img[Y0:Y1]; fg=np.abs(band.astype(int)[...,:3]).sum(2)>60
    cols=[band[r][fg[r]].mean(0) if fg[r].any() else None for r in range(Y1-Y0)]
    bgpx=img[200,10].copy()
    img[Y0:Y1]=bgpx; img[Y2:Y3,:X3]=bgpx
    H=Y1-Y0; font=ImageFont.truetype(fontpath('NanumSquareNeo-eHv.ttf'),H-5)
    L=Image.new('L',(256,H)); dr=ImageDraw.Draw(L)
    tw=dr.textlength(TEXT,font=font); dr.text((int((256+X3-tw)/2),H//2),TEXT,font=font,fill=255,anchor='lm')
    m=np.array(L).astype(float)/255
    o=np.array(L.filter(ImageFilter.MaxFilter(3))).astype(float)/255
    out=img[Y0:Y1].astype(float)
    for r in range(H):
        c=np.array([200+40*r//H,235,255,255.])
        dark=np.array([0,0,40,255.])
        px=dark*o[r,:,None]+out[r]*(1-o[r,:,None])
        px=c*m[r,:,None]+px*(1-m[r,:,None]); out[r]=px
    img[Y0:Y1]=np.clip(out,0,255).astype(np.uint8)
    return encode(b,img),img,tw
if __name__=='__main__':
    import gdfs,ahf
    d=gdfs.Disc(disc=1);fs=d.files();lba,size,_,_=fs['AHFDATA/MAINMENU.AHF'];a=d.read(lba,size)
    for e in ahf.parse(a):
        if 'TITLE_LOCALTEXT' in e['name']:
            nb,img,tw=make(a[e['off']:e['off']+e['size']]); print('w',tw)
            Image.fromarray(decode(nb)).resize((512,512),0).save(os.path.join(ROOT,'view','t_ko.png'))

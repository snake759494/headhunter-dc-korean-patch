# Korean replacements for language-specific textures (German slot is the one the game shows)
from paths import fontpath
import os,sys,re,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import pvr,title_tex
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
F_BOLD=fontpath('NanumSquareNeo-eHv.ttf')
F_REG=fontpath('NanumSquareNeo-cBd.ttf')
def font(path,px):
    return ImageFont.truetype(path,px)
def draw_text(img,txt,cx,cy,fpath,px,color,anchor='mm'):
    L=Image.new('L',(img.shape[1],img.shape[0]));d=ImageDraw.Draw(L)
    d.text((cx,cy),txt,font=font(fpath,px),fill=255,anchor=anchor)
    m=np.array(L).astype(float)[...,None]/255
    c=np.array(color,float)
    out=img.astype(float); out=c*m+out*(1-m)
    return np.clip(out,0,255).astype(np.uint8)
# ---------- buttons ----------
LABELS={'YESNO':['예','예','아니오','아니오','시작','시작'],'CANCEL':['취소','취소']}
def buttons(img,labels):
    a=img.astype(int); h,w=a.shape[:2]
    # frame rows: bright opaque rows across the left cell column
    v=a[:,10:70,:3].sum(2).mean(1); al=a[:,10:70,3].mean(1)
    mn=a[:,10:70,:3].sum(2).min(1); amin=a[:,10:70,3].min(1)
    fr=(mn>480)&(amin>200)   # frame rows are uniformly bright across the cell
    edges=[y for y in range(h) if fr[y]]
    xs=np.where(a[edges[0],:,:3].sum(1)>540)[0] if edges else np.arange(w)
    x0,x1=xs.min(),xs.max()
    # bands = runs of non-frame rows
    bands=[];s=None
    for y in range(h+1):
        nf=y<h and not fr[y]
        if nf and s is None: s=y
        if not nf and s is not None: bands.append((s,y)); s=None
    out=img.copy(); k=0
    for y0,y1 in bands:
        if k>=len(labels): break
        if y1-y0<8: continue
        reg=a[y0:y1,x0+2:x1-1]
        edge=np.concatenate([reg[:,1:4],reg[:,-4:-1]],1)
        bg=np.median(edge,axis=1)           # per-row background from the cell's side edges
        diff=np.abs(reg-bg[:,None,:]).sum(2)
        m=diff>70
        if m.sum()<12: continue
        ys,xx=np.where(m)
        ty0,ty1=ys.min(),ys.max()+1
        # rows touched by text: rebuild their background by interpolating the clean rows around them
        a0=max(0,ty0-1); a1=min(len(bg)-1,ty1)
        for r in range(ty0,ty1):
            t=(r-a0)/max(1,a1-a0); bg[r]=bg[a0]*(1-t)+bg[a1]*t
        diff=np.abs(reg-bg[:,None,:]).sum(2); m=diff>70
        ys,xx=np.where(m)
        ty0,ty1=ys.min(),ys.max()+1; tx0,tx1=xx.min(),xx.max()+1
        t=reg[m]; br=t[:,:3].sum(1); col=t[br>=np.percentile(br,85)].mean(0)
        if col[3]<200: col[3]=255
        # erase text: replace bbox (+1) with row background
        yy0=max(0,ty0-1); yy1=min(y1-y0,ty1+1)
        for r in range(yy0,yy1):
            out[y0+r,x0+3:x1-2]=bg[r].astype(np.uint8)
        hgt=ty1-ty0
        cx=(x0+x1)/2; cy=y0+(ty0+ty1)/2
        px=min(int(round(hgt*1.3)),y1-y0-3)
        while px>8 and font(F_BOLD,px).getlength(labels[k])>x1-x0-8: px-=1
        out=draw_text(out,labels[k],cx,cy,F_BOLD,px,col)
        k+=1
    return out
# ---------- 50/60Hz notice ----------
HZ_TEXT='60Hz 모드는 더 부드럽고 빠른 화면 갱신을 제공하지만, 일부 TV는 이 모드를 지원하지 않습니다. TV가 60Hz에서 정상 작동하는지 확실하지 않다면 TEST 옵션을 선택하십시오.'
HZ_Q='화면이 제대로 표시되었습니까?'
def _wrap(txt,f,widths):
    words=txt.split(' ');lines=[];cur=''
    for wd in words:
        t=(cur+' '+wd) if cur else wd
        if cur and f.getlength(t)>widths[min(len(lines),len(widths)-1)]: lines.append(cur);cur=wd
        else: cur=t
    lines.append(cur); return lines
def hz(img):
    a=img; al=a[...,3]
    col=a[al>200][:,:4].mean(0); col[3]=255
    def ext(k):
        c=np.where((al[16*k:16*k+16]>8).any(0))[0]; return (c.max()+1) if len(c) else 0
    f=font(F_REG,13)
    seconds=[ext(k) for k in (5,6,7,8,9)]
    widths=[256+s-2 for s in seconds]
    out=img.copy(); out[0:192]=0
    def put(s,k):
        L=Image.new('L',(256,16)); ImageDraw.Draw(L).text((1,8),s,font=f,fill=255,anchor='lm')
        mm=np.array(L).astype(float)[...,None]/255
        out[16*k:16*k+16]=np.clip(col*mm+out[16*k:16*k+16]*(1-mm),0,255).astype(np.uint8)
    # display line i = grid row i followed by grid row i+5; fill pieces word by word in reading order
    slots=[]
    for i in range(5): slots+= [(i,254),(i+5,seconds[i]-2)]
    words=HZ_TEXT.split(' '); si=0; cur=''
    for wd in words:
        t=(cur+' '+wd) if cur else wd
        if cur and f.getlength(t)>slots[si][1]:
            put(cur,slots[si][0]); si+=1; cur=wd
        else: cur=t
    put(cur,slots[si][0]); assert si<len(slots)
    put(HZ_Q,10)
    # big JA / NEIN area (rows 192..228) -> 예 / 아니오
    big=a[192:230]; bc=big[big[...,3]>200][:,:4].mean(0) if (big[...,3]>200).any() else col; bc[3]=255
    out[192:232]=0
    out=draw_text(out,'예',2,200,F_BOLD,17,bc,'lm')
    out=draw_text(out,'아니오',2,219,F_BOLD,19,bc,'lm')
    return out
# ---------- in-game menu tabs (MAP/VM/ITEM/STAT, glow + thin versions) ----------
TABS={'MAP':'지도','VM':'VM','ITEM':'아이템','STAT':'상태'}
def _words(al,x0,x1,y0,y1):
    r=(al[y0:y1,x0:x1]>8).any(1); out=[];s=None
    for y,v in enumerate(list(r)+[False]):
        if v and s is None: s=y
        if not v and s is not None:
            c=np.where((al[y0+s:y0+y,x0:x1]>8).any(0))[0]
            out.append((y0+s,y0+y,x0+c.min(),x0+c.max()+1)); s=None
    return out
def _glow_text(img,box,txt,fpath,col,glow):
    y0,y1,x0,x1=box; h=y1-y0; w=x1-x0
    px=h+2
    while px>6 and font(fpath,px).getlength(txt)>w-1: px-=1
    L=Image.new('L',(img.shape[1],img.shape[0])); d=ImageDraw.Draw(L)
    d.text(((x0+x1)/2,(y0+y1)/2),txt,font=font(fpath,px),fill=255,anchor='mm')
    m=np.array(L).astype(float)[...,None]/255
    out=img.astype(float)
    if glow is not None:
        from PIL import ImageFilter
        g=np.array(L.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))).astype(float)[...,None]/255
        g=np.clip(g*1.6,0,1); out=np.array(glow,float)*g+out*(1-g)
    out=np.array(col,float)*m+out*(1-m)
    return np.clip(out,0,255).astype(np.uint8)
def tabs(img):
    al=img[...,:3].astype(int).sum(2)//3; out=img.copy(); BG=img[127,127].copy()
    order=['MAP','VM','ITEM','STAT']
    left=_words(al,0,66,0,100); right=_words(al,70,128,0,60)
    assert len(left)==4 and len(right)==4,(left,right)
    for k,(box) in enumerate(left):
        y0,y1,x0,x1=box; reg=img[y0:y1,x0:x1]; t=reg[reg[...,:3].astype(int).sum(-1)>60]
        col=t[t[:,:3].sum(1)>=np.percentile(t[:,:3].sum(1),85)].mean(0); col[3]=255
        glow=np.array([0,90,140,255.])
        out[max(0,y0-2):y1+2,max(0,x0-3):x1+3]=BG
        out=_glow_text(out,(y0,y1,x0,x1),TABS[order[k]],F_BOLD,col,glow)
    for k,box in enumerate(right):
        y0,y1,x0,x1=box; reg=img[y0:y1,x0:x1]; t=reg[reg[...,:3].astype(int).sum(-1)>90]; col=t.mean(0); col[3]=255
        out[y0:y1,x0:x1]=BG
        out=_glow_text(out,box,TABS[order[k]],F_REG,col,None)
    return out
# ---------- radar warning (DANG|ER and WARN|ING are each one on-screen word split over two rows) ----------
def radar(img):
    al=img[...,3]; out=img.copy(); col=np.array([255,255,255,255.]); BG=np.zeros(4,np.uint8)
    ws=[ (np.where((al[16*k:16*k+16]>8).any(0))[0].max()+1) for k in range(4)]
    out[:64]=BG
    for (k1,k2,txt) in ((0,1,'위험'),(2,3,'경고')):
        total=ws[k1]+ws[k2]
        f=font(F_BOLD,16); tw=int(f.getlength(txt))+2
        G=Image.new('L',(tw,20)); ImageDraw.Draw(G).text((1,10),txt,font=f,fill=255,anchor='lm'); G=G.crop(G.getbbox())  # fill the full 16px band like the original letters
        sw=int(total*0.86); G=G.resize((sw,16),Image.LANCZOS)      # wide letters like the original
        L=Image.new('L',(200,16)); L.paste(G,((total-sw)//2,0)); m=np.array(L).astype(float)[...,None]/255
        for part,k in ((m[:,:64],k1),(m[:,ws[k1]:ws[k1]+64],k2)):
            seg=out[16*k:16*k+16].astype(float); seg=col*part+seg*(1-part)
            out[16*k:16*k+16]=np.clip(seg,0,255).astype(np.uint8)
    return out
# ---------- dispatcher ----------
def target(name):
    n=name.upper().split('\\')[-1]
    if n=='HZ_TXT_GERMAN.PVR': return 'hz'
    if re.match(r'YESNO_GERMAN\.PVR$',n): return 'YESNO'
    if re.match(r'CANCEL_GERMAN\.PVR$',n): return 'CANCEL'
    if n=='TOP_TEXT.PVR': return 'tabs'
    if n=='HUD_RADAR_TEXT.PVR': return 'radar'
    return None
_CACHE={}
def make(name,data):
    key=(name.upper().split(chr(92))[-1],data)
    if key in _CACHE: return _CACHE[key]
    r=_make(name,data); _CACHE[key]=r; return r
def _make(name,data):
    t=target(name)
    img=title_tex.decode(data)
    out={'hz':hz,'tabs':tabs,'radar':radar}[t](img) if t in ('hz','tabs','radar') else buttons(img,LABELS[t])
    return title_tex.encode(data,out),out
if __name__=='__main__':
    import gdfs,ahf
    for disc in (1,2):
        d=gdfs.Disc(disc=disc);fs=d.files()
        for p in sorted(fs):
            if not p.upper().endswith('.AHF'): continue
            b=d.read(*fs[p][:2])
            for e in ahf.parse(b):
                if target(e['name']):
                    nb,img=make(e['name'],b[e['off']:e['off']+e['size']])
                    fn=os.path.join(ROOT,'view','ko_'+p.split('/')[-1]+'_'+e['name'].split('\\')[-1]+'.png')
                    Image.fromarray(title_tex.decode(nb)).save(fn); print(fn)

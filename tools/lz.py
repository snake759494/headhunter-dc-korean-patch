# Moero Justice Gakuen word-LZ: flag u16 (MSB first, 1=ref); ref u16: len=x>>11, dist=x&0x7ff (words);
# len==0 -> next u16 is len; len==0 there -> end of stream.
import struct
def dec(d):
    n=len(d)//2;w=struct.unpack('<%dH'%n,d[:n*2]);out=[];p=0
    while p<n:
        f=w[p];p+=1
        for bit in range(15,-1,-1):
            if p>=n: break
            x=w[p];p+=1
            if f>>bit&1:
                L=x>>11;D=x&0x7ff
                if L==0:
                    D=x;L=w[p];p+=1
                if D==0:
                    if L==0: return out,p
                    out+=[0]*L;continue
                s=len(out)-D
                for j in range(L): out.append(out[s+j])
            else: out.append(x)
    return out,p
def split(d):
    q=0;res=[]
    while q<len(d)-4:
        out,p=dec(d[q:]);end=q+p*2
        res.append((q,struct.pack('<%dH'%len(out),*out),p*2))
        q=(end+0x7ff)&~0x7ff
    return res
def enc(data):
    """greedy compressor (hash chain), returns bytes ending with terminator"""
    if len(data)%2: data+=b'\0'
    w=struct.unpack('<%dH'%(len(data)//2),data);n=len(w)
    items=[];i=0;head={}
    while i<n:
        bl=0;bd=0
        if i+1<n:
            key=(w[i],w[i+1]);cands=head.get(key,[])
            for j in reversed(cands[-64:]):
                if i-j>0x7ff: break
                l=0
                while i+l<n and w[j+l]==w[i+l] and l<0xffff: l+=1
                if l>bl: bl=l;bd=i-j
                if l>=200: break
        # also check run dist1 handled by above
        if bl>=2:
            items.append(('r',bl,bd))
            for t in range(i,i+bl):
                if t+1<n: head.setdefault((w[t],w[t+1]),[]).append(t)
            i+=bl
        else:
            items.append(('l',w[i]))
            if i+1<n: head.setdefault((w[i],w[i+1]),[]).append(i)
            i+=1
    items.append(('end',))
    out=[]
    for k in range(0,len(items),16):
        grp=items[k:k+16];f=0;body=[]
        for bi,it in enumerate(grp):
            if it[0]=='l': body.append(it[1])
            else:
                f|=1<<(15-bi)
                if it[0]=='end': body+=[0,0]
                elif it[1]<32: body.append((it[1]<<11)|it[2])
                else: body+=[it[2],it[1]]
        out.append(f);out+=body
    return struct.pack('<%dH'%len(out),*out)

def profile(d):
    """for original stream: list in_words_consumed at each output word index"""
    n=len(d)//2;w=struct.unpack('<%dH'%n,d[:n*2]);prof=[];p=0;o=0
    while p<n:
        p+=1;f=w[p-1]
        for bit in range(15,-1,-1):
            x=w[p];p+=1
            if f>>bit&1:
                L=x>>11
                if L==0:
                    L=w[p];p+=1
                    if L==0: return prof
                prof+=[p]*L
            else: prof.append(p)
    return prof

def enc_safe(data,prof,margin=0,depth=1024):
    """like enc but input position never lags original profile (in-place decompression safety)"""
    w=struct.unpack('<%dH'%(len(data)//2),data);n=len(w)
    T=max(o-p for o,p in enumerate(prof))-margin
    items=[];i=0;head={};inw=0;cnt=0
    def cost(kind,L):
        return (2 if (kind=='r' and L>=32) else 1)
    def best(i):
        bl=0;bd=0
        if i+1<n:
            for j in reversed(head.get((w[i],w[i+1]),[])[-depth:]):
                if i-j>0x7ff: break
                l=0
                while i+l<n and w[j+l]==w[i+l] and l<0xffff: l+=1
                if l>bl: bl=l;bd=i-j
                if l>=300: break
        return bl,bd
    while i<n:
        bl,bd=best(i)
        if 2<=bl<32 and i+1<n:
            if i+1<n: head.setdefault((w[i],w[i+1]),[]).append(i)
            b2,_=best(i+1);head[(w[i],w[i+1])].pop()
            if b2>bl+1: bl=0
        # input words consumed after this item (flag words included approx: one per 16 items)
        if bl>=2:
            # shrink match so that input stays ahead: need inw+c >= prof[i+bl-1]-margin
            while bl>=2:
                c=inw+cost('r',bl)+(cnt+16)//16
                if (i+bl-1)-c<=T: break
                bl=bl//2 if bl>64 else bl-1
        if bl>=2:
            items.append(('r',bl,bd));inw+=cost('r',bl)
            for t in range(i,i+bl):
                if t+1<n: head.setdefault((w[t],w[t+1]),[]).append(t)
            i+=bl
        else:
            items.append(('l',w[i]));inw+=1
            if i+1<n: head.setdefault((w[i],w[i+1]),[]).append(i)
            i+=1
        cnt+=1
    items.append(('end',))
    out=[]
    for k in range(0,len(items),16):
        grp=items[k:k+16];f=0;body=[]
        for bi,it in enumerate(grp):
            if it[0]=='l': body.append(it[1])
            else:
                f|=1<<(15-bi)
                if it[0]=='end': body+=[0,0]
                elif it[1]<32: body.append((it[1]<<11)|it[2])
                else: body+=[it[2],it[1]]
        out.append(f);out+=body
    return struct.pack('<%dH'%len(out),*out)

def check_safe(c,prof):
    p2=profile(c);return max(o-p for o,p in enumerate(prof)) - max(o-p for o,p in enumerate(p2))

def _pack(items):
    out=[]
    for k in range(0,len(items),16):
        grp=items[k:k+16];f=0;body=[]
        for bi,it in enumerate(grp):
            if it[0]=='l': body.append(it[1])
            else:
                f|=1<<(15-bi)
                if it[0]=='end': body+=[0,0]
                elif it[1]<32: body.append((it[1]<<11)|it[2])
                else: body+=[it[2],it[1]]
        out.append(f);out+=body
    return out

def enc_inplace(data,prof,target_words,margin=512,tail=8192,depth=1024,pad_only=True):
    """in-place-safe encoding of exactly target_words words"""
    w=struct.unpack('<%dH'%(len(data)//2),data);n=len(w)
    T=max(o-p for o,p in enumerate(prof))
    items=[];i=0;head={};inw=0;cnt=0
    def best(i):
        bl=0;bd=0
        if i+1<n:
            for j in reversed(head.get((w[i],w[i+1]),[])[-depth:]):
                if i-j>0x7ff: break
                l=0
                while i+l<n and w[j+l]==w[i+l] and l<4096: l+=1
                if l>bl: bl=l;bd=i-j
                if l>=300: break
        return bl,bd
    while i<n:
        bl,bd=best(i)
        if 2<=bl<32 and i+1<n:
            head.setdefault((w[i],w[i+1]),[]).append(i);b2,_=best(i+1);head[(w[i],w[i+1])].pop()
            if b2>bl+1: bl=0
        while bl>=2:
            c=inw+(2 if bl>=32 else 1)+(cnt+16)//16+1
            lim=T-(margin if i+bl<n-tail else 0)
            if (i+bl-1)-c<=lim: break
            bl=bl//2 if bl>64 else bl-1
        if bl>=2:
            items.append(('r',bl,bd));inw+=(2 if bl>=32 else 1)
            for t in range(max(i,i+bl-64),i+bl):
                if t+1<n:
                    h=head.setdefault((w[t],w[t+1]),[]);h.append(t)
                    if len(h)>4096: del h[:2048]
            i+=bl
        else:
            items.append(('l',w[i]));inw+=1
            if i+1<n: head.setdefault((w[i],w[i+1]),[]).append(i)
            i+=1
        cnt+=1
    # expand trailing refs into literals until size reaches target
    pos=[];o=0
    for it in items: pos.append(o);o+=it[1] if it[0]=='r' else 1
    def size(its): return len(_pack(its+[('end',)]))
    cur=size(items)
    assert cur<=target_words,(cur,target_words)
    k=-1 if pad_only else len(items)-1
    while cur<target_words and k>=0:
        it=items[k]
        if it[0]=='r':
            o=pos[k];lits=[('l',w[o+j]) for j in range(it[1])]
            trial=items[:k]+lits+items[k+1:]
            s=size(trial)
            if s<=target_words: items=trial;cur=s
            else:
                # partial: split into literals + shorter ref
                for m in range(1,it[1]-1):
                    t2=items[:k]+[('l',w[o+j]) for j in range(m)]+[('r',it[1]-m,it[2])]+items[k+1:]
                    s2=size(t2)
                    if s2>target_words: break
                    best_t=(t2,s2)
                if 'best_t' in dir() and best_t[1]>cur: items,cur=best_t
                break
        k-=1
    out=_pack(items+[('end',)])
    while len(out)<target_words: out.append(0)   # trailing pad (never read)
    return struct.pack('<%dH'%len(out),*out)

def enc_fast(data,prof,target_words,margin=256):
    w=struct.unpack('<%dH'%(len(data)//2),data);n=len(w)
    T=max(o-p for o,p in enumerate(prof))
    items=[];i=0;last={};inw=0;cnt=0
    while i<n:
        bl=0;bd=0
        cands=[i-1,i-80,i-160]
        if i+1<n: cands.append(last.get((w[i],w[i+1]),-1))
        for j in cands:
            if j<0 or i-j>0x7ff or i-j<=0: continue
            l=0
            while i+l<n and w[j+l]==w[i+l] and l<4096: l+=1
            if l>bl: bl=l;bd=i-j
        while bl>=2:
            c=inw+(2 if bl>=32 else 1)+cnt//16+2
            if (i+bl-1)-c<=T-margin-(2 if i<n-40 else 1): break
            bl=bl//2 if bl>64 else bl-1
        if i+1<n: last[(w[i],w[i+1])]=i
        if bl>=2:
            items.append(('r',bl,bd));inw+=(2 if bl>=32 else 1)
            for t in range(i+1,min(i+bl,n-1)): last[(w[t],w[t+1])]=t
            i+=bl
        else:
            items.append(('l',w[i]));inw+=1;i+=1
        cnt+=1
    out=_pack(items+[('end',)])
    assert len(out)<=target_words,(len(out),target_words)
    out+= [0]*(target_words-len(out))
    return struct.pack('<%dH'%len(out),*out)

def enc_opt(data,depth=64):
    """optimal-parse encoder (cost in words), supports zero-fill refs (dist 0)."""
    w=struct.unpack('<%dH'%(len(data)//2),data);n=len(w)
    # zero run lengths
    zr=[0]*(n+1)
    for i in range(n-1,-1,-1): zr[i]=zr[i+1]+1 if w[i]==0 else 0
    INF=1<<60;cost=[INF]*(n+1);cost[0]=0;how=[None]*(n+1)
    head={};
    for i in range(n):
        c=cost[i]
        if c==INF: continue
        # literal (cost 16 units = 1 word; flag overhead 1 unit)
        v=c+17
        if v<cost[i+1]: cost[i+1]=v;how[i+1]=('l',)
        cands=[]
        if zr[i]>=2:
            L=min(zr[i],0xffff)
            for l in (L,min(L,31)):
                if l>=2:cands.append((l,0))
        if i+1<n:
            key=(w[i],w[i+1]);lst=head.get(key)
            if lst:
                best=0
                for j in reversed(lst[-depth:]):
                    if i-j>0x7ff: break
                    l=0;mx=min(n-i,0xffff)
                    while l<mx and w[j+l]==w[i+l]: l+=1
                    if l>best:
                        best=l;cands.append((l,i-j))
                        if l>=31: cands.append((31,i-j))
                    if l>=512: break
            head.setdefault(key,[]).append(i)
        bestc={}
        for l,dd in cands:
            if l>bestc.get(dd,0): bestc[dd]=l
        top=sorted(bestc.items(),key=lambda t:-t[1])
        if top:
            dd0,l0=top[0]
            Ls=[(L,dd0) for L in range(2,min(l0,31)+1)]+[(L,dd0) for L in range(32,l0+1,max(1,(l0-32)//16 or 1))]+[(l0,dd0)]
        else: Ls=[]
        for L,dd in Ls:
            if True:
                cc=c+(17 if L<32 else 33)
                if cc<cost[i+L]: cost[i+L]=cc;how[i+L]=('r',L,dd)
    items=[];i=n
    while i>0:
        h=how[i]
        if h[0]=='l': items.append(('l',w[i-1]));i-=1
        else: items.append(('r',h[1],h[2]));i-=h[1]
    items.reverse()
    out=_pack(items+[('end',)])
    return struct.pack('<%dH'%len(out),*out)

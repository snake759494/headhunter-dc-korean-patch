import numpy as np
def tw_index(w,h):
    n=min(w,h);x=np.arange(w)[None,:].repeat(h,0);y=np.arange(h)[:,None].repeat(w,1)
    def inter(a,b):
        r=np.zeros_like(a);bit=0
        for i in range(int(np.log2(n))):
            r|=((b>>i)&1)<<(2*i); r|=((a>>i)&1)<<(2*i+1)
        return r
    xi=x%n;yi=y%n
    base=inter(xi,yi)
    blk=(x//n)+(y//n)*(w//n)
    return base+blk*n*n
def untwiddle(a,w,h):
    idx=tw_index(w,h);return a[idx]
def twiddle(img):
    h,w=img.shape[:2];idx=tw_index(w,h);out=np.zeros(w*h,img.dtype);out[idx.reshape(-1)]=img.reshape(-1);return out
def rgb565(a): return np.stack([(a>>11&31)*8,(a>>5&63)*4,(a&31)*8],-1).astype(np.uint8)
def argb4444(a): return np.stack([(a>>8&15)*17,(a>>4&15)*17,(a&15)*17,(a>>12&15)*17],-1).astype(np.uint8)
def argb1555(a): return np.stack([(a>>10&31)*8,(a>>5&31)*8,(a&31)*8],-1).astype(np.uint8)

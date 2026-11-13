# validate Korean strings: python tools/check_tr.py [tr/file.json ...]  (no args = all)
import json,os,sys,glob
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
ICON=set('[]@Ñº§ª')
def ok_char(c): return c=='\n' or 0x20<=ord(c)<0x7f or '가'<=c<='힣' or c in ICON
def check(p):
    d=json.load(open(p,encoding='utf8')); errs=[]; csv=d['rel'].upper().endswith('.CSV')
    for i,s in enumerate(d['segs']):
        ko=s['ko']
        if not ko.strip(): errs.append((i,'empty')); continue
        bad=sorted({c for c in ko if not ok_char(c)})
        if bad: errs.append((i,'bad chars %r'%bad))
        if csv and ';' in ko: errs.append((i,'semicolon'))
    return errs
if __name__=='__main__':
    fs=sys.argv[1:] or sorted(glob.glob(os.path.join(W,'tr','*.json')))
    n=0
    for p in fs:
        for i,m in check(p): print(os.path.basename(p),i,m); n+=1
    print('errors',n)

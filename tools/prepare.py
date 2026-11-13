# extract what the build needs from your own discs: python tools/prepare.py
#  - checks Track 3 of both discs, writes orig/1ST_READ.BIN, text_en/ and text_index.json
import os,sys,hashlib,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gdfs
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
MD5={1:'208145da634104c4c05c185e71550fad',2:'2fe16b28a2915900b3a3187b5eedd379'}
for disc in (1,2):
    p=os.path.join(W,gdfs.NAME%(disc,3))
    if not os.path.exists(p): raise SystemExit('missing: '+p)
    h=hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<24),b''): h.update(b)
    print('disc',disc,h.hexdigest(),'OK' if h.hexdigest()==MD5[disc] else 'MISMATCH')
    if h.hexdigest()!=MD5[disc]: raise SystemExit(1)
d=gdfs.Disc(disc=1); fs=d.files(); l,s,_,_=fs['1ST_READ.BIN']
os.makedirs(os.path.join(W,'orig'),exist_ok=True)
open(os.path.join(W,'orig','1ST_READ.BIN'),'wb').write(d.read(l,s))
subprocess.check_call([sys.executable,os.path.join(W,'tools','extract_text.py')])
print('ready')

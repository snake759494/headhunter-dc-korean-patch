# Extract all LOCALE text entries (English + CSV) from both discs' AHF files, dedup by (name, content)
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(__file__)); import gdfs, ahf
W = os.path.join(os.path.dirname(__file__), '..')
out = {}; where = {}
for disc in (1, 2):
    d = gdfs.Disc(disc=disc); fs = d.files()
    for k, (l, s, _, _) in sorted(fs.items()):
        if not k.endswith('.AHF'): continue
        b = d.read(l, s)
        for e in ahf.parse(b):
            n = e['name'].upper()
            if 'LOCALE' not in n: continue
            if any(x in n for x in ('GERMAN', 'FRENCH', 'SPANISH', 'ITALIAN')): continue
            data = b[e['off']:e['off'] + e['size']]
            key = n
            if key in out and out[key] != data:
                key = n + '#' + hashlib.md5(data).hexdigest()[:6]
            out[key] = data; where.setdefault(key, []).append('%d:%s' % (disc, k))
os.makedirs(os.path.join(W, 'text_en'), exist_ok=True)
idx = {}
for k, v in out.items():
    BS = chr(92); fn = k.replace('HEADHUNTER' + BS + 'LOCALE' + BS, '').replace(BS, '__').replace('#', '__')
    open(os.path.join(W, 'text_en', fn), 'wb').write(v); idx[fn] = {'name': k, 'where': where[k], 'size': len(v)}
json.dump(idx, open(os.path.join(W, 'text_index.json'), 'w'), indent=1)
print(len(out), sum(len(v) for v in out.values()))

# locate font files: repository root or fonts/
import os
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
def fontpath(name):
    for d in (ROOT,os.path.join(ROOT,'fonts')):
        p=os.path.join(d,name)
        if os.path.exists(p): return p
    raise SystemExit('font not found: %s (put it in the repository root or fonts/)'%name)

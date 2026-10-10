from pathlib import Path
import json
from sexpr import *
root=parse(Path('Swayatt_PCB.kicad_sch').read_text(encoding='utf-8'))
lib={s[1]:s for s in children(one(root,'lib_symbols'),'symbol')}
for s in children(root,'symbol'):
    ref=prop(s,'Reference')[2]
    if ref.startswith('#'): continue
    print(ref,one(s,'lib_id')[1],one(s,'at')[1:],one(s,'mirror'))
    for sub in children(lib[one(s,'lib_id')[1]],'symbol'):
        for p in children(sub,'pin'):
            print(' ',one(p,'number')[1],one(p,'name')[1],one(p,'at')[1:])
for name in ('erc','drc'):
    p=Path('engineering/baseline')/(name+'.json')
    if p.exists(): print(name,p.read_text()[:16000])

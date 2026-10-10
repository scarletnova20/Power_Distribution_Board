"""Resolve reported endpoint-to-via-centre warnings without excluding checks."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
raw=parse(target.read_text());vias={one(v,'uuid')[1]:v for v in children(raw,'via')}
affected={}
for finding in json.loads((root/'candidate_drc.json').read_text())['violations']:
    if finding['type']!='track_not_centered_on_via':continue
    for item in finding['items']:
        if item['uuid'] in vias:affected[item['uuid']]=vias[item['uuid']]
count=0
for via in affected.values():
    at=one(via,'at')[1:3];xy=list(map(float,at));net=one(via,'net')[1]
    for track in children(raw,'segment'):
        if one(track,'net')[1]!=net:continue
        for key in ('start','end'):
            end=one(track,key)
            if 0<math.dist(list(map(float,end[1:3])),xy)<.35:end[1:3]=at;count+=1
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='segment' and one(v,'start')[1:3]==one(v,'end')[1:3])]
target.write_text(dump(raw)+'\n');print('Centered',count,'track endpoints')

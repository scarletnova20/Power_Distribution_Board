from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one
import pcbnew as p
root=Path(__file__).resolve().parent;target=root/'PDB_50A.kicad_pcb'
raw=parse(target.read_text());added=json.loads((root/'power_arrays.json').read_text());intent={v['uuid']:v for v in added}
remove=set()
for v in children(raw,'via'):
    uid=one(v,'uuid')[1]
    if uid in intent and one(v,'net')[1]!=intent[uid]['net']:remove.add(uid)
for finding in json.loads((root/'drc.json').read_text())['violations']:
    for item in finding['items']:
        if item['uuid'] in intent:remove.add(item['uuid'])
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='via' and one(v,'uuid')[1] in remove)]
# Remove only the displaced quiet-ground branch, preserving its other junctions.
branch={'645ed84d-794f-400b-b768-bb544e3290ca'}
for t in children(raw,'segment'):
    if one(t,'net')[1]=='/GNDA' and one(t,'layer')[1]=='F.Cu':
        if any(abs(float(one(t,k)[1])-83.6)<1e-6 for k in ('start','end')):branch.add(one(t,'uuid')[1])
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='segment' and one(v,'uuid')[1] in branch)]
target.write_text(dump(raw)+'\n')
helper=(root.parent/'release42/grid_helpers.py').read_text(encoding='utf-8-sig').replace(".1499 if f.GetReference() in ('U1','U3') else .1999",'.1999')
namespace={};exec(compile(helper,'grid_helpers50','exec'),namespace)
b=p.LoadBoard(str(target));namespace['b']=b;namespace['fs']={f.GetReference():f for f in b.GetFootprints()}
assert namespace['route']('/GNDA',(83.4685,217.5272,0),(82.2,215.5,0))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'power_arrays_rejected.json').write_text(json.dumps([v for v in added if v['uuid'] in remove],indent=2)+'\n')
(root/'power_arrays.json').write_text(json.dumps([v for v in added if v['uuid'] not in remove],indent=2)+'\n')
print('Removed rejected transfer vias',len(remove),flush=True)

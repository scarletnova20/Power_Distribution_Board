"""Place the INA228 differential capacitor beside its input pins and reroute affected nets."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one,Atom
import pcbnew as p
import grid_helpers as g
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_sense_filter.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
raw=parse(backup.read_text())
lookup={one(v,'uuid')[1]:v for key in ('segment','via') for v in children(raw,key)}
for finding in json.loads((root/'candidate_drc.json').read_text())['violations']:
    if finding['type']!='track_not_centered_on_via':continue
    items=[lookup[i['uuid']] for i in finding['items']]
    track=next(i for i in items if i[0]=='segment');via=next(i for i in items if i[0]=='via')
    at=one(via,'at')[1:3]
    end=min((one(track,'start'),one(track,'end')),key=lambda v:math.dist(list(map(float,v[1:3])),list(map(float,at))))
    assert math.dist(list(map(float,end[1:3])),list(map(float,at)))<.25
    end[1:3]=at
affected={'/DIG_SENSE_P','/DIG_SENSE_N','/Voltage'}
raw[:]=[v for v in raw if not (isinstance(v,list) and v and v[0] in ('segment','via') and one(v,'net')[1] in affected)]
obstructing={'d8c05933-3c6a-4f8e-bf9f-2ed3244ba270','e710d1d9-0aec-4b60-8c2a-d638cb6f2220'}
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='segment' and one(v,'uuid')[1] in obstructing)]
# Remove only previously inserted stitching vias under the two new footprints.
stitch={(round(x,3),round(y,3)) for _,x,y in json.loads((root/'candidate_stitching.json').read_text())}
removed=[]
for v in list(children(raw,'via')):
    x,y=map(float,one(v,'at')[1:3])
    if (round(x,3),round(y,3)) not in stitch:continue
    if (83.1<x<85.5 and 212.4<y<216.1) or (85.2<x<88.4 and 212.5<y<214.5):raw.remove(v);removed.append([x,y])
target.write_text(dump(raw)+'\n')
b=p.LoadBoard(str(target));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
g.fs['C16'].SetPosition(pt(84.3,214.0));g.fs['C16'].SetOrientationDegrees(270)
g.fs['C15'].SetPosition(pt(86.8,213.9))
base=g.masks
def masks(net):
    blocked,vb=base(net)
    for x,y in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)):
        for mask in blocked:g.segment(mask,x,y,x,y,3.36)
        g.segment(vb,x,y,x,y,3.51)
    return blocked,vb
g.masks=masks
def pad(ref,pin):
    q=next(q for q in g.fs[ref].Pads() if q.GetNumber()==pin)
    return (p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),0)
jobs=[('/DIG_SENSE_P',pad('U3','10'),pad('C16','1')),
      ('/DIG_SENSE_N',pad('U3','9'),pad('C16','2')),
      ('/Vin',pad('U3','8'),(88.326,213.8062,0)),
      ('/DIG_SENSE_P',pad('C16','1'),pad('R15','2')),
      ('/DIG_SENSE_N',pad('C16','2'),pad('R16','2')),
      ('/Voltage',pad('C15','1'),pad('R9','1')),
      ('/Voltage',pad('R9','1'),pad('TP3','1')),
      ('/Voltage',pad('TP3','1'),pad('R8','2')),
      ('/GNDA',(85.775,215,0),pad('C15','2'))]
results=[]
for net,a,c in jobs:results.append({'net':net,'start':a,'end':c,'routed':g.route(net,a,c)})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'sense_filter_routes.json').write_text(json.dumps({'routes':results,'removed_stitch_vias':removed},indent=2)+'\n')
print('Sense-filter routing:',sum(q['routed'] for q in results),'/',len(results),flush=True)

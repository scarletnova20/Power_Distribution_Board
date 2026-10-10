"""Reserve short regulator control connections before general signal routing."""
from pathlib import Path
import math,json
import pcbnew as p
import grid_helpers as g
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_local_controls.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
b=p.LoadBoard(str(backup));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
def point(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pad(ref,num):return next(q for q in g.fs[ref].Pads() if q.GetNumber()==num)
f=g.fs['NT1'];f.SetPosition(point(86.8,215));f.SetOrientationDegrees(180)
ground=pad('U1','21').GetNet()
for x in (84.5,85.3,86.1):
    for y in (211.1,211.9):
        v=p.PCB_VIA(b);v.SetPosition(point(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(ground);v.SetLocked(True);b.Add(v)
base_masks=g.masks
def masks(net):
    blocked,vb=base_masks(net)
    for x,y in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)):
        for layer in blocked:g.segment(layer,x,y,x,y,3.36)
        g.segment(vb,x,y,x,y,3.56)
    return blocked,vb
g.masks=masks
def position(q):
    v=q.GetPosition();return (p.ToMM(v.x),p.ToMM(v.y),3 if q.GetParentFootprint().IsFlipped() else 0)
jobs=[('GNDA',[('U1','10'),('NT1','1')]),('PGND',[('NT1','2'),('U1','21')]),
      ('COMP',[('U1','6'),('R7','1'),('C11','1')]),
      ('COMP_RC',[('R7','2'),('C12','1')]),
      ('FB',[('U1','7'),('C11','2'),('C12','2'),('R6','1'),('R5','2')]),
      ('RT',[('U1','8'),('R4','2')]),('RAMP',[('U1','9'),('C3','2')]),
      ('SS',[('U1','11'),('C6','2')]),('BST',[('U1','20'),('C7','2')]),
      ('BUCK_BIAS',[('U1','1'),('C5','2')])]
report=[]
for net,refs in jobs:
    coords=[position(pad(*pair)) for pair in refs];connected={0};remaining=set(range(1,len(coords)))
    while remaining:
        _,i,j=min((math.dist(coords[i][:2],coords[j][:2]),i,j) for i in connected for j in remaining)
        before={t.m_Uuid.AsString() for t in b.GetTracks()}
        success=g.route('/'+net,coords[i],coords[j]);report.append({'net':net,'from':refs[i],'to':refs[j],'routed':success})
        for t in b.GetTracks():
            if t.m_Uuid.AsString() not in before:t.SetLocked(True)
        connected.add(j);remaining.remove(j)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'local_control_routes.json').write_text(json.dumps(report,indent=2))
print('Local connections completed',sum(r['routed'] for r in report),'/',len(report),flush=True)

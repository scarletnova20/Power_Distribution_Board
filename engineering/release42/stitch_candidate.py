"""Connect reserved power planes using screened 0.5/0.3 mm through vias.

DRC must follow: raster screening is deliberately not a fabrication check.
"""
from pathlib import Path
import json,math
import pcbnew as p
import grid_helpers as g
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_candidate_stitch.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
b=p.LoadBoard(str(backup));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
# DRC identified these as orphan tails after Specctra optimization.
tails={'82e77f42-1052-4ff3-9276-483b236b0fe1','1f856dfe-d9ed-404c-9019-42c427e7f9e8'}
# Use the saved filled polygons for screening; refill once after all edits.
added=[]
holes=[]
for f in g.fs.values():
    for q in f.Pads():
        d=q.GetDrillSize()
        if d.x or d.y:holes.append((p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),p.ToMM(max(d.x,d.y))/2))
for net in ('/BAT_FUSED','/VCC','/Vin','/PGND'):
    _,blocked=g.masks(net)
    zones=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net]
    front=[z for z in zones if z.GetLayer()==p.F_Cu]
    other=[z for z in zones if z.GetLayer()!=p.F_Cu]
    if not front:continue
    for x in [60.8+i*.8 for i in range(49)]:
        for y in [190.8+i*.8 for i in range(49)]:
            j,i=g.idx(x,y,0)[1:]
            if blocked[j,i]:continue
            if any(math.hypot(x-hx,y-hy)<3.6 for hx,hy in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5))):continue
            if any(math.hypot(x-hx,y-hy)<r+.15+.26 for hx,hy,r in holes):continue
            pt=p.VECTOR2I(p.FromMM(x),p.FromMM(y))
            if not any(z.GetFilledPolysList(p.F_Cu).Contains(pt) for z in front):continue
            if not any(z.GetFilledPolysList(z.GetLayer()).Contains(pt) for z in other):continue
            if any(math.hypot(x-ax,y-ay)<1.05 for _,ax,ay in added):continue
            v=p.PCB_VIA(b);v.SetPosition(pt);v.SetWidth(p.FromMM(.5));v.SetDrill(p.FromMM(.3))
            v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(front[0].GetNet());v.SetLocked(True);b.Add(v)
            added.append((net,round(x,3),round(y,3)))
for t in list(b.GetTracks()):
    if t.m_Uuid.AsString() in tails:b.Remove(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'candidate_stitching.json').write_text(json.dumps(added,indent=2)+'\n')
print('Added',len(added),'screened stitching vias',flush=True)

"""Add screened positive-path transfer arrays to reduce measured-model crowding."""
from pathlib import Path
import sys,json,math,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'release42'))
import grid_helpers as g
import numpy as np
import pcbnew as p
root=Path(__file__).resolve().parent;target=root/'PDB_50A.kicad_pcb'
backup=root/'before_power_arrays.kicad_pcb'
assert not backup.exists(),'Construction step must not be repeated'
shutil.copy2(target,backup)
b=p.LoadBoard(str(target));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
added=[];existing=[(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
# Positive rail B.Cu bridge. Higher-priority local switching pours keep their area.
net=next(q.GetNet() for q in g.fs['J12'].Pads() if q.GetNumber()=='1')
z=p.ZONE(b);z.SetLayer(p.B_Cu);z.SetNet(net);z.SetAssignedPriority(5)
z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetZoneName('50A positive return from shunts to ESC')
outline=z.Outline();outline.NewOutline()
for x,y in [(79.2,190.4),(95.5,190.4),(95.5,207.0),(83.5,207.0),(83.5,211.9),(79.2,211.9)]:outline.Append(p.FromMM(x),p.FromMM(y))
b.Add(z);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
regions={'/BAT_FUSED':[(67.5,194.9,72.5,196.6),(61.2,196,65.5,222.5)],
 '/VCC':[(67,198.8,70.4,223.5),(73.8,202.5,78.2,211.5)],
 '/Vin':[(80,191.5,86.3,196.3),(80,202.5,82.5,211.5),(84,196.5,89.5,207)]}
for net,rects in regions.items():
    _,blocked=g.masks(net)
    # g uses a 0.5mm via; grow to 0.6mm and retain extra process margin.
    grown=blocked.copy()
    for dj in (-2,-1,0,1,2):
        for di in (-2,-1,0,1,2):grown|=np.roll(blocked,(dj,di),(0,1))
    zones=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net]
    nobj=next(q.GetNet() for f in g.fs.values() for q in f.Pads() if q.GetNetname()==net)
    for x1,y1,x2,y2 in rects:
        for x in np.arange(x1,x2+.001,.75):
            for y in np.arange(y1,y2+.001,.75):
                x,y=round(float(x),3),round(float(y),3);j,i=g.idx(x,y,0)[1:]
                if grown[j,i] or any(math.hypot(x-a,y-c)<.65 for a,c in existing):continue
                if any(math.hypot(x-a,y-c)<3.6 for a,c in [(62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)]):continue
                point=p.VECTOR2I(p.FromMM(x),p.FromMM(y))
                connected_layers={z.GetLayer() for z in zones if z.GetFilledPolysList(z.GetLayer()).Contains(point)}
                if len(connected_layers)<2:continue
                v=p.PCB_VIA(b);v.SetPosition(point);v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
                v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nobj);v.SetLocked(True);b.Add(v)
                existing.append((x,y));added.append({'uuid':v.m_Uuid.AsString(),'net':net,'xy':[x,y]})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'power_arrays.json').write_text(json.dumps(added,indent=2)+'\n')
print('Added screened transfer vias',len(added),flush=True)

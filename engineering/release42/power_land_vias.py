"""Direct, screened through-via arrays in the four main solder lands.

These cannot be replaced by thin tracks to remote ground planes. Requires
fabricator-qualified filled and copper-capped vias suitable for solder lands.
"""
from pathlib import Path
import json,math
import numpy as np
import pcbnew as p
import grid_helpers as g
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
backup=root/'before_power_land_vias.kicad_pcb'
if not backup.exists():backup.write_bytes(target.read_bytes())
b=p.LoadBoard(str(backup));g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
existing=[(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
added=[];counts={}
for ref in ('J1','J12'):
    for q in g.fs[ref].Pads():
        net=q.GetNetname();cx,cy=p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)
        _,blocked=g.masks(net)
        # Original masks screen diameter 0.5 mm; grow by 0.05 mm per side.
        grown=blocked.copy()
        for dj in (-1,0,1):
            for di in (-1,0,1):grown|=np.roll(blocked,(dj,di),(0,1))
        for dx in (-2.4,-1.6,-.8,0,.8,1.6,2.4):
            for dy in (-2.4,-1.6,-.8,0,.8,1.6,2.4):
                x,y=round(cx+dx,3),round(cy+dy,3);j,i=g.idx(x,y,0)[1:]
                if grown[j,i]:continue
                if any(math.hypot(x-a,y-c)<.65 for a,c in existing):continue
                if any(math.hypot(x-a,y-c)<3.6 for a,c in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5))):continue
                v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
                v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH)
                v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(q.GetNet());v.SetLocked(True);b.Add(v)
                existing.append((x,y));added.append({'ref':ref,'pad':q.GetNumber(),'net':net,'x':x,'y':y,'uuid':v.m_Uuid.AsString()})
        counts[ref+'.'+q.GetNumber()]=sum(a['ref']==ref and a['pad']==q.GetNumber() for a in added)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'power_land_vias.json').write_text(json.dumps({'added_by_pad':counts,'vias':added},indent=2)+'\n')
print('Direct power-land vias added:',counts,flush=True)

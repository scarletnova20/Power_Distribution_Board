"""Connect power pours across layers using clearance-screened stitching vias."""
from pathlib import Path
import math,json
import pcbnew as p
import grid_helpers as g
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb');g.b=b;g.fs={f.GetReference():f for f in b.GetFootprints()}
backup=Path('engineering/release42/before_stitch.kicad_pcb')
if not backup.exists():backup.write_bytes(Path('Swayatt_PCB_42x42.kicad_pcb').read_bytes())
added=[]
for net in ('/BAT_FUSED','/VCC','/Vin','/PGND'):
    _,blocked=g.masks(net)
    zones=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net and z.GetLayer()==p.F_Cu]
    if not zones:continue
    for x in [61+i*.8 for i in range(48)]:
        for y in [191+i*.8 for i in range(48)]:
            j,i=g.idx(x,y,0)[1:]
            if blocked[j,i]:continue
            if any(math.hypot(x-hx,y-hy)<3.6 for hx,hy in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5))):continue
            pt=p.VECTOR2I(p.FromMM(x),p.FromMM(y))
            if not any(z.GetFilledPolysList(p.F_Cu).Contains(pt) for z in zones):continue
            if any(math.hypot(x-ax,y-ay)<1.5 for _,ax,ay in added):continue
            via=p.PCB_VIA(b);via.SetPosition(pt);via.SetWidth(p.FromMM(.5));via.SetDrill(p.FromMM(.3))
            via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(zones[0].GetNet());b.Add(via)
            added.append((net,x,y))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
Path('engineering/release42/stitching.json').write_text(json.dumps(added,indent=2))
print('Added stitching vias',len(added),flush=True)

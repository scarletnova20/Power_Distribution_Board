"""Remove only newly added stitching vias rejected by the subsequent DRC."""
from pathlib import Path
import json
import pcbnew as p
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb')
added=json.loads(Path('engineering/release42/stitching.json').read_text())
positions={(round(x,4),round(y,4)) for net,x,y in added}
original=p.LoadBoard('engineering/release42/before_stitch.kicad_pcb')
original_ids={t.m_Uuid.AsString() for t in original.GetTracks()}
issues=json.loads(Path('engineering/release42/drc.json').read_text())['violations']
bad={item['uuid'] for v in issues for item in v['items']}
removed=[]
for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA) or t.m_Uuid.AsString() not in bad:continue
    point=t.GetPosition();key=(t.GetNetname(),round(p.ToMM(point.x),4),round(p.ToMM(point.y),4))
    assert key[1:] in positions and t.m_Uuid.AsString() not in original_ids,'Refusing to remove pre-existing via '+str(key)
    removed.append(key);b.Remove(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
Path('engineering/release42/removed_stitching.json').write_text(json.dumps(removed,indent=2))
print('Removed rejected candidate vias',len(removed),flush=True)

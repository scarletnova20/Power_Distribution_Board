"""Remove only newly inserted stitching vias rejected by independent DRC."""
from pathlib import Path
import json
import pcbnew as p
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
b=p.LoadBoard(str(target));original=p.LoadBoard(str(root/'before_candidate_stitch.kicad_pcb'))
original_ids={t.m_Uuid.AsString() for t in original.GetTracks()}
bad={i['uuid'] for v in json.loads((root/'candidate_drc.json').read_text())['violations'] for i in v['items']}
audit=root/'candidate_via_audit.json'
wrong_positions={(round(v['x'],3),round(v['y'],3)) for v in json.loads(audit.read_text())['mismatched']} if audit.exists() else set()
removed=[]
for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA):continue
    xy=(round(p.ToMM(t.GetPosition().x),3),round(p.ToMM(t.GetPosition().y),3))
    if t.m_Uuid.AsString() not in bad and xy not in wrong_positions:continue
    assert t.m_Uuid.AsString() not in original_ids,'Refusing to remove an existing connection'
    removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'x':p.ToMM(t.GetPosition().x),'y':p.ToMM(t.GetPosition().y)})
    b.Remove(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'candidate_rejected_stitching.json').write_text(json.dumps(removed,indent=2)+'\n')
print('Removed',len(removed),'rejected new vias',flush=True)

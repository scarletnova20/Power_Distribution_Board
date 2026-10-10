"""Center reported connected track ends on their vias. Adapted from
engineering/center_via_tracks.py for the release50 candidate; no rule changes."""
import sys,json; sys.path.insert(0,'../vendor')
from pathlib import Path
import pcbnew as p
b=p.LoadBoard('PDB_50A.kicad_pcb')
items={t.m_Uuid.AsString():t for t in b.GetTracks()}
count=0
for issue in json.loads(Path(sys.argv[1]).read_text())['violations']:
    if issue['type']!='track_not_centered_on_via': continue
    pair=[items[i['uuid']] for i in issue['items']]
    via=next(t for t in pair if isinstance(t,p.PCB_VIA))
    track=next(t for t in pair if not isinstance(t,p.PCB_VIA))
    pos=via.GetPosition()
    d=lambda pt:(pt.x-pos.x)**2+(pt.y-pos.y)**2
    if d(track.GetStart())<d(track.GetEnd()):
        assert d(track.GetStart())<p.FromMM(.45)**2; track.SetStart(pos)
    else:
        assert d(track.GetEnd())<p.FromMM(.45)**2; track.SetEnd(pos)
    count+=1
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard('PDB_50A.kicad_pcb',b)
print('Centered',count,'reported track ends')

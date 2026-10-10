"""Center reported connected track ends without changing design rules."""
from pathlib import Path
import json
import pcbnew as p
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
if not Path('engineering/before_centering.kicad_pcb').exists():
    Path('engineering/before_centering.kicad_pcb').write_bytes(Path('Swayatt_PCB.kicad_pcb').read_bytes())
items={t.m_Uuid.AsString():t for t in b.GetTracks()}
count=0
for issue in json.loads(Path('engineering/drc.json').read_text())['violations']:
    if issue['type']!='track_not_centered_on_via':continue
    pair=[items[i['uuid']] for i in issue['items']]
    via=next(t for t in pair if isinstance(t,p.PCB_VIA))
    track=next(t for t in pair if not isinstance(t,p.PCB_VIA))
    pos=via.GetPosition()
    distance=lambda pt:(pt.x-pos.x)**2+(pt.y-pos.y)**2
    if distance(track.GetStart())<distance(track.GetEnd()):
        assert distance(track.GetStart())<p.FromMM(.45)**2
        track.SetStart(pos)
    else:
        assert distance(track.GetEnd())<p.FromMM(.45)**2
        track.SetEnd(pos)
    count+=1
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
print('Centered',count,'reported track ends')

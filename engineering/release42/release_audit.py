"""Read-only extraction of placement, copper routing and component release data."""
from pathlib import Path
import pcbnew as p
import json,xml.etree.ElementTree as ET,math,sys
work=Path('engineering/release42')
candidate='--candidate' in sys.argv
b=p.LoadBoard(str(work/'release_candidate.kicad_pcb') if candidate else 'Swayatt_PCB_42x42.kicad_pcb')
rows=[]
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
    pads=[]
    for q in f.Pads():
        pos=q.GetPosition();size=q.GetSize()
        pads.append({'number':q.GetNumber(),'net':q.GetNetname(),'xy':[p.ToMM(pos.x),p.ToMM(pos.y)],'size':[p.ToMM(size.x),p.ToMM(size.y)]})
    rows.append({'ref':f.GetReference(),'value':f.GetValue(),'footprint':str(f.GetFPID().GetLibItemName()),'xy':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],
                 'side':'B' if f.IsFlipped() else 'F','angle':f.GetOrientationDegrees(),'pads':pads})
summary={}
for t in b.GetTracks():
    item=summary.setdefault(t.GetNetname(),{'length_mm':0,'widths_mm':set(),'vias':0})
    if isinstance(t,p.PCB_VIA):item['vias']+=1
    else:
        item['length_mm']+=p.ToMM(t.GetLength());item['widths_mm'].add(p.ToMM(t.GetWidth()))
for item in summary.values():item['widths_mm']=sorted(item['widths_mm']);item['length_mm']=round(item['length_mm'],3)
(work/('candidate_geometry.json' if candidate else 'release_audit.json')).write_text(json.dumps({'components':rows,'routing':summary},indent=2))
for r in rows:
    if r['ref'] in ['J1','J12','Q1','Q2','Q3','Q4','R10','R11','NT2','NT3','U1','L1','D1'] or r['ref'] in ['C'+str(i) for i in range(1,13)]+['R'+str(i) for i in range(1,8)]:print(json.dumps(r))
print(json.dumps(summary,indent=2))

from pathlib import Path
import pcbnew as p,json,math
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb')
holes=[(62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)]
rows=[]
for f in b.GetFootprints():
    bb=f.GetBoundingBox(False,False)
    rect=[p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())]
    hits=[i+1 for i,(x,y) in enumerate(holes) if math.hypot(max(rect[0]-x,0,x-rect[2]),max(rect[1]-y,0,y-rect[3]))<3.25 and not f.GetReference().startswith('H')]
    rows.append({'ref':f.GetReference(),'side':'B' if f.IsFlipped() else 'F','bounds':rect,'hardware_collisions':hits})
Path('engineering/release42/placement_audit.json').write_text(json.dumps(rows,indent=2))
print('Hardware collisions:',[r for r in rows if r['hardware_collisions']])
print('Footprints',len(rows))

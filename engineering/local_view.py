import pcbnew as p
from pathlib import Path
import html
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1200" viewBox="78 203 13 14"><rect x="78" y="203" width="13" height="14" fill="#18202d"/>']
colors={}
palette=['#00e0a0','#d0acff','#ffc56a','#8aafff','#ed84bf','#e0ef8c','#7bdada']
def color(net):
    if net=='/COMP':return '#ff5555'
    if net not in colors:colors[net]=palette[len(colors)%len(palette)]
    return colors[net]
for t in b.GetTracks():
    via=isinstance(t,p.PCB_VIA)
    if not via and t.GetLayer()!=p.B_Cu:continue
    a,c=t.GetStart(),t.GetEnd();x,y,u,v=[p.ToMM(z) for z in (a.x,a.y,c.x,c.y)]
    col=color(t.GetNetname())
    if via:s.append(f'<circle cx="{x}" cy="{y}" r="{p.ToMM(t.GetWidth(p.B_Cu))/2}" fill="{col}"/><circle cx="{x}" cy="{y}" r=".1" fill="#18202d"/>')
    else:s.append(f'<path d="M{x},{y} L{u},{v}" fill="none" stroke="{col}" stroke-width="{p.ToMM(t.GetWidth())}"/>')
for f in b.GetFootprints():
    for q in f.Pads():
        if not q.GetLayerSet().Contains(p.B_Cu):continue
        bb=q.GetBoundingBox();x,y,w,h=[p.ToMM(z) for z in (bb.GetX(),bb.GetY(),bb.GetWidth(),bb.GetHeight())]
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color(q.GetNetname())}" opacity=".7"/>')
        if 78<x<91 and 203<y<217:
            label=html.escape(f.GetReference()+'.'+q.GetNumber()+q.GetNetname())
            s.append(f'<text x="{x}" y="{y+h/2}" font-size=".18" fill="white">{label}</text>')
s.append('</svg>');Path('engineering/local.svg').write_text(''.join(s))

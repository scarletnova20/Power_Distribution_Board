"""Create a separately preserved analog placement candidate for release review."""
from pathlib import Path
import pcbnew as p
import json,sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop,Atom
root=Path('engineering/release42')
backup=root/'before_fabrication_review'
backup.mkdir(exist_ok=True)
for ext in ('kicad_pcb','kicad_sch','kicad_pro'):
    src=Path('Swayatt_PCB_42x42.'+ext)
    dst=backup/src.name
    if not dst.exists():dst.write_bytes(src.read_bytes())
b=p.LoadBoard(str(backup/'Swayatt_PCB_42x42.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()}
# An SMD input reservoir removes the two PTH obstructions in the control area.
old=fs['C13'];new=p.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/footprints/Capacitor_SMD.pretty','C_Elec_8x10.2')
b.Add(new);new.SetReference('C13');new.SetValue('47u 50V EEH-ZA1H470P');new.SetFPID(p.LIB_ID('Capacitor_SMD','C_Elec_8x10.2'));new.SetPath(old.GetPath())
nets={q.GetNumber():q.GetNet() for q in old.Pads()}
for q in new.Pads():q.SetNet(nets[q.GetNumber()])
new.SetPosition(old.GetPosition());new.SetOrientation(old.GetOrientation());b.Remove(old);fs['C13']=new
fs['C9'].SetValue('120u 10V 10SVPC120M ESR27mR')
fs['R7'].SetValue('39.2k 1%')
placements={
 'R7':(91,210.95,0),'C12':(93.35,210.95,0),'C11':(91,212.45,0),
 'R6':(93.4,212.65,180),'R5':(95.1,211.6,90),'R4':(90.9,214,180),
 'C3':(93.4,214.5,180),'C5':(91,207.75,180),'C6':(83,214.7,0),
 'C2':(86.5,197.6,0),'C1':(88,203.7,0),'C8':(83.9,200.8,0),
 'C7':(81.4,206.2,0),'D1':(78.5,203,90),'L1':(75,215,0),
 'J10':(98.5,205,90),'R1':(91,200.4,0),'R2':(93.4,201.9,90),
 'C4':(91,202.6,90),'C13':(91,211.25,90),'C10':(73,220,0),
}
def point(x,y):return p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y)))
def rect(f):
    bb=f.GetBoundingBox(False,False)
    return tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()))
def overlap(a,c):return a[0]<c[2]+.12 and c[0]<a[2]+.12 and a[1]<c[3]+.12 and c[1]<a[3]+.12
moving=set(placements)
order=['C13','J10','D1','L1','C1','C2','C7','C8','C10','C5','R7','C12','C11','R6','R5','R4','C3','C6','R1','R2','C4']
for ref in order:
    ax,ay,preferred=placements[ref];f=fs[ref];obstacles=[]
    for other,h in fs.items():
        if other in moving or other.startswith('H'):continue
        if f.IsFlipped()==h.IsFlipped():obstacles.append(rect(h))
        else:
            for q in h.Pads():
                if q.GetAttribute()==p.PAD_ATTRIB_PTH:
                    bb=q.GetBoundingBox();obstacles.append(tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())))
    best=None
    for angle in (preferred,(preferred+90)%360,(preferred+180)%360,(preferred+270)%360):
        f.SetOrientationDegrees(angle);f.SetPosition(point(0,0));r=rect(f)
        for ix in range(240,401):
            x=ix*.25
            for iy in range(760,921):
                y=iy*.25;score=(x-ax)**2+(y-ay)**2+(.2 if angle!=preferred else 0)
                if best is not None and score>=best[0]:continue
                s=(r[0]+x,r[1]+y,r[2]+x,r[3]+y)
                if s[0]<59.5 or s[1]<189.5 or s[2]>100.5 or s[3]>230.5:continue
                if any(math.hypot(max(s[0]-hx,0,hx-s[2]),max(s[1]-hy,0,hy-s[3]))<3.5 for hx,hy in ((62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5))):continue
                if any(overlap(s,o) for o in obstacles):continue
                best=(score,x,y,angle)
    if best is None:raise RuntimeError('No legal placement for '+ref)
    _,x,y,angle=best;f.SetPosition(point(x,y));f.SetOrientationDegrees(angle);moving.remove(ref)
    print(ref,x,y,angle,flush=True)
# All existing tracks are kept only in the preserved source: moved control
# components must be rerouted, with power widths enforced in the next stage.
removed=list(b.GetTracks())
for t in removed:b.Remove(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(root/'analog_candidate.kicad_pcb'),b)
(root/'analog_candidate.kicad_pro').write_bytes((backup/'Swayatt_PCB_42x42.kicad_pro').read_bytes())
(root/'fp-lib-table').write_text(Path('fp-lib-table').read_text().replace('${KIPRJMOD}/Swayatt_Local.pretty','${KIPRJMOD}/../../Swayatt_Local.pretty'))
print('Saved analog placement candidate; main board unchanged',flush=True)

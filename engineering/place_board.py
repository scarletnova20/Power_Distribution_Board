"""Deterministic double-sided placement within the unchanged 40mm outline."""
from pathlib import Path
import pcbnew as p
import json, math

source=Path('engineering/before_layout/Swayatt_PCB.kicad_pcb')
if not source.exists():
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(Path('Swayatt_PCB.kicad_pcb').read_bytes())
b=p.LoadBoard(str(source))
assert not list(b.GetTracks()) and not list(b.Zones()), 'Placement source must be unrouted'
b.SetCopperLayerCount(4)
fs={f.GetReference():f for f in b.GetFootprints()}
origin=(60,190)
def xy(x,y):return p.VECTOR2I(p.FromMM(x+60),p.FromMM(y+190))
def place(ref,x,y,angle=0,back=False):
    f=fs[ref]
    if f.IsFlipped()!=back:f.Flip(f.GetPosition(),False)
    f.SetOrientationDegrees(angle)
    f.SetPosition(xy(x,y))
    f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
    return f
def rect(f):
    box=f.GetBoundingBox(False,False)
    return (p.ToMM(box.GetX())-60,p.ToMM(box.GetY())-190,
            p.ToMM(box.GetRight())-60,p.ToMM(box.GetBottom())-190)
def tht(f):return any(q.GetAttribute()==p.PAD_ATTRIB_PTH for q in f.Pads())
def overlap(a,c,gap=.12):
    return a[0]<c[2]+gap and c[0]<a[2]+gap and a[1]<c[3]+gap and c[1]<a[3]+gap
def obstacles(back):
    result=[]
    for ref,r in placed.items():
        f=fs[ref]
        if f.IsFlipped()==back:result.append((ref,r))
        else:
            for q in f.Pads():
                if q.GetAttribute()!=p.PAD_ATTRIB_PTH:continue
                bb=q.GetBoundingBox()
                result.append((ref,(p.ToMM(bb.GetX())-60-.15,p.ToMM(bb.GetY())-190-.15,
                  p.ToMM(bb.GetRight())-60+.15,p.ToMM(bb.GetBottom())-190+.15)))
    return result
placed={}
fixed={
 'J1':(10,4,0,False),'J12':(30,4,0,False),
 'Q1':(8,11,0,False),'Q2':(8,18,0,False),'Q3':(8,25,0,False),'Q4':(8,32,0,False),
 'R10':(19,14,0,False),'R11':(19,20,0,False),
 'D2':(30,12,0,False),'C13':(31,23,90,False),
 'J5':(25,31.2,0,False),'J6':(29,31.2,0,False),'J7':(33,31.2,0,False),'J8':(37,31.2,0,False),
 'BEC1':(9,2.6,0,True),'J3':(29,3,0,True),'J4':(3,16,90,True),'J10':(37,15,90,True),
 'J11':(34.5,26.9,0,True),'J2':(13,33,0,True),
 'L1':(13,19,0,True),'D1':(27,9,0,True),'U1':(25.5,20.6,0,True),
 'C1':(27,14.8,0,True),'C9':(12,8.77,0,True),
}
issues=[]
for ref,pos in fixed.items():
    f=place(ref,*pos);r=rect(f)
    if min(r[:2])<.25 or max(r[2:])>39.75:issues.append([ref,'boundary',r])
    for other,rr in obstacles(f.IsFlipped()):
        if overlap(r,rr):
            issues.append([ref,other,r,rr])
    placed[ref]=r
if issues:
    print(json.dumps({'fixed_issues':issues},indent=2),flush=True)
    p.SaveBoard('engineering/placement_trial.kicad_pcb',b)
    raise SystemExit(1)
# Small parts prefer their functional group and shortest connections to placed pads.
backrefs=set('C2 C3 C4 C5 C6 C7 C8 C10 C11 C12 R1 R2 R4 R5 R6 R7 NT1'.split())
anchors={
 'U5':(4,5),'U3':(20,25),'U2':(24,27),'U4':(19,35),'C2':(31,16),
 'C20':(4,5),'C21':(4,5),'R14':(4,5),
 'R12':(4,13),'R19':(4,20),'R20':(4,27),'R21':(4,34),
 'NT2':(19,17),'NT3':(22,17),
 'C14':(26,28),'RL1':(26,28),'R8':(25,27),'R9':(25,27),'C15':(25,27),
 'R15':(22,24),'R16':(22,24),'C16':(23,24),'C17':(20,27),
 'R17':(18,28),'R18':(18,28),'C18':(19,35),'C19':(19,35),
 'D3':(16,38),'R13':(16,37),'TP1':(9,7),'TP2':(24,28),'TP3':(24,28),
 'C7':(23,15),'C5':(30,16),'C8':(23,12),'R3':(23,12),
 'C10':(11,30),'NT1':(26,23),
}
priority=['U5','U3','U2','U4','C2','R3']
for ref in priority+[r for r in fs if r not in fixed and r not in priority]:
    back=ref in backrefs
    ax,ay=anchors.get(ref,(30,20) if back else (20,28))
    best=None
    obs=obstacles(back)
    # Use footprint courtyard-inclusive boxes and keep THT bodies clear on both faces.
    for ang in (0,90,180,270):
        f=place(ref,0,0,ang,back);local=rect(f)
        for ix in range(2,79):
            x=ix*.5
            for iy in range(2,79):
                y=iy*.5;r=(local[0]+x,local[1]+y,local[2]+x,local[3]+y)
                if min(r[:2])<.25 or max(r[2:])>39.75:continue
                if any(overlap(r,rr) for o,rr in obs):continue
                score=(x-ax)**2+(y-ay)**2+(.01 if ang else 0)
                if best is None or score<best[0]:best=(score,x,y,ang,r)
    if best is None:raise RuntimeError('No placement space for '+ref)
    _,x,y,ang,r=best;place(ref,x,y,ang,back);placed[ref]=r
    print('Placed',ref,x,y,ang,'B' if back else 'F',flush=True)
assert len(placed)==len(fs)
out={ref:{'x':round(p.ToMM(f.GetPosition().x)-60,3),'y':round(p.ToMM(f.GetPosition().y)-190,3),
 'angle':f.GetOrientationDegrees(),'side':'B' if f.IsFlipped() else 'F','bounds':placed[ref]} for ref,f in fs.items()}
Path('engineering/placement.json').write_text(json.dumps(out,indent=2))
p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
print('Placed all',len(fs),'footprints',flush=True)
print('Export API',[x for x in dir(p) if 'Specctra' in x],flush=True)


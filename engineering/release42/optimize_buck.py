"""Compact the buck power stage and place its control parts around U1."""
from pathlib import Path
import sys,math,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop
import pcbnew as p
Path('engineering/release42/before_buck.kicad_pcb').write_bytes(Path('Swayatt_PCB_42x42.kicad_pcb').read_bytes())
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb');fs={f.GetReference():f for f in b.GetFootprints()}
old=fs['L1'];f=p.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/footprints/Inductor_SMD.pretty','L_Coilcraft_XAL8080-XXX');b.Add(f)
f.SetReference('L1');f.SetValue('33u XAL8080-333MED');f.SetFPID(p.LIB_ID('Inductor_SMD','L_Coilcraft_XAL8080-XXX'));f.SetPath(old.GetPath());f.Flip(f.GetPosition(),False)
nets={q.GetNumber():q.GetNet() for q in old.Pads()}
for q in f.Pads():q.SetNet(nets[q.GetNumber()])
fs['L1']=f;b.Remove(old)
fixed={'L1':(77,211.5,180),'D1':(78.5,200,90),'C9':(66,217.375,180),'U1':(85.5,210.6,180),
       'J2':(75,225.55,0),'J4':(63,205.85,90)}
def pos(x,y):return p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y)))
for ref,(x,y,ang) in fixed.items():fs[ref].SetPosition(pos(x,y));fs[ref].SetOrientationDegrees(ang)
anchors={'C1':(87,204),'C2':(93,208),'C3':(91,214),'C4':(89,224),'C5':(91,207),
 'C6':(83,207),'C7':(82,208),'C8':(81,203),'C10':(73,218.5),'C11':(90,211),
 'C12':(91,210),'R1':(90,208),'R2':(90,224),'R4':(91,212),'R5':(92,212),
 'R6':(92,214),'R7':(92,210),'NT1':(85,207)}
moving=set(anchors)
holes=[(62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)]
def rect(f):
    bb=f.GetBoundingBox(False,False);return tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()))
def overlaps(r,s):return r[0]<s[2]+.1 and s[0]<r[2]+.1 and r[1]<s[3]+.1 and s[1]<r[3]+.1
def obstacles(f):
    obs=[]
    for ref,g in fs.items():
        if ref in moving or ref==f.GetReference() or ref.startswith('H'):continue
        if g.IsFlipped()==f.IsFlipped():obs.append((ref,rect(g)))
        else:
            for q in g.Pads():
                if q.GetAttribute()==p.PAD_ATTRIB_PTH:
                    bb=q.GetBoundingBox();obs.append((ref,tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()))))
    return obs
for ref in fixed:
    f=fs[ref];r=rect(f)
    for other,s in obstacles(f):
        if overlaps(r,s):print('FIXED COLLISION',ref,other,r,s,flush=True)
for ref,anchor in anchors.items():
    f=fs[ref];obs=obstacles(f);best=None
    for ang in (0,90,180,270):
        f.SetOrientationDegrees(ang);f.SetPosition(pos(0,0));r=rect(f)
        for ix in range(120,201):
            for iy in range(380,461):
                x,y=ix*.5,iy*.5;s=(r[0]+x,r[1]+y,r[2]+x,r[3]+y)
                if s[0]<59.5 or s[1]<189.5 or s[2]>100.5 or s[3]>230.5:continue
                if any(math.hypot(max(s[0]-hx,0,hx-s[2]),max(s[1]-hy,0,hy-s[3]))<3.55 for hx,hy in holes):continue
                if any(overlaps(s,o) for _,o in obs):continue
                score=(x-anchor[0])**2+(y-anchor[1])**2
                if best is None or score<best[0]:best=(score,x,y,ang)
    if best is None:raise RuntimeError('No placement '+ref)
    _,x,y,ang=best;f.SetPosition(pos(x,y));f.SetOrientationDegrees(ang);moving.remove(ref)
    print('Placed',ref,x,y,ang,flush=True)
for f in fs.values():f.Reference().SetVisible(False);f.Value().SetVisible(False)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
sch=parse(Path('Swayatt_PCB_42x42.kicad_sch').read_text())
for s in children(sch,'symbol'):
    if prop(s,'Reference')[2]=='L1':
        prop(s,'Value')[2]='33u XAL8080-333MED';prop(s,'Footprint')[2]='Inductor_SMD:L_Coilcraft_XAL8080-XXX'
Path('Swayatt_PCB_42x42.kicad_sch').write_text(dump(sch)+'\n')

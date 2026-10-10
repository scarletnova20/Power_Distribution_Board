from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop,Atom
import pcbnew as p
def a(v):return Atom(str(v))
lib=Path('Swayatt_Local.pretty')
fp=parse((lib/'Aux_Wire_2.kicad_mod').read_text());fp[1]='Aux_Wire_2_42'
for i,q in enumerate(children(fp,'pad')):
    one(q,'at')[1:]=[a(-2 if i==0 else 2),a(0)];one(q,'size')[1:]=[a(3),a(3)]
for r in children(fp,'fp_rect'):
    m=.25 if one(r,'layer')[1].endswith('CrtYd') else 0
    one(r,'start')[1:]=[a(-3.5-m),a(-1.5-m)];one(r,'end')[1:]=[a(3.5+m),a(1.5+m)]
one(fp,'descr')[1]='Direct solder 3A auxiliary wire lands, 3x3mm; external strain relief.'
(lib/'Aux_Wire_2_42.kicad_mod').write_text(dump(fp)+'\n')
b=p.LoadBoard('Swayatt_PCB_42x42.kicad_pcb');fs={f.GetReference():f for f in b.GetFootprints()}
old=fs['J11'];f=p.FootprintLoad(str(lib.resolve()),'Aux_Wire_2_42');b.Add(f)
f.SetReference('J11');f.SetValue(old.GetValue());f.SetFPID(p.LIB_ID('Swayatt_Local','Aux_Wire_2_42'));f.SetPath(old.GetPath())
f.Flip(f.GetPosition(),False);f.SetPosition(p.VECTOR2I(p.FromMM(94.4),p.FromMM(218.4)))
net={q.GetNumber():q.GetNet() for q in old.Pads()}
for q in f.Pads():q.SetNet(net[q.GetNumber()])
f.Reference().SetVisible(False);f.Value().SetVisible(False);fs['J11']=f
b.Remove(old)
for ref,x,y in [('J5',84.5,221.2),('J6',88.2,221.2),('J7',91.9,221.2),('J8',99,217.0)]:
    fs[ref].SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
holes=[(62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)]
def rect(f):
    bb=f.GetBoundingBox(False,False);return tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()))
def overlap(r,s):return r[0]<s[2]+.1 and s[0]<r[2]+.1 and r[1]<s[3]+.1 and s[1]<r[3]+.1
moving={'R8','R2','C4','R1','C6','TP1','R6','U2'}
for ref,anchor in [('U2',(80,219)),('R8',(94,217)),('R2',(90,222)),('C4',(90,225.5)),('R1',(87,220.5)),('C6',(87,224)),('R6',(95,222)),('TP1',(81.5,228))]:
    f=fs[ref];obs=[]
    for other,g in fs.items():
        if other in moving or other.startswith('H'):continue
        if f.IsFlipped()==g.IsFlipped():obs.append(rect(g))
        else:
            for q in g.Pads():
                if q.GetAttribute()==p.PAD_ATTRIB_PTH:
                    bb=q.GetBoundingBox();obs.append(tuple(p.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())))
    best=None
    for angle in (0,90,180,270):
        f.SetOrientationDegrees(angle);f.SetPosition(p.VECTOR2I(0,0));r=rect(f)
        for ix in range(120,201):
            for iy in range(380,461):
                x,y=ix*.5,iy*.5;s=(r[0]+x,r[1]+y,r[2]+x,r[3]+y)
                if s[0]<59.5 or s[1]<189.5 or s[2]>100.5 or s[3]>230.5:continue
                if any(math.hypot(max(s[0]-hx,0,hx-s[2]),max(s[1]-hy,0,hy-s[3]))<3.55 for hx,hy in holes):continue
                if any(overlap(s,o) for o in obs):continue
                score=(x-anchor[0])**2+(y-anchor[1])**2
                if best is None or score<best[0]:best=(score,x,y,angle)
    if best is None:raise RuntimeError('Cannot place '+ref)
    _,x,y,angle=best;f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));f.SetOrientationDegrees(angle);moving.remove(ref)
    print('Placed',ref,x,y,angle,flush=True)
for z in b.Zones():
    if z.GetIsRuleArea():z.SetDoNotAllowPads(False)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
# Remove only U1's now-invalid legacy silk graphics; pin 1 stays in Fab.
raw=parse(Path('Swayatt_PCB_42x42.kicad_pcb').read_text())
for f in children(raw,'footprint'):
    if prop(f,'Reference')[2]=='U1':
        f[:]=[v for v in f if not(isinstance(v,list) and v and str(v[0]).startswith('fp_') and one(v,'layer') and str(one(v,'layer')[1]).endswith('SilkS'))]
Path('Swayatt_PCB_42x42.kicad_pcb').write_text(dump(raw)+'\n')
local=parse((lib/'LM5576_PWP20.kicad_mod').read_text())
local[:]=[v for v in local if not(isinstance(v,list) and v and str(v[0]).startswith('fp_') and one(v,'layer') and str(one(v,'layer')[1]).endswith('SilkS'))]
(lib/'LM5576_PWP20.kicad_mod').write_text(dump(local)+'\n')
sch=parse(Path('Swayatt_PCB_42x42.kicad_sch').read_text())
for s in children(sch,'symbol'):
    if prop(s,'Reference')[2]=='J11':prop(s,'Footprint')[2]='Swayatt_Local:Aux_Wire_2_42'
    if prop(s,'Reference')[2]=='J2':prop(s,'Value')[2]='PIXHAWK 6X POWER 5024430670 VERTICAL'
Path('Swayatt_PCB_42x42.kicad_sch').write_text(dump(sch)+'\n')

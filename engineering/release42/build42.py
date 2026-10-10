"""Build the 42 mm mechanical revision from the preserved routed checkpoint."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop,Atom
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'engineering/before_release42'
stock=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
def a(v):return Atom(str(v))
def n(k,*args):return [a(k),*args]
def pt(x,y):return p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y)))
# Dedicated wire lands preserve clearly defined hand-soldered interfaces.
for old,new,pitch,w,h in [('Power_Wire_2','Power_Wire_2_42',7,6,6),('BEC_Wire_4','BEC_Wire_4_42',3.5,2.5,3)]:
    fp=parse((ROOT/'Swayatt_Local.pretty'/(old+'.kicad_mod')).read_text())
    fp[1]=new; pads=children(fp,'pad')
    for i,q in enumerate(pads):
        one(q,'at')[1:]=[a((i-(len(pads)-1)/2)*pitch),a(0)]
        one(q,'size')[1:]=[a(w),a(h)]
    width=(len(pads)-1)*pitch+w
    for r in children(fp,'fp_rect'):
        margin=.25 if one(r,'layer')[1].endswith('CrtYd') else 0
        one(r,'start')[1:]=[a(-width/2-margin),a(-h/2-margin)]
        one(r,'end')[1:]=[a(width/2+margin),a(h/2+margin)]
    one(fp,'descr')[1]='Direct solder wire land, no discrete connector; separate strain relief required. '+str(w)+' x '+str(h)+' mm lands.'
    (ROOT/'Swayatt_Local.pretty'/(new+'.kicad_mod')).write_text(dump(fp)+'\n')
# TI PWP0020A / MXA20A Rev C, LM5576 datasheet p37: EP 3.0 x 4.2,
# lead lands 1.78 x .42 at 5.94 mm opposing-row spacing.
fp=parse((stock/'Package_SO.pretty/HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm.kicad_mod').read_text())
fp[1]='LM5576_PWP20';one(fp,'descr')[1]='TI LM5576 PWP0020A MXA20A Rev C land pattern; 3.0x4.2 EP and 1.78x0.42 lands, 5.94mm rows.'
fp[:]=[v for v in fp if not(isinstance(v,list) and v and v[0]=='pad' and v[1]=='')]
for q in children(fp,'pad'):
    if q[1]=='21':
        one(q,'size')[1:]=[a(3),a(4.2)]
        one(q,'layers')[1:]=['F.Cu','F.Mask']
    else:
        at=one(q,'at'); at[1]=a(-2.97 if float(at[1])<0 else 2.97)
        one(q,'size')[1:]=[a(1.78),a(.42)]
for x in (-.75,.75):
    for y in (-1.4,0,1.4):
        fp.append(n('pad','',a('smd'),a('rect'),n('at',a(x),a(y)),n('size',a(1.15),a(1.05)),n('layers','F.Paste')))
(ROOT/'Swayatt_Local.pretty/LM5576_PWP20.kicad_mod').write_text(dump(fp)+'\n')
raw=parse((src/'Swayatt_PCB.kicad_pcb').read_text())
# Preserve original UUIDs, update exact outline, and add mechanical parts through API.
edges=[v for v in children(raw,'gr_line') if one(v,'layer')[1]=='Edge.Cuts']
for e,(x,y,u,v) in zip(edges,[(59,189,101,189),(101,189,101,231),(101,231,59,231),(59,231,59,189)]):
    one(e,'start')[1:]=[a(x),a(y)];one(e,'end')[1:]=[a(u),a(v)]
Path('engineering/release42/input.kicad_pcb').write_text(dump(raw)+'\n')
b=p.LoadBoard('engineering/release42/input.kicad_pcb')
fs={f.GetReference():f for f in b.GetFootprints()}
vertical=parse((stock/'Connector_Molex.pretty/Molex_CLIK-Mate_502443-0670_1x06-1MP_P2.00mm_Vertical.kicad_mod').read_text())
vertical[1]='CLIK_Mate_502443_0670'
(ROOT/'Swayatt_Local.pretty/CLIK_Mate_502443_0670.kicad_mod').write_text(dump(vertical)+'\n')
changes={'J1':('Power_Wire_2_42',73.5,193.75),'J12':('Power_Wire_2_42',87.2,193.75),
         'BEC1':('BEC_Wire_4_42',72.75,192.5),'J3':('BEC_Wire_4_42',87.25,192.5),
         'U1':('LM5576_PWP20',85.5,210.6),'J2':('CLIK_Mate_502443_0670',74,224)}
pad_moves={}; replacements=[]
for ref,(name,x,y) in changes.items():
    old=fs[ref];f=p.FootprintLoad(str(ROOT/'Swayatt_Local.pretty'),name)
    b.Add(f)
    f.SetFPID(p.LIB_ID('Swayatt_Local',name));f.SetReference(ref);f.SetValue(old.GetValue())
    f.SetPath(old.GetPath());f.SetSheetfile(old.GetSheetfile());f.SetSheetname(old.GetSheetname())
    if old.IsFlipped():f.Flip(f.GetPosition(),False)
    f.SetOrientation(old.GetOrientation());f.SetPosition(pt(x,y));f.SetLocalClearance(old.GetLocalClearance())
    nets={q.GetNumber():q.GetNet() for q in old.Pads() if q.GetNumber()}
    oldpos={q.GetNumber():q.GetPosition() for q in old.Pads() if q.GetNumber()}
    for q in f.Pads():
        if q.GetNumber() in nets:
            q.SetNet(nets[q.GetNumber()]);o=oldpos[q.GetNumber()]
            pad_moves[(o.x,o.y,q.GetNetCode())]=q.GetPosition()
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
    replacements.append(old);fs[ref]=f
# Retain C16's previous correction. Shift two corner-adjacent connectors.
for ref,dx,dy in [('J7',-.9,0),('J8',0,-4.1),('J11',0,-2),('Q4',.9,0),('R21',1,-2.5),('R8',-1,-1)]:
    f=fs[ref];ops=[(q,q.GetPosition()) for q in f.Pads()]
    f.SetPosition(f.GetPosition()+pt(dx,dy))
    for q,o in ops:pad_moves[(o.x,o.y,q.GetNetCode())]=q.GetPosition()
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):continue
    for get,set in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
        o=get();key=(o.x,o.y,t.GetNetCode())
        if key in pad_moves:set(pad_moves[key])
# Remove originals after all footprint iteration; keep references alive until save.
for f in replacements:b.Remove(f)
for i,(x,y) in enumerate([(62.5,192.5),(97.5,192.5),(62.5,227.5),(97.5,227.5)],1):
    f=p.FootprintLoad(str(stock/'MountingHole.pretty'),'MountingHole_3.2mm_M3')
    f.SetReference('H'+str(i));f.SetValue('M3 3.2mm NPTH');f.SetPosition(pt(x,y));f.Reference().SetVisible(False)
    f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(f)
    # Screw-head envelope on both faces, and all-layer copper keepout.
    z=p.ZONE(b);ls=p.LSET()
    for layer in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu):ls.AddLayer(layer)
    z.SetLayerSet(ls);z.SetIsRuleArea(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True)
    z.SetZoneName('H'+str(i)+' M3 hardware clearance dia6.5mm')
    poly=z.Outline();poly.NewOutline()
    for j in range(64):poly.Append(p.FromMM(x+3.25*math.cos(j*math.tau/64)),p.FromMM(y+3.25*math.sin(j*math.tau/64)))
    b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
sch=parse((src/'Swayatt_PCB.kicad_sch').read_text())
for s in children(sch,'symbol'):
    ref=prop(s,'Reference')[2]
    if ref in changes:prop(s,'Footprint')[2]='Swayatt_Local:'+changes[ref][0]
Path('Swayatt_PCB_42x42.kicad_sch').write_text(dump(sch)+'\n')
data=json.loads((src/'Swayatt_PCB.kicad_pro').read_text())
rules=data['board']['design_settings']['rules'];rules['min_silk_clearance']=.15
for k,v in data['board']['design_settings']['rule_severities'].items():
    if v=='ignore':data['board']['design_settings']['rule_severities'][k]='warning'
Path('Swayatt_PCB_42x42.kicad_pro').write_text(json.dumps(data,indent=2)+'\n')
print('Built 42x42 mechanical revision with 35x35 M3 pattern; requires full rerouting/DRC before release.')

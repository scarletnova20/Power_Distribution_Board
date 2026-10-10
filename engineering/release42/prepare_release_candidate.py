from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop,Atom
import pcbnew as p
root=Path('engineering/release42')
raw=parse((root/'analog_candidate.kicad_pcb').read_text())
def rename(v):
    if isinstance(v,list):return [rename(x) for x in v]
    return '/9V_DJI' if v=='/12V_DJI' else v
raw=rename(raw)
stack=one(one(raw,'setup'),'stackup')
for layer in children(stack,'layer'):
    if layer[1] in ('In1.Cu','In2.Cu'):one(layer,'thickness')[1]=Atom('.07')
    if layer[1]=='dielectric 2':one(layer,'thickness')[1]=Atom('.90')
setup=one(raw,'setup');one(setup,'capping')[1]=Atom('yes');one(setup,'filling')[1]=Atom('yes')
for z in children(raw,'zone'):
    net=one(z,'net')
    if net is None or net[1] not in ('/BAT_FUSED','/VCC'):continue
    pts=[(60.4,190.4),(73.2,190.4),(73.2,197.4),(66,197.4),(66,229.6),(60.4,229.6)] if net[1]=='/BAT_FUSED' else [(66.4,197.8),(78.8,197.8),(78.8,229.6),(66.4,229.6)]
    one(one(z,'polygon'),'pts')[1:]=[[Atom('xy'),Atom(str(x)),Atom(str(y))] for x,y in pts]
target=root/'release_candidate.kicad_pcb';target.write_text(dump(raw)+'\n')
b=p.LoadBoard(str(target));fs={f.GetReference():f for f in b.GetFootprints()}
for f in fs.values():f.Reference().SetVisible(False);f.Value().SetVisible(False)
def point(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
fs['C2'].SetPosition(point(86.5,198.5))
fs['J1'].SetValue('4S FUSED INPUT 16.8V MAX NORMAL')
fs['J12'].SetValue('SPEEDYBEE ESC BATTERY 4S')
fs['J10'].SetValue('EXTERNAL BEC 9V DJI');fs['J11'].SetValue('9V DJI OUTPUT')
# Explicit power routing rather than 0.2mm autorouted branch traces.
nets={q.GetNetname():q.GetNet() for f in fs.values() for q in f.Pads() if q.GetNumber()}
def track(net,layer,width,coords):
    for a,c in zip(coords,coords[1:]):
        t=p.PCB_TRACK(b);t.SetStart(point(*a));t.SetEnd(point(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
def via(net,x,y):
    v=p.PCB_VIA(b);v.SetPosition(point(x,y));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);v.SetLocked(True);b.Add(v)
track('/5V_Servo',p.B_Cu,1.8,[(89,192.5),(89,195.4),(94,195.4),(94,198.2)])
for x in (93.6,94.4):
    for y in (197.4,198.2,199):
        via('/5V_Servo',x,y)
track('/5V_Servo',p.In2_Cu,2.8,[(94,197.4),(94,201),(94.5,202),(94.5,223.74),(84.5,223.74)])
track('/9V_Servo',p.B_Cu,1.5,[(63,203.85),(63,205.3)])
for x in (61.8,62.6,63.4,64.2):via('/9V_Servo',x,205.3)
for layer in (p.B_Cu,p.In1_Cu):track('/9V_Servo',layer,.8,[(61.8,205.3),(64.2,205.3)])
track('/9V_Servo',p.In1_Cu,1.5,[(63,205.3),(66,216.5),(95.5,216.5),(95.5,219.54),(99,219.54)])
track('/9V_DJI',p.In2_Cu,1.2,[(98,203),(97,204),(97,215.5),(97.2,217.8)])
for x,y in ((97.6,202.6),(98.4,203.4),(96.8,217.8),(97.6,217.8)):via('/9V_DJI',x,y)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
(root/'release_candidate.kicad_pro').write_bytes((root/'analog_candidate.kicad_pro').read_bytes())
sch=parse((root/'before_fabrication_review/Swayatt_PCB_42x42.kicad_sch').read_text())
def rename_sch(v):
    if isinstance(v,list):return [rename_sch(x) for x in v]
    return '9V_DJI' if v=='12V_DJI' else v
sch=rename_sch(sch)
updates={'C13':('47u 50V EEH-ZA1H470P','Capacitor_SMD:C_Elec_8x10.2'),
 'C9':('120u 10V 10SVPC120M ESR27mR',None),'R7':('39.2k 1%',None),
 'J1':('4S FUSED INPUT 16.8V MAX NORMAL',None),'J12':('SPEEDYBEE ESC BATTERY 4S',None),
 'J10':('EXTERNAL BEC 9V DJI',None),'J11':('9V DJI OUTPUT',None)}
for sym in children(sch,'symbol'):
    ref=prop(sym,'Reference')[2]
    if ref in updates:
        value,footprint=updates[ref];prop(sym,'Value')[2]=value
        if footprint:prop(sym,'Footprint')[2]=footprint
(root/'release_candidate.kicad_sch').write_text(dump(sch)+'\n')
(root/'sym-lib-table').write_text(Path('sym-lib-table').read_text().replace('${KIPRJMOD}/Swayatt_Local.kicad_sym','${KIPRJMOD}/../../Swayatt_Local.kicad_sym'))
print('Prepared 4S release candidate with dedicated auxiliary power routes',flush=True)

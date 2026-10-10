"""Rebuild the unrouted design as a reviewable, locally self-contained schematic.
High-current mechanical selection remains a release blocker; no manufacturing export.
"""
from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as ET
import uuid, math, json
from sexpr import *

def a(v): return Atom(str(v))
def node(k,*vs): return [a(k),*vs]
def uid(): return str(uuid.uuid4())
def xy(k,x,y,rot=None): return node(k,a(round(x,4)),a(round(y,4)),*([a(rot)] if rot is not None else []))
def effects(size=1,hide=False,just=None):
    e=node('effects',node('font',node('size',a(size),a(size))))
    if hide:e.append(node('hide',a('yes')))
    if just:e.append(node('justify',a(just)))
    return e

base=Path('engineering/baseline')
root=parse((base/'Swayatt_PCB.kicad_sch').read_text(encoding='utf-8'))
lib=one(root,'lib_symbols')
libs={s[1]:deepcopy(s) for s in children(lib,'symbol')}
symbols={prop(s,'Reference')[2]:deepcopy(s) for s in children(root,'symbol') if not prop(s,'Reference')[2].startswith('#')}
nl=ET.parse(base/'netlist.xml').getroot()
nets={}
renames={'GND':'PGND','Net-(D1-K)':'SW','Net-(U1-SW)':'SW','Net-(U1-VCC)':'BUCK_BIAS','Net-(J1-Pin_1)':'BAT_RAW','Net-(Q1-D)':'BAT_FUSED','Net-(Q1-G)':'PMOS_GATE','Net-(C8-Pad2)':'SNUB','Net-(C12-Pad1)':'COMP_RC'}
renamed_sources={}
for n in nl.find('nets'):
    name=n.attrib['name']; name=renames.get(name,name.removeprefix('/'))
    if name.startswith('Net-(U1-'):name=name[8:-1]
    renamed_sources.setdefault(name,set()).add(n.attrib['name'])
    for p in n:nets[(p.attrib['ref'],p.attrib['pin'])]=None if name.startswith('unconnected-') else name
for name,sources in renamed_sources.items():
    if len(sources)>1 and sources!={'Net-(D1-K)','Net-(U1-SW)'}:
        raise ValueError(f'Unapproved net-name collision: {name}: {sorted(sources)}')

def use_stock(library,name):
    key=library+':'+name
    if key not in libs:
        stock=parse((Path('C:/Program Files/KiCad/10.0/share/kicad/symbols')/(library+'.kicad_sym')).read_text(encoding='utf-8'))
        s=deepcopy(next(s for s in children(stock,'symbol') if s[1]==name))
        if one(s,'extends'):
            parent_name=one(s,'extends')[1]
            parent=deepcopy(libs[use_stock(library,parent_name)])
            parent[1]=key
            for sub in children(parent,'symbol'):sub[1]=name+sub[1][len(parent_name):]
            for p in children(s,'property'):
                oldp=prop(parent,p[1])
                if oldp:parent.remove(oldp)
                parent.append(deepcopy(p))
            s=parent
        s[1]=key;libs[key]=s
    return key

def add(ref,template,key=None):
    s=deepcopy(symbols[template]);one(s,'uuid')[1]=uid();prop(s,'Reference')[2]=ref
    if key:one(s,'lib_id')[1]=key
    s[:]=[v for v in s if not (isinstance(v,list) and v and v[0] in ('pin','instances'))]
    symbols[ref]=s
    return s

# Datasheet pin functions; OUT is a voltage-sense input despite the table's O tag.
u=libs[one(symbols['U1'],'lib_id')[1]]
types={'1':'power_out','3':'power_in','4':'power_in','7':'input','9':'output','10':'power_in','11':'output','12':'input','13':'power_in','14':'power_in','17':'power_out','18':'passive','21':'power_in'}
for sub in children(u,'symbol'):
    for p in children(sub,'pin'):
        pn=one(p,'number')[1]
        if pn in types:p[1]=a(types[pn])
q=use_stock('Transistor_FET','Q_PMOS_GDS');one(symbols['Q1'],'lib_id')[1]=q
nets[('Q1','1')]='PMOS_GATE';nets[('Q1','2')]='BAT_FUSED'
for pn in ('17','18','19'):nets[('U1',pn)]='SW'
for pn in ('15','16'):nets[('U1',pn)]='IS_RETURN'
nets[('U1','21')]='PGND';nets[('D1','2')]='IS_RETURN';nets[('R3','2')]='IS_RETURN'
for ref in ('J3','J4','J10'):nets[(ref,'1')]='Vin'
for ref,pin in [('C14','2'),('U2','2'),('RL1','2'),('R9','2'),('C4','1'),('R2','1')]:nets[(ref,pin)]='GNDA'
nets[('U2','5')]='out';nets[('C14','1')]='out'

add('C15','C14');nets.update({('C15','1'):'Voltage',('C15','2'):'GNDA'})
add('D2','D1',use_stock('Device','D_Zener'));nets.update({('D2','1'):'VCC',('D2','2'):'PMOS_GATE'})
add('D3','D1',use_stock('Device','LED'));nets.update({('D3','1'):'PGND',('D3','2'):'LED_A'})
add('R13','R4');nets.update({('R13','1'):'out',('R13','2'):'LED_A'})
add('R14','R4');nets.update({('R14','1'):'VCC',('R14','2'):'PMOS_GATE'})
add('TP1','R4',use_stock('Connector','TestPoint'));nets[('TP1','1')]='5V_PI'
for ref,net,sense in [('NT2','VCC','SENSE_P'),('NT3','Vin','SENSE_N')]:
    add(ref,'NT1');nets[(ref,'1')]=net;nets[(ref,'2')]=sense
nets[('U2','3')]='SENSE_P';nets[('U2','4')]='SENSE_N'

# Pixhawk 6X power ports carry digital I2C, never analog telemetry.
for ref,net in [('TP2','Current'),('TP3','Voltage')]:
    add(ref,'TP1');nets[(ref,'1')]=net
nets[('J2','3')]='SCL';nets[('J2','4')]='SDA'
add('U4','U2',use_stock('Regulator_Linear','TLV75533PDBV'))
for pn,net in {'1':'out','2':'GNDA','3':'out','4':None,'5':'3V3'}.items():nets[('U4',pn)]=net
# INA228 is not present in the installed stock library. Draw the datasheet DGS pinout.
ina=node('symbol','Custom:INA228',node('pin_names',node('offset',a(.508))),node('in_bom',a('yes')),node('on_board',a('yes')),
    node('property','Reference','U',xy('at',0,12.7,0),effects(1.27)),node('property','Value','INA228',xy('at',0,10.16,0),effects(1.27)))
ina.append(node('symbol','INA228_0_1',node('rectangle',xy('start',-7.62,7.62),xy('end',7.62,-7.62),node('stroke',node('width',a(.254)),node('type',a('default'))),node('fill',node('type',a('background'))))))
pins=node('symbol','INA228_1_1')
for pn,name,typ,x,y,rot in [('1','A1','input',-12.7,-2.54,0),('2','A0','input',-12.7,-5.08,0),('3','~{ALERT}','open_collector',12.7,-5.08,180),('4','SDA','bidirectional',12.7,0,180),('5','SCL','input',12.7,2.54,180),('6','VS','power_in',0,12.7,270),('7','GND','power_in',0,-12.7,90),('8','VBUS','input',-12.7,0,0),('9','IN-','input',-12.7,2.54,0),('10','IN+','input',-12.7,5.08,0)]:
    pins.append(node('pin',a(typ),a('line'),xy('at',x,y,rot),node('length',a(5.08)),node('name',name,effects(1.0)),node('number',pn,effects(1.0))))
ina.append(pins);libs['Custom:INA228']=ina;add('U3','U2','Custom:INA228')
for pn,net in {'1':'3V3','2':'3V3','3':None,'4':'SDA','5':'SCL','6':'3V3','7':'GNDA','8':'Vin','9':'DIG_SENSE_N','10':'DIG_SENSE_P'}.items():nets[('U3',pn)]=net
for ref,p,n in [('R15','SENSE_P','DIG_SENSE_P'),('R16','SENSE_N','DIG_SENSE_N'),('R17','3V3','SCL'),('R18','3V3','SDA')]:
    add(ref,'R4');nets[(ref,'1')]=p;nets[(ref,'2')]=n
for ref,p,n in [('C16','DIG_SENSE_P','DIG_SENSE_N'),('C17','3V3','GNDA'),('C18','out','GNDA'),('C19','3V3','GNDA')]:
    add(ref,'C14');nets[(ref,'1')]=p;nets[(ref,'2')]=n
for key,net in list(nets.items()):
    if net=='9V_DJI':nets[key]='12V_DJI'
# External fuse is explicitly outside the board and precedes the input connector.
add('BT1','J1');one(symbols['BT1'],'on_board')[1]=a('no');one(symbols['F1'],'on_board')[1]=a('no')
nets[('BT1','1')]='BAT_RAW';nets[('BT1','2')]='PGND';nets[('J1','1')]='BAT_FUSED'

# Change the output bulk symbol to visibly polarized, retaining its pin mapping.
one(symbols['C9'],'lib_id')[1]=use_stock('Device','C_Polarized')
values={'C1':'2.2u 100V X7R','C2':'2.2u 100V X7R','C4':'10n 25V','C5':'470n 25V','C6':'10n 25V','C7':'22n 100V X7R','C8':'330p 100V C0G','C9':'150u 10V polymer ESR<=30mR','C10':'22u 16V X7R','C11':'22p C0G','C12':'10n C0G','C13':'47u 100V low-ESR','C14':'100n 25V','C15':'100n 25V','R1':'90.9k 1%','R2':'10k 1%','R8':'20k 1% 0.25W','R12':'10k 0.5W','R13':'1k 1%','R14':'100k','D2':'BZT52H-C12','D3':'GREEN','Q1':'SQM120P06-07L','L1':'33u DR127-330-R','D1':'STPS5H100B','F1':'80A >=58V HOLDER UNRESOLVED','TP1':'5V_PI AUX'}
fps={'C1':'Capacitor_SMD:C_1812_4532Metric','C2':'Capacitor_SMD:C_1812_4532Metric','C7':'Capacitor_SMD:C_0805_2012Metric','C8':'Capacitor_SMD:C_0805_2012Metric','R8':'Resistor_SMD:R_1206_3216Metric','R12':'Resistor_SMD:R_2010_5025Metric','D2':'Diode_SMD:D_SOD-123F','D3':'LED_SMD:LED_0805_2012Metric','TP1':'TestPoint:TestPoint_Pad_D1.5mm','L1':'Swayatt_Local:DR127','D1':'Swayatt_Local:STPS5H100B','F1':''}
for ref,val in values.items():prop(symbols[ref],'Value')[2]=val
for ref,fp in fps.items():prop(symbols[ref],'Footprint')[2]=fp
for ref,val in {'U3':'INA228AIDGSR I2C=0x45','U4':'TLV75533PDBV','R15':'10R 1%','R16':'10R 1%','R17':'4.7k','R18':'4.7k','C16':'100n 100V X7R','C17':'100n 25V','C18':'1u 16V','C19':'1u 16V','F1':'80A 58V 142.5631.5802 EXTERNAL','BT1':'BATTERY HARNESS EXTERNAL','J1':'FUSED BATTERY INPUT','J2':'PIXHAWK 6X DIGITAL POWER','J10':'BEC_12V_DJI','TP2':'CURRENT ANALOG TEST','TP3':'VOLTAGE ANALOG TEST'}.items():prop(symbols[ref],'Value')[2]=val
for ref,fp in {'U3':'Package_SO:MSOP-10_3x3mm_P0.5mm','U4':'Package_TO_SOT_SMD:SOT-23-5','J2':'Connector_Molex:Molex_CLIK-Mate_502494-0670_1x06-1MP_P2.00mm_Horizontal','C16':'Capacitor_SMD:C_0805_2012Metric','F1':'','BT1':''}.items():prop(symbols[ref],'Footprint')[2]=fp
prop(symbols['C13'],'Value')[2]='47u 100V EEUFS2A470L'
for ref in ('J1','J12'):prop(symbols[ref],'Footprint')[2]='Swayatt_Local:Power_Wire_2'
for ref in ('J3','J4','J10','BEC1'):prop(symbols[ref],'Footprint')[2]='Swayatt_Local:BEC_Wire_4'
prop(symbols['J11'],'Footprint')[2]='Swayatt_Local:Aux_Wire_2'
for ref in ('TP2','TP3'):
    prop(symbols[ref],'Footprint')[2]='TestPoint:TestPoint_Pad_D1.5mm'
for ref in ('R10','R11'):
    prop(symbols[ref],'Value')[2]='500u 3W 1% WSLP2512L5000FEA'
    prop(symbols[ref],'Footprint')[2]='Swayatt_Local:WSLP2512_L5000'

# User selected 4-6S operation with SpeedyBee Mini V2 ESC (25.2V max).
# Four parallel NMOS devices provide reverse-battery protection. Sources face
# the battery and drains face the shunt, so body diodes conduct forward during
# initial startup. This is deliberately NOT an inrush-limiting load switch.
nmos=use_stock('Transistor_FET','Q_NMOS_GDS')
one(symbols['Q1'],'lib_id')[1]=nmos
for i in range(2,5):add(f'Q{i}','Q1',nmos)
for i,rr in enumerate(('R12','R19','R20','R21'),1):
    ref=f'Q{i}'
    if rr not in symbols:add(rr,'R4')
    for pn,net in {'1':f'GATE_Q{i}','2':'VCC','3':'BAT_FUSED'}.items():nets[(ref,pn)]=net
    nets[(rr,'1')]='NMOS_DRIVE';nets[(rr,'2')]=f'GATE_Q{i}'
    prop(symbols[ref],'Value')[2]='ISC027N10NM6 100V 2.7mR'
    prop(symbols[ref],'Footprint')[2]='Swayatt_Local:ISC027N10NM6_GDS'
    prop(symbols[rr],'Value')[2]='4.7R'
    prop(symbols[rr],'Footprint')[2]='Resistor_SMD:R_0603_1608Metric'
nets[('R14','1')]='NMOS_DRIVE';nets[('R14','2')]='BAT_FUSED'
prop(symbols['R14'],'Value')[2]='1M gate-source bleed'
# Integrated gate drive is limited to 13.9V, within the MOSFET +/-20V rating.
# D2 is now the bidirectional input TVS; it must not forward-conduct on reversal.
one(symbols['D2'],'lib_id')[1]=use_stock('Device','D_TVS')
nets[('D2','1')]='BAT_FUSED';nets[('D2','2')]='PGND'
prop(symbols['D2'],'Value')[2]='SMCJ28CA bidirectional'
prop(symbols['D2'],'Footprint')[2]='Diode_SMD:D_SMC'

ctl=node('symbol','Custom:LM74502H',node('pin_names',node('offset',a(.508))),node('in_bom',a('yes')),node('on_board',a('yes')),
    node('property','Reference','U',xy('at',0,12.7,0),effects(1.27)),node('property','Value','LM74502H',xy('at',0,10.16,0),effects(1.27)))
ctl.append(node('symbol','LM74502H_0_1',node('rectangle',xy('start',-7.62,7.62),xy('end',7.62,-7.62),node('stroke',node('width',a(.254)),node('type',a('default'))),node('fill',node('type',a('background'))))))
ctlpins=node('symbol','LM74502H_1_1')
for pn,name,typ,x,y,rot in [('1','EN','input',-12.7,0,0),('2','GND','power_in',0,-12.7,90),('3','NC','no_connect',12.7,-5.08,180),('4','VCAP','passive',12.7,5.08,180),('5','VS','power_in',-12.7,5.08,0),('6','GATE','output',12.7,2.54,180),('7','OV','input',-12.7,-5.08,0),('8','SRC','input',12.7,0,180)]:
    ctlpins.append(node('pin',a(typ),a('line'),xy('at',x,y,rot),node('length',a(5.08)),node('name',name,effects(1)),node('number',pn,effects(1))))
ctl.append(ctlpins);libs['Custom:LM74502H']=ctl;add('U5','U2','Custom:LM74502H')
prop(symbols['U5'],'Value')[2]='LM74502HDDFR REVERSE ONLY'
prop(symbols['U5'],'Footprint')[2]='Swayatt_Local:LM74502_DDF8'
for pn,net in {'1':'BAT_FUSED','2':'PGND','3':None,'4':'CHARGE_PUMP','5':'BAT_FUSED','6':'NMOS_DRIVE','7':'PGND','8':'BAT_FUSED'}.items():nets[('U5',pn)]=net
for ref,pn,nn,val,fp in [('C20','CHARGE_PUMP','BAT_FUSED','1u 25V X7R','Capacitor_SMD:C_0805_2012Metric'),('C21','BAT_FUSED','PGND','100n 100V X7R','Capacitor_SMD:C_0805_2012Metric')]:
    add(ref,'C14');nets[(ref,'1')]=pn;nets[(ref,'2')]=nn
    prop(symbols[ref],'Value')[2]=val;prop(symbols[ref],'Footprint')[2]=fp
prop(symbols['J1'],'Value')[2]='4-6S FUSED INPUT 25.2V MAX'
prop(symbols['J12'],'Value')[2]='SPEEDYBEE ESC BATTERY 4-6S'

# Organize by function on A2. Every pin has an explicit named connection or NC.
groups=[('POWER PATH - NOT RELEASED FOR 80A',30,30,['J1','F1','Q1','R10','R11','J12','R12','D2','R14','C13']),('BUCK POWER',30,95,['C1','C2','C5','C7','D1','C8','R3','L1','C9','C10']),('BUCK CONTROL',30,160,['R1','R2','C4','R4','C3','C6','R5','R6','R7','C12','C11','NT1','R13','D3']),('ANALOG TEST AND KELVIN INTERFACES',30,245,['NT2','NT3','C14','RL1','R8','R9','C15','J2']),('EXTERNAL BEC AND SERVO INTERFACES',300,120,['BEC1','J3','J4','J10','J5','J6','J7','J8','J11','TP1'])]
positions={}
for title,x,y,refs in groups:
    for i,ref in enumerate(refs):positions[ref]=(x+(i%5)*48.26,y+15.24+(i//5)*27.94)
positions['U1']=(350.52,53.34);positions['U2']=(350.52,248.92)
groups.append(('PIXHAWK 6X DIGITAL TELEMETRY / I2C 0x45',300,285,['R15','R16','R17','R18','C16','C17','C18','C19','TP2','TP3']))
for title,x,y,refs in groups[-1:]:
    for i,ref in enumerate(refs):positions[ref]=(x+(i%5)*48.26,y+15.24+(i//5)*27.94)
positions.update({'BT1':(271.78,45.24),'U3':(462.28,248.92),'U4':(462.28,370.84)})
groups.append(('4-6S NMOS REVERSE PROTECTION / NO INRUSH LIMIT',405,22,['Q2','Q3','Q4','R19','R20','R21','C20','C21']))
for i,ref in enumerate(groups[-1][3]):positions[ref]=(410+(i%3)*50.8,40+(i//3)*25.4)
positions['U5']=(520.7,207.01)
positions={ref:(round(x/1.27)*1.27,round(y/1.27)*1.27) for ref,(x,y) in positions.items()}
new=[a('kicad_sch'),deepcopy(one(root,'version')),node('generator','eeschema'),node('generator_version','10.0'),deepcopy(one(root,'uuid')),node('paper','A2'),node('title_block',node('title','Swayatt_PCB - electrical corrections / RELEASE HOLD'),node('rev','WIP-40mm'),node('comment',a(1),'80 A power path, fuse, cooling and FC interface remain unqualified'))]
newlib=node('lib_symbols');new.append(newlib)
local=node('kicad_symbol_lib',node('version',a(20241209)),node('generator','kicad_symbol_editor'))
used={}
for s in symbols.values():
    key=one(s,'lib_id')[1]
    if key not in used:
        name=key.replace(':','_'); used[key]='Swayatt_Local:'+name
        sym=deepcopy(libs[key]); old=sym[1].split(':')[-1];sym[1]=name
        for sub in children(sym,'symbol'):sub[1]=name+sub[1][len(old):]
        local.append(deepcopy(sym));sym[1]=used[key];newlib.append(sym)
    one(s,'lib_id')[1]=used[key]

def label(name,x,y,angle=0):
    new.append(node('label',name,xy('at',x,y,angle),effects(.95,just='left' if angle==0 else 'right'),node('uuid',uid())))

def wire(x1,y1,x2,y2):
    new.append(node('wire',node('pts',xy('xy',x1,y1),xy('xy',x2,y2)),node('stroke',node('width',a(0)),node('type',a('default'))),node('uuid',uid())))

for ref,s in symbols.items():
    x,y=positions[ref];one(s,'at')[1:]=[a(x),a(y),a(0)]
    s[:]=[v for v in s if not (isinstance(v,list) and v and v[0] in ('pin','instances','mirror'))]
    for p in children(s,'property'):
        p[:]=p[:3]+[xy('at',x+3.81,y+(0 if p[1]=='Reference' else 2.54),0),effects(.95,hide=p[1] not in ('Reference','Value'),just='left')]
    if ref in ('U1','U2','U3','U4','U5'):
        above={'U1':34,'U2':15,'U3':23,'U4':13,'U5':18}[ref]
        for field,offset in [('Reference',above),('Value',above-3)]:
            one(prop(s,field),'at')[1:]=[a(x),a(y-offset),a(0)]
            e=one(prop(s,field),'effects')
            e[:]=[v for v in e if not (isinstance(v,list) and v[0]=='justify')]
    if ref in ('D1','D2','D3','NT1','NT2','NT3'):
        for field,offset in [('Reference',-6.35),('Value',-3.81)]:
            one(prop(s,field),'at')[1:]=[a(x),a(y+offset),a(0)]
            e=one(prop(s,field),'effects')
            e[:]=[v for v in e if not (isinstance(v,list) and v[0]=='justify')]
    s.append(node('instances',node('project','Swayatt_PCB',node('path','/'+one(root,'uuid')[1],node('reference',ref),node('unit',a(1))))))
    sym=next(v for v in children(newlib,'symbol') if v[1]==one(s,'lib_id')[1])
    for sub in children(sym,'symbol'):
        for p in children(sub,'pin'):
            pn=one(p,'number')[1]; net=nets.get((ref,pn))
            px,py,ang=map(float,one(p,'at')[1:]);px+=x;py=y-py
            if net is None:new.append(node('no_connect',xy('at',px,py),node('uuid',uid())));continue
            # Pin angle points into the symbol, so extend in the opposite direction.
            dx=-math.cos(math.radians(ang))*2.54;dy=math.sin(math.radians(ang))*2.54
            ex,ey=round(px+dx,4),round(py+dy,4);wire(px,py,ex,ey)
            label(net,ex,ey,0 if dx>=0 else 180)
    new.append(s)

for title,x,y,refs in groups:new.append(node('text',title,xy('at',x,y,0),effects(1.5,just='left'),node('uuid',uid())))
for text,x,y in [('40 x 40 mm target. No manufacturing release until thermal and power-path redesign is resolved.',30,330),('J2: 1/2=5V, 3=SCL, 4=SDA, 5/6=PGND. Pixhawk 6X digital power interface.',30,338),('Servo pin 1: intentional NC. PWM must come from FC harness; this PCB distributes servo power only.',30,346),('NT2/NT3: dedicated Kelvin pickup at symmetric shunt terminals; no load current in SENSE_P/N.',30,354),('NT1: PGND/GNDA single PCB bond adjacent to U1 EP. Keep FC power return off GNDA.',30,362),('F1 is in the external battery harness ahead of J1. DJI rail is 12V from external BEC.',30,370)]:new.append(node('text',text,xy('at',x,y,0),effects(1.2,just='left'),node('uuid',uid())))

# Flags document externally supplied rails / passive power-path transfers, not fictitious IC outputs.
flag=deepcopy(libs[use_stock('power','PWR_FLAG')]);flag[1]='Swayatt_Local:PWR_FLAG';newlib.append(flag)
lf=deepcopy(flag);lf[1]='PWR_FLAG';local.append(lf)
for i,net in enumerate(('PGND','GNDA','Vin','out','BAT_FUSED')):
    x,y=round((310+i*35.56)/1.27)*1.27,round(395/1.27)*1.27;ref=f'#FLG0{i+1}'
    f=node('symbol',node('lib_id','Swayatt_Local:PWR_FLAG'),xy('at',x,y,0),node('unit',a(1)),node('in_bom',a('no')),node('on_board',a('yes')),node('dnp',a('no')),node('uuid',uid()),node('property','Reference',ref,xy('at',x,y,0),effects(1,True)),node('property','Value','PWR_FLAG',xy('at',x,y-5.08,0),effects(1)),node('instances',node('project','Swayatt_PCB',node('path','/'+one(root,'uuid')[1],node('reference',ref),node('unit',a(1))))))
    new.append(f);wire(x,y,x,y+2.54);label(net,x,y+2.54)
new.append(node('embedded_fonts',a('no')))
Path('Swayatt_PCB.kicad_sch').write_text(dump(new)+'\n',encoding='utf-8')
Path('Swayatt_Local.kicad_sym').write_text(dump(local)+'\n',encoding='utf-8')
Path('sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Swayatt_Local")(type "KiCad")(uri "${KIPRJMOD}/Swayatt_Local.kicad_sym")(options "")(descr "Project-local verified symbols")))\n')
Path('engineering/intended_nets.json').write_text(json.dumps({f'{r}.{p}':n for (r,p),n in nets.items() if r in symbols},indent=2))
print('Wrote',len(symbols),'components; main power path remains a release blocker.')

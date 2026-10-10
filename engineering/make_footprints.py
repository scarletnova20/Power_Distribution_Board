from pathlib import Path
from copy import deepcopy
from sexpr import *
import uuid

dest=Path('Swayatt_Local.pretty');dest.mkdir(exist_ok=True)
stock=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
def a(s):return Atom(str(s))
def n(k,*v):return [a(k),*v]
def save(f,name):
    f[1]=name
    (dest/(name+'.kicad_mod')).write_text(dump(f)+'\n',encoding='utf-8')
def basic(name,w,h):
    return n('footprint',name,n('version',a(20241229)),n('generator','pcbnew'),n('layer','F.Cu'),n('attr',a('smd')),
        n('property','Reference','REF**',n('at',a(0),a(-h/2-1),a(0)),n('layer','F.SilkS'),n('effects',n('font',n('size',a(.8),a(.8)),n('thickness',a(.12))))),
        n('property','Value',name,n('at',a(0),a(h/2+1),a(0)),n('layer','F.Fab'),n('effects',n('font',n('size',a(.8),a(.8)),n('thickness',a(.12))))),
        n('fp_rect',n('start',a(-w/2),a(-h/2)),n('end',a(w/2),a(h/2)),n('stroke',n('width',a(.1)),n('type',a('solid'))),n('fill',a('none')),n('layer','F.Fab')),
        n('fp_rect',n('start',a(-w/2-.25),a(-h/2-.25)),n('end',a(w/2+.25),a(h/2+.25)),n('stroke',n('width',a(.05)),n('type',a('solid'))),n('fill',a('none')),n('layer','F.CrtYd')))
def pad(num,x,y,w,h,paste=True):
    return n('pad',str(num),a('smd'),a('rect'),n('at',a(x),a(y)),n('size',a(w),a(h)),n('layers','F.Cu','F.Mask',*(['F.Paste'] if paste else [])))
f=basic('DR127',14.0,12.5)
f.extend([pad('1',-4.975,0,3.85,5.5),pad('2',4.975,0,3.85,5.5)])
f.append(n('descr','Eaton DR127-330-R; drawing Technical Data 4315 p6; 13.8mm pad span, 3.85 x 5.5mm lands'))
save(f,'DR127')
# Vishay 30122 rev 09-Sep-2024, p2, 0.5 to 0.99 mOhm row:
# a=3.05mm land length, b=3.68mm width, l=1.27mm inner gap.
# Two-terminal part; Kelvin traces must pick up at the inner land edges.
f=basic('WSLP2512_L5000',7.37,3.68)
f.extend([pad('1',-2.16,0,3.05,3.68),pad('2',2.16,0,3.05,3.68)])
f.append(n('descr','Vishay WSLP2512L5000FEA, 0.5mOhm 3W 1%; 30122 p2 low-resistance land pattern. Two terminals; Kelvin routing required.'))
save(f,'WSLP2512_L5000')
# ISC027N10NM6 PG-TDSON-8 FL. Schematic uses logical G=1,D=2,S=3.
# Physical pins 1/2/3=S, 4=G, 5/6/7/8 and exposed metal=D.
f=parse((stock/'Package_SON.pretty/Infineon_PG-TDSON-8_6.15x5.15mm.kicad_mod').read_text(encoding='utf-8'))
for land in children(f,'pad'):
    if land[1]:land[1]={'1':'3','2':'3','3':'3','4':'1','5':'2'}[land[1]]
f.append(pad('3',-2.825,-.635,1.2,3.19,False))
one(f,'descr')[1]='ISC027N10NM6 PG-TDSON-8 FL; enlarged source interconnection; logical pads 1=G (physical 4), 2=D (physical 5-8/tab), 3=S (physical 1-3). Infineon datasheet rev2.2 p1,p10.'
save(f,'ISC027N10NM6_GDS')
# TI DDF0008A 4222047/E: 1.05 x 0.45mm lands, 0.65mm pitch,
# 2.6mm opposing-row center spacing. Retains the project's 0.20mm gap.
f=parse((stock/'Package_TO_SOT_SMD.pretty/SOT-23-8.kicad_mod').read_text(encoding='utf-8'))
for land in children(f,'pad'):
    at=one(land,'at');at[1]=a(-1.3 if float(at[1])<0 else 1.3)
    size=one(land,'size');size[1:]=[a(1.05),a(.45)]
    if one(land,'roundrect_rratio'):one(land,'roundrect_rratio')[1]=a(.111111)
one(f,'descr')[1]='TI LM74502HDDFR DDF0008A land pattern, drawing 4222047/E July 2024; 1.05x0.45mm lands, 0.65mm pitch, 2.6mm row spacing.'
save(f,'LM74502_DDF8')
f=parse((stock/'Package_TO_SOT_SMD.pretty/TO-252-2.kicad_mod').read_text(encoding='utf-8'))
for p in children(f,'pad'):
    p[1]={'1':'2','2':'1','3':''}.get(p[1],p[1])
f.append(n('descr','STPS5H100B: DPAK lead 1=A (symbol pad 2), tab 2=K (symbol pad 1), lead 3=NC'))
save(f,'STPS5H100B')
# Heavy-wire lands are an interface geometry; their ampacity needs the final copper/harness design.
for name,count,pitch,w,h in [('BEC_Wire_4',4,4,3,4),('Power_Wire_2',2,10,8,6),('Aux_Wire_2',2,5,4,5)]:
    f=basic(name,(count-1)*pitch+w,h)
    for i in range(count):f.append(pad(i+1,(i-(count-1)/2)*pitch,0,w,h,False))
    f.append(n('descr','Direct solder wire interface; provide external strain relief; solder alloy is not an ampacity upgrade'))
    save(f,name)
Path('fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Swayatt_Local")(type "KiCad")(uri "${KIPRJMOD}/Swayatt_Local.pretty")(options "")(descr "Project-local footprints")))\n')
print('Created project footprints')
for p in (stock/'Package_SO.pretty').glob('*TDSON*'):print(p.name)

"""Apply Panasonic C6 land pattern: a=2.1, b=9.1, c=1.6 mm.

Source: https://industrial.panasonic.com/cdbs/www-data/pdf/AAB8000/AAB8000COL10.pdf
The library and embedded footprint are edited identically in local coordinates.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one,children,prop,Atom

name='Panasonic_OSCON_C6_10SVPC120M'
root=Path('engineering/release42')
stock=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints/Capacitor_SMD.pretty/C_Elec_6.3x5.8.kicad_mod')
def update(fp):
    for pad in children(fp,'pad'):
        a=one(pad,'at');a[1]=Atom(str(-2.8 if float(a[1])<0 else 2.8))
        one(pad,'size')[1:]=[Atom('3.5'),Atom('1.6')]
    for line in children(fp,'fp_line'):
        if not str(one(line,'layer')[1]).endswith('.CrtYd'):continue
        for key in ('start','end'):
            a=one(line,key)
            if abs(float(a[1]))>4:a[1]=Atom(str(-4.8 if float(a[1])<0 else 4.8))
    # Generic 5.8 mm body STEP model is not the selected 5.9 mm body.
    fp[:]=[x for x in fp if not (isinstance(x,list) and x and x[0]=='model')]
lib=parse(stock.read_text());lib[1]=name;update(lib)
one(lib,'descr')[1]='Panasonic 10SVPC120M C6, 6.3mm diameter, 6.0mm maximum height; manufacturer land pattern a2.1 b9.1 c1.6'
(Path('Swayatt_Local.pretty')/(name+'.kicad_mod')).write_text(dump(lib)+'\n')
board=root/'release_candidate.kicad_pcb';raw=parse(board.read_text())
fp=next(f for f in children(raw,'footprint') if prop(f,'Reference')[2]=='C9')
fp[1]='Swayatt_Local:'+name;update(fp)
board.write_text(dump(raw)+'\n')
sch=root/'release_candidate.kicad_sch';raw=parse(sch.read_text())
symbol=next(s for s in children(raw,'symbol') if prop(s,'Reference')[2]=='C9')
next(x for x in children(symbol,'property') if x[1]=='Footprint')[2]='Swayatt_Local:'+name
sch.write_text(dump(raw)+'\n')
print('C9 manufacturer land pattern applied to library, board and schematic')

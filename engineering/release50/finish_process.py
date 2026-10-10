from pathlib import Path
import sys,uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one,prop,Atom
import pcbnew as p
target=Path('engineering/release50/PDB_50A.kicad_pcb');raw=parse(target.read_text())
for f in children(raw,'footprint'):
    if prop(f,'Reference')[2]=='U1':one(f,'clearance')[1]=Atom('.16')
for t in children(raw,'segment'):
    if one(t,'uuid')[1]=='8a3e3537-7e2c-4329-8285-a69aac4f94d0':
        raw.remove(t)
        pts=[(83.4685,216.0605),(83.6,216.0605),(83.6,215.5),(82.908,215.5)]
        for a,c in zip(pts,pts[1:]):raw.append(parse(f'(segment (start {a[0]} {a[1]}) (end {c[0]} {c[1]}) (width 0.2) (layer "F.Cu") (net "/GNDA") (uuid "{uuid.uuid4()}"))'))
target.write_text(dump(raw)+'\n')
b=p.LoadBoard(str(target));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
print('Rerouted INA228 return around TI land pattern; U1 uses published 0.16mm process clearance')

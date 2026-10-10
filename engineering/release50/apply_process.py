"""Resolve actual process findings using TI's DGS0010A land pattern."""
from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,children,one,prop,Atom
import pcbnew as p
root=Path(__file__).resolve().parent;target=root/'PDB_50A.kicad_pcb'
backup=root/'before_process.kicad_pcb'
if not backup.exists():shutil.copy2(target,backup)
raw=parse(target.read_text())
for f in children(raw,'footprint'):
    ref=prop(f,'Reference')[2]
    if ref in ('U1','U3'):
        clearance=one(f,'clearance')
        if clearance is not None:clearance[1]=Atom('.2')
    if ref=='U3':
        f[1]='Swayatt_Local:INA228_DGS0010A'
        for pad in children(f,'pad'):
            one(pad,'size')[1:]=[Atom('1.45'),Atom('0.3')]
            at=one(pad,'at');at[1]=Atom('-2.2' if float(at[1])<0 else '2.2')
            rr=one(pad,'roundrect_rratio')
            if rr:rr[1]=Atom(str(.05/.3))
        # Land centers move outwards by 0.1 mm; move matching trace endpoints.
        for t in children(raw,'segment'):
            if one(t,'layer')[1]!='F.Cu':continue
            for key in ('start','end'):
                point=one(t,key)
                if 214-1e-6<=float(point[2])<=216+1e-6:
                    for old,new in ((77.9,77.8),(82.1,82.2)):
                        if abs(float(point[1])-old)<1e-6:point[1]=Atom(str(new))
target.write_text(dump(raw)+'\n')
lib=parse(Path('C:/Program Files/KiCad/10.0/share/kicad/footprints/Package_SO.pretty/MSOP-10_3x3mm_P0.5mm.kicad_mod').read_text())
lib[1]='INA228_DGS0010A'
for pad in children(lib,'pad'):
    one(pad,'size')[1:]=[Atom('1.45'),Atom('.3')]
    at=one(pad,'at');at[1]=Atom('-2.2' if float(at[1])<0 else '2.2')
    rr=one(pad,'roundrect_rratio')
    if rr:rr[1]=Atom(str(.05/.3))
Path('Swayatt_Local.pretty/INA228_DGS0010A.kicad_mod').write_text(dump(lib)+'\n')
schpath=root/'PDB_50A.kicad_sch';s=parse(schpath.read_text())
for f in children(s,'symbol'):
    if prop(f,'Reference')[2]=='U3':prop(f,'Footprint')[2]='Swayatt_Local:INA228_DGS0010A'
schpath.write_text(dump(s)+'\n')
b=p.LoadBoard(str(target));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
print('Applied TI DGS0010A pads, updated escape endpoints and refilled to process clearance',flush=True)

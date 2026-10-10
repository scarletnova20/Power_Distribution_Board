from pathlib import Path
from sexpr import *
for lib,words in [('Sensor_Current',['INA228']),('Regulator_Linear',['TLV75533'])]:
    r=parse((Path('C:/Program Files/KiCad/10.0/share/kicad/symbols')/(lib+'.kicad_sym')).read_text(encoding='utf-8'))
    for s in children(r,'symbol'):
        if any(w in s[1] for w in words): print(lib,s[1],one(s,'extends'),prop(s,'Footprint'))
for p in Path('C:/Program Files/KiCad/10.0/share/kicad/footprints/Connector_Molex.pretty').glob('*CLIK*06*'): print(p.name)
for p in Path('C:/Program Files/KiCad/10.0/share/kicad/footprints').rglob('*TDSON*'):print(p)

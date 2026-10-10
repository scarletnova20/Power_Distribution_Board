from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump
import pcbnew as p
raw=parse(Path('Swayatt_PCB_42x42.kicad_pcb').read_text())
raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0] in ('segment','arc','via'))]
Path('engineering/release42/unrouted.kicad_pcb').write_text(dump(raw)+'\n')
b=p.LoadBoard('engineering/release42/unrouted.kicad_pcb')
fs={f.GetReference():f for f in b.GetFootprints()}
fs['J2'].SetPosition(p.VECTOR2I(p.FromMM(75),p.FromMM(224)))
fs['R2'].SetPosition(p.VECTOR2I(p.FromMM(91.25),p.FromMM(218.8)))
fs['R2'].SetOrientationDegrees(0)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard('Swayatt_PCB_42x42.kicad_pcb',b)
print('Prepared clean rerouting input')

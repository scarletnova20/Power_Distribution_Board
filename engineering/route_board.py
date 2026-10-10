import pcbnew as p
import sys
from pathlib import Path
from sexpr import parse,dump
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
if '--import' in sys.argv:
    assert p.ImportSpecctraSES(b,'engineering/routed.ses')
    if list(b.Zones()):
        b.BuildConnectivity()
        p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard('Swayatt_PCB.kicad_pcb',b)
    print('Imported',len(list(b.GetTracks())),'tracks/vias',flush=True)
else:
    # Filled zone fragments must not be mistaken for a single connected plane
    # by DSN. Route every pad/via connection; retain and refill actual zones on import.
    raw=parse(Path('Swayatt_PCB.kicad_pcb').read_text(encoding='utf-8'))
    raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='zone')]
    Path('engineering/router_input.kicad_pcb').write_text(dump(raw)+'\n',encoding='utf-8')
    routing=p.LoadBoard('engineering/router_input.kicad_pcb')
    assert p.ExportSpecctraDSN(routing,'engineering/placed.dsn')
    dsn=Path('engineering/placed.dsn').read_text()
    large='Via[0-3]_600:300_um';small='Via[0-3]_500:200_um'
    dsn=dsn.replace('(via "'+large+'")','(via "'+small+'")')
    lib='    (padstack "'+small+'"\n'+''.join('      (shape (circle '+layer+' 500))\n' for layer in ('F.Cu','In1.Cu','In2.Cu','B.Cu'))+'      (attach off)\n    )\n'
    dsn=dsn.replace('    (padstack "'+large+'"',lib+'    (padstack "'+large+'"')
    Path('engineering/placed.dsn').write_text(dsn)
    print('Exported DSN',flush=True)

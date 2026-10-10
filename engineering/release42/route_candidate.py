from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,dump,one
import pcbnew as p
root=Path('engineering/release42');target=root/'release_candidate.kicad_pcb'
if '--import' in sys.argv:
    b=p.LoadBoard(str(target));assert p.ImportSpecctraSES(b,str(root/'candidate_routed.ses'))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(target),b)
    print('Imported candidate routing',len(list(b.GetTracks())),flush=True)
else:
    raw=parse(target.read_text())
    raw[:]=[v for v in raw if not(isinstance(v,list) and v and v[0]=='zone' and one(v,'keepout') is None)]
    (root/'candidate_router_input.kicad_pcb').write_text(dump(raw)+'\n')
    b=p.LoadBoard(str(root/'candidate_router_input.kicad_pcb'))
    assert p.ExportSpecctraDSN(b,str(root/'candidate.dsn'))
    print('Exported routing with reserved power and control paths',flush=True)

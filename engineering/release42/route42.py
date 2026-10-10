"""Route the latest mechanical revision without touching the 40 mm checkpoint."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sexpr import parse, dump, one
import pcbnew as p

board = Path('Swayatt_PCB_42x42.kicad_pcb')
work = Path('engineering/release42')
if '--import' in sys.argv:
    b = p.LoadBoard(str(board))
    session = sys.argv[sys.argv.index('--session')+1] if '--session' in sys.argv else 'routed.ses'
    assert p.ImportSpecctraSES(b, str(work/session))
    b.BuildConnectivity()
    p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(board), b)
    print('Imported tracks/vias:', len(list(b.GetTracks())), flush=True)
else:
    backup = work/'before_resume_20260908.kicad_pcb'
    if not backup.exists():
        backup.write_bytes(board.read_bytes())
    raw = parse(board.read_text())
    # Keep mounting hardware rule areas in the router input.
    raw[:] = [v for v in raw if not (isinstance(v,list) and v and
              v[0]=='zone' and one(v,'keepout') is None)]
    target = work/'router_input.kicad_pcb'
    target.write_text(dump(raw)+'\n')
    b = p.LoadBoard(str(target))
    assert p.ExportSpecctraDSN(b, str(work/'placed.dsn'))
    print('Exported DSN with hardware keepouts', flush=True)

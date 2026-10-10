"""Generate a traceable engineering-review package, never a fabrication release."""
from pathlib import Path
import subprocess,sys,json,hashlib,shutil,collections
root=Path(__file__).resolve().parent
out=root/'lioncircuits_review'
cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
board=root/'PDB_50A.kicad_pcb'
for name in ('gerbers','drill','assembly','previews','source','checks'):(out/name).mkdir(parents=True,exist_ok=True)
log=(out/'export.log').open('w',encoding='utf-8')
def run(args,allowed=(0,)):
    result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
    log.flush()
    if result.returncode not in allowed:raise RuntimeError(f'Export failed ({result.returncode}): {args}')
    print('Completed', ' '.join(args[1:4]),flush=True)
# verify50 deliberately returns 1 for DFM failures; inspect the report below.
run([sys.executable,str(root/'verify50.py')],allowed=(0,1))
v=json.loads((root/'verification.json').read_text())
assert v['board_sha256']==hashlib.sha256(board.read_bytes()).hexdigest(), 'Stale board verification'
assert v['schematic_sha256']==hashlib.sha256(board.with_suffix('.kicad_sch').read_bytes()).hexdigest(), 'Stale schematic verification'
assert not v['electrical_failures'] and not v['layout_net_failures'] and all(v['extra_checks'].values())
assert v['erc_findings']==0 and v['unconnected']==0 and not v['ignored_checks'] and not v['exclusions']
run([cli,'pcb','export','gerbers','--output',str(out/'gerbers'),
     '--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts',
     '--subtract-soldermask','--disable-aperture-macros',str(board)])
run([cli,'pcb','export','drill','--output',str(out/'drill'),'--format','excellon',
     '--excellon-separate-th','--generate-map','--map-format','svg','--generate-report',
     '--report-path',str(out/'drill/drill_report.txt'),str(board)])
run([cli,'pcb','export','gerbers','--output',str(out/'assembly'),
     '--layers','F.Paste,B.Paste,F.Fab,B.Fab','--sketch-pads-on-fab-layers','--disable-aperture-macros',str(board)])
run([cli,'pcb','export','pos','--output',str(out/'assembly/positions.csv'),
     '--format','csv','--units','mm','--side','both','--exclude-dnp',str(board)])
run([cli,'pcb','export','ipc2581','--output',str(out/'source/PDB_50A.xml'),str(board)])
for side,layers in [('front','F.Cu,F.SilkS,Edge.Cuts'),('back','B.Cu,B.SilkS,Edge.Cuts'),
                    ('assembly_front','F.Fab,Edge.Cuts'),('assembly_back','B.Fab,Edge.Cuts'),
                    ('inner_2','In1.Cu,Edge.Cuts'),('inner_3','In2.Cu,Edge.Cuts'),
                    ('mask_front','F.Mask,Edge.Cuts'),('mask_back','B.Mask,Edge.Cuts')]:
    args=[cli,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board',
          '--exclude-drawing-sheet','--output',str(out/'previews'/f'{side}.svg')]
    if 'back' in side:args+=['--mirror']
    if side.startswith('assembly'):args+=['--sketch-pads-on-fab-layers']
    run(args+[str(board)])
# LionCircuits inner-layer naming. Update Gerber job references with the files.
mapping={}
for old,new in [('PDB_50A-In1_Cu.g1','INNER_2.G2L'),('PDB_50A-In2_Cu.g2','INNER_3.G3L'),('PDB_50A-Edge_Cuts.gm1','OUTLINE.GKO')]:
    src=out/'gerbers'/old
    assert src.exists(),src
    src.replace(out/'gerbers'/new);mapping[old]=new
for job in (out/'gerbers').glob('*.gbrjob'):
    content=job.read_text()
    for old,new in mapping.items():content=content.replace(old,new)
    job.write_text(content)
for name in ('PDB_50A.kicad_pcb','PDB_50A.kicad_sch','PDB_50A.kicad_pro','PDB_50A.kicad_dru','requirements.json'):
    shutil.copy2(root/name,out/'source'/name)
for name in ('verification.json','drc.json','erc.json','netlist.xml'):
    shutil.copy2(root/name,out/'checks'/name)
shutil.copy2(root/'BOM_REVIEW.csv',out/'assembly/BOM_REVIEW.csv')
report=json.loads((root/'drc.json').read_text())
summary=collections.Counter(f['type'] for f in report['violations'])
(out/'checks/drc_summary.json').write_text(json.dumps(dict(summary),indent=2)+'\n')
log.close()
print('LionCircuits DRC findings',dict(summary),flush=True)
print('Package is HOLD FOR ENGINEERING REVIEW, not released',flush=True)

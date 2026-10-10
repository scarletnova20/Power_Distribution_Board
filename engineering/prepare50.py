"""Create the 50 A working revision once; older checkpoints remain historical."""
from pathlib import Path
import sys,json,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sexpr import parse,dump,children,one,prop
root=Path('engineering/release50');root.mkdir(exist_ok=True)
source=Path('engineering/release42')
target=root/'PDB_50A'
assert not target.with_suffix('.kicad_pcb').exists(),'Do not overwrite the working revision'
for ext in ('.kicad_pcb','.kicad_sch','.kicad_pro'):
    shutil.copy2(source/('release_candidate'+ext),target.with_suffix(ext))
for name in ('sym-lib-table','fp-lib-table'):
    src=source/name
    if src.exists():shutil.copy2(src,root/name)
    else:(root/name).write_text(Path(name).read_text().replace('${KIPRJMOD}/','${KIPRJMOD}/../../'))
s=parse(target.with_suffix('.kicad_sch').read_text())
for n in children(s,'text'):
    n[1]=n[1].replace('80A','50A').replace('80 A','50 A')
for c in children(one(s,'title_block'),'comment'):c[2]=c[2].replace('80 A','50 A')
one(one(s,'title_block'),'rev')[1]='50A-4S-42mm-REVIEW'
for sym in children(s,'symbol'):
    if prop(sym,'Reference')[2]=='F1':
        prop(sym,'Value')[2]='EXTERNAL FUSE + HOLDER TBD FOR 50A SYSTEM'
        prop(sym,'Description')[2]='Rating/MPN open pending fault current, inrush, harness and temperature derating'
target.with_suffix('.kicad_sch').write_text(dump(s)+'\n')
p=json.loads(target.with_suffix('.kicad_pro').read_text(encoding='utf-8-sig'))
rules=p['board']['design_settings']['rules']
# Published 2 oz minimum 0.16 mm; retain existing stricter 0.20 mm routing.
rules.update(min_clearance=.16,min_track_width=.2,min_via_annular_width=.1,
             min_through_hole_diameter=.3,min_via_diameter=.5,
             min_hole_clearance=.25,min_hole_to_hole=.25,min_copper_edge_clearance=.5)
target.with_suffix('.kicad_pro').write_text(json.dumps(p,indent=2)+'\n')
target.with_suffix('.kicad_dru').write_text('''(version 1)
# JLCPCB published capability screen; final stackup/plating acceptance OPEN.
# Existing net-class 0.20 mm clearance retained, above published 0.16 mm.
(rule "2oz PTH component annulus" (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'") (constraint annular_width (min 0.254mm)))
(rule "PTH to other copper" (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'") (constraint hole_clearance (min 0.30mm)))
(rule "Component hole spacing" (condition "A.Type == 'Pad' && B.Type == 'Pad'") (constraint hole_to_hole (min 0.45mm)))
''')
req={'system_continuous_A':50,'battery_max_V':16.8,'battery_nominal_V':14.8,'capacity_Ah':8.4,
 'ambient_max_C':50,'baseline_cooling':'natural convection; no guaranteed airflow',
 'outline_mm':[42,42],'copper_candidates_um':[70,105],'working_copper_um':70,
 'process_candidate':'JLCPCB 4 layer 2 oz all layers, 1.6mm; final stackup/filled-capped vias and minimum plating acceptance OPEN',
 'transient_profile':None,'battery_fault_current_A':None,'cells':None,'BMS':None,
 'BEC_models':{'Pi_5V':None,'servo_5V':None,'servo_9V':None,'DJI_9V':None},
 'harness_connectors':None,'wire_gauge_and_length':None,
 'qualification':{'A_fabrication_ready':False,'B_50A_thermal_prototype':False,'C_50A_production':False},
 'obsolete_requirement':'80 A is superseded and is not a release gate'}
(root/'requirements.json').write_text(json.dumps(req,indent=2)+'\n')
print('Created isolated 50 A candidate',target)

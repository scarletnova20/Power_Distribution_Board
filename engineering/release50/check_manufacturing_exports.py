"""Independent Gerber/Excellon parsing, source comparison and visual outputs."""
from pathlib import Path
import sys,json,csv,hashlib,shutil,collections,math
root=Path(__file__).resolve().parent;out=root/'lioncircuits_review'
sys.path[:0]=[str(root.parent/'fab_vendor'),str(root.parent/'vendor'),str(root.parent)]
from gerbonara import GerberFile,ExcellonFile
from gerbonara.layers import LayerStack
from gerbonara.utils import MM
from sexpr import parse,children,one,prop,dump
import pymupdf
raw=parse((root/'PDB_50A.kicad_pcb').read_text())
old=parse((root/'before_fabrication/PDB_50A.kicad_pcb').read_text())
def copper_signature(board):
    parts=[]
    for item in board:
        if not isinstance(item,list):continue
        if item[0] in ('segment','arc','via','zone'):parts.append(item)
        elif item[0]=='footprint':
            parts.append([item[0],item[1]]+[v for v in item[2:] if isinstance(v,list) and v[0] in
                ('at','layer','pad','clearance','net_tie_pad_groups','attr')])
    # The user-approved external BEC revision renames these two nets only.
    # Normalize just those names, retaining every geometry and connectivity field.
    signature = dump(parts).replace('"/12V_Servo"', '"/9V_Servo"').replace('"/12V_DJI"', '"/9V_DJI"')
    return hashlib.sha256(signature.encode()).hexdigest()
assert copper_signature(raw)==copper_signature(old),'Copper changed; recalculate power model'
assert one(one(raw,'setup'),'stackup')==one(one(old,'setup'),'stackup'),'Stackup changed'
assert one(raw,'general')==one(old,'general'),'Board thickness changed'
prior=json.loads((root/'power_0.1mm_70um_repaired.json').read_text())
assert prior['board_sha256']==hashlib.sha256((root/'before_fabrication/PDB_50A.kicad_pcb').read_bytes()).hexdigest()
mapping={('top','copper'):'PDB_50A-F_Cu.gtl',('inner_2','copper'):'INNER_2.G2L',
 ('inner_3','copper'):'INNER_3.G3L',('bottom','copper'):'PDB_50A-B_Cu.gbl',
 ('top','mask'):'PDB_50A-F_Mask.gts',('bottom','mask'):'PDB_50A-B_Mask.gbs',
 ('top','silk'):'PDB_50A-F_Silkscreen.gto',('bottom','silk'):'PDB_50A-B_Silkscreen.gbo',
 ('mechanical','outline'):'OUTLINE.GKO'}
layers={key:GerberFile.open(out/'gerbers'/filename) for key,filename in mapping.items()}
pth=ExcellonFile.open(out/'drill/PDB_50A-PTH.drl',plated=True)
npth=ExcellonFile.open(out/'drill/PDB_50A-NPTH.drl',plated=False)
def hole_key(obj):return (round(obj.x,5),round(obj.y,5),round(obj.tool.diameter,5))
actual_vias=collections.Counter(hole_key(o) for o in pth.objects if abs(o.tool.diameter-.3)<1e-8)
expected_vias=collections.Counter((round(float(one(v,'at')[1]),5),round(-float(one(v,'at')[2]),5),round(float(one(v,'drill')[1]),5)) for v in children(raw,'via'))
unmatched=list(actual_vias.elements());errors=[]
for expected in expected_vias.elements():
    nearest=min(unmatched,key=lambda actual:math.dist(actual[:2],expected[:2]) if actual[2]==expected[2] else math.inf)
    error=math.dist(nearest[:2],expected[:2]);errors.append(error)
    assert error<=math.sqrt(2)*.000501,'Via drill mismatch exceeds 0.001mm output quantization'
    unmatched.remove(nearest)
assert not unmatched,'Unexpected via drills'
assert len(pth.objects)==355 and len(npth.objects)==4
native_pads=list(csv.DictReader((out/'pad_coordinates.csv').open()))
component_drills={(round(o.x,3),round(o.y,3),round(o.tool.diameter,3)) for o in pth.objects if abs(o.tool.diameter-1.)<1e-8}
expected_component_drills={(round(float(q['x_mm']),3),round(-float(q['y_mm']),3),1.) for q in native_pads if q['kind']=='thru_hole'}
assert component_drills==expected_component_drills and len(component_drills)==12
assert {(round(o.x,5),round(o.y,5),round(o.tool.diameter,5)) for o in npth.objects}=={
 (62.5,-192.5,3.2),(97.5,-192.5,3.2),(62.5,-227.5,3.2),(97.5,-227.5,3.2)}
outline=layers[('mechanical','outline')]
corners=collections.Counter()
for o in outline.objects:
    corners[(round(o.x1,5),round(o.y1,5))]+=1
    corners[(round(o.x2,5),round(o.y2,5))]+=1
assert len(outline.objects)==4 and set(corners)=={(59.,-189.),(101.,-189.),(101.,-231.),(59.,-231.)} and set(corners.values())=={2}
job=json.loads((out/'gerbers/PDB_50A-job.gbrjob').read_text())
for entry in job['FilesAttributes']:assert (out/'gerbers'/entry['Path']).exists(),entry
bounds=((58.5,-231.5),(101.5,-188.5))
colors={' '.join(key):('#bb3322' if key[1]=='copper' else '#1479ab' if key[1]=='mask' else '#00aa55' if key[1]=='silk' else '#000000') for key in mapping}
colors.update({'drill pth':'#ffffff','drill npth':'#000000'})
def save_svg(name,svg):
    path=out/'previews'/f'{name}.svg';path.write_text(str(svg),encoding='utf-8')
    doc=pymupdf.open(str(path));page=doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1700/page.rect.width,1700/page.rect.width)).save(str(path.with_suffix('.png')))
for key,layer in layers.items():
    name='gerber_'+'_'.join(key)
    stack=LayerStack({key:layer,('mechanical','outline'):outline})
    save_svg(name,stack.to_svg(force_bounds=bounds,colors=colors))
# Use separate layer views: clear-polarity silk must not erase copper in a
# simple SVG overlay. Remove the earlier task-generated composite previews.
for side in ('top','bottom'):
    for ext in ('svg','png'):
        path=out/'previews'/f'gerber_{side}_composite.{ext}'
        if path.exists():path.unlink()
# Via-fill identification drawing, top-view native coordinates, no mirrored data.
tags=['<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="205mm" viewBox="56 184 48 55">',
 '<rect x="56" y="184" width="48" height="55" fill="white"/>',
 '<text x="59" y="186" font-size="1.1">PDB_50A - VIA FILL MAP - REVIEW ONLY</text>',
 '<rect x="59" y="189" width="42" height="42" fill="#f5f5f5" stroke="black" stroke-width="0.1"/>']
for v in children(raw,'via'):
    x,y=map(float,one(v,'at')[1:3]);tags.append(f'<circle cx="{x}" cy="{y}" r="0.22" fill="#0066cc"/>')
for f in children(raw,'footprint'):
    if not prop(f,'Reference')[2].startswith('H'):continue
    x,y=map(float,one(f,'at')[1:3]);tags.append(f'<circle cx="{x}" cy="{y}" r="1.6" fill="white" stroke="black" stroke-width="0.1"/>')
tags+=['<text x="59" y="233" font-size="1">Blue: all 343 vias - resin fill + copper cap BOTH sides.</text>',
 '<text x="59" y="235" font-size="0.85">0.30 mm via drill; keep connector and mounting holes OPEN.</text>',
 '<text x="59" y="237" font-size="0.85">Native top view: X right, Y down. CAM Y = minus native Y.</text>','</svg>']
save_svg('via_fill_map','\n'.join(tags))
# Native design includes embedded pads/symbols. Bundle project-local libraries.
for name in ('Swayatt_Local.pretty','Swayatt_Local.kicad_sym'):
    src=root.parents[1]/name;dest=out/'source'/name
    if src.is_dir():shutil.copytree(src,dest,dirs_exist_ok=True)
    else:shutil.copy2(src,dest)
for name in ('fp-lib-table','sym-lib-table'):
    (out/'source'/name).write_text((root/name).read_text().replace('${KIPRJMOD}/../../','${KIPRJMOD}/'))
report=dict(board_sha256=hashlib.sha256((root/'PDB_50A.kicad_pcb').read_bytes()).hexdigest(),
    gerber_parser='gerbonara 1.5.0',parsed_layers=len(layers),plated_holes=len(pth.objects),
    nonplated_holes=len(npth.objects),via_drills_match=True,maximum_via_coordinate_rounding_mm=max(errors),
    drill_coordinate_resolution_mm=.001,closed_42mm_outline=True,gerber_job_paths_valid=True,
    copper_geometry_unchanged=True,stackup_unchanged=True,component_drills_match=True,copper_signature=copper_signature(raw),
    previous_board_sha256=prior['board_sha256'],
    power_report_reconciled='power_0.1mm_70um_repaired.json; copper/stackup unchanged after normalizing only /9V_Servo to /12V_Servo and /9V_DJI to /12V_DJI; ESC-only model excludes BEC conversion losses',
    limitations=['Parsing/coordinate checks do not establish copper connectivity independently of KiCad',
                'Graphical review still required','LionCircuits DFM failures remain; not released'])
(out/'checks/export_verification.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(root/'power_0.1mm_70um_repaired.json',out/'checks/power_0.1mm_70um_repaired.json')
print(json.dumps(report,indent=2),flush=True)

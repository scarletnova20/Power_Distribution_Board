"""Apply manufacturing constraints and readable silk; preserve electrical geometry."""
from pathlib import Path
import sys,json,shutil
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent))
from sexpr import parse,dump,one,children,prop,Atom
backup=root/'before_fabrication'
backup.mkdir(exist_ok=True)
for name in ('PDB_50A.kicad_pcb','PDB_50A.kicad_pro','PDB_50A.kicad_sch','PDB_50A.kicad_dru','verification.json'):
    if not (backup/name).exists():shutil.copy2(root/name,backup/name)
target=root/'PDB_50A.kicad_pcb';raw=parse(target.read_text(encoding='utf-8-sig'))
setup=one(raw,'setup')
def setting(node,key,value):
    item=one(node,key)
    if item is None:node.append([Atom(key),Atom(str(value))])
    else:item[1]=Atom(str(value))
setting(setup,'solder_mask_min_width',0.2)
changed=0
for parent in [raw]+children(raw,'footprint'):
    for item in parent:
        if not isinstance(item,list):continue
        layer=one(item,'layer')
        if not layer or layer[1] not in ('F.SilkS','B.SilkS'):continue
        stroke=one(item,'stroke')
        if stroke is not None and float(one(stroke,'width')[1])<.15:
            setting(stroke,'width',.15);changed+=1
        effects=one(item,'effects')
        if effects is not None:
            font=one(effects,'font');size=one(font,'size')
            size[1:]=[Atom(str(max(1.,float(v)))) for v in size[1:]]
            setting(font,'thickness',.15)
target.write_text(dump(raw)+'\n',encoding='utf-8')
pro=root/'PDB_50A.kicad_pro';data=json.loads(pro.read_text(encoding='utf-8-sig'))
rules=data['board']['design_settings']['rules']
rules.update(min_silk_clearance=.15,min_text_height=1.,min_text_thickness=.15,solder_mask_to_copper_clearance=.09)
data['board']['design_settings']['defaults'].update(silk_line_width=.15,silk_text_thickness=.15)
pro.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Strengthened manufacturing rules; silk strokes enlarged:',changed,flush=True)

"""Check serialized net assignments and direct vias in the main power lands."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,children,one
root=Path('engineering/release42');board=root/'release_candidate.kicad_pcb'
raw=parse(board.read_text());vias=children(raw,'via')
by_id={one(v,'uuid')[1]:v for v in vias}
expected=json.loads((root/'power_land_vias.json').read_text())['vias']
missing=[];wrong=[]
for e in expected:
    v=by_id.get(e['uuid'])
    if v is None:missing.append(e)
    elif one(v,'net')[1]!=e['net']:wrong.append({'expected':e,'actual':one(v,'net')[1]})
lands={'J1.1':('/BAT_FUSED',70,193.75),'J1.2':('/PGND',77,193.75),
       'J12.1':('/Vin',83.7,193.75),'J12.2':('/PGND',90.7,193.75)}
counts={}
for key,(net,x,y) in lands.items():
    inside=[]
    for v in vias:
        if one(v,'net')[1]!=net:continue
        vx,vy=map(float,one(v,'at')[1:3]);radius=float(one(v,'size')[1])/2
        if abs(vx-x)+radius<=3 and abs(vy-y)+radius<=3:inside.append(one(v,'uuid')[1])
    counts[key]={'net':net,'vias_fully_inside_6mm_land':len(inside),'uuids':inside}
report={'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'main_lands':counts,
        'missing_intended_vias':missing,'incorrect_net_assignments':wrong,
        'scope':'Geometry/net audit only. Does not certify ampacity, plating, solder fill, current sharing or temperature.'}
(root/'power_land_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v['vias_fully_inside_6mm_land'] for k,v in counts.items()})
print('Missing intended vias:',len(missing),'Incorrect nets:',len(wrong))

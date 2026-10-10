"""Compare intended power-via nets with the serialized board, independently of pcbnew."""
from pathlib import Path
import sys,json,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sexpr import parse,children,one
root=Path('engineering/release42')
raw=parse((root/'release_candidate.kicad_pcb').read_text())
vias={tuple(round(float(n),3) for n in one(v,'at')[1:3]):one(v,'net')[1] for v in children(raw,'via')}
intended=json.loads((root/'candidate_stitching.json').read_text())
missing=[];mismatched=[];good=collections.Counter()
for net,x,y in intended:
    actual=vias.get((x,y))
    if actual is None:missing.append([net,x,y])
    elif actual!=net:mismatched.append({'intended':net,'actual':actual,'x':x,'y':y})
    else:good[net]+=1
report={'correct_by_net':dict(good),'missing':missing,'mismatched':mismatched}
(root/'candidate_via_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

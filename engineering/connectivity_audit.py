import xml.etree.ElementTree as E
import json
from pathlib import Path
from sexpr import *
r=E.parse('engineering/corrected_netlist.xml').getroot()
actual={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'].removeprefix('/') for net in r.find('nets') for n in net}
expected=json.loads(Path('engineering/intended_nets.json').read_text())
sch=parse(Path('Swayatt_PCB.kicad_sch').read_text(encoding='utf-8'))
lib={s[1]:s for s in children(one(sch,'lib_symbols'),'symbol')}
errors=[]
for s in children(sch,'symbol'):
    ref=prop(s,'Reference')[2]
    if ref.startswith('#'):continue
    for sub in children(lib[one(s,'lib_id')[1]],'symbol'):
        for p in children(sub,'pin'):
            pn=one(p,'number')[1];net=expected.get(ref+'.'+pn);observed=actual.get((ref,pn))
            if net is not None and observed!=net:errors.append((ref,pn,net,observed))
print('Connectivity mismatches:',len(errors))
for err in errors:print(err)
Path('engineering/connectivity_audit.json').write_text(json.dumps({'mismatches':errors,'component_count':len(r.find('components'))},indent=2))
if errors:raise SystemExit(1)

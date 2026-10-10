"""Independent layout gate; does not qualify electrical or thermal performance."""
from pathlib import Path
import pcbnew as p
import json,hashlib,xml.etree.ElementTree as ET
b=p.LoadBoard('Swayatt_PCB.kicad_pcb')
nl=ET.parse('engineering/corrected_netlist.xml').getroot()
expected={(pin.attrib['ref'],pin.attrib['pin']):net.attrib['name']
          for net in nl.find('nets') for pin in net}
fs={f.GetReference():f for f in b.GetFootprints()}
fail=[]
if len(fs)!=74:fail.append('Expected all 74 onboard components')
for f in fs.values():
    box=f.GetBoundingBox(False,False)
    if not(60<=p.ToMM(box.GetX()) and 190<=p.ToMM(box.GetY()) and
           p.ToMM(box.GetRight())<=100 and p.ToMM(box.GetBottom())<=230):
        fail.append('Outside outline: '+f.GetReference())
    for q in f.Pads():
        e=expected.get((f.GetReference(),q.GetNumber()))
        if e is not None and e!=q.GetNetname():fail.append('Pad-net mismatch '+f.GetReference()+'.'+q.GetNumber())
    for ref,pin in expected:
        if ref==f.GetReference() and pin not in {q.GetNumber() for q in f.Pads()}:
            fail.append('Missing physical pad '+ref+'.'+pin)
edges=[d for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
ends=[(round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)) for e in edges for v in (e.GetStart(),e.GetEnd())]
corners={(60.,190.),(100.,190.),(100.,230.),(60.,230.)}
if len(edges)!=4 or set(ends)!=corners or any(ends.count(c)!=2 for c in corners):fail.append('Outline is not the exact closed 40mm square')
project=json.loads(Path('Swayatt_PCB.kicad_pro').read_text())
settings=project['board']['design_settings']
if settings['drc_exclusions']:fail.append('DRC exclusions present')
ignored=[k for k,v in settings['rule_severities'].items() if v=='ignore']
if ignored:fail.append('Ignored DRC checks: '+str(ignored))
erc=json.loads(Path('engineering/erc.json').read_text())
drc=json.loads(Path('engineering/drc.json').read_text())
ev=[v for s in erc['sheets'] for v in s['violations']]
dv=drc['violations']
if ev:fail.append('ERC findings remain')
if dv:fail.append('DRC findings remain')
if drc['unconnected_items']:fail.append('Unrouted connections remain')
report={'board_size_mm':[40,40],'layers':b.GetCopperLayerCount(),'components_placed':len(fs),
        'tracks_and_vias':len(list(b.GetTracks())),'zones':len(list(b.Zones())),
        'erc_errors':sum(x['severity']=='error' for x in ev),'erc_warnings':sum(x['severity']=='warning' for x in ev),
        'drc_errors':sum(x['severity']=='error' for x in dv),'drc_warnings':sum(x['severity']=='warning' for x in dv),
        'unrouted':len(drc['unconnected_items']),'failures':fail,
        'board_sha256':hashlib.sha256(Path('Swayatt_PCB.kicad_pcb').read_bytes()).hexdigest()}
Path('engineering/final_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
raise SystemExit(bool(fail))

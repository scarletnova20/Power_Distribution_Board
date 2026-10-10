"""Independent mechanical and netlist checks for the 42 mm revision."""
from pathlib import Path
import sys, json, hashlib, xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pcbnew as p
from electrical_invariants import read_netlist, check

work=Path('engineering/release42')
candidate='--candidate' in sys.argv
prefix='candidate_' if candidate else ''
board=work/'release_candidate.kicad_pcb' if candidate else Path('Swayatt_PCB_42x42.kicad_pcb')
b=p.LoadBoard(str(board))
nl=ET.parse(work/(prefix+'netlist.xml')).getroot()
expected={(q.attrib['ref'],q.attrib['pin']):net.attrib['name'] for net in nl.find('nets') for q in net}
fs={f.GetReference():f for f in b.GetFootprints()}
excluded={c.attrib['ref'] for c in nl.find('components') if any(q.attrib.get('name')=='exclude_from_board' for q in c.findall('property'))}
errors=[]
for (ref,pin),net in expected.items():
    if ref not in fs:
        if ref not in excluded: errors.append('Missing footprint '+ref)
        continue
    pads=[q for q in fs[ref].Pads() if q.GetNumber()==pin]
    if not pads or any(q.GetNetname()!=net for q in pads):errors.append('Pad-net mismatch '+ref+'.'+pin)
for f in fs.values():
    bb=f.GetBoundingBox(False,False)
    if not (p.FromMM(59)<=bb.GetX() and p.FromMM(189)<=bb.GetY() and bb.GetRight()<=p.FromMM(101) and bb.GetBottom()<=p.FromMM(231)):
        errors.append('Footprint outside board '+f.GetReference())
edges=[d for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
ends=[(round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)) for e in edges for v in (e.GetStart(),e.GetEnd())]
corners={(59.,189.),(101.,189.),(101.,231.),(59.,231.)}
if len(edges)!=4 or set(ends)!=corners or any(ends.count(c)!=2 for c in corners):errors.append('Outline is not closed 42 mm square')
checks,electrical=check(*read_netlist(work/(prefix+'netlist.xml')))
report={'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'footprints':len(fs),
        'tracks_and_vias':len(list(b.GetTracks())),'layers':b.GetCopperLayerCount(),
        'layout_and_pad_net_failures':errors,'electrical_check_count':len(checks),
        'electrical_failures':electrical,'manufacturing_release':False}
drc=json.loads((work/(prefix+'drc.json')).read_text())
erc=json.loads((work/(prefix+'erc.json')).read_text())
project=json.loads(board.with_suffix('.kicad_pro').read_text(encoding='utf-8-sig'))
settings=project['board']['design_settings']
report.update(drc_findings=len(drc['violations']),unconnected_items=len(drc['unconnected_items']),
              erc_findings=sum(len(s['violations']) for s in erc['sheets']),
              ignored_checks=[k for k,v in settings['rule_severities'].items() if v=='ignore'],
              drc_exclusions=settings['drc_exclusions'])
(work/(prefix+'verification.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
sys.exit(bool(errors or electrical or report['drc_findings'] or report['unconnected_items'] or report['erc_findings'] or report['ignored_checks'] or report['drc_exclusions']))

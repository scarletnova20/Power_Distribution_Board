"""Refresh candidate ERC/DRC, LED topology and review previews sequentially."""
from pathlib import Path
import sys,subprocess,json,xml.etree.ElementTree as ET,hashlib
root=Path('engineering/release42')
cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
def run(args):
    subprocess.run(args,check=True)
if '--previews-only' not in sys.argv:
    run([cli,'sch','export','netlist','--format','kicadxml','--output',str(root/'candidate_netlist.xml'),str(root/'release_candidate.kicad_sch')])
for domain,command,suffix in ([] if '--previews-only' in sys.argv else [('sch','erc','sch'),('pcb','drc','pcb')]):
    run([cli,domain,command,'--format','json','--output',str(root/('candidate_'+command+'.json')),str(root/('release_candidate.kicad_'+suffix))])
if '--previews-only' not in sys.argv:
    run([sys.executable,str(root/'verify42.py'),'--candidate'])
    run([sys.executable,str(root/'export_candidate_bom.py')])
nl=ET.parse(root/'candidate_netlist.xml').getroot()
pins={n.attrib['ref']+'.'+n.attrib['pin']:net.attrib['name'] for net in nl.find('nets') for n in net}
components={c.attrib['ref']:c for c in nl.find('components')}
checks={
 'resistor_on_regulated_output':pins['R13.1']==pins['J2.1']=='/out',
 'resistor_to_LED_anode':pins['R13.2']==pins['D3.2']=='/LED_A',
 'LED_cathode_grounded':pins['D3.1']==pins['J2.5']=='/PGND',
 'current_limit_1k':components['R13'].findtext('value')=='1k 1%',
 'LED_in_assembly':not any(p.attrib.get('name')=='dnp' for p in components['D3'].findall('property')),
}
assert all(checks.values()),checks
report={'checks':checks,'board_sha256':hashlib.sha256((root/'release_candidate.kicad_pcb').read_bytes()).hexdigest(),
 'indicator':'5V ON; rail energized only, not precision power-good or whole-board self-test',
 'estimated_current_mA_at_5V_with_assumed_2V_LED':3.,
 'resistor_loss_mW_at_same_assumption':9.,'exact_LED_MPN':'UNSELECTED; green 0805 assembly selection remains open',
 'manufacturing_release':False}
(root/'led_verification.json').write_text(json.dumps(report,indent=2)+'\n')
preview=root/'led_review';preview.mkdir(exist_ok=True)
run([cli,'pcb','export','svg','--layers','F.Cu,F.SilkS,Edge.Cuts','--page-size-mode','2','--output',str(preview/'front.svg'),str(root/'release_candidate.kicad_pcb')])
run([cli,'sch','export','svg','--output',str(preview/'schematic'),str(root/'release_candidate.kicad_sch')])
sys.path.insert(0,str(root.parent/'vendor'))
import pymupdf
for path in preview.rglob('*.svg'):
    doc=pymupdf.open(str(path));page=doc[0]
    page.get_pixmap(matrix=pymupdf.Matrix(1800/page.rect.width,1800/page.rect.width)).save(str(path.with_suffix('.png')))
print(json.dumps(report,indent=2))

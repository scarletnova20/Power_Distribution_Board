"""Fresh checks for the active 50 A candidate; no production-rating inference."""
from pathlib import Path
import sys,subprocess,json,hashlib,xml.etree.ElementTree as ET,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from electrical_invariants import check,read_netlist
import pcbnew as p
root=Path(__file__).resolve().parent;board=root/'PDB_50A.kicad_pcb';sch=board.with_suffix('.kicad_sch')
cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
def run(args):subprocess.run(args,check=True)
run([cli,'sch','export','netlist','--format','kicadxml','--output',str(root/'netlist.xml'),str(sch)])
run([cli,'sch','erc','--format','json','--output',str(root/'erc.json'),str(sch)])
run([cli,'pcb','drc','--format','json','--output',str(root/'drc.json'),str(board)])
b=p.LoadBoard(str(board));fs={f.GetReference():f for f in b.GetFootprints()}
nl=ET.parse(root/'netlist.xml').getroot();pins,members,components=read_netlist(root/'netlist.xml')
excluded={c.attrib['ref'] for c in nl.find('components') if any(v.attrib.get('name')=='exclude_from_board' for v in c.findall('property'))}
errors=[]
for key,net in pins.items():
    ref,pin=key.split('.',1)
    if ref in excluded:continue
    if ref not in fs:errors.append('Missing '+ref);continue
    pads=[q for q in fs[ref].Pads() if q.GetNumber()==pin]
    if not pads or any(q.GetNetname()!=net for q in pads):errors.append('Pad net '+key)
for f in fs.values():
    bb=f.GetBoundingBox(False,False)
    if not(p.FromMM(59)<=bb.GetX() and p.FromMM(189)<=bb.GetY() and bb.GetRight()<=p.FromMM(101) and bb.GetBottom()<=p.FromMM(231)):errors.append('Outside outline '+f.GetReference())
checks,failures=check(pins,members,components)
extra={
 'LED_5V_branch':pins['R13.1']==pins['J2.1'] and pins['R13.2']==pins['D3.2'] and pins['D3.1']==pins['J2.5'],
 'Pi_is_external_testpoint_only':members[pins['TP1.1']]=={'TP1.1','BEC1.3'},
 'independent_BEC_outputs':len({pins[k] for k in ('BEC1.3','J3.3','J4.3','J10.3','J2.1')})==5,
 'main_ESC_pads':pins['J12.1']==pins['R10.2'] and pins['J12.2']==pins['J1.2'],
 'fuse_not_automatically_rated_50A':'TBD' in components['F1']['value'] and 'F1' in excluded,
 'INA228_manufacturer_footprint':components['U3']['footprint']=='Swayatt_Local:INA228_DGS0010A',
 'four_layers':b.GetCopperLayerCount()==4}
edges=[d for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
ends=[(round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)) for e in edges for v in (e.GetStart(),e.GetEnd())]
corners={(59.,189.),(101.,189.),(101.,231.),(59.,231.)}
extra['closed_42mm_outline']=len(edges)==4 and set(ends)==corners and all(ends.count(c)==2 for c in corners)
intent=json.loads((root/'power_arrays.json').read_text()) if (root/'power_arrays.json').exists() else []
actual={v.m_Uuid.AsString():v.GetNetname() for v in b.GetTracks() if isinstance(v,p.PCB_VIA)}
extra['new_power_vias_have_intended_nets']=all(actual.get(v['uuid'])==v['net'] for v in intent)
drc=json.loads((root/'drc.json').read_text());erc=json.loads((root/'erc.json').read_text())
settings=json.loads(board.with_suffix('.kicad_pro').read_text(encoding='utf-8-sig'))['board']['design_settings']
report={'current_requirement_A':50,'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),
 'schematic_sha256':hashlib.sha256(sch.read_bytes()).hexdigest(),'footprints':len(fs),'tracks_vias':len(list(b.GetTracks())),
 'electrical_checks':len(checks),'electrical_failures':failures,'layout_net_failures':errors,'extra_checks':extra,
 'drc_findings':len(drc['violations']),'unconnected':len(drc['unconnected_items']),
 'erc_findings':sum(len(s['violations']) for s in erc['sheets']),
 'ignored_checks':[k for k,v in settings['rule_severities'].items() if v=='ignore'],'exclusions':settings['drc_exclusions'],
 'A_fabrication_ready':False,'B_50A_thermal_prototype':False,'C_50A_production':False}
(root/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
old={r['Reference']:r for r in csv.DictReader((root.parent/'release42/candidate_BOM_REVIEW.csv').open(encoding='utf-8'))}
with (root/'BOM_REVIEW.csv').open('w',newline='',encoding='utf-8') as out:
    writer=csv.writer(out);writer.writerow(['Reference','Value','Footprint','Manufacturer','MPN','Status','Note'])
    for ref,c in sorted(components.items()):
        info=old.get(ref,{})
        mpn=info.get('Verified ordering code','');manufacturer=info.get('Manufacturer','')
        note=info.get('Notes','Exact assembly selection OPEN')
        if ref=='F1':mpn='';manufacturer='';note='External fuse AND holder OPEN; obsolete 80A selection withdrawn; not replaced by an assumed50A fuse'
        if ref=='U3':manufacturer='Texas Instruments';mpn='INA228AIDGSR';note='TI DGS0010A land pattern; Kelvin geometry/calibration review OPEN'
        if ref in ('Q1','Q2','Q3','Q4'):manufacturer='Infineon';mpn='ISC027N10NM6ATMA1';note='Four parallel NMOS retained; hot/current-sharing/thermal qualification OPEN'
        writer.writerow([ref,c['value'],c['footprint'],manufacturer,mpn,'REVIEW - NOT RELEASED',note])
print(json.dumps(report,indent=2),flush=True)
sys.exit(bool(errors or failures or not all(extra.values()) or report['drc_findings'] or report['unconnected'] or report['erc_findings'] or report['ignored_checks'] or report['exclusions']))

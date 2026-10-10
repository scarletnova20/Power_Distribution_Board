"""Generate the consolidated design record from the current verified sources."""
from pathlib import Path
import json, csv, hashlib, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent
load=lambda name:json.loads((root/name).read_text())
v=load('verification.json'); req=load('requirements.json')
boardhash=hashlib.sha256((root/'PDB_50A.kicad_pcb').read_bytes()).hexdigest()
assert v['board_sha256']==boardhash, 'Run verify50 first'
lines=['# PDB_50A — design and fabrication record', '', 'Revision record: 2026-09-11. Team_RotorFPV.', '',
'**Release status: HOLD — not fabrication ready; 50 A is a design target, not a tested rating.**', '',
'This document consolidates the current native design, interfaces, manufacturing request and evidence. It supersedes historical 80 A descriptions. The authoritative project is `PDB_50A.kicad_pcb/.kicad_sch/.kicad_pro/.kicad_dru` in `engineering/release50`.', '',
'Board SHA-256: `'+boardhash+'`', '',
'## Requirements', '',
'| Item | Current requirement |','|---|---|',
'| Continuous load | 50 A aggregate |',
'| Battery | 4S2P Li-ion; recorded 14.8 V nominal, 16.8 V maximum normal, 8.4 Ah |',
'| Environment | 50 °C maximum ambient; natural convection, no guaranteed airflow |',
'| Board | 42 × 42 mm; four copper layers; nominal 1.6 mm |',
'| Fabricator | LionCircuits Custom; process acceptance pending |', '',
'Battery cells, BMS, fault current, harness lengths/gauges/connectors and exact external 5 V / 12 V BEC models remain unspecified.', '',
'## Circuit and operating limits', '',
'The input uses an external fuse/holder (F1; selection open), four parallel reverse-protection NMOS devices Q1–Q4 (ISC027N10NM6) and U5 (LM74502HDDFR). MOSFET sources face BAT_FUSED and drains face VCC; each gate has a 4.7 ohm resistor. U5 implements reverse-polarity protection only. Startup can flow through body diodes; controlled inrush, load disconnect and active overvoltage protection are not implemented. D2 is the existing SMCJ28CA; transient coordination is unqualified.', '',
'U1 is the LM5576 buck stage; U4 supplies 3.3 V. U2 INA169 provides analog current telemetry and U3 INA228 digital telemetry (schematic address 0x45). The two parallel shunts provide 0.25 milliohm nominal sensing. J12 is the main ESC power interface. External BEC interfaces remain separate supplies; do not parallel their outputs.', '',
'BEC1/TP1 is an auxiliary Pi-output test branch, not the Pi 5 A load path. J5–J8 pin 1 has no routed control signal; servo control must be supplied externally. J2 uses I2C, not the analog TP2/TP3 outputs. Connector numbering below is extracted from the native netlist; use the assembly orientation and pin numbers, not apparent left/right position in a mirrored view.', '',
'## Connector and testpoint pinout', '', '| Reference | Pin | Native net |','|---|---|---|']
net=ET.parse(root/'netlist.xml').getroot()
pins=[]
for n in net.find('nets'):
    for node in n.findall('node'):
        ref=node.get('ref')
        if ref.startswith(('J','TP')) or ref=='BEC1':pins.append((ref,node.get('pin'),n.get('name')))
for ref,pin,name in sorted(pins):lines.append(f'| {ref} | {pin} | {name} |')
lines += ['', '## Mechanical and manufacturing specification', '',
(root/'lioncircuits_review/MANUFACTURING_REQUIREMENTS.md').read_text(encoding='utf-8').split('\n',1)[1], '',
'Mounting hole centers in native coordinates: (62.5,192.5), (97.5,192.5), (62.5,227.5), (97.5,227.5) mm. Four 3.2 mm NPTH holes on a 35 × 35 mm pattern, 3.5 mm from the edges. Outline corners are (59,189) through (101,231) mm. There are 343 plated via holes and 12 plated component holes. Connector and mounting holes remain open.', '',
'Native Y increases downwards; manufacturing Y has opposite sign. Bottom viewing images may be mirrored; manufacturing coordinate data must not be mirrored. Nine manufacturing layers are supplied: four copper, two mask, two silk and outline, with separate PTH/NPTH Excellon drills. IPC-2581 and local libraries accompany native source.', '',
'## Verification on this revision', '', '| Check | Result |','|---|---|',
f"| ERC findings | {v['erc_findings']} |", f"| Unconnected items | {v['unconnected']} |",
f"| Electrical invariants | {v['electrical_checks']} checked; {len(v['electrical_failures'])} failures |",
f"| Additional checks | {sum(v['extra_checks'].values())}/{len(v['extra_checks'])} pass |",
f"| Pad-net/layout failures | {len(v['layout_net_failures'])} |",
f"| DRC findings | {v['drc_findings']} — manufacturing gate fails |",
f"| Ignored checks / exclusions | {len(v['ignored_checks'])} / {len(v['exclusions'])} |", '',
'The independent inventory identifies 902 tracks below 0.254 mm and 343 via annuli below 0.1524 mm. Fine-pitch lands at U1/U3/U5 also conflict. Reported DRC examples are capped and are not the full inventory. LionCircuits capability page was checked again on 2026-09-11: https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb . Historical zero-DRC results used another process and do not release this board.', '',
'## Power and telemetry calculations', '',
'The preserved 0.1 mm mesh DC screen estimates 9.757 W positive-path plus 2.024 W return loss, total 11.781 W and approximately 0.236 V loop drop at 50 A ESC-only load. Assumptions: 70 µm copper, 18 µm barrel plating, uniform 125 °C, 5.4 milliohm MOSFET resistance, ideal contacts. Q1–Q4 carry approximately 18.285 / 11.969 / 10.000 / 9.746 A. Unequal sharing needs thermal review. Mesh convergence is unestablished. Fuse, holder, harness, contact and BEC conversion losses are excluded; each extra milliohm adds 2.5 W at 50 A.', '',
'Nominal shunt drop is 12.5 mV at 50 A. Analog current scaling is 25 mV/A (1.25 V at 50 A). The INA169 offset screen alone can represent 4 A; do not assume calibrated accuracy. TP3 divider ratio is 19.1818 battery volts per testpoint volt, giving 0.8758 V at 16.8 V. Dedicated external ADC input protection/reference remains unselected. Detailed assumptions and error screens are in `analytical50.json`; these are calculations, not measurement results.', '',
'## Release gates and acceptance evidence', '',
'| Gate | Required closure evidence | Current status |','|---|---|---|',
'| Bare-board DFM | Written custom-process acceptance for actual geometry, or redesign to accepted rules and fresh DRC without hidden violations | OPEN |',
'| Stackup / vias | Approved stackup, minimum finished copper and barrel plating; resin fill, cap flatness/thickness/void criteria | OPEN |',
'| Manufacturing data | Fresh source hashes, parsed Gerber/drill agreement, visual CAM review, supplier CAM approval and bare-board electrical test requirement | Review outputs available; supplier acceptance OPEN |',
'| Assembly | Exact orderable BOM, polarity and mating harness verification, paste/thermal-pad review and tooling panel | OPEN |',
'| Protection | Verified cell/BMS fault current, fuse/holder interrupt capability and time-current coordination; measured hot-plug/transients against actual parts | OPEN |',
'| 50 A operation | Thermal solution and current sharing, measured steady-state temperatures/drop at 50 °C ambient under worst actual loads; documented limits from selected components | OPEN |', '',
'Before energizing a prototype, inspect assembly and polarity, check rail-to-ground resistance and begin from a current-limited source. Verify rails, telemetry and BEC isolation at low load before a controlled load ramp. Record individual MOSFET/shunt/connector temperatures and voltage drops; establish stop limits from final component ratings. Qualification must use the actual harness and cooling. A 15-minute 50 A test needs 12.5 Ah; the recorded 8.4 Ah pack cannot supply that duration even ideally. High-current testing remains a separate qualified engineering activity.', '',
'## Full BOM review register', '', '| Reference | Value | Footprint | Manufacturer | MPN | Open detail |','|---|---|---|---|---|---|']
for row in csv.DictReader((root/'BOM_REVIEW.csv').open(encoding='utf-8')):
    lines.append('| '+' | '.join(row[k].replace('|','/') for k in ('Reference','Value','Footprint','Manufacturer','MPN','Note'))+' |')
lines += ['', 'All BOM entries remain review status. Blank MPNs are unresolved purchasing selections, not permission to substitute.', '',
'## Labelling and source evidence', '',
'`label_placement.json` records each reference position, side and angle. References use 0.8 mm height and 0.16 mm strokes, with a 1.0 mm Team_RotorFPV name on front silk. This exceeds the published 0.5842 mm legend height; the earlier project preference of 1.0 mm could not fit. 58 references fit on silk within 4.5 mm of their component centers; 20 crowded references remain on fabrication layers. The indexed front/back component locators and pin table identify all parts. `checks/label_verification.json` records final silk checks; `checks/export_verification.json` verifies copper preservation.', '',
'Evidence files: `verification.json`, `drc.json`, `erc.json`, `netlist.xml`, `analytical50.json`, `power_0.1mm_70um_repaired.json`, `lioncircuits_review/feature_audit.json`, `lioncircuits_review/checks/export_verification.json`, `BOM_REVIEW.csv` and `requirements.json`.', '',
'`PDB_50A_LionCircuits_REVIEW_HOLD.zip` is a review archive. `SUPPLIER_REVIEW_REQUEST.txt` is prepared and unsent. No supplier message or production order has been sent by this work.', '']
text='\n'.join(lines)
(root/'PDB_50A_DESIGN_RECORD.md').write_text(text,encoding='utf-8')
(root/'lioncircuits_review/PDB_50A_DESIGN_RECORD.md').write_text(text,encoding='utf-8')
print('Design record written')

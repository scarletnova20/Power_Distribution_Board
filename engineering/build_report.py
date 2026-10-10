"""Package the actual, unreleased checkpoint; never infer manufacturing readiness."""
from pathlib import Path
import csv, hashlib, json, zipfile
import xml.etree.ElementTree as ET

out = Path('engineering')
read = lambda name: json.loads((out / name).read_text())
erc, drc = read('erc.json'), read('drc.json')
inv, sync = read('electrical_invariants.json'), read('pcb_sync_audit.json')
audit = read('connectivity_audit.json')
layout = read('final_verification.json')
assert layout['board_sha256'] == hashlib.sha256(Path('Swayatt_PCB.kicad_pcb').read_bytes()).hexdigest()
netlist = out / 'corrected_netlist.xml'
assert inv['netlist_sha256'] == hashlib.sha256(netlist.read_bytes()).hexdigest()
nl = ET.parse(netlist).getroot()
ev = [v for s in erc['sheets'] for v in s['violations']]
with (out / 'BOM_checkpoint.csv').open('w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Reference', 'Value', 'Footprint', 'Release status'])
    for c in nl.find('components'):
        w.writerow([c.attrib['ref'], c.findtext('value'), c.findtext('footprint'), 'WORK IN PROGRESS - NOT RELEASED'])
report = f'''# Swayatt PCB: 4-6S / 80 A target, NOT FOR FABRICATION

Updated 2026-09-07. Placement and routing pass the current layout checks.
The design remains unreleased and has no qualified current rating.
The recovered schematic generator records the user's selection of 4-6S with
the SpeedyBee BLS 35A Mini V2 ESC. Earlier pending-choice notes predate that
redesign. Maximum normal battery voltage is 25.2 V at 4.2 V/cell.

## Current circuit and corrections

- Q1-Q4: parallel ISC027N10NM6 NMOS, sources to BAT_FUSED, drains to VCC,
  followed by the parallel 0.5 mOhm shunts and measured Vin rail.
- U5 part number corrected to LM74502HDDFR. Its local LM74502_DDF8 footprint
  follows TI DDF0008A: 1.05 x 0.45 mm lands, 0.65 mm pitch, 2.6 mm row spacing.
  This retains 0.20 mm pad clearance. The schematic symbol clears the title block.
- Four separate 4.7 ohm gate resistors, 1 MOhm gate-source bleed, 1 uF charge-pump
  capacitor to VS and 100 nF VS bypass. D2 is SMCJ28CA bidirectional input TVS.
- OV is grounded. This is reverse-polarity protection only: body diodes permit
  startup current with gates off. No inrush limiter, load disconnect or OVP exists.
- LM5576 bias remains isolated from battery. The 5.019 V nominal buck, INA228
  address 0x45, 250 uOhm shunt, real test-point footprints, Vishay low-resistance
  shunt lands and Pixhawk 6X digital power interface remain implemented.

## Actual checks

| Check | Result |
|---|---|
| Schematic / PCB components | {len(nl.find('components'))} / {sync['footprints']} |
| ERC findings | {len(ev)} |
| Independent checks / failures | {len(inv['checks'])} / {len(inv['failures'])} |
| Deliberate fault tests detected | {sum(inv['regression_self_tests'].values())} / {len(inv['regression_self_tests'])} |
| Intended net / PCB pad-net mismatches | {len(audit['mismatches'])} / {len(sync['pad_net_mismatches'])} |
| DRC geometric findings | {len(drc['violations'])} |
| DRC unconnected items | {len(drc['unconnected_items'])} |
| Tracks and vias / zones | {layout['tracks_and_vias']} / {layout['zones']} |
| Independent layout verification failures | {len(layout['failures'])} |

All 74 onboard footprints fit inside the closed 40 x 40 mm outline. The board
has four copper layers and 12 filled zones. All inherited ignored DRC checks
are enabled, with no exclusions. U1/U3 retain their existing 0.15 mm local
clearance; minimum track width remains 0.20 mm. DRC does not establish ampacity,
analog layout quality, transient behavior or thermal performance.

## Estimates and remaining work

Four equal 2.7 mOhm branches give 0.675 mOhm and 4.32 W at 80 A at the specified
cold resistance. Shunt heating is 1.60 W total. Hot resistance, unequal sharing,
interconnect and converter losses are additional. These are not measured ratings.
The old 42.88 W single-PMOS estimate describes the superseded circuit only.

Complete input precharge/hot-plug and transient coordination with ESC/BECs before
finalizing the layout. The input TVS does not establish an ESC-safe transient
envelope and is not a continuous regenerative-energy sink. Include all connected
capacitance and active startup loads; check charged-output reverse insertion.

Finalize fuse/holder interruption capability, wire gauge, copper reinforcement,
strain relief, mounting, heatsink and airflow. An insulated heatsink may overhang
the board, as already authorized. The current nominal 1.6 mm stackup specifies
70/35/35/70 um copper; this is not a qualified 80 A implementation. Via arrays
and routed sense nets now exist. Review their current sharing, Kelvin geometry,
buck switching loops and sense-noise coupling before release. Confirm filled
and capped via-in-pad fabrication where required: current board defaults do
not encode that requirement. Complete output-capacitor selection, buck stability,
harness mapping, firmware calibration and prototype validation.

Accepted loads: three 5 V servos at 2.5 A stall each; one 9 V servo at 3.6 A;
external 12 V DJI O4 Pro BEC with a 3 A interface allowance; external Pi 5 supply
delivering 5.1 V / 5 A at the Pi. FC remains Pixhawk 6X V2. Servo PWM uses a
separate harness. J12 supplies measured battery voltage directly to the ESC.

## Sources and files

- [TI orderable part](https://www.ti.com/product/LM74502H/part-details/LM74502HDDFR)
- [TI datasheet](https://www.ti.com/lit/ds/symlink/lm74502.pdf): controller and DDF0008A land pattern.
- [Infineon MOSFET](https://www.infineon.com/assets/row/public/documents/24/49/infineon-isc027n10nm6-datasheet-en.pdf).
- Earlier detailed buck/telemetry calculations and sources are preserved in
  before_resume_audit/ENGINEERING_CHECKPOINT.md; its pending-voltage and PMOS
  implementation statements are superseded here.
- CONTINUATION.md and ESC_INTEGRATION.md document the current resumption state.
- Actual reports, BOM, previews, generator scripts and hashes accompany the ZIP.
  It is a source checkpoint, not a manufacturing package.
'''
(out / 'ENGINEERING_CHECKPOINT.md').write_text(report, encoding='utf-8')
files = [Path(x) for x in ('Swayatt_PCB.kicad_sch', 'Swayatt_PCB.kicad_pcb', 'Swayatt_PCB.kicad_pro',
                          'Swayatt_Local.kicad_sym', 'sym-lib-table', 'fp-lib-table')]
files += list(Path('Swayatt_Local.pretty').glob('*.kicad_mod'))
files += [out / x for x in ('ENGINEERING_CHECKPOINT.md', 'BOM_checkpoint.csv', 'erc.json', 'drc.json',
          'corrected_netlist.xml', 'connectivity_audit.json', 'pcb_sync_audit.json', 'CONTINUATION.md',
          'electrical_invariants.py', 'electrical_invariants.json', 'ESC_INTEGRATION.md',
          'revise_schematic.py', 'make_footprints.py', 'sync_pcb.py', 'sexpr.py',
          'connectivity_audit.py', 'build_report.py', 'intended_nets.json')]
files += list((out / 'baseline').glob('*'))
files += [out / 'before_resume_audit/ENGINEERING_CHECKPOINT.md']
files += [out / name for name in ('final_verification.json', 'final_verify.py',
          'finish_routes.py', 'center_via_tracks.py', 'place_board.py',
          'power_copper.py', 'stackup_rules.py', 'route_board.py',
          'front.svg', 'front.png', 'back.svg', 'back.png', 'render_board.py',
          'before_resume_2145.kicad_pcb')]
files += list((out / 'schematic_preview').glob('*.svg')) + list((out / 'schematic_preview').glob('*.png'))
files = [f for f in files if f.is_file()]
hashes = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
(out / 'checkpoint_sha256.json').write_text(json.dumps(hashes, indent=2))
files.append(out / 'checkpoint_sha256.json')
with zipfile.ZipFile(out / 'Swayatt_PCB_CHECKPOINT_NOT_FOR_FABRICATION.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files: z.write(f, str(f))
print('Updated report, BOM and unreleased source archive.')
print('ERC:', len(ev), 'DRC geometry:', len(drc['violations']), 'unconnected:', len(drc['unconnected_items']))

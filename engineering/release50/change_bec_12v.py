"""Apply the user-confirmed external 5 V / 12 V BEC interface revision."""
from pathlib import Path
import shutil
import json

root = Path(__file__).resolve().parent
backup = root / 'before_bec_12v'
backup.mkdir(exist_ok=False)
names = ['PDB_50A.kicad_pcb', 'PDB_50A.kicad_sch', 'PDB_50A.kicad_pro',
         'PDB_50A.kicad_dru', 'requirements.json', 'netlist.xml', 'verification.json',
         'PDB_50A_LionCircuits_REVIEW_HOLD.zip', 'PDB_50A_LionCircuits_GERBERS_REVIEW_ONLY.zip']
for name in names:
    shutil.copy2(root / name, backup / name)
for name in ['PDB_50A.kicad_pcb', 'PDB_50A.kicad_sch', 'requirements.json',
             'build_design_record.py', 'lioncircuits_review/README.md',
             'lioncircuits_review/HARNESS_WORKSHEET.md']:
    path = root / name
    data = path.read_text(encoding='utf-8')
    path.write_text(data.replace('9V', '12V').replace('9 V', '12 V'), encoding='utf-8')
path = root / 'requirements.json'
req = json.loads(path.read_text())
req['BEC_revision'] = {
    'date': '2026-09-11', 'architecture': 'External BEC modules retained, confirmed by user',
    'outputs_V': [5, 12], 'changed_branches': ['J4/J8 servo', 'J10/J11 DJI'],
    'output_current_A': None, 'load_voltage_compatibility': 'Exact load models remain unspecified'
}
path.write_text(json.dumps(req, indent=2) + '\n')
path = root / 'CONTINUATION.md'
path.write_text('# Latest: external BEC revision, 2026-09-11\n\n'
    'User confirmed external BECs retained; outputs are now 5 V and 12 V.\n'
    'J4/J8 servo and J10/J11 DJI branches change from 9 V to 12 V.\n'
    'Five-volt branches and all copper geometry remain unchanged.\n'
    'Previous native files and review ZIPs are in before_bec_12v/.\n'
    'Exact BEC/load models and output current ratings remain unspecified.\n\n'
    + path.read_text(encoding='utf-8'), encoding='utf-8')
print('External BEC interfaces changed to 12 V; previous revision preserved.')

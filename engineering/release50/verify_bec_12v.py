"""Compare full connectivity with the preserved pre-revision netlist."""
from pathlib import Path
import sys, json, hashlib
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent))
from electrical_invariants import read_netlist
old, _, _ = read_netlist(root / 'before_bec_12v/netlist.xml')
new, members, _ = read_netlist(root / 'netlist.xml')
rename = {'/9V_Servo': '/12V_Servo', '/9V_DJI': '/12V_DJI'}
assert new == {pin: rename.get(net, net) for pin, net in old.items()}
assert members['/12V_Servo'] == {'J4.3', 'J8.2'}
assert members['/12V_DJI'] == {'J10.3', 'J11.1'}
assert not any('9V' in net for net in members)
for net in ('/5V_PI', '/5V_Servo'):
    assert members[net] == {pin for pin, name in old.items() if name == net}
report = {
    'board_sha256': hashlib.sha256((root / 'PDB_50A.kicad_pcb').read_bytes()).hexdigest(),
    'schematic_sha256': hashlib.sha256((root / 'PDB_50A.kicad_sch').read_bytes()).hexdigest(),
    'net_renames': rename, 'full_connectivity_preserved': True,
    'five_volt_branches_unchanged': True,
    '12V_servo_pins': sorted(members['/12V_Servo']),
    '12V_DJI_pins': sorted(members['/12V_DJI']),
    'architecture': 'External BEC modules retained; this PCB does not set their output voltage',
    'load_compatibility': 'Exact BEC/load models and output currents remain unspecified'
}
(root / 'lioncircuits_review/checks/bec_12v_verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))

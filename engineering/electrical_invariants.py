"""Independent datasheet-based topology checks, not generated from intended_nets.

Run after exporting corrected_netlist.xml. This verifies selected electrical
invariants; it does not qualify voltage transients, ampacity or loop stability.
Sources: TI LM5576 SNVS447K, INA228 SBOSA29, TLV755P SBVS293.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import sys
import xml.etree.ElementTree as ET


def read_netlist(path):
    root = ET.parse(path).getroot()
    pin_net = {}
    members = {}
    for net in root.find('nets'):
        name = net.attrib['name']
        members[name] = set()
        for pin in net:
            key = pin.attrib['ref'] + '.' + pin.attrib['pin']
            pin_net[key] = name
            members[name].add(key)
    components = {c.attrib['ref']: {
        'value': c.findtext('value'), 'footprint': c.findtext('footprint', '')
    } for c in root.find('components')}
    return pin_net, members, components


def check(pin_net, members, components):
    errors = []
    checks = []

    def record(description, success):
        checks.append(description)
        if not success:
            errors.append(description)

    def same(description, *pins):
        names = [pin_net.get(pin) for pin in pins]
        record(description, None not in names and len(set(names)) == 1)

    def separate(description, *pins):
        names = [pin_net.get(pin) for pin in pins]
        record(description, None not in names and len(set(names)) == len(names))

    # The bias output is ~7.15 V; absolute maximum 14 V. It must never
    # share the 50.4 V battery net. A power_out symbol/ERC cannot ensure this.
    record('U1 VCC pin 1 connects ONLY to C5 bias bypass',
           members.get(pin_net.get('U1.1')) == {'U1.1', 'C5.2'})
    separate('Buck bias, battery, SW, bootstrap and regulated output are distinct',
             'U1.1', 'Q1.3', 'U1.17', 'U1.20', 'U1.12')
    same('Buck VIN pins and input capacitors use post-shunt battery',
         'U1.3', 'U1.4', 'C1.2', 'C2.2', 'R10.2', 'R11.2')
    same('SW/PRE connect to inductor, diode cathode and bootstrap low side',
         'U1.17', 'U1.18', 'U1.19', 'L1.2', 'D1.1', 'C7.1', 'C8.1')
    record('Bootstrap high side contains only U1 BST20 and C7',
           members.get(pin_net.get('U1.20')) == {'U1.20', 'C7.2'})
    same('Catch diode/snubber return through the IS pins',
         'D1.2', 'R3.2', 'U1.15', 'U1.16')
    separate('IS current measurement is not bypassed to PGND', 'D1.2', 'U1.13')
    same('Exposed pad, power grounds and input/output capacitor returns',
         'U1.21', 'U1.13', 'U1.14', 'C1.1', 'C2.1', 'C9.2', 'C10.2')
    same('Analog ground and quiet feedback/timing returns',
         'U1.10', 'R4.1', 'C3.1', 'C6.1', 'R6.2', 'NT1.1')
    separate('GNDA and PGND remain separate schematic nets', 'NT1.1', 'NT1.2')
    same('Feedback node connects divider midpoint and COMP network',
         'U1.7', 'R5.2', 'R6.1', 'C11.2', 'C12.2')
    same('Regulated output feeds the divider, monitor supply and FC power',
         'U1.12', 'L1.1', 'R5.1', 'U2.5', 'J2.1', 'J2.2')
    same('All external BEC inputs are measured downstream of the shunts',
         'J3.1', 'J4.1', 'J10.1', 'BEC1.1', 'J12.1', 'R10.2')
    same('INA169 IN+ and INA228 positive input filter use positive Kelvin net',
         'U2.3', 'R15.1', 'NT2.2')
    same('INA169 IN- and INA228 negative input filter use negative Kelvin net',
         'U2.4', 'R16.1', 'NT3.2')
    same('INA228 positive filter polarity', 'U3.10', 'R15.2', 'C16.1')
    same('INA228 negative filter polarity', 'U3.9', 'R16.2', 'C16.2')
    same('INA228 VBUS is post-shunt battery', 'U3.8', 'R10.2')
    same('INA228 address 0x45 straps and VS connect to regulated 3V3',
         'U3.1', 'U3.2', 'U3.6', 'U4.5', 'C17.1')
    same('Pixhawk pin 3 is SCL', 'J2.3', 'U3.5', 'R17.2')
    same('Pixhawk pin 4 is SDA', 'J2.4', 'U3.4', 'R18.2')
    same('Pixhawk return uses power ground', 'J2.5', 'J2.6', 'NT1.2')
    separate('Analog telemetry never connects directly to FC I2C',
             'TP2.1', 'TP3.1', 'J2.3', 'J2.4')
    for ref in ('TP1', 'TP2', 'TP3'):
        record(ref + ' has a real single-pad test-point footprint',
               components[ref]['footprint'] == 'TestPoint:TestPoint_Pad_D1.5mm')
    for ref in ('R10', 'R11'):
        record(ref + ' has the low-value WSLP2512 land pattern and selected MPN',
               components[ref]['footprint'] == 'Swayatt_Local:WSLP2512_L5000'
               and 'WSLP2512L5000FEA' in components[ref]['value'])
    same('Controller supply, enable, source and bypass use fused battery',
         'U5.1', 'U5.5', 'U5.8', 'C21.1', 'C20.2', 'Q1.3')
    same('Controller ground and disabled OV input use power ground',
         'U5.2', 'U5.7', 'C21.2', 'D2.2', 'J1.2')
    record('Charge pump output connects only to C20',
           members.get(pin_net.get('U5.4')) == {'U5.4', 'C20.1'})
    record('Controller has the verified DDF orderable part and footprint',
           components['U5']['value'] == 'LM74502HDDFR REVERSE ONLY'
           and components['U5']['footprint'] == 'Swayatt_Local:LM74502_DDF8')
    record('Input TVS is bidirectional for reverse battery operation',
           components['D2']['value'] == 'SMCJ28CA bidirectional')
    same('Input TVS and gate bleed return to fused battery',
         'D2.1', 'R14.2', 'Q1.3', 'J1.1')
    same('Gate drive and bleed connect to controller output',
         'U5.6', 'R14.1', 'R12.1', 'R19.1', 'R20.1', 'R21.1')
    separate('Battery, protected rail and controller gate drive are distinct',
             'Q1.3', 'Q1.2', 'U5.6')
    for i, resistor in enumerate(('R12', 'R19', 'R20', 'R21'), 1):
        ref = f'Q{i}'
        same(ref + ' source faces battery', ref + '.3', 'J1.1')
        same(ref + ' drain faces positive shunt terminals',
             ref + '.2', 'R10.1', 'R11.1', 'NT2.1')
        record(ref + ' gate connects only to its individual resistor',
               members.get(pin_net.get(ref + '.1')) == {ref + '.1', resistor + '.2'})
        record(ref + ' uses selected NMOS logical GDS footprint',
               components[ref]['value'] == 'ISC027N10NM6 100V 2.7mR'
               and components[ref]['footprint'] == 'Swayatt_Local:ISC027N10NM6_GDS')
    return checks, errors


if __name__ == '__main__':
    netlist = Path('engineering/corrected_netlist.xml')
    data = read_netlist(netlist)
    checks, errors = check(*data)
    regression = {}
    if '--self-test' in sys.argv:
        # Recreate the previous VCC collision in memory. The independent
        # checker must reject it, even if intended_nets would agree with it.
        pins, members, components = deepcopy(data)
        old, battery = pins['U1.1'], pins['Q1.3']
        moved = members.pop(old)
        members[battery].update(moved)
        for pin in moved:
            pins[pin] = battery
        regression['rejects_previous_bias_battery_short'] = bool(check(pins, members, components)[1])
        pins, members, components = deepcopy(data)
        components['TP2']['footprint'] = 'Resistor_SMD:R_0603_1608Metric'
        regression['rejects_previous_testpoint_footprint'] = bool(check(pins, members, components)[1])
        pins, members, components = deepcopy(data)
        pins['Q2.2'], pins['Q2.3'] = pins['Q2.3'], pins['Q2.2']
        regression['rejects_reversed_parallel_mosfet'] = bool(check(pins, members, components)[1])
        pins, members, components = deepcopy(data)
        pins['C20.2'] = pins['U5.2']
        regression['rejects_ground_referenced_charge_pump'] = bool(check(pins, members, components)[1])
        if not all(regression.values()):
            errors.append('Regression detector self-test failed')
    report = {
        'scope': 'Selected independent pin-topology and footprint invariants only',
        'netlist_sha256': hashlib.sha256(netlist.read_bytes()).hexdigest(),
        'checks': checks, 'failures': errors, 'regression_self_tests': regression,
        'manufacturing_release': False,
    }
    Path('engineering/electrical_invariants.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Independent electrical invariants: {len(checks)} checks, {len(errors)} failures')
    print(json.dumps(regression))
    for error in errors:
        print('FAIL:', error)
    sys.exit(bool(errors))

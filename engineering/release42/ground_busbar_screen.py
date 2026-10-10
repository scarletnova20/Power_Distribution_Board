"""Compare a proposed copper ground bridge with the measured-geometry DC screen.

No busbar has been installed or qualified; joint resistance is an acceptance
budget, not a measured value. Geometry remains subject to mechanical review.
"""
from pathlib import Path
import json,hashlib
root=Path('engineering/release42')
available=[(json.loads(path.read_text()),path) for path in root.glob('ground_resistance_*.json')]
board_hash=hashlib.sha256((root/'release_candidate.kicad_pcb').read_bytes()).hexdigest()
available=[entry for entry in available if entry[0].get('board_sha256')==board_hash]
if not available:
    raise RuntimeError('No ground resistance model matches the current candidate board; rerun the screen')
ground,model=min(available,key=lambda entry:(entry[0]['mesh_mm'],entry[1].name))
r_pcb=ground['results'][0]['resistance_ohm_at_100C']
rho=1.724e-8*(1+.00393*80)
cases=[]
for length in (25,30,35):
    area=6e-3*1e-3
    r_copper=rho*(length/1000)/area
    joint_budget=20e-6
    r_bar=r_copper+joint_budget
    equivalent=r_bar*r_pcb/(r_bar+r_pcb)
    i_bar=80*r_pcb/(r_bar+r_pcb);i_pcb=80-i_bar
    cases.append({'width_mm':6,'thickness_mm':1,'developed_length_mm':length,
      'ideal_copper_resistance_ohm_at_100C':r_copper,'two_joint_resistance_budget_ohm':joint_budget,
      'bridge_resistance_with_budget_ohm':r_bar,'bridge_current_A':i_bar,'PCB_ground_current_A':i_pcb,
      'total_parallel_loss_W':6400*equivalent,'PCB_ground_loss_W':i_pcb*i_pcb*r_pcb,
      'bridge_loss_W':i_bar*i_bar*r_bar,'copper_mass_g':6*1*length*.00896})
report={'scope':'Proposed reinforcement screening only; no mechanical or thermal qualification',
        'PCB_model':model.name,'PCB_board_sha256':ground['board_sha256'],
        'assumed_uniform_temperature_C':100,'cases':cases,
        'requirements':['Entire conductive span insulated except termination feet',
          'Clearance over J12 positive solder land and its actual wire/harness must be verified',
          'Strain relief must not rely solely on PCB pad adhesion',
          'Measure completed bridge plus joints with four-wire resistance measurement',
          'Qualify at full 80 A even though ideal parallel model shares some current with PCB']}
(root/'ground_busbar_screen.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(cases,indent=2))

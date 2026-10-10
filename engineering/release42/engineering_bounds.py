"""Analytical screening, explicitly not measured electrical/thermal qualification."""
from pathlib import Path
import math,json,itertools
import numpy as np
f=1/(135e-12*21000+580e-9)
vo=1.225*(1+5110/1650)
freq=np.logspace(1,6,4000)
s=2j*np.pi*freq
results=[]
for cp,cc,esr,load,rcomp in itertools.product((96e-6,144e-6),(8e-6,22e-6),(.01,.027),(.1,3),(39200*.99,39200*1.01)):
    # TI's 2 A/V current-mode small-signal approximation; exact output-network
    # impedance includes polymer ESR and a parallel ceramic capacitor.
    zcap=1/(1/(esr+1/(s*cp))+s*cc)
    zout=1/(1/zcap+load/vo)
    zcomp=1/(1/(rcomp+1/(s*10e-9))+s*22e-12)
    loop=2*zout*zcomp/5110*np.exp(-s/(2*f))
    magnitude=np.abs(loop)
    crossings=np.flatnonzero((magnitude[:-1]>=1)&(magnitude[1:]<1))
    if not len(crossings):continue
    i=int(crossings[0]);phase=np.unwrap(np.angle(loop))[i]*180/np.pi
    results.append({'crossover_hz':float(freq[i]),'estimated_phase_margin_deg':float(180+phase)})
rho=1.724e-8
branches={}
for name,current,length,width,thickness in [('Pi existing screen',5,30.155,.2,.07),('Pi proposed screen',5,40,2,.07),('Servo existing screen',7.5,40.878,.2,.07),('Servo proposed screen',7.5,45,3,.07)]:
    # Uniform-strip screening only; excludes actual layer changes, planes and vias.
    resistance=rho*(length/1000)/((width/1000)*(thickness/1000))*(1+.00393*(100-20))
    branches[name]={'current_A':current,'length_mm':length,'width_mm':width,'copper_mm':thickness,'assumed_copper_C':100,
                   'resistance_ohm':resistance,'drop_V':current*resistance,'loss_W':current*current*resistance}
report={'scope':'Analytical screening only; not a qualified model or measured rating',
 'battery':{'full_V':16.8,'nominal_V':14.8,'capacity_Ah':8.4,'stated_C_rating':25,'arithmetic_rating_A':210,
            'PCB_target_A':80,'soak_minutes':15,'soak_required_Ah':20,'ideal_pack_runtime_minutes_at_80A':6.3,
            'cell_model':None,'BMS_rating':None,'pack_resistance_ohm':None,'fault_current_A':None},
 'buck':{'output_V':vo,'switching_hz':f,'inductor_uH':33,'L_DCR_max_ohm_at_25C':.0485,
         'inductor_ripple_A_at_16_8V':vo*(1-vo/16.8)/(33e-6*f),
         'output_capacitor':'Panasonic 10SVPC120M, 120uF +/-20%, 10V, ESR max27mOhm at100kHz',
         'compensation_R_ohm':39200,'compensation_C_F':10e-9,'HF_C_F':22e-12,
         'corner_count':len(results),'crossover_min_hz':min(x['crossover_hz'] for x in results),
         'crossover_max_hz':max(x['crossover_hz'] for x in results),
         'phase_margin_min_deg_estimate':min(x['estimated_phase_margin_deg'] for x in results),
         'model_limits':['TI 2A/V approximation excludes device gain spread','ceramic effective capacitance is a screening range, not selected-part evidence',
                         'ESR frequency/temperature dependence not modeled','half-cycle delay approximation','load-step/Bode measurements required']},
 'thermal_screen':{'ambient_C':50,'MOSFET_RDS_multiplier_assumed':1.7,
   'MOSFET_total_W_equal_sharing':80**2*(.0027*1.7/4),'shunt_total_W_equal_sharing':80**2*.00025,
   'MOSFET_top_RthJC_max_C_per_W':20,'TIM_Rth_assumed_C_per_W_per_device':4,
   'junction_design_limit_C':125,'note':'Assumed multiplier/TIM are design screening bounds, not verified assembly values'},
 'uniform_trace_screen':branches,
 'Pi_topology_note':'Existing /5V_PI net has only BEC1.3 and TP1.1; its PCB trace is a test-point branch, not a 5A distribution path. Pi power must run directly from the external BEC through the specified harness. The Pi trace calculation above is hypothetical and must not be interpreted as actual PCB dissipation.'}
t=report['thermal_screen'];loss=t['MOSFET_total_W_equal_sharing']
t['max_shared_heatsink_RthSA_C_per_W_MOSFET_only']=(125-50-(loss/4)*(20+4))/loss
Path('engineering/release42/engineering_bounds.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

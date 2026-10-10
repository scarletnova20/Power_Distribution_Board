"""50 A component, telemetry, inrush and conditional thermal calculations."""
from pathlib import Path
import json,math
root=Path(__file__).resolve().parent
I=50;V=16.8;ambient=50;limit=125
shunt25=.00025;shunt_hot=shunt25*1.01*(1+.0004*(125-25))
mosfet=[]
for gate,r25 in [(10,.0027),(8,.0032)]:
    rhot=2*r25;total=I*I*rhot/4;per=total/4
    mosfet.append({'gate_V':gate,'datasheet_max_RDS_25C_ohm':r25,'hot_multiplier_ASSUMED':2,
      'hot_RDS_ohm_ASSUMED':rhot,'equal_share_bank_loss_W':total,'equal_share_each_loss_W':per,
      'required_shared_sink_RthSA_C_per_W':(limit-ambient-per*(20+4))/total,
      'thermal_assumptions':'125C junction target, top RthJC max20C/W, assumed TIM4C/W/device, MOSFET-only shared sink; no cross-heating'})
rhi=20000;rlo=1100;gain=(rhi+rlo)/rlo
vmin=V*(rlo*.99)/(rhi*1.01+rlo*.99);vmax=V*(rlo*1.01)/(rhi*.99+rlo*1.01)
tau=1/(1/rhi+1/rlo)*100e-9
sensor={'shunt_ohm_nominal':shunt25,'shunt_voltage_V_at_50A':I*shunt25,
 'shunt_max_ohm_at_125C_from_1pct_400ppm':shunt_hot,'shunt_loss_W_hot_bound':I*I*shunt_hot,
 'analog_V_per_A_nominal':shunt25*100,'analog_V_at_50A':I*shunt25*100,
 'INA169_offset_A_equivalent_1mV':.001/shunt25,
 'INA169_note':'1mV max offset at specified datasheet conditions equals 4A; max hot offset not guaranteed by typical drift',
 'INA169_25C_50A_error_A_screen':4+50*(.01+.01+.01+.001),
 'INA169_error_scope':'Linear sum: offset, 1% transconductance, assumed1% RL1,1% shunt,0.1% nonlinearity; excludes layout,temperature,ADC and common-mode error',
 'INA228_50A_25C_error_A_screen':.004+50*(.0005+.01),
 'INA228_error_scope':'1uV offset +0.05% gain +1% shunt; excludes Kelvin/temperature/bus layout/calibration',
 'INA228_125C_error_A_screen':.008+50*(.0005+.002+.0504),
 'INA228_hot_error_scope':'2uV offset including drift,0.05% gain+20ppm/C*100C,shunt1% plus400ppm/C*100C; not complete assembled accuracy',
 'INA228_fullscale_A_low_range':.04096/shunt25,'INA228_fullscale_A_high_range':.16384/shunt25,
 'INA228_filter_differential_Hz':1/(2*math.pi*20*100e-9),
 'voltage_testpoint_scale_Vbattery_per_Vtest':gain,'voltage_testpoint_at_16_8V':V/gain,
 'divider_1pct_output_range_V':[vmin,vmax],'voltage_filter_tau_s':tau,'voltage_filter_Hz':1/(2*math.pi*tau),
 'R8_loss_W_at_16_8V':(V/(rhi+rlo))**2*rhi,
 'ADC_connection':'TP3 only; J2 is I2C, no analog ADC connected; external ADC reference/input clamp unselected',
 'ADC_protection':'Divider and C15 filtering present; no dedicated clamp/window guarantee; cannot qualify an unspecified ADC'}
cap_known=(47+2.2+2.2)*1e-6
inrush={'known_nominal_input_capacitance_F':cap_known,'known_cap_energy_J_at_16_8V':.5*cap_known*V*V,
 'ESC_supplied_capacitance_F_published':470e-6,'ESC_cap_energy_J_nominal':.5*470e-6*V*V,
 'energy_with_known_nominal_caps_J':.5*(cap_known+470e-6)*V*V,
 'scope':'Published supplied ESC capacitor is not verified fitted hardware; excludes onboard ESC/BEC input caps, bias effects, tolerance and startup loads',
 'energy_per_added_mF_J':.5*.001*V*V,'peak_current_A':None,'lead_inductance_H':None,
 'surge_voltage_V':None,'TVS_qualification':False,'fuse_MPN':None,'holder_MPN':None,
 'energy_per_uH_at_50A_J':.5*1e-6*I*I,
 'inrush_equations':'I=C*dV/dt; initial RC current=16.8/R_total; lead overshoot=L*dI/dt; energy=0.5*C*V^2',
 'fuse_rule':'Rated current after actual temperature/holder derating must carry50A; time-current and I2t must clear before harness/PCB damage, interrupt rating >= verified fault current',
 'external_series_loss_W_per_milliohm_at_50A':2.5,
 'missing_losses':['fuse','holder','main connectors','wires','solder contacts','BEC conversion']}
report={'current_requirement_A':50,'ambient_C':ambient,'MOSFET_cases':mosfet,'telemetry':sensor,'transients_and_fuse':inrush,
 'battery_15min_soak_Ah':I*.25,'ideal_pack_runtime_min_at_50A':8.4/I*60,
 'production_qualified':False}
(root/'analytical50.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

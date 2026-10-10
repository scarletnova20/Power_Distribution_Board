# Protection review — 4S baseline

This review is not a protection qualification. The user supplied 16.8 V maximum
normal battery voltage, 80 A continuous PCB current, 50 C ambient and no assured
airflow. Cell identity, pack resistance, BMS behavior, available fault current,
connectors/wiring and external BEC input/startup limits remain unknown.

## Implemented topology

The verified netlist has four parallel NMOS devices with sources on BAT_FUSED
and drains on VCC, followed by two parallel 0.5 mΩ shunts into Vin. D2 connects
BAT_FUSED to PGND. U5 is LM74502, and its OV input is grounded.

This is a reverse-battery stage. For positive battery input, the MOSFET body
diodes provide a path into the load even when the gates are off. Therefore the
present circuit does not implement controlled hot-plug precharge, positive
fault-current interruption, or overvoltage load disconnect. Slowing the gate
ramp cannot remove that body-diode path. TI's controller supports additional
functions with the appropriate external topology; those capabilities must not
be attributed to this one-bank implementation.

Source: [TI LM74502 datasheet](https://www.ti.com/lit/ds/symlink/lm74502.pdf).
The topology conclusion above comes from the candidate netlist.

## TVS coordination

D2 remains SMCJ28CA, not a newly qualified 4S selection. The upstream clamp-current
path from J1 to D2 is long and includes thin routed copper; its loop inductance,
pulse-current heating and local overshoot need correction/evaluation before
release. DRC does not evaluate these effects.

A possible 4S candidate, Diodes Incorporated SMCJ18CA, has 18 V standoff,
20–22.1 V breakdown and a 29.2 V specified maximum clamp at its rated pulse
condition. It is bidirectional. These are component test conditions, not a
guarantee of the voltage anywhere on this PCB. No replacement has been made.
The package land pattern, temperature/pulse derating, wiring inductance,
repetitive energy and external BEC/ESC limits must be coordinated first.

Source: [manufacturer SMCJ18CA page](https://www.diodes.com/part/view/SMCJ18CA).

## Input fuse and precharge

The stated 25C pack rating gives 210 A arithmetically; it does not specify fault
current or an interruption rating. An 80 A nominal fuse is also not automatically
an 80 A continuous solution at 50 C. The final fuse/holder needs its temperature
derating, time-current curve, DC interruption rating and let-through energy
checked against the actual pack and the PCB/harness damage limits.

Either a qualified external precharge/anti-spark assembly or a redesigned
back-to-back switching stage is needed if controlled inrush is required. The
existing circuit must not be labeled as providing that function. Precharge
energy depends on all downstream capacitance and startup loads, which are not
yet specified for the external BECs/ESC. Fuse and precharge decisions remain open.

## Evidence required to close this review

- Cell and pack data, BMS fault behavior, pack/harness resistance and connectors.
- External BEC and ESC permitted input transients, input capacitance and startup
  waveforms; simultaneous operating load budget.
- Final fuse/holder and precharge specifications, with fault-energy coordination.
- Oscilloscope measurements at the battery input, U5 supply, MOSFET terminals,
  protected rail and external loads under the defined hot-plug/load-step cases.
- Verification that repetitive clamp operation and fault clearing do not exceed
  device, copper, solder-joint or harness limits.

# Swayatt_PCB engineering checkpoint — NOT FOR FABRICATION

Date: 2026-09-07. KiCad 10.0.3.

**The requested finished 40 × 40 mm, 12S / 80 A PCB has NOT been completed.**
This is an electrical-correction checkpoint. Components are parked outside a separate
40 × 40 mm target outline. There is no component placement inside that outline,
no routing, no copper zones, and no manufacturing package. Do not order this board.
The outstanding work is not waiting on permission from the user.

## Accepted requirements

- 40 × 40 mm PCB; external main fuse permitted.
- Pixhawk 6X V2. Its power connector uses I2C, not analog current/voltage signals.
- Three 5 V servos, each 2.5 A stall: 7.5 A aggregate design load.
- One 9 V servo, 3.6 A stall.
- DJI O4 Pro Air Unit: external 12 V BEC. A 3 A interface allowance was selected;
  this is a design allowance, not a manufacturer-specified maximum current.
- Raspberry Pi 5 8 GB: provision external 5.1 V / 5 A supply at the Pi.
- No existing cooling equipment. The PCB has not been thermally qualified.

## Implemented in the project

1. U1 SW17/SW18/PRE19 now share the buck switching node with L1, D1 cathode,
   C7 and the snubber. C7 connects BST20 to SW; in the original netlist it already
   connected BST to the isolated power-stage node, so joining that node to SW was
   the actual required correction.
2. D1 anode and U1 IS15/IS16 now form a dedicated IS_RETURN net. They are no longer
   shorted directly to ground. The snubber returns to IS_RETURN across the diode.
3. U1 EP21 is assigned PGND. U1 ground copper, connected thermal vias and heat spreading
   are NOT implemented because the PCB remains unrouted.
4. Q1 symbol changed from DGS to GDS: footprint pad 1 is gate, pad 2/tab is drain,
   pad 3 is source. The original symbol would have exchanged gate and drain.
   Value clarified to Vishay SQM120P06-07L. This remains unsuitable for 80 A here.
5. Added D2 BZT52H-C12, cathode at source/VCC and anode at gate; upgraded R12 to
   10 kohm / 0.5 W / 2010; added R14 100 kohm gate-source bleed.
6. All BEC battery inputs now use post-shunt Vin. They are included in system current.
7. Added NT2/NT3 to explicitly separate SENSE_P/N from the high-current rails.
   These define the Kelvin connection intent; actual Kelvin traces are NOT routed.
8. U2 supply and C14 now use the regulated output. U2, the telemetry divider, load
   resistor and filtering use GNDA. NT1 remains the sole intentional PCB ground bond.
   FC power-return pins remain PGND so FC load current does not traverse GNDA.
9. Added U3 INA228, U4 TLV75533 3.3 V supply, decoupling, 10 ohm matched input
   resistors, 100 nF differential filter and 4.7 kohm I2C pullups. Address pins tied
   to 3.3 V select 0x45. ALERT is intentionally unused.
10. J2 now uses the 2.00 mm Molex CLIK-Mate 502494-0670 footprint and the Pixhawk
    power pinout: 1/2=5 V, 3=SCL, 4=SDA, 5/6=PGND.
    The analog current/voltage outputs are retained at TP2/TP3, not connected to J2.
11. Added C15 100 nF to the analog voltage test node; added TP1 for the auxiliary Pi rail.
12. DJI rail renamed to 12V_DJI. J10 supplies it through an external BEC.
13. Added D3 green LED and R13 1 kohm from the regulated output. PCB placement and
    the required '5V ON' silkscreen remain unfinished.
14. R1/R2/C4/C11 now have calculated values. L1 is 33 uH DR127-330-R to match C3=330 pF.
15. C1/C2 changed to 2.2 uF / 100 V, 1812. C13 changed to Panasonic EEUFS2A470L,
    47 uF / 100 V, 8 mm diameter, 3.5 mm pitch. R8 enlarged to 1206 / 0.25 W.
16. D1 selected as STPS5H100B, a 100 V / 5 A DPAK Schottky, with a local footprint
    mapping cathode/anode correctly. This intentionally supersedes the requested SMC
    package in favor of a thermally useful, datasheet-supported buck diode package.
17. Removed the invalid Mini fuse holder. F1 is now an off-board 58 V / 80 A MIDI
    fuse, Littelfuse 142.5631.5802, before J1 in the battery harness.
    Exact holder, interrupt rating and fuse derating are not finalized.
18. Replaced main XT60 footprints and high-load BEC headers with direct-solder wire
    pad interfaces. These geometries have NO established 80 A ampacity. Wire gauge,
    strain relief, clearances and copper reinforcement require the final layout.
19. Servo signal pins and SYNC have explicit no-connect markers. Servo PWM comes
    from a separate FC harness; it is not invented on unused FC power pins.
20. Created project-local symbols and footprints, removed dangling schematic stubs,
    synchronized 65 PCB footprints, and checked all pad-net assignments.

## Calculations

| Quantity | Result / basis |
|---|---|
| Regulated voltage | 1.225 × (1 + 5.11k/1.65k) = 5.018788 V nominal |
| Switching frequency | 1/(135 ps × 21k + 580 ns) = 292.826 kHz nominal |
| UVLO | R1=90.9k, R2=10k, both 1%; rising 11.906 V, falling 10.897 V nominal |
| UVLO hysteresis | 0.1 V × (1+90.9k/10k) = 1.009 V nominal input-referred |
| C4 filter | 10 nF; R1 parallel R2 = 9.009k; time constant 90.1 us |
| SD at 50.4 V | Approximately 5.040 V, below the datasheet's 8 V clamp region |
| Soft start | C6=10 nF; 1.225 × C / 10 uA = 1.225 ms typical |
| Compensation | R7=49.9k, C12=10 nF in series; C11=22 pF parallel COMP-to-FB |
| Compensation zero/pole | 318.9 Hz / approximately 145.0 kHz |
| Approximate crossover | 2 × (49.9k/5.11k)/(2 pi × 172 uF) = 18.1 kHz, first-order estimate |
| Inductor ripple at 50.4 V | 0.468 A peak-to-peak; 3 A load peak = 3.234 A |
| Inductor capability | Eaton 33 uH DR127: 3.23 A RMS for about 40 C rise, 6.22 A saturation at stated test conditions |
| Output ripple estimate | About 15–16 mV p-p for 172 uF nominal and ESR <=30 mOhm; not measured |
| Shunt equivalent | 250 uOhm; 20 mV at 80 A |
| Shunt heating | 80² × 250 uOhm = 1.60 W total, 0.80 W per equal branch |
| Analog current scaling | 250 uOhm × 100k/1k = 25 mV/A; 2.0 V at 80 A |
| Analog 3.3 V equivalence | 132 A nominal; this is no longer a Pixhawk ADC connection |
| Analog current offset | INA169 maximum 1 mV input offset corresponds to 4 A; calibration needed |
| Voltage scaling | Vin/19.181818; 2.6275 V at 50.4 V |
| Voltage filter | (20k parallel 1.1k) × 100 nF = 104.3 us; approximately 1.53 kHz |
| R8 heating | Approximately 114 mW at 50.4 V; 0.25 W part specified |
| INA228 filter | (10+10) ohm × 100 nF = 2 us; approximately 79.6 kHz |
| LED | (5.019 − 2.1)/1k = 2.92 mA for assumed 2.1 V green LED Vf |
| Gate pull-down at 50.4 V | (50.4−12)/10k = 3.84 mA; resistor dissipation = 147.5 mW |
| Zener at 50.4 V | Subtract 12/100k bleed: 3.72 mA and 44.6 mW nominal |
| Q1 loss at 80 A | 80² × 6.7 mOhm = 42.88 W at the 25 C resistance rating, worse hot |
| Snubber estimate | 330 pF × 50.4² × 292826 Hz = 0.245 W; verify empirically |

The loop calculation is a first-order estimate based on TI's reference compensation.
It is not a measured phase-margin result or a switching simulation. The output-capacitor
MPN, effective capacitance, ESR curve and load-transient response must be finalized.
UVLO is a regulator startup threshold, not 4S–12S cell-count-aware battery protection.

## Current engineering status against the requested final report

| Requested item | Current status |
|---|---|
| Component count | 67 schematic components including 2 external items; 65 PCB footprints |
| PCB dimensions | 40 × 40 mm target outline only; components remain outside it |
| Layers | 2, inherited from source |
| Copper | 35 um / 1 oz per side, inherited; not qualified for 80 A |
| Battery range | 14.8–50.4 V intent; no hardware validation |
| Maximum designed current | 80 A target NOT ACHIEVED; no rated continuous current assigned |
| 5 V regulator | 5.019 V / 3 A electrical target; thermal implementation incomplete |
| Switching frequency | 292.826 kHz nominal |
| Shunt | 250 uOhm nominal |
| Current telemetry | Digital INA228 at J2; analog 25 mV/A at TP2 |
| Voltage telemetry | Digital INA228 at J2; analog 19.1818:1 divider at TP3 |
| Fuse/holder | External 80 A / 58 V MIDI selected; holder and fault-current suitability open |
| VGS protection | 12 V Zener + 10k/0.5 W pull-down + 100k source-gate bleed implemented electrically |
| U1 thermal pad | Net assignment corrected; thermal layout incomplete |
| UVLO | 90.9k / 10k / 10 nF |
| Compensation | 49.9k / 10 nF / 22 pF; stability verification open |
| Indicator | Green LED + 1k; placement and silk open |
| ERC | 0 errors/warnings reported by actual KiCad ERC |
| DRC | FAIL: 138 unconnected items; 0 other geometric violations |
| Warnings | ERC 0; DRC geometric 0 |
| Manufacturing assumptions | Not finalized; no fabrication release |
| Remaining limitations | Placement, routing, ampacity, thermal and transient protection, assembly MPNs, firmware and harness qualification |

## Why no Gerbers are supplied

The PCB has 0 tracks and 0 zones. The 138 unconnected items alone prohibit release.
An ERC-clean schematic does not make this an 80 A design. The original Q1 still dissipates
about 43 W at 80 A, so adding a gate clamp does not solve its conduction-loss problem.
The project deliberately retains release-hold markings rather than presenting an unsafe
layout as finished. No errors or unconnected routes were excluded to claim DRC success.
The fine-pitch U1/U3 footprints use 0.15 mm local pad clearance; this is an explicit
manufacturing requirement for their package escape, not evidence of high-current routing.

## Cooling and power-stage recommendation — NOT IMPLEMENTED

Replace the single PMOS with a high-side N-channel reverse-battery architecture and
parallel 100 V MOSFETs. As a loss example, four ISC027N10NM6 parts at 2.7 mOhm each
give 0.675 mOhm equivalent and 4.32 W at 80 A at the stated cold resistance. Hot loss
will be higher. This illustrates the improvement; it is not a finalized circuit or BOM.

For a compact 40 mm board, plan for an electrically insulated aluminum heat spreader
and forced airflow, with a provisional assembly heat budget around 12–15 W and a
40 C ambient design target. A heat sink thermal resistance budget near 3 C/W would
limit its rise to 36–45 C, before interface and junction rises. The required sink may
extend beyond the board or require a fan. Its actual rating must be verified at the
installed airflow. Do not place bare metal across exposed copper at different potentials.
Thicker copper alone cannot solve the original 43 W PMOS loss.

No controller/transient network has been selected for that replacement. In particular,
the studied LM74700-Q1 has a 65 V input absolute maximum and a limited cathode-anode
differential rating; it must not be blindly substituted for 12S hot reversal or cable
transients. A nominal '54 V TVS' does not guarantee a clamp below 60/65/75 V.
Battery hot-plug, ESC regeneration, reverse connection, fuse interruption and thermal
rise require a coordinated power-stage design and prototype validation.

## Firmware and harness notes

Holybro documents the INA228 digital-module path for high-voltage Pixhawk 6X systems.
Set the driver shunt resistance to **0.00025 ohm** and address **0x45 (69 decimal)**;
do not copy an unrelated module's calibration. Current ArduPilot INA2XX support exposes
BATTx_SHUNT; verify the installed firmware's parameter set and calibrate against a meter.
PX4 driver configuration for this particular shunt has not been verified.
Do not use the old analog BATT_VOLT_MULT/AMP_PERVLT settings for the digital interface.
Pullup resistance and I2C rise time must be checked with the actual flight controller and cable.

All external BECs must tolerate 12S maximum voltage and transients. The 5 V servo BEC
must support simultaneous 7.5 A stall load; the 9 V servo BEC must support 3.6 A.
The Pi BEC must deliver its voltage at the Pi under load; USB-C 5 A negotiation or
an intentional supported alternative is outside the current PCB interface.
DJI power is provided here; UART/MSP/OSD compatibility and harness routing are not implemented.

## Sources

- [TI LM5576 datasheet](https://www.ti.com/lit/ds/symlink/lm5576.pdf): pins, UVLO, timing, compensation and layout guidance.
- [TI INA169](https://www.ti.com/product/INA169): current-output transconductance and common-mode limits.
- [TI INA228 datasheet](https://www.ti.com/lit/ds/symlink/ina228.pdf): DGS pinout, I2C address and measurement ranges.
- [TI TLV755P datasheet](https://www.ti.com/lit/ds/symlink/tlv755p.pdf): low-voltage regulator pinout and decoupling.
- [Holybro baseboard V2 pinout](https://docs.holybro.com/autopilot/pixhawk-baseboards/pixhawk-baseboard-v2-ports): digital power connector.
- [Holybro digital power setup](https://docs.holybro.com/power-module-and-pdb/power-module/digital-power-module-pm-setup): INA228 high-voltage module support.
- [ArduPilot digital power-module setup](https://ardupilot.org/copter/docs/common-ark-power-modules.html): configurable INA2XX shunt resistance.
- [Vishay SQM120P06-07L](https://www.vishay.com/doc/?67026=): Q1 resistance, pinout and thermal limits.
- [Nexperia BZT52H series](https://assets.nexperia.com/documents/data-sheet/BZT52H_SER.pdf): clamp ratings.
- [ST STPS5H100](https://www.st.com/resource/en/datasheet/stps5h100.pdf): DPAK diode.
- [Eaton DR inductor series](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-dr-high-power-density-high-efficiency-shielded-drum-core-power-inductors-data-sheet.pdf): DR127 electrical and land pattern.
- [Panasonic EEUFS2A470L](https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/aluminum-electrolytic-capacitors-radial-lead-type/series/83320/model/83542): input bulk capacitor rating and dimensions.
- [Littelfuse catalog](https://www.littelfuse.com/assetdocs/north-america-automotive-aftermarket-catalog?assetguid=13ad227a-4401-4c48-9fc7-35f9733c6d29): external 58 V MIDI fuse candidate.
- [Raspberry Pi power documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html): Pi 5 power requirements.
- [DJI O4 specifications](https://www.dji.com/o4-air-unit/specs): Pro operating voltage range.
- [Infineon ISC027N10NM6](https://www.infineon.com/assets/row/public/documents/24/49/infineon-isc027n10nm6-datasheet-en.pdf): proposed loss comparison only.

## Files and verification provenance

- `engineering/baseline/`: original three KiCad files and original ERC/DRC/netlist.
- `engineering/erc.json`, `engineering/drc.json`: actual latest KiCad reports.
- `engineering/connectivity_audit.json`: exported schematic compared to intended pin nets.
- `engineering/pcb_sync_audit.json`: synchronized pad-net comparison.
- `engineering/BOM_checkpoint.csv`: work-in-progress values and footprints, not a purchasing BOM.
- `engineering/schematic_preview/Swayatt_PCB.svg`: native KiCad export. Raster visual QA
  was not completed: bundled SVG renderer was unavailable and no browser was connected.

Original baseline: 21 ERC findings; 14 PCB geometric findings and 102 unconnected items.
This checkpoint adds the missing circuits, so its higher unconnected count is expected.
Neither placing components outside the outline nor clearing geometric overlaps counts as
completion of placement or routing.

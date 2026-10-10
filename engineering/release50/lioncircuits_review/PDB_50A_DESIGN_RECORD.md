# PDB_50A — design and fabrication record

Revision record: 2026-09-11. Team_RotorFPV.

**Release status: HOLD — not fabrication ready; 50 A is a design target, not a tested rating.**

This document consolidates the current native design, interfaces, manufacturing request and evidence. It supersedes historical 80 A descriptions. The authoritative project is `PDB_50A.kicad_pcb/.kicad_sch/.kicad_pro/.kicad_dru` in `engineering/release50`.

Board SHA-256: `c9c3f9b4b2eaea11e62d7a06adaa5d6bd7cebcf41989441f326c62a01ae33d8d`

## Requirements

| Item | Current requirement |
|---|---|
| Continuous load | 50 A aggregate |
| Battery | 4S2P Li-ion; recorded 14.8 V nominal, 16.8 V maximum normal, 8.4 Ah |
| Environment | 50 °C maximum ambient; natural convection, no guaranteed airflow |
| Board | 42 × 42 mm; four copper layers; nominal 1.6 mm |
| Fabricator | LionCircuits Custom; process acceptance pending |

Battery cells, BMS, fault current, harness lengths/gauges/connectors and exact external 5 V / 12 V BEC models remain unspecified.

## Circuit and operating limits

The input uses an external fuse/holder (F1; selection open), four parallel reverse-protection NMOS devices Q1–Q4 (ISC027N10NM6) and U5 (LM74502HDDFR). MOSFET sources face BAT_FUSED and drains face VCC; each gate has a 4.7 ohm resistor. U5 implements reverse-polarity protection only. Startup can flow through body diodes; controlled inrush, load disconnect and active overvoltage protection are not implemented. D2 is the existing SMCJ28CA; transient coordination is unqualified.

U1 is the LM5576 buck stage; U4 supplies 3.3 V. U2 INA169 provides analog current telemetry and U3 INA228 digital telemetry (schematic address 0x45). The two parallel shunts provide 0.25 milliohm nominal sensing. J12 is the main ESC power interface. External BEC interfaces remain separate supplies; do not parallel their outputs.

BEC1/TP1 is an auxiliary Pi-output test branch, not the Pi 5 A load path. J5–J8 pin 1 has no routed control signal; servo control must be supplied externally. J2 uses I2C, not the analog TP2/TP3 outputs. Connector numbering below is extracted from the native netlist; use the assembly orientation and pin numbers, not apparent left/right position in a mirrored view.

## Connector and testpoint pinout

| Reference | Pin | Native net |
|---|---|---|
| BEC1 | 1 | /Vin |
| BEC1 | 2 | /PGND |
| BEC1 | 3 | /5V_PI |
| BEC1 | 4 | /PGND |
| J1 | 1 | /BAT_FUSED |
| J1 | 2 | /PGND |
| J10 | 1 | /Vin |
| J10 | 2 | /PGND |
| J10 | 3 | /12V_DJI |
| J10 | 4 | /PGND |
| J11 | 1 | /12V_DJI |
| J11 | 2 | /PGND |
| J12 | 1 | /Vin |
| J12 | 2 | /PGND |
| J2 | 1 | /out |
| J2 | 2 | /out |
| J2 | 3 | /SCL |
| J2 | 4 | /SDA |
| J2 | 5 | /PGND |
| J2 | 6 | /PGND |
| J3 | 1 | /Vin |
| J3 | 2 | /PGND |
| J3 | 3 | /5V_Servo |
| J3 | 4 | /PGND |
| J4 | 1 | /Vin |
| J4 | 2 | /PGND |
| J4 | 3 | /12V_Servo |
| J4 | 4 | /PGND |
| J5 | 1 | unconnected-(J5-Pin_1-Pad1) |
| J5 | 2 | /5V_Servo |
| J5 | 3 | /PGND |
| J6 | 1 | unconnected-(J6-Pin_1-Pad1) |
| J6 | 2 | /5V_Servo |
| J6 | 3 | /PGND |
| J7 | 1 | unconnected-(J7-Pin_1-Pad1) |
| J7 | 2 | /5V_Servo |
| J7 | 3 | /PGND |
| J8 | 1 | unconnected-(J8-Pin_1-Pad1) |
| J8 | 2 | /12V_Servo |
| J8 | 3 | /PGND |
| TP1 | 1 | /5V_PI |
| TP2 | 1 | /Current |
| TP3 | 1 | /Voltage |

## Mechanical and manufacturing specification


Part: PDB_50A. Fabricator: LionCircuits Custom service. Units: mm.
Authoritative outline: `gerbers/OUTLINE.GKO`. The drawing has only board edges.

| Item | Proposed requirement |
| --- | --- |
| Finished outline | 42.00 x 42.00; square routed outline; no V-scoring |
| Thickness | 1.60 nominal; proposed tolerance +/-10% |
| Layer order | F.Cu / In1.Cu / In2.Cu / B.Cu |
| Copper | 2 oz nominal on all four layers; minimum finished thickness must be stated by fabricator |
| Material | FR-4; laminate/Tg and actual build-up require fabricator proposal |
| Finish | ENIG |
| Mask/legend | Green LPI mask; white legend both sides |
| Mask artwork | 1:1 pad openings; minimum web set to 0.16; proposed registration must be accepted |
| Legend | 0.16 strokes; references at least 0.8 high; team name 1.0 high |
| Holes | All 343 vias are 0.30 nominal drill; separate NPTH mounting holes |
| Via treatment | Nonconductive resin-filled, planarized, copper-capped BOTH sides; solderable exposed via-in-pad regions |
| Hole treatment exceptions | Do not fill connector holes or mounting holes; use via-fill schedule to identify vias |
| Electrical test | 100% bare-board continuity and isolation test against supplied design/net data |
| CAM changes | Return proposed changes for review; no copper thinning, omitted caps or automatic trace/pad reduction |

The embedded 0.20/0.90/0.20 dielectric build-up is an engineering placeholder,
not a LionCircuits stackup. Request the real layer separations, finished copper
tolerances and **minimum**, rather than average, copper barrel plating. The
existing DC model assumed 18 um barrel plating and takes no conductivity
credit for resin filling. That assumption is not a vendor guarantee.

All vias are required to be filled/capped because many overlap solder lands.
Mask tenting or ink plugging is not an equivalent process. Copper-cap thickness,
flatness, permitted voids and inspection method require the fabricator's
proposal. Identify vias by the schedule and native design, not diameter alone.

The current artwork does not meet the published Custom 2 oz trace/space and
annular-ring screen. See the feature inventory and DRC report. This is a
mandatory process hold, not a cosmetic issue.

For automated assembly, LionCircuits lists a 50 x 100 minimum board size and
requires smaller boards to be panelized. Request the assembler's tooling-panel
drawing, fiducials and tab placement before ordering assembly; no assembly panel
is released here. [Assembly capability](https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb)

The stencil and BOM are review outputs. Confirm paste deposition for U1's
thermal pad, Q1-Q4 and shunts, all polarized-part orientations, and the J2
mating harness before assembly. J5-J8 pin 1 has no routed signal connection;
these headers do not generate servo control signals.


Mounting hole centers in native coordinates: (62.5,192.5), (97.5,192.5), (62.5,227.5), (97.5,227.5) mm. Four 3.2 mm NPTH holes on a 35 × 35 mm pattern, 3.5 mm from the edges. Outline corners are (59,189) through (101,231) mm. There are 343 plated via holes and 12 plated component holes. Connector and mounting holes remain open.

Native Y increases downwards; manufacturing Y has opposite sign. Bottom viewing images may be mirrored; manufacturing coordinate data must not be mirrored. Nine manufacturing layers are supplied: four copper, two mask, two silk and outline, with separate PTH/NPTH Excellon drills. IPC-2581 and local libraries accompany native source.

## Verification on this revision

| Check | Result |
|---|---|
| ERC findings | 0 |
| Unconnected items | 0 |
| Electrical invariants | 52 checked; 0 failures |
| Additional checks | 9/9 pass |
| Pad-net/layout failures | 0 |
| DRC findings | 901 — manufacturing gate fails |
| Ignored checks / exclusions | 0 / 0 |

The independent inventory identifies 902 tracks below 0.254 mm and 343 via annuli below 0.1524 mm. Fine-pitch lands at U1/U3/U5 also conflict. Reported DRC examples are capped and are not the full inventory. LionCircuits capability page was checked again on 2026-09-11: https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb . Historical zero-DRC results used another process and do not release this board.

## Power and telemetry calculations

The preserved 0.1 mm mesh DC screen estimates 9.757 W positive-path plus 2.024 W return loss, total 11.781 W and approximately 0.236 V loop drop at 50 A ESC-only load. Assumptions: 70 µm copper, 18 µm barrel plating, uniform 125 °C, 5.4 milliohm MOSFET resistance, ideal contacts. Q1–Q4 carry approximately 18.285 / 11.969 / 10.000 / 9.746 A. Unequal sharing needs thermal review. Mesh convergence is unestablished. Fuse, holder, harness, contact and BEC conversion losses are excluded; each extra milliohm adds 2.5 W at 50 A.

Nominal shunt drop is 12.5 mV at 50 A. Analog current scaling is 25 mV/A (1.25 V at 50 A). The INA169 offset screen alone can represent 4 A; do not assume calibrated accuracy. TP3 divider ratio is 19.1818 battery volts per testpoint volt, giving 0.8758 V at 16.8 V. Dedicated external ADC input protection/reference remains unselected. Detailed assumptions and error screens are in `analytical50.json`; these are calculations, not measurement results.

## Release gates and acceptance evidence

| Gate | Required closure evidence | Current status |
|---|---|---|
| Bare-board DFM | Written custom-process acceptance for actual geometry, or redesign to accepted rules and fresh DRC without hidden violations | OPEN |
| Stackup / vias | Approved stackup, minimum finished copper and barrel plating; resin fill, cap flatness/thickness/void criteria | OPEN |
| Manufacturing data | Fresh source hashes, parsed Gerber/drill agreement, visual CAM review, supplier CAM approval and bare-board electrical test requirement | Review outputs available; supplier acceptance OPEN |
| Assembly | Exact orderable BOM, polarity and mating harness verification, paste/thermal-pad review and tooling panel | OPEN |
| Protection | Verified cell/BMS fault current, fuse/holder interrupt capability and time-current coordination; measured hot-plug/transients against actual parts | OPEN |
| 50 A operation | Thermal solution and current sharing, measured steady-state temperatures/drop at 50 °C ambient under worst actual loads; documented limits from selected components | OPEN |

Before energizing a prototype, inspect assembly and polarity, check rail-to-ground resistance and begin from a current-limited source. Verify rails, telemetry and BEC isolation at low load before a controlled load ramp. Record individual MOSFET/shunt/connector temperatures and voltage drops; establish stop limits from final component ratings. Qualification must use the actual harness and cooling. A 15-minute 50 A test needs 12.5 Ah; the recorded 8.4 Ah pack cannot supply that duration even ideally. High-current testing remains a separate qualified engineering activity.

## Full BOM review register

| Reference | Value | Footprint | Manufacturer | MPN | Open detail |
|---|---|---|---|---|---|
| BEC1 | Conn_01x04 | Swayatt_Local:BEC_Wire_4_42 |  |  | External Pi BEC; PCB /5V_PI connection is a test-point branch, not the 5 A load path |
| BT1 | BATTERY HARNESS EXTERNAL |  |  |  | Exact ordering code/assembly specification requires BOM review |
| C1 | 2.2u 100V X7R | Capacitor_SMD:C_1812_4532Metric |  |  | Exact MLCC and effective capacitance under DC bias must be verified |
| C10 | 22u 16V X7R | Capacitor_SMD:C_1206_3216Metric |  |  | Exact MLCC and effective capacitance under DC bias must be verified |
| C11 | 22p C0G | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C12 | 10n C0G | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C13 | 47u 50V EEH-ZA1H470P | Capacitor_SMD:C_Elec_8x10.2 | Panasonic | EEH-ZA1H470P | SMD hybrid reservoir |
| C14 | 100n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C15 | 100n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C16 | 100n 100V X7R | Capacitor_SMD:C_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C17 | 100n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C18 | 1u 16V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C19 | 1u 16V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C2 | 2.2u 100V X7R | Capacitor_SMD:C_1812_4532Metric |  |  | Exact MLCC and effective capacitance under DC bias must be verified |
| C20 | 1u 25V X7R | Capacitor_SMD:C_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C21 | 100n 100V X7R | Capacitor_SMD:C_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C3 | 330p | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C4 | 10n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C5 | 470n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C6 | 10n 25V | Capacitor_SMD:C_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C7 | 22n 100V X7R | Capacitor_SMD:C_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C8 | 330p 100V C0G | Capacitor_SMD:C_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| C9 | 120u 10V 10SVPC120M ESR27mR | Swayatt_Local:Panasonic_OSCON_C6_10SVPC120M | Panasonic | 10SVPC120M | Manufacturer C6 land pattern applied |
| D1 | STPS5H100B | Swayatt_Local:STPS5H100B |  |  | Exact ordering code/assembly specification requires BOM review |
| D2 | SMCJ28CA bidirectional | Diode_SMD:D_SMC |  |  | Existing SMCJ28CA; 4S clamp selection and pulse-current path not qualified |
| D3 | GREEN 5V ON | LED_SMD:LED_0805_2012Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| F1 | EXTERNAL FUSE + HOLDER TBD FOR 50A SYSTEM |  |  |  | External fuse AND holder OPEN; obsolete 80A selection withdrawn; not replaced by an assumed50A fuse |
| J1 | 4S FUSED INPUT 16.8V MAX NORMAL | Swayatt_Local:Power_Wire_2_42 |  |  | Exact ordering code/assembly specification requires BOM review |
| J10 | EXTERNAL BEC 12V DJI | Swayatt_Local:BEC_Wire_4 |  |  | Exact ordering code/assembly specification requires BOM review |
| J11 | 12V DJI OUTPUT | Swayatt_Local:Aux_Wire_2_42 |  |  | Exact ordering code/assembly specification requires BOM review |
| J12 | SPEEDYBEE ESC BATTERY 4S | Swayatt_Local:Power_Wire_2_42 |  |  | Exact ordering code/assembly specification requires BOM review |
| J2 | PIXHAWK 6X POWER 5024430670 VERTICAL | Swayatt_Local:CLIK_Mate_502443_0670 |  |  | Exact ordering code/assembly specification requires BOM review |
| J3 | BEC_5V_SERVOS | Swayatt_Local:BEC_Wire_4_42 |  |  | Exact ordering code/assembly specification requires BOM review |
| J4 | BEC_12V_SERVOS | Swayatt_Local:BEC_Wire_4 |  |  | Exact ordering code/assembly specification requires BOM review |
| J5 | Servo_5V_1 | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical |  |  | Exact ordering code/assembly specification requires BOM review |
| J6 | Servo_5V_2 | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical |  |  | Exact ordering code/assembly specification requires BOM review |
| J7 | Servo_5V_3 | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical |  |  | Exact ordering code/assembly specification requires BOM review |
| J8 | Servo_12V_1 | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical |  |  | Exact ordering code/assembly specification requires BOM review |
| L1 | 33u XAL8080-333MED | Inductor_SMD:L_Coilcraft_XAL8080-XXX | Coilcraft | XAL8080-333MED | 33 uH; manufacturer electrical data reviewed |
| NT1 | NetTie_2 | NetTie:NetTie-2_SMD_Pad0.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| NT2 | NetTie_2 | NetTie:NetTie-2_SMD_Pad0.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| NT3 | NetTie_2 | NetTie:NetTie-2_SMD_Pad0.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| Q1 | ISC027N10NM6 100V 2.7mR | Swayatt_Local:ISC027N10NM6_GDS | Infineon | ISC027N10NM6ATMA1 | Four parallel NMOS retained; hot/current-sharing/thermal qualification OPEN |
| Q2 | ISC027N10NM6 100V 2.7mR | Swayatt_Local:ISC027N10NM6_GDS | Infineon | ISC027N10NM6ATMA1 | Four parallel NMOS retained; hot/current-sharing/thermal qualification OPEN |
| Q3 | ISC027N10NM6 100V 2.7mR | Swayatt_Local:ISC027N10NM6_GDS | Infineon | ISC027N10NM6ATMA1 | Four parallel NMOS retained; hot/current-sharing/thermal qualification OPEN |
| Q4 | ISC027N10NM6 100V 2.7mR | Swayatt_Local:ISC027N10NM6_GDS | Infineon | ISC027N10NM6ATMA1 | Four parallel NMOS retained; hot/current-sharing/thermal qualification OPEN |
| R1 | 90.9k 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R10 | 500u 3W 1% WSLP2512L5000FEA | Swayatt_Local:WSLP2512_L5000 | Vishay | WSLP2512L5000FEA | Kelvin pickup/current sharing review remains open |
| R11 | 500u 3W 1% WSLP2512L5000FEA | Swayatt_Local:WSLP2512_L5000 | Vishay | WSLP2512L5000FEA | Kelvin pickup/current sharing review remains open |
| R12 | 4.7R | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R13 | 1k 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R14 | 1M gate-source bleed | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R15 | 10R 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R16 | 10R 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R17 | 4.7k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R18 | 4.7k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R19 | 4.7R | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R2 | 10k 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R20 | 4.7R | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R21 | 4.7R | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R3 | 10, 1W | Resistor_SMD:R_2512_6332Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R4 | 21k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R5 | 5.11k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R6 | 1.65k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R7 | 39.2k 1% | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R8 | 20k 1% 0.25W | Resistor_SMD:R_1206_3216Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| R9 | 1.1k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| RL1 | 100k | Resistor_SMD:R_0603_1608Metric |  |  | Exact ordering code/assembly specification requires BOM review |
| TP1 | 5V_PI AUX | TestPoint:TestPoint_Pad_D1.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| TP2 | CURRENT ANALOG TEST | TestPoint:TestPoint_Pad_D1.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| TP3 | VOLTAGE ANALOG TEST | TestPoint:TestPoint_Pad_D1.5mm |  |  | Exact ordering code/assembly specification requires BOM review |
| U1 | LM5576MH | Swayatt_Local:LM5576_PWP20 |  |  | Exact ordering code/assembly specification requires BOM review |
| U2 | INA169NA_3KG4 | Package_TO_SOT_SMD:SOT-23-5 |  |  | Exact ordering code/assembly specification requires BOM review |
| U3 | INA228AIDGSR I2C=0x45 | Swayatt_Local:INA228_DGS0010A | Texas Instruments | INA228AIDGSR | TI DGS0010A land pattern; Kelvin geometry/calibration review OPEN |
| U4 | TLV75533PDBV | Package_TO_SOT_SMD:SOT-23-5 |  |  | Exact ordering code/assembly specification requires BOM review |
| U5 | LM74502HDDFR REVERSE ONLY | Swayatt_Local:LM74502_DDF8 |  |  | Exact ordering code/assembly specification requires BOM review |

All BOM entries remain review status. Blank MPNs are unresolved purchasing selections, not permission to substitute.

## Labelling and source evidence

`label_placement.json` records each reference position, side and angle. References use 0.8 mm height and 0.16 mm strokes, with a 1.0 mm Team_RotorFPV name on front silk. This exceeds the published 0.5842 mm legend height; the earlier project preference of 1.0 mm could not fit. 58 references fit on silk within 4.5 mm of their component centers; 20 crowded references remain on fabrication layers. The indexed front/back component locators and pin table identify all parts. `checks/label_verification.json` records final silk checks; `checks/export_verification.json` verifies copper preservation.

Evidence files: `verification.json`, `drc.json`, `erc.json`, `netlist.xml`, `analytical50.json`, `power_0.1mm_70um_repaired.json`, `lioncircuits_review/feature_audit.json`, `lioncircuits_review/checks/export_verification.json`, `BOM_REVIEW.csv` and `requirements.json`.

`PDB_50A_LionCircuits_REVIEW_HOLD.zip` is a review archive. `SUPPLIER_REVIEW_REQUEST.txt` is prepared and unsent. No supplier message or production order has been sent by this work.

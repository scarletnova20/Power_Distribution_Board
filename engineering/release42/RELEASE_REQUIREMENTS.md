# Fabrication release requirements, updated 2026-09-08

## User-confirmed operating conditions

- PCB continuous-current target: 80 A. Qualification soak: at least 15 minutes.
- Maximum ambient: 50 C. No guaranteed forced airflow. UAV airflow is margin only.
- Battery: custom 4S2P Li-ion, 8400 mAh, nominal about 14.8 V, full 16.8 V.
- Stated pack C-rating: 25C, mathematically 210 A. This is not a verified continuous
  capability or a prospective short-circuit-current specification.
- Exact cells, pack resistance, BMS, wiring, connectors and available fault current:
  UNKNOWN. Do not infer these from the stated C-rating.
- A 15-minute 80 A soak consumes 20 Ah. The 8.4 Ah flight pack cannot supply that
  duration; use a properly rated laboratory source or larger verified test source.
- Keep external BEC interfaces /5V_PI, /5V_Servo, /9V_Servo, and /9V_DJI.
  The older /12V_DJI designation is superseded by the latest user instruction.
- Pi 5 interface target: regulated 5 V, up to 5 A. It is not powered by the LM5576.
- LM5576 supplies the FC/telemetry rail, nominal 5.019 V, design load up to 3 A.
- Exact BEC models, ratings and startup behavior: UNKNOWN. Previously recorded
  servo stall loads (three at 2.5 A, one at 3.6 A) are provisional interface design
  loads, not statements of actual BEC capability. Earlier DJI 3 A is only an
  interface allowance, not a verified BEC current rating.
- An insulated heatsink may overhang the board. Its actual thermal resistance,
  mounting and interface must be specified; no reliance on propwash.

## Release gates

1. Exact assembly BOM and verified footprints, polarity and harness pinout.
2. Short regulator control paths; local AGND bond; short switching-current loops.
3. Power copper and via arrays sized for the specified branch currents, with
   calculated resistance/drop/loss and thermal-path implementation.
4. Output capacitor selection and regulator compensation analysis.
5. Battery/BEC specifications sufficient for fuse, hot-plug, inrush and transient
   coordination. User explicitly requires these remain unqualified until verified.
6. Fabricator stackup, plated-hole and via-fill/cap requirements encoded in the
   manufacturing drawing and accepted by the intended fabrication process.
7. Fresh ERC/DRC, schematic parity, independent netlist/layout checks, and visual
   inspection of the actual exported manufacturing layers.
8. Thermal/electrical prototype verification for an 80 A continuous product rating.
   Design calculations are not a substitute for measured qualification.

The existing root-level routed board remains a saved checkpoint. The active
working revision is `release_candidate`; see `WORKING_REVISION.md`. It must not
be ordered while these gates are open.

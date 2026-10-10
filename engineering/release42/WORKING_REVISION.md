# Working fabrication review — 2026-09-09

Latest LED/status review: existing D3/R13 retained and verified; front silkscreen
now reads `5V ON`, schematic value identifies the indicator, and the inherited
Schottky description is corrected. Fresh ERC/DRC show zero findings/unconnected
items; 52 electrical invariants and five LED checks pass. See
`SCHEMATIC_AND_MANUFACTURING_SUMMARY.md`, `led_verification.json` and
`led_review/`. The board hash changed because of annotations/value text;
`led_copper_unchanged.json` verifies all other serialized board items match the
pre-edit board. Old resistance files retain their original board hashes.
They describe unchanged copper geometry, but scripts correctly require explicit
provenance reconciliation before accepting them for the new whole-file hash.
No manufacturing release. Backups are in `before_led_status/`.

Active review files are `release_candidate.kicad_pcb`, `.kicad_sch`, and
`.kicad_pro` in this directory. They have not replaced the older root-level
`Swayatt_PCB_42x42` checkpoint. Neither revision is released for manufacture.

Latest verified candidate: 78 footprints, 1247 tracks/vias, four copper layers;
zero DRC findings, zero unconnected items, zero ERC findings, 52 electrical
invariants passed, schematic-to-board pad nets match. No ignored checks or DRC
exclusions. See `candidate_verification.json` for the exact board hash.

Implemented in the candidate:

- User-confirmed 4S/16.8 V normal input and external `/9V_DJI` naming.
- Four 70 µm copper layers; filled/capped through-via process requested.
- Short LM5576 COMP/BST/BIAS/SS routes, local AGND/PGND net tie, thermal vias,
  input/switch-node copper, and a dedicated IS-return power path.
- Explicit wider external servo/DJI distribution paths.
- Panasonic EEH-ZA1H470P input reservoir and 10SVPC120M output capacitor;
  C9 uses the manufacturer's C6 land dimensions, not the generic footprint.
- R7 changed to 39.2 kΩ; preliminary regulator model in `engineering_bounds.py`.
- Power-plane stitching, with DRC failures and unintended net assignments removed.
- INA228 C16 moved to (84.3, 214.0), with approximately 2.6 mm / 2.4 mm input
  routes; C15 relocated to (86.8, 213.9) to accommodate it.
- All default-ignored candidate DRC checks enabled; via endpoint warnings fixed.
- Main battery-negative land now has 34 direct vias to the ground plane. This
  fixes a real current-path bottleneck that ordinary DRC did not identify.
- Explicit 1.0/0.8 mm BEC supply paths and a wider Pi-BEC ground bridge; direct
  J4 ground vias and three C9 output-capacitor return vias. The displaced Pi
  test-point and MOSFET-drive routes are reconnected.
- `power_land_audit.json` verifies all intended new main-land vias survive with
  the correct nets. Fully enclosed main-land via counts are J1+=5, J1-=34,
  J12+=15 and J12-=6; adjacent plane stitching is additional. Counts alone are
  not ampacity ratings.

Open release work includes main-path resistance/current sharing, thermal assembly
and measured qualification, Kelvin pickup review, exact remaining assembly BOM,
transient/inrush/fuse coordination, harness specifications and fabrication
process acceptance. The user explicitly requires unknown battery/BEC properties
to remain unknown and forbids claiming transient qualification without them.
`RELEASE_REQUIREMENTS.md` records operating conditions and release gates.

## Current resistance investigation

`ground_resistance_screen.py` models the saved PGND fill, pads, tracks and vias
using a four-layer DC finite-difference network. The 0.2 mm mesh converged to
0.783 mΩ with assumed 20 µm plating and 0.774 mΩ with 25 µm plating, at an
assumed uniform copper temperature of 100 C. This is approximately 5.0 W at
80 A before adding solder/harness resistance. The 0.1 mm mesh gave 0.595 mΩ,
or 3.81 W. The 0.05 mm mesh gave 0.565 mΩ, or 3.62 W; the two finer meshes differ
by about 5.1%. Treat this as a limited-accuracy screening result, not an exact
resistance or temperature prediction. The AMG solver reproduced the original
0.2 mm result and enables
finer checks; project-local SciPy 1.17.1 and PyAMG 5.3.0 are in `engineering/vendor`.
This is a screening result, not a temperature prediction or a qualified rating.
The model ignores rounded pad corners and uses ideal distributed
contacts and lumped via barrels; its limitations are in the JSON report.

The user selected retaining 42 mm and evaluating a heavier-copper process.
See `HEAVY_COPPER_REVIEW.md` for the resulting evaluation. No new fabrication
stackup has been accepted or implemented.

No analysis jobs remain running. `ground_busbar_screen.json` compares proposed
reinforcement against the finest saved mesh. The candidate itself has no busbar
installed or specified as a released assembly item. `candidate_BOM_REVIEW.csv`
is generated from the current candidate netlist and explicitly leaves unknown
ordering codes blank. The older root-level BOM is not the candidate BOM.

Protection review confirms D2 is upstream on BAT_FUSED, and all four MOSFETs
are parallel with their sources toward the battery. The body-diode path bypasses
gate-ramp inrush control. This is reverse-polarity protection, not an implemented
back-to-back load-disconnect/inrush stage. D2 remains SMCJ28CA; a lower-standoff
4S TVS has been researched but is NOT yet selected or installed. Its long
input-clamp current path also needs review. External battery/BEC data remain
necessary for protection qualification.

## Independent solver review, 2026-09-09 continuation

`test_copper_solver.py` passes five analytical checks: a series strip, a
multilevel series strip, a rectangular sheet, a via/plane series network and
floating islands. Resistance, terminal current balance and energy balance
agree within 1e-8 relative tolerance; results are in `copper_solver_tests.json`.
These validate network solution behavior, not the PCB rasterizer or ampacity.
The current board SHA-256 still matches the saved 0.05 mm resistance model
and candidate verification. `ground_busbar_screen.py` now rejects models from
other board hashes before selecting the finest available mesh.

Code review also identifies geometry approximations needing a sensitivity
study: the rasterizer treats via pads as solid copper disks without removing
drill bores, and connects each barrel at one grid node. Filled/capped vias do
not by themselves specify conductive hole fill. Pad shapes are approximated
as rectangles. Therefore numerical mesh convergence alone does not establish
physical-model accuracy. Existing 3.62 W ground-loss screening remains
provisional. No PCB geometry or mechanical option was changed during this review;
the user subsequently selected retaining 42 mm and evaluating heavier copper.
Evaluate that option before implementing a new stackup; reinforcement is not
the selected direction.

## Construction-script warning

Several scripts rebuild from preserved snapshots. Do not rerun them against a
later improved board without deliberately reconciling those changes:
`prepare_release_candidate.py`, `route_local_controls.py`,
`local_power_copper.py`, `stitch_candidate.py`, `localize_sense_filter.py`.
Also preserve later changes before rerunning `power_land_vias.py` or
`widen_bec_feeds.py`, which likewise rebuild from snapshots.
The last script also reads a DRC report whose UUIDs must match its source board.

Use `verify42.py --candidate` and `release_audit.py --candidate`; without that
flag they check the older root-level board. Netlist export must explicitly use
`--format kicadxml`. KiCad CLI jobs on the same project run sequentially.

KiCad 10 Python can return invalid SWIG wrappers after removing board items.
Perform geometry reads before removals, or edit serialized items before loading.
Power-via intent must be audited after save; DRC alone did not detect all
unintended net reassignments from the initial stitching operation.

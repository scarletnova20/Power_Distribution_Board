# Latest continuation: 2026-09-11, labels and design documentation

See `release50/CONTINUATION.md`. Labelling pass and comprehensive
`release50/PDB_50A_DESIGN_RECORD.md` are complete. There are 58 silk references
and 20 assembly-only references, with indexed maps for all 78 components.
Fresh checks: zero silk/text findings, zero ERC/unconnected, 52+9 checks pass.
LionCircuits DRC still fails (908 findings); geometry inventory and copper are
unchanged. Review archives regenerated. User has not uploaded the PCB yet;
`lioncircuits_review/UPLOAD_FOR_REVIEW.txt` describes the feasibility submission.
No fabrication release or qualified 50 A operation is claimed.

# Historical continuation: 2026-09-10, LionCircuits process review

User selected LionCircuits. Active `release50/PDB_50A` now has its published
Custom 2 oz rule screen and fails it: 901 reported DRC findings. Independent
inventory: 902 narrow tracks and 343 small via annuli. Electrical checks still
pass. A verified review-only Gerber/drill/source archive is prepared; no
fabrication release. See `release50/CONTINUATION.md` and
`release50/lioncircuits_review/README.md`. The older zero-DRC results below used
a different process and must not be represented as LionCircuits acceptance.

# Historical continuation: 2026-09-10, 50 A candidate

The active candidate is now `release50/PDB_50A.kicad_pcb` with its matching
schematic and project. See `release50/CONTINUATION.md` and `requirements.json`.
The 50 A continuous, 4S / 16.8 V requirement supersedes the historical 80 A
target below. The repaired candidate passes fresh ERC/DRC with zero findings
and zero unconnected items; all 52 electrical and nine additional checks pass.
It remains unqualified for fabrication and 50 A thermal/production operation.

# Historical continuation: 2026-09-08, 42 mm routing completed

The newer `Swayatt_PCB_42x42` project supersedes the 40 mm layout for ongoing
work. It was recovered from the 2026-09-07 22:33 placement revision in
`engineering/release42/`. See `release42/CONTINUATION.md` for current status.
It now has zero DRC/ERC findings and zero unconnected items, with all checks
enabled, 78 footprints and 976 tracks/vias. All 52 electrical invariants pass.
The original 40 mm board is preserved. Neither revision is released for manufacture.

# Historical continuation state, 2026-09-07, after routing repair

Placement and routing now pass layout checks. The qualified 80 A board is NOT
achieved. No manufacturing release.

## Requirements recovered

The incoming revise_schematic.py explicitly records that the user selected 4-6S
with the SpeedyBee BLS 35A Mini V2 ESC. That implementation was newer than the
previous handoff. Do not ask the old 12S-versus-ESC question again. Maximum
normal voltage is 25.2 V. The 80 A aggregate target and 40 x 40 mm outline remain.
An electrically insulated heatsink may extend beyond the board, already accepted.
Pixhawk 6X V2 and the servo/DJI/Pi loads are recorded in ENGINEERING_CHECKPOINT.md.

## This continuation

The late-evening resume found placement, four-layer copper and most routing
already implemented after the earlier notes below. It repaired four missing
signal connections, removed shorting ground segments near the bottom edge,
rerouted the affected ground branch and an obstructing /out segment, moved C16
0.3 mm, and added three U1 escape vias. All five inherited ignored DRC checks
were enabled. Track endpoints were centered on vias without weakening rules.
The saved board has zero DRC findings and zero unconnected items, with no
ignored checks or exclusions. Independent layout verification passes.

Earlier schematic work retained:

- Found the partially implemented four-parallel-NMOS circuit and synchronized
  it to the PCB (76 schematic components, 74 onboard footprints).
- Corrected U5 LM74502HDDCR to LM74502HDDFR using TI's orderable-part page.
- Added TI DDF0008A land pattern as Swayatt_Local:LM74502_DDF8; this fixes the
  generic footprint's six clearance findings without reducing the 0.20 mm rule.
- Moved U5 away from the schematic title block; regenerated and reviewed preview.
- Extended independent checks from 28 to 52 and deliberate fault tests from
  two to four, covering reversed MOSFET orientation and incorrect pump return.
- Updated report generation/BOM/archive to reflect the 4-6S NMOS implementation.
- Incoming board/schematic and old notes/generator preserved in before_resume_audit/.

## Actual circuit limits

Q1-Q4 ISC027N10NM6 sources face BAT_FUSED, drains face VCC and the shunts.
Each gate has a 4.7 ohm resistor. U5 VS/EN/SRC connect to fused battery; OV is
grounded. C20 connects VCAP to VS. D2 is bidirectional SMCJ28CA across input.
This is reverse-polarity protection only. Body diodes allow startup current:
there is no inrush limiting, load disconnect or active OVP. Do not describe the
controller's optional features as implemented. ESC transient coordination remains
open. Preserve regenerative return-current considerations in any redesign.

Cold equal-sharing MOSFET loss is 4.32 W at 80 A; shunts add 1.60 W. No thermal
rating follows from these calculations. The original single PMOS is superseded.

## Validation and next work

See generated ENGINEERING_CHECKPOINT.md and actual JSON reports for final counts.
52 independent checks pass and all four fault tests are detected. ERC passes;
netlist and PCB pad-net comparisons match. All 74 onboard footprints are inside
the exact closed 40 x 40 mm outline, with four layers, 1657 tracks/vias and 12
filled zones. final_verification.json records the verified board SHA-256.
The stackup is nominally 1.6 mm with 70/35/35/70 um copper. Front/back SVG and
PNG previews were regenerated and visually inspected.

Next: finish hot-plug/precharge and ESC/BEC transient coordination, select harness,
fuse/holder, reinforcement and thermal implementation. Review buck loop area,
feedback/COMP routing, Kelvin pickup geometry and power copper bottlenecks;
DRC-clean connectivity is not proof of analog or high-current performance.
Confirm filled/capped via-in-pad fabrication requirements; current defaults
do not encode them. Placement/routing may need revision following these reviews.
The supplied ESC capacitor is only part of startup capacitance. Prototype
electrical and thermal measurements will be required for qualification.

For regeneration: make_footprints.py, revise_schematic.py, KiCad netlist export,
electrical_invariants.py --self-test, connectivity_audit.py, sync_pcb.py, ERC/DRC,
SVG export and visual review, then build_report.py. These scripts regenerate the
schematic; preserve any manual schematic edits before using them. sync_pcb.py
preserves current placement and tracks but does not refresh a changed footprint
if its library identifier remains identical; inspect that case explicitly.

Do not rerun placement or routing generators over this checkpoint casually.
finish_routes.py --rebuild-from-backup reconstructs the repair from
before_resume_2145.kicad_pcb and does not include subsequent endpoint centering.
Then run DRC and center_via_tracks.py until centering findings clear, rerun DRC,
final_verify.py, preview export/render and build_report.py. A KiCad process
may hang in the filesystem sandbox while accessing its settings: terminate only
the task-owned stalled process and rerun with the required tool escalation.

Source verification: TI LM74502 datasheet and LM74502HDDFR part page;
Infineon ISC027N10NM6 datasheet. Links are in ENGINEERING_CHECKPOINT.md.

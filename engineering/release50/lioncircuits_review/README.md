# LionCircuits engineering review — HOLD

This package is for process feasibility and DFM review. **Do not manufacture
from this revision.** The user selected LionCircuits on 2026-09-10. Previous
JLCPCB capability assumptions do not constitute acceptance by LionCircuits.

The design target is 50 A continuous aggregate, 4S2P Li-ion, 16.8 V maximum
normal input, 42 x 42 mm, 50 C ambient and no guaranteed airflow. This package
does not establish the assembled board's current rating.

## Concrete process conflict

LionCircuits' published Custom 2 oz process lists 10 mil track width/spacing
and 6 mil annular rings. Exact conversions are 0.254 mm and 0.1524 mm.
The actual board has **902 narrower track segments**, **343 vias with smaller
annuli**, and fine-pitch pad gaps on U1/U3/U5. Full coordinates and UUIDs are
in `undersize_tracks.json`, `undersize_via_annuli.csv`, and `feature_audit.json`.
Source: [LionCircuits rigid capabilities](https://www.lioncircuits.com/pcb-manufacturing-capabilities/rigid-pcb), accessed 2026-09-10.

The route therefore needs a written custom-process acceptance or substantial
redesign to an accepted stackup. No waiver is assumed. Do not shrink component
lands or thin power copper merely to make the manufacturing check pass.

## Contents

- `gerbers/`: four copper layers, mask, silk, outline and Gerber job.
- `drill/`: separate plated/non-plated Excellon files and drill maps/report.
- `assembly/`: paste, fabrication layers, native placement CSV and incomplete
  assembly BOM. These are supporting review files, not an assembly release.
- `source/`: native KiCad source and IPC-2581 export.
- `checks/`: fresh electrical/DFM reports and independent export checks.
- `previews/`: inspection images. All `gerber_*` images share the top-view
  registration. KiCad `back.svg`, `mask_back.svg` and `assembly_back.svg`
  are mirrored bottom views for viewing only.
- `via_fill_schedule.csv`: all 343 through vias requiring fill and copper cap.
- `pad_coordinates.csv`: pad/net inventory in native KiCad coordinates.
- `MANUFACTURING_REQUIREMENTS.md`: proposed build specification and holds.
- `SUPPLIER_REVIEW_REQUEST.txt`: prepared request; it has not been sent.

Manufacturing coordinates are absolute, millimetres, with no mirroring.
KiCad board Y increases downwards; Excellon/Gerber Y has the opposite sign.
Use native coordinate columns in the via schedule with Y negated for CAM.
Never drill both a combined PTH file and an additional duplicate via file.

`checks/verification.json` must be read with the new LionCircuits rule set.
The historical zero-DRC result used different manufacturing constraints and
is not a LionCircuits manufacturing pass.

Fresh DRC (2026-09-11) reports 901 findings: 199 annular-ring, 199 track-width and 503
clearance findings. Treat these as reported examples, not a complete inventory:
the independent feature audit finds 902 narrow segments and 343 small annuli.
ERC, all 52 electrical invariants and nine extra checks pass, with zero
unconnected items. No checks are ignored and no exclusions were added.

## Remaining electrical/assembly decisions

The 2026-09-11 label pass adds Team_RotorFPV, 58 readable silk references and
20 assembly-only references with indexed location maps for all 78 components.
Zero silk/text DRC findings. Read `PDB_50A_DESIGN_RECORD.md` for the full design
record and `UPLOAD_FOR_REVIEW.txt` for submission instructions. The user has
not uploaded this board to LionCircuits yet. Copper/stackup/drills are unchanged.

The user confirmed 4S2P Li-ion but does not have exact BEC model names. Battery
cells/BMS, fault current, BEC limits/startup, fuse/holder, wire gauge/length and
connector parts remain unspecified. 5 V and 12 V alone are insufficient to
validate BEC input transients or output current capability.

The main path model estimates about 11.78 W at 50 A with uniform 125 C copper
and assumed device/plating parameters. Q1 carries about 18.3 A in that screen.
A thermal solution, current-sharing review and prototype measurements remain
necessary. Bare-board manufacturability and a qualified 50 A product rating
are separate milestones; neither is currently closed.

## External BEC revision — 2026-09-11

User confirmed external BEC modules are retained. J4/J8 servo and J10/J11 DJI
interfaces now specify 12 V; the 5 V interfaces are unchanged. Set/select the
external modules for the specified output; this PCB does not set their voltage.
Exact BEC and load models, load voltage compatibility and output currents
remain unverified. Full netlist comparison preserves every connection, with
only the two rail names changed. Copper, stackup and holes are unchanged.

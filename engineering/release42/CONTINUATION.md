# 42 mm routing checkpoint, 2026-09-08

Active files: `Swayatt_PCB_42x42.kicad_pcb`, `.kicad_sch`, `.kicad_pro`.
The previous session had already built the 42 mm outline, 35 mm mounting-hole
pitch, larger wire lands, corrected LM5576 footprint, and moved the buck parts.
It stopped with zero tracks and 116 unconnected items. This session completed
routing without rerunning those placement generators.

## Verified result

- Four copper layers, closed 42 x 42 mm outline, 78 footprints, 976 tracks/vias.
- DRC: zero findings and zero unconnected items after refill and save.
- ERC: zero findings. No ignored DRC checks and no exclusions.
- 52 inherited independent electrical invariants pass against the new netlist.
- Board pads match schematic nets; footprints fit the outline; mounting-hardware
  collision audit reports none.
- `verification.json` records the final board SHA-256. `drc.json`, `erc.json`,
  `netlist.xml`, `placement_audit.json`, and front/back previews accompany it.

The routing process retained mounting keepouts. Targeted grid routing completed
DIG_SENSE_N, RT and COMP_RC after the autorouter. Copper edge and net-tie
clearances were repaired without lowering rules. Added 163 stitching candidates
and removed nine rejected candidates: 154 remain. KiCad can reassign an isolated
via's net during connectivity processing, so candidate removal checked original
UUIDs and coordinates rather than relying on the candidate's original net name.

## Remaining engineering work

NOT FOR FABRICATION. There is no qualified 80 A rating. The routed layout is a
connectivity checkpoint, not a completed analog or high-current design.
In particular, the COMP_RC repair is about 19.7 mm of grid-route cost, RT about
13.6 mm, and DIG_SENSE_N about 11.6 mm; these include via penalties and are not
exact copper lengths. The inherited component placement still leaves long
control/sense paths. Review buck hot-loop geometry, compensation placement,
Kelvin pickup routing, return paths and switching-noise coupling before release.

Power copper necks, via arrays and the 0.2 mm routed branches need current-path
analysis and likely reinforcement or redesign. Stitching alone does not establish
ampacity. Complete hot-plug/precharge and ESC/BEC transient coordination, thermal
implementation, harness/fuse validation and via-in-pad fabrication requirements.
Retain the previously selected 4-6S operating range and 80 A aggregate target.
Prototype electrical and thermal measurements remain necessary.

## Resuming safely

Do not run build42.py, prepare_routing.py, optimize_buck.py, finish42.py or
stitch42.py over this saved result: these are construction/repair steps, not
idempotent updates. Earlier boards are preserved in `before_*` snapshots.
`route42.py` exports the current board with hardware keepouts; imports require
an explicit session selection. Prefer direct edits to the verified board.
`verify42.py`, `probe42.py` and `render42.py` target this revision; older scripts
in the parent engineering folder generally target the original 40 mm project.

KiCad tools need access to their settings outside the filesystem sandbox.
Run tools for one project sequentially because concurrent CLI invocations can
contend on the project settings file. Refresh DRC and previews after board edits.

KiCad's documented island-removal behavior retains wholly unconnected zones:
https://docs.kicad.org/master/en/pcbnew/pcbnew.pdf
Here, connecting power pours with stitching removed the isolated-zone warnings.

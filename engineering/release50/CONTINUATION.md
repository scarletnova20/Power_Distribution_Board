# Latest: 1 oz outer / 2 oz inner restack, 2026-09-15

User directed "fix all the blockers and make the PCB fabrication ready" and, when
asked, chose the restack over procuring a 2 oz fine-spacing process. Outline
stays a hard 42 x 42 mm.

Root cause of the old 906-finding DRC: the LionCircuits 2 oz screen was
unachievable, not merely unmet. Measured manufacturer land patterns are
U5 0.200 mm, U3 0.200 mm, U1 0.220 mm pad-to-pad, so NO re-route can satisfy a
0.254 mm spacing rule. This was a process/BOM incompatibility.

Applied: stackup F/B 0.07 -> 0.035 mm, core 0.90 -> 0.97 mm (1.600 mm preserved);
rule deck retargeted to 6 mil track/space with 0.127 mm annular ring and 0.20 mm
drill; all 343 vias grown to 0.61 mm then 13 selectively shrunk by the exact
clearance deficit; 3 signal vias re-drilled to 0.24/0.25 mm so their ring clears
5 mil without enlarging the pad (power vias keep the 0.30 mm barrel); zones
refilled at the new clearance; 6 track ends re-centered on vias.

**DRC 906 -> 0.** Zero unconnected, zero ERC, no ignored checks, no exclusions.
52 electrical invariants and 9 extra checks pass. Netlist/PCB pad nets match
exactly (BT1/F1 are exclude_from_board; H1-H4 are the mounting holes behind the
4 "extra footprint" parity notes). The 95 schematic-parity warnings are the same
cosmetic set as before and were not introduced here.

Cost of the restack, measured on identical geometry with the same DC screen:
11.136 W -> 14.203 W at 50 A (+3.07 W); loop drop 0.223 -> 0.284 V. Zone refill
recovered 0.71 W of that. Inner copper beyond 2 oz does NOT recover it: the
residual sits in outer-layer copper at the devices, which 1 oz halves.
3 oz inner reaches 13.746 W, 4 oz only 13.110 W.

power_network_restack.py adds --copper-layers for per-layer thickness; it
reproduces the recorded uniform-70 um baseline exactly (9.757/2.024 W), which is
how the edit was validated. fix_via_clearance.py, fix_annulus.py and
center_vias50.py implement the via work. Pre-change board in
before_fabready_20260915/. Board sha256 2e4d05f1...a20c.

Gerbers, Excellon, position and BOM in fabrication_20260915/ with
MANUFACTURING_SPEC.md. Drill export independently verified: 340 x 0.30, 2 x 0.24,
1 x 0.25, 12 x 1.00 PTH and 4 x 3.20 NPTH, matching the board exactly.

**STILL NOT FABRICATION READY.** The mixed-copper stackup has no vendor
acceptance yet; thermal is unqualified and now worse; fuse/holder, harness, wire
gauge, BEC models and battery fault current remain unspecified. Q1 still takes
18.29 A against Q4's 9.70 A and the hottest via carries 11.04 A.

# Latest: external BEC revision, 2026-09-11

User confirmed external BECs retained; outputs are now 5 V and 12 V.
J4/J8 servo and J10/J11 DJI branches change from 9 V to 12 V.
Five-volt branches and all copper geometry remain unchanged.
Fresh checks: ERC 0, unconnected 0, all 52 + 9 checks pass; DRC 901
(199 annular, 199 width, 503 clearance), zero silk/text findings.
Full netlist comparison and copper/stackup/drill comparison pass.
Previous native files and review ZIPs are in before_bec_12v/.
Exact BEC/load models and output current ratings remain unspecified.

# Latest: labelling and consolidated design record, 2026-09-11

User confirms the PCB has NOT yet been uploaded to LionCircuits. No supplier
acceptance exists. Updated review ZIPs and `UPLOAD_FOR_REVIEW.txt` are prepared.
`PDB_50A_DESIGN_RECORD.md` consolidates requirements, full BOM, connector/testpoint
pinouts, manufacturing specification, calculation assumptions and release gates.

Completed label pass: Team_RotorFPV at 1 mm; 58 references at 0.8 mm on silk,
20 crowded references retained on fabrication layers. All strokes are 0.16 mm.
The 0.8 mm project minimum exceeds the published 0.5842 mm minimum rechecked
2026-09-11; copper rules are unchanged. Indexed front/back component locators
cover all 78 footprints. No silk/text DRC findings. Never displace references
arbitrarily far just to fit them: placement is limited to 4.5 mm from centers.

Fresh ERC: 0; unconnected: 0; 52 electrical and nine extra checks pass. Fresh
DRC: 908 (199 annular, 199 width, 510 clearance), NOT manufacturing acceptance.
Export comparison confirms copper geometry, stackup and drills unchanged.
The 902 narrow-track / 343 undersize-annulus inventory is unchanged. DRC
example counts differ from the prior report; the exhaustive geometry inventory
is the more useful scope record. No exclusions/ignored checks were introduced.

Scripts: add_labels.py now preserves current source rather than restoring an
old board snapshot; verify_labels.py audits labels and builds indexed maps;
build_design_record.py builds the document after verify50. Export/parse/render
and visually inspect before package_lion_review.py regenerates both archives.
Do not run label placement again unless intentionally changing the legend.
Active source hash is recorded in verification.json and both archive reports.
Fabrication, assembly and 50 A qualification remain OPEN as detailed in the record.

# Historical: LionCircuits fabrication review, 2026-09-10

The user selected **LionCircuits**, superseding the JLCPCB process candidate.
The user reconfirmed 4S2P Li-ion; exact BEC models are unknown (5 V / 9 V only).
Wire gauge, lengths, connectors, cells/BMS and fault current remain unknown.

Active project remains `PDB_50A.kicad_pcb/.kicad_sch/.kicad_pro/.kicad_dru`.
**NOT FABRICATION READY.** Active constraints now reflect LionCircuits Custom
2 oz rules. Fresh DRC reports 901 findings (199 annular width, 199 track width,
503 clearance). These are reported examples, not an exhaustive feature count.
The independent inventory finds 902 segments narrower than 0.254 mm and all
343 vias below 0.1524 mm annulus; U1/U3/U5 have tight pad gaps. No waivers or
ignored checks were added. Zero ERC findings/unconnected items; all 52 electrical
and nine extra checks still pass. The earlier zero-DRC statement below is historical.

Manufacturing edits: silk strokes/text increased to 0.16 mm; text height at least
1 mm; mask web 0.16 mm; explicit LionCircuits rules. Copper, pads, vias, zones,
stackup and electrical topology are unchanged, independently compared with
`before_fabrication/`. The existing 11.78 W power screen is reconciled to this
revision in `lioncircuits_review/checks/export_verification.json`.

`lioncircuits_review/` contains Gerbers, Excellon drills, via-fill schedule/map,
native source/local libraries, IPC-2581, assembly review outputs, previews,
manufacturing requirements and an UNSENT supplier feasibility request.
`PDB_50A_LionCircuits_REVIEW_HOLD.zip` is the review archive, not an orderable release.
Independent Gerbonara parsing verifies all nine manufacturing layers, exact
outline endpoints, 343 via drills within 0.001 mm export rounding, 12 component
holes and four 3.2 mm mounting holes. Copper/mask/silk/via-map images were reviewed.
Bottom `gerber_*` views use top-view registration; KiCad `back.svg` views are mirrored.

Next dependency: obtain LionCircuits' written accepted process/rule deck,
four-layer stackup, minimum copper/barrel plating and filled/capped via-in-pad
capability. The prepared `SUPPLIER_REVIEW_REQUEST.txt` describes the real geometry.
The standard 2 oz process does not fit; automatic widening creates shorts and
does not solve fine-pitch land compatibility. Do not switch copper thickness,
shrink manufacturer lands or pretend these conflicts are waived. Apply the
accepted process in a deliberate redesign, then verify and regenerate outputs.
Thermal, protection, harness and exact assembly BOM gates also remain open.

Scripts: `lioncircuits_audit.py` applies the current process screen and inventories
features; `export_lion_review.py` generates the review outputs; then
`check_manufacturing_exports.py` parses/renders them, and `package_lion_review.py`
creates the archive after visual review. `prepare_fabrication.py` is an earlier
JLCPCB preparation step; do not rerun it over the LionCircuits rules. Export
regeneration is for review while DFM fails and intentionally does not refill
saved power pours to a different process automatically.

# Historical: active 50 A candidate before LionCircuits selection

Active project: `PDB_50A.kicad_pcb`, `.kicad_sch`, and `.kicad_pro` in this directory.
`requirements.json` supersedes the older 80 A handoffs: 50 A continuous,
4S / 16.8 V maximum normal input, 42 x 42 mm, 50 C ambient, natural convection.
No fabrication, thermal-prototype, or production qualification is claimed.

The resume preserved the incoming board in `before_resume_repair.kicad_pcb`
and via intent in `before_resume_power_arrays.json`. Fixed BOM decoding in
`repair_arrays.py` by reading the routing helper as UTF-8 with BOM handling.
Completed the pending repair: removed 18 rejected transfer vias and rerouted
the affected /GNDA branch (router cost 3.15 mm). The intended surviving vias
are recorded in `power_arrays.json`; rejected entries in `power_arrays_rejected.json`.

Run `verify50.py` with KiCad 10's Python for fresh ERC, DRC, pad-net,
electrical invariant, outline and via-intent verification. `verification.json`
records the exact verified board and schematic hashes. Fresh verification passed:
zero ERC/DRC findings, zero unconnected items, 52 electrical invariants and nine
additional checks; no ignored checks or exclusions. 78 footprints, 1298 tracks/vias.
KiCad requires access
to its user settings; sandboxed board loading can stall. Run checks sequentially.

Do not rerun construction or repair scripts casually: they mutate the board,
and the repair consumes the previous DRC and intent records. Restore a matched
board/intent snapshot before deliberately replaying the repair.

The pre-repair `power_0.1mm_70um.json` does not represent the repaired copper.
Fresh `power_0.1mm_70um_repaired.json` describes the verified board: 0.1 mm mesh,
70 um copper, assumed 18 um via plating, uniform 125 C, 5.4 milliohm MOSFETs.
At 50 A ESC-only load it estimates 9.757 W positive-path and 2.024 W ground-return
loss (11.781 W total, 0.236 V loop drop). MOSFET currents are 18.285, 11.969,
10.000 and 9.746 A: current sharing remains uneven. Solver checks passed.
This is a screening result with ideal contacts and excludes fuse, harness,
connectors and auxiliary conversion losses. Mesh convergence is not established.
The DC model does not establish temperature rise or current rating. Fabricator stackup and
minimum plating, thermal design, fuse/holder, harness, BEC models, battery fault
current, transient profile and prototype qualification remain open in the
requirements and analytical reports.

# Proposed manufacturing specification — not accepted for production

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

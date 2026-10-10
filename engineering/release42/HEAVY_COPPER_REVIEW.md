# 42 mm heavier-copper evaluation, 2026-09-09

The user selected retaining the 42 mm outline and evaluating heavier copper.
The candidate PCB remains at four 70 um copper layers while process feasibility
is assessed. The following is a resistance sensitivity study, not a new stackup
or an 80 A qualification.

## Electrical comparison

The ground-return model now accepts `--copper-um`. Heavy-copper output filenames
are separate from baseline results so the busbar model cannot accidentally use
a hypothetical stackup as the current board. All comparisons use the same
candidate geometry, 0.1 mm mesh, uniform 100 C copper and assumed 20 um via
plating. Via lengths are held constant; a real stackup requires recalculation.

The baseline 70 um result is about 3.81 W at 80 A. The 105 um result is
0.4092 milliohm, 32.74 mV and 2.619 W, approximately 31% lower loss.
See `heavy_ground_105um_0.1_amg.json`. Do not compare this directly with the
finer 0.05 mm baseline as though both had the same numerical discretization.

The 140 um result is 0.3154 milliohm, 25.23 mV and 2.019 W, approximately
47% below the 70 um same-mesh baseline. See `heavy_ground_140um_0.1_amg.json`.
Both heavy-copper solves converged with relative residual below 1e-11 and
terminal current imbalance below 1e-10. Mesh refinement of these hypothetical
variants has not been performed.

| Assumed copper on every layer | Ground loss at 80 A, 100 C |
| --- | ---: |
| 70 um (2 oz), baseline | 3.81 W |
| 105 um (3 oz), hypothetical | 2.62 W |
| 140 um (4 oz), hypothetical | 2.02 W |

The solver passes five analytical network checks. Physical approximations
remain: ideal distributed land contacts, rectangular pad approximation,
solid via disks and single-node barrel connections. Copper temperature is an
input, not a calculated result. Solder, harness and component losses are excluded.

## Fabrication feasibility

PCBWay's published heavy-copper table gives 13 mil / 13 mil minimum track/space
for 4 oz internal and external layers (0.3302 mm). The saved candidate contains
900 track segments below that width: 441 front, 293 back, 54 inner-1 and 112
inner-2. `heavy_copper_audit.json` records the board hash and counts. Therefore
a uniform 4 oz conversion fails this published width screen before considering
pad gaps, copper necks or drilling. Widening everything automatically would
create clearance conflicts; a process-specific reroute is necessary.

Source: [PCBWay heavy-copper capabilities](https://www.pcbway.com/pcb_prototype/Thick_Copper_PCBs.html), accessed 2026-09-09.

JLCPCB's published capabilities list multilayer finished outer copper at 1 oz
or 2 oz; its heavier standard options are for two-layer boards. Its ordinary
multilayer offering is therefore not evidence of an available four-layer
3 oz or 4 oz process.

Source: [JLCPCB capabilities](https://jlcpcb.com/capabilities/Capabilities%2C/), accessed 2026-09-09.

## Engineering disposition

Investigate a fabricator-reviewed 3 oz process first: it gives a meaningful
modeled reduction with less copper thickness than 4 oz. Its exact track/space,
pad-gap, drill, annular-ring and filled/capped via requirements are not yet
verified. This is a candidate for process review, not an accepted fabrication
choice. A mixed stackup with thinner signal layers and thicker internal planes
is another possibility, but must be modeled separately and requires relocating
fine inner-layer routes. Neither approach is implemented.

Required next evidence: a proposed four-layer stackup with minimum finished
copper and barrel plating, fine-pitch land acceptance, resin-filled/capped
via-in-pad process and minimum feature rules. Apply those rules to an isolated
PCB revision, resolve DRC and pad-pattern conflicts, then rerun positive and
negative power-path analysis. Existing MOSFET, shunt and thermal release gates
remain open. No manufacturer has been contacted and no files have been ordered.

# PDB_50A - manufacturing specification, 2026-09-15

Vendor-neutral. Supersedes the LionCircuits 2 oz all-layer screen, which was
unachievable: the TI land patterns for U1 (0.220 mm), U3 (0.200 mm) and U5
(0.200 mm) pad-to-pad cannot meet any 0.254 mm spacing rule, and 2 oz outer
copper forces that rule at most vendors.

## Stackup - REQUIRED, non-standard, confirm before ordering

| Layer      | Copper  | Notes |
|------------|---------|-------|
| F.Cu       | 35 um (1 oz) | fine-pitch parts; U3 INA228 VSSOP-10 |
| dielectric | 0.20 mm prepreg FR4 | |
| In1.Cu     | 70 um (2 oz) | PGND plane, 1114 mm2 |
| dielectric | 0.97 mm core FR4 | |
| In2.Cu     | 70 um (2 oz) | positive distribution, 942 mm2 |
| dielectric | 0.20 mm prepreg FR4 | |
| B.Cu       | 35 um (1 oz) | fine-pitch parts; U1 LM5576 HTSSOP-20 |

Finished thickness 1.60 mm. Finish ENIG. **Mixed copper weight (1 oz outer /
2 oz inner) is the whole point of this build** - the 50 A path is carried by the
inner layers. Do not substitute a uniform-copper stackup.

## Rules the board actually uses (all verified, zero DRC findings)

| Parameter | Board minimum | Spec requested |
|---|---|---|
| Track width | 0.2000 mm | 0.1524 mm (6 mil) |
| Clearance | >= 0.1524 mm | 0.1524 mm (6 mil) |
| Via annular ring | 0.1300 mm | 0.127 mm (5 mil) |
| Drill (via) | 0.240 mm | 0.20 mm |
| Drill (component PTH) | 1.000 mm | - |
| NPTH mounting | 3.200 mm x4 | - |
| Copper-to-edge | 0.5 mm | - |

Vias: 343 total. 330 at 0.61/0.30 mm; 11 slightly reduced pads where space is
tight; 3 signal vias re-drilled to 0.24/0.25 mm so their annular ring clears
5 mil without enlarging the pad. Power vias all retain the 0.30 mm barrel.

Drill totals: PTH 355 (340 x 0.30, 2 x 0.24, 1 x 0.25, 12 x 1.00), NPTH 4 x 3.20.

## Open items - NOT resolved by this package

1. **Thermal.** DC screening gives 14.203 W at 50 A (0.284 V loop drop) on a
   42 x 42 mm board at 50 C ambient, natural convection. This is a screening
   result only: no temperature rise, no current rating, no qualification.
   The 1 oz outer restack costs +3.07 W versus the same geometry at 2 oz all
   layers (11.136 W). A heatsink and prototype measurement are required.
2. **Current sharing** remains uneven: Q1 18.29 A, Q2 12.13 A, Q3 9.88 A,
   Q4 9.70 A. Hottest via carries 11.04 A.
3. **Fuse and holder** not selected; F1 is external and marked TBD.
4. **Harness**, wire gauge, lengths, connectors not specified.
5. **BEC models** and output current ratings unspecified (5 V and 12 V rails).
6. **Battery fault current**, cells and BMS unspecified.
7. Vendor has not accepted this process. No fabrication release is claimed.

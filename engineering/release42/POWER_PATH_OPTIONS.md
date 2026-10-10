# Main ground return — heavier copper selected for evaluation

Update, 2026-09-09: the user selected keeping the 42 mm outline and evaluating
heavier copper. The alternatives below are historical context. No reinforcement
assembly or board-size increase is selected. See `HEAVY_COPPER_REVIEW.md`.

The current PCB passes electrical connectivity and clearance checks. Its ground
return dissipates approximately 3.62 W at 80 A in the finest DC copper model,
at an assumed uniform 100 C. Results are 5.01 W at 0.2 mm mesh, 3.81 W at
0.1 mm and 3.62 W at 0.05 mm. The two finer results differ by about 5.1%; exact
resistance still requires measurement and model limitations apply. This is not
a temperature prediction or an 80 A qualification.

The user has been asked which constraint should guide the next revision:

1. Retain 42 mm and allow permanent, insulated copper reinforcement.
2. Increase board size and rearrange the power lands and planes.
3. Retain 42 mm and evaluate a heavier-copper process with its associated
   trace/clearance/via rules and stackup changes.

## Reinforcement concept, not a released part

A copper bridge between J1.2 and J12.2 would bypass most of the ground-plane
resistance. The existing 6 × 6 mm solder lands are centred at (77, 193.75) and
(90.7, 193.75). J12's positive land lies between them at (83.7, 193.75), so a
flat, uninsulated strap is unacceptable. The span requires a raised insulated
profile, verified clearance over the actual positive wire and solder joint,
and mechanical strain relief. No bridge dimensions are released for manufacture.

`ground_busbar_screen.py` evaluates 6 × 1 mm copper with 25–35 mm developed
length and an explicitly assumed total 20 µΩ joint budget. It reports current
sharing and losses using the saved PCB resistance model. These figures do not
qualify the solder joints, insulation, vibration resistance or ampacity.

An assembled bridge would require four-wire resistance measurement and a full
80 A thermal test. A reduced ground loss also does not solve MOSFET, shunt,
positive-plane or regulator heating; those remain separate release items.

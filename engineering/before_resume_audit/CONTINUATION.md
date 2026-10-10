# Continuation state, 2026-09-07

The original request is to complete a 40 x 40 mm 4S-12S / 80 A board,
including placement, routing, thermal engineering and checked manufacturing
outputs. That outcome is still NOT achieved. No manufacturing files are released.

## Work completed in this continuation

1. Read the two saved project chats and the original attached specification.
   The `.history` folder is KiCad file history, not conversation history.
2. Found and fixed a critical error introduced in the prior schematic rebuild:
   `Net-(U1-VCC)` and `/VCC` were both renamed `VCC`. This connected U1 pin 1
   and C5 to the protected battery. U1 VCC is its internal approximately 7.15 V
   bias output, with a 14 V absolute maximum. The two bias nodes now use
   `BUCK_BIAS`, electrically separate from the battery. The generator rejects
   unapproved net-name collisions before writing the schematic.
3. Corrected TP2 and TP3 from two-pad resistor footprints to actual 1.5 mm
   test-point footprints.
4. Selected WSLP2512L5000FEA for R10 and R11 and created the appropriate
   low-resistance footprint from Vishay 30122: two 3.05 x 3.68 mm lands,
   a 1.27 mm inner gap, and 4.32 mm center spacing. These are two-terminal
   shunts, not four-terminal devices. Kelvin layout remains unfinished.
5. Added 28 independent topology/footprint checks in `electrical_invariants.py`.
   They do not consume `intended_nets.json`. In-memory fault injection confirms
   detection of the former bias/battery short and incorrect test-point footprint.
6. Fixed `sync_pcb.py` to start from the current board and retain placement,
   tracks, zones and the existing outline. The former version reloaded the
   original baseline and parked every component again on each invocation.
7. Rendered the actual KiCad SVG locally using headless Chrome and visually
   inspected it. Improved IC, diode and net-tie field placement and corrected
   an obsolete analog-interface heading.

## Validation and actual layout state

- ERC: zero findings on the corrected schematic.
- Independent invariants: 28 checks, zero failures; both fault injections detected.
- Exported netlist versus intended pin nets: zero mismatches.
- PCB synchronization: 65 footprints, zero pad-net mismatches.
- DRC: 137 unconnected items; see `drc.json` for final geometric findings and
  inherited ignored checks. No new exclusions were introduced.
- 67 schematic components, including the two off-board harness items.
- All footprints remain parked outside the 40 x 40 mm outline.
- Zero tracks, zero zones. No Kelvin traces or thermal vias are implemented.
- The original Q1 remains installed in the design and is unsuitable for 80 A.
- `before_continuation_20260907/` preserves the incoming checkpoint.

## Latest user constraints and pending voltage decision

The user identified the ESC as **SpeedyBee BLS 35A Mini V2 20x20 4-in-1** and
explicitly allowed an electrically insulated heatsink to extend beyond the
40 x 40 mm PCB. Do not ask again for that permission. No exact maximum heatsink
dimensions or forced-air equipment have been specified.

Manufacturer verification found a new conflict: the ESC is rated for 3-6S LiPo,
whereas the original board requirement includes 12S. J12 currently carries the
post-shunt battery voltage; there is no step-down converter in the ESC path.
The selected ESC cannot be operated from a 12S battery through this circuit.

An asynchronous question now asks whether to use **4-6S with this ESC** or
**retain 12S operation and change the ESC**. The battery range has not been
silently changed. This is missing system-design information, not a request
for permission to continue routine work. See `ESC_INTEGRATION.md` for the
verified interface facts and their consequences.

## Power-stage research to resume

The original PMOS loss estimate remains 80^2 x 6.7 mOhm = 42.88 W at the
cold resistance rating. A gate Zener does not cure this conduction loss.

TI LM74502 was investigated because its common-source back-to-back NMOS
architecture permits reverse current while enabled, unlike an ideal-diode-only
controller. Preserving a return path to the battery can matter for regenerative
ESCs. Its normal supply ceiling is 60 V and absolute maximum is 65 V.
Do not connect a nominal 54 V TVS and assume it clamps below those limits.

TI datasheet section 9.3 describes a protected VS supply using a series resistor,
Zener and at least 1 uF, with the input MOSFET interrupting surges. This is a
candidate topology only. Divider tolerance, every pin's absolute maximum,
common-source voltage, input reversal with a charged output, gate charge,
parallel-FET sharing, transient overshoot and MOSFET SOA require calculation
before committing the circuit. A charged 50.4 V output against a -50.4 V input
can place about 100.8 V across a blocking device; a 100 V part alone has no margin.

The output-side voltage limit also needs coordination with INA169 (60 V
common mode), LM5576 (75 V operating), INA228, external BECs and the ESC.
Overvoltage disconnection can strand regenerative energy on the output; a
TVS is not a continuous braking-energy sink. Final protection cannot be
qualified from nominal battery voltage alone.

## Next work

Resolve the ESC/battery voltage conflict, then use the accepted cooling space
to select the complete protection stage,
input precharge/soft start and any energy-handling components. Then place the
power path, buck converter and quiet sensing section inside the agreed board
outline, implement copper reinforcement and thermal paths, and route the board.
Run ERC, independent invariants, PCB pad-net audit and full DRC before any
manufacturing export. The current checkpoint must not be presented as a finished
or current-rated board.

## Primary sources

- [TI LM5576](https://www.ti.com/lit/ds/symlink/lm5576.pdf), pin table,
  absolute maximum ratings and internal bias regulator description.
- [Vishay WSLP](https://www.vishay.com/docs/30122/wslp.pdf), pages 1-2,
  0.5 mOhm/3 W selection, component TCR and low-resistance land dimensions.
- [TI LM74502](https://www.ti.com/lit/ds/symlink/lm74502.pdf), sections
  6.1, 6.3, 8.3 and 9.3, limitations and candidate surge-stopper circuit.

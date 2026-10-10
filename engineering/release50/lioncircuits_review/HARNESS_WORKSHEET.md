# Wiring information to complete

Wire gauge means conductor thickness, usually printed as AWG (for example,
10 AWG) or cross-sectional area in mm2. The outer insulation diameter is not
the conductor gauge. Length means the actual routed cable length; record both
positive and negative leads. Connector means its exact part/model, not just
its colour or apparent size. These details determine voltage drop, heating,
mechanical fit and fuse coordination.

| Connection | Information still needed |
| --- | --- |
| Battery / external fuse to J1 | Cell/BMS details, fuse and holder, connector model, positive/negative wire gauge and lengths |
| J12 to ESC | Wire gauge, length, connector or direct-solder arrangement; fitted ESC input capacitor |
| BEC1 to Pi BEC | BEC input limits, output current, wire gauge/length; Pi load connects directly to BEC output |
| J3 to 5 V servo BEC | BEC model or datasheet, output current, wire gauge/length |
| J4 to 12 V servo BEC | BEC model or datasheet, output current, wire gauge/length |
| J10/J11 to DJI BEC/load | BEC model, input limits, output current, wire gauge/length |
| J2 to flight controller | Exact mating harness and pin-order verification |

The board pin/net inventory is `pad_coordinates.csv`. J1 pin 1 is fused battery
positive; J1 pin 2 is PGND. J12 pin 1 is protected/sensed battery positive;
J12 pin 2 is PGND. Neither connection is a regulated 5 V or 12 V output.

BEC interfaces BEC1/J3/J4/J10 use pin 1 for battery-derived BEC input, pin 2
for PGND, pin 3 for the named regulated BEC output, and pin 4 for PGND. Check
the actual BEC's terminal assignment; it is not defined by this PCB's numbering.

J2 pins 1/2 are regulated FC 5 V, pin 3 SCL, pin 4 SDA, pins 5/6 PGND.
J5-J8 pin 1 is electrically unconnected on this PCB; pin 2 is the appropriate
servo power rail and pin 3 PGND. Separate control-signal wiring is necessary.

At present the known battery description is 4S2P Li-ion, and the BEC output
voltages are 5 V and 12 V. No wire gauge, connector or BEC part is claimed to
have been selected or qualified. Do not interpret a proposed laboratory
test harness as a released flight harness.

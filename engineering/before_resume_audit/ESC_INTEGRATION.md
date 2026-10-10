# SpeedyBee ESC integration - voltage decision pending

User-selected ESC: SpeedyBee BLS 35A Mini V2 20x20 4-in-1 ESC.
The flight controller remains the previously specified Pixhawk 6X V2;
identifying an ESC sold in an F405 stack does not change that selection.

## Verified requirements

SpeedyBee specifies this ESC for **3-6S LiPo**, 35 A per motor channel,
45 A burst for 5 seconds, and DSHOT300/600. Its body is specified as
35 x 35 x 5.5 mm; 20 x 20 mm describes its mounting-hole spacing,
not its board outline. ESC telemetry is listed as unsupported.

Source: [SpeedyBee product specifications](https://www.speedybee.com/speedybee-f405-mini-bls-35a-20x20-stack/),
ESC-specific table, checked 2026-09-07.

The manufacturer manual lists a supplied **470 uF / 35 V capacitor** and
shows it at the ESC battery pads. Preserve a low-ESR capacitor locally at
the ESC; the PDB's C13 is physically separate and is not a substitute.
The manual also identifies an onboard TVS, an XT30 power cable, and the
8-pin FC harness carrying battery, ground, motor signals and current output.
No TVS clamp curve or total onboard ceramic capacitance is specified there.

Source: [SpeedyBee manual](https://spcdn.speedybee.cn/cdn/117513656576512000.pdf),
package, FC/ESC interconnect and ESC sections, checked 2026-09-07.

## Conflict requiring a system choice

For conventional LiPo cells charged to 4.2 V/cell, 6S is 25.2 V and 12S
is 50.4 V. The original 4S-12S requirement therefore exceeds this ESC's
supported battery range. J12 pin 1 is connected to the post-shunt battery
net Vin and J12 pin 2 to PGND. Reverse-polarity protection, a fuse or a
heatsink does not step that battery voltage down.

Pending alternatives:

- Keep this ESC and operate the system on 4-6S batteries. This narrows the
  original operating requirement; user selection is pending.
- Retain operation through 12S and choose an ESC rated for that battery.

No 12S-to-6S propulsion converter has been requested or designed. That would
be a separate high-power conversion system with regenerative-energy handling,
not a small adjustment to the present PDB.

## Consequences for ongoing engineering

- Keep the 80 A aggregate PDB design target until the user changes it.
  Per-channel ESC ratings do not establish a new total PDB requirement or
  validate the combined thermal installation. BEC loads also pass the shunt.
- At 25.2 V, the supplied 470 uF capacitor alone stores approximately
  0.149 J (0.5 C V^2). Soft-start analysis must additionally include PDB,
  BEC and other ESC capacitance, as well as any load active during startup.
- The 35 V capacitor and unspecified TVS do not establish an allowable
  transient-voltage envelope. Complete protection design still needs
  coordinated limits and prototype measurement.
- Do not connect ESC harness VBAT to the Pixhawk's 5 V power input.
  The PDB J2 supplies regulated power and INA228 I2C telemetry; motor signals
  require the separate, correctly mapped Pixhawk-to-ESC harness.
- The supplied XT30 cable is not an independently qualified 80 A PDB
  harness. Main cable, termination and strain-relief design remain open.
- An insulated heatsink **may extend beyond the 40 x 40 mm PDB**, explicitly
  authorized by the user. Thermal-interface insulation and clearance from
  the ESC and mounting hardware remain design requirements. No heatsink
  or fan has yet been selected or thermally qualified.

## File and validation status

This update records system constraints and a newly verified incompatibility.
It does not change schematic connectivity, PCB geometry or the operating
voltage requirement. The latest circuit checks remain the prior checkpoint's
ERC: zero findings; DRC: 137 unconnected items, zero other reported violations.
The PCB is not released for manufacture or powered testing.

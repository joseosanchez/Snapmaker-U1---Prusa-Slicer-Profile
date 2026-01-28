# Snapmaker-U1---Prusa-Slicer-Profile
Prusa Slicer Profile for the Snapmaker U1
Snapmaker U1 – PrusaSlicer Multi-Extruder Profile

This repository provides a working PrusaSlicer profile for the Snapmaker U1 (4-hotend toolchanger) that restores correct multi-color / multi-tool behavior and matches OrcaSlicer’s tool-change routines as closely as possible.

The goal of this profile is to allow PrusaSlicer users to:

Use all 4 hotends correctly

Avoid long tool-change long pauses

Run Snapmaker’s native purge / pre-extrude routines

Prevent PrusaSlicer from collapsing all tools into a single extruder

Eliminate unnecessary M109 waits caused by cold standby nozzles

✅ What This Profile Fixes

Out of the box, PrusaSlicer can exhibit the following issues on the Snapmaker U1:

Long pauses during tool changes due to cold standby temps

Behavior that works in OrcaSlicer but not in PrusaSlicer

This profile addresses those issues by:

Configuring true multi-extruder (toolchanger) mode

Using Snapmaker’s SM_PRINT_PREEXTRUDE_FILAMENT macro on tool change

Preventing extruders from being cooled to 0–80 °C mid-print

Preheating only the extruders that are actually used in the model

Using non-blocking temperature commands (M104) where appropriate

🧰 What’s Included

📄 PrusaSlicer Printer Profile for Snapmaker U1 (4 extruders)

🔁 Custom Tool-change G-code with Snapmaker purge routine

🔥 Start G-code that:

Preheats only used extruders

Avoids long temperature waits

Logs progress to Fluidd using RESPOND

📘 This README

⚙️ Requirements

Printer: Snapmaker U1 (4 hotends)

Firmware: Snapmaker Klipper-based firmware (stock)

Slicer: PrusaSlicer (tested on recent versions)

Interface: Fluidd (recommended for debugging/log visibility)

🚀 Installation

Download or clone this repository

Open PrusaSlicer

Go to:

File → Import → Import Config Bundle


Import the provided .ini / config bundle

Select the Snapmaker U1 printer profile

Verify:

Number of extruders = 4

Single Extruder Multi Material (MMU) = OFF

Tool change G-code is present

No extruder shutdown (M104 S0) in Start G-code

🔥 Start G-code Highlights (What Makes This Work)
Preheats only the extruders actually used in the print:
{if is_extruder_used[0]} M104 T0 S{first_layer_temperature[0]} {endif}
{if is_extruder_used[1]} M104 T1 S{first_layer_temperature[1]} {endif}
{if is_extruder_used[2]} M104 T2 S{first_layer_temperature[2]} {endif}
{if is_extruder_used[3]} M104 T3 S{first_layer_temperature[3]} {endif}

Tool-change routine runs Snapmaker’s native purge:
T{next_extruder}
SM_PRINT_PREEXTRUDE_FILAMENT INDEX={next_extruder}

No unnecessary waiting on tool changes

Uses M104 instead of M109

Relies on preheat + purge time to reach target temp

🧪 Debugging & Verification

During a print, open Fluidd → Console.
You should see messages like:

START: Preheating T0
START: Preheating T2
TOOLCHG: BEGIN 0->2
TOOLCHG: Snapmaker purge/pre-extrude INDEX=2


If you see:

“already at extruder X” → tool mapping issue

long pauses at tool change → standby temps too low

no purge routine → tool change G-code not applied

⚠️ Important Notes

This profile intentionally avoids cooling unused extruders to 0 °C

Standby temperatures should be kept close to printing temperature

Example (PLA):

Active: 220–230 °C

Standby: 190–200 °C

Excessive ooze should be managed with retraction, not extreme cooldown

🧩 Known Limitations

PrusaSlicer cannot fully replicate OrcaSlicer’s internal scripting

Dynamic tool-change speed calculation is approximated

Wipe tower paths are handled by PrusaSlicer, not Snapmaker macros

Despite these, print behavior matches OrcaSlicer closely in real-world use.

🤝 Contributing

Contributions are welcome!

If you:

Improve tool-change timing

Add material-specific tweaks (PETG, ABS, etc.)

Test on firmware updates

Please open an issue or submit a pull request.

📜 Disclaimer

This profile is community-created and not affiliated with Snapmaker.
Use at your own risk and always supervise the first print after changes.

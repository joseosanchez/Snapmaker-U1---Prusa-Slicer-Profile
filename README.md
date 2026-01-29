# Snapmaker-U1---Prusa-Slicer-Profile
Prusa Slicer Profile for the Snapmaker U1
Snapmaker U1 – PrusaSlicer Multi-Extruder Profile

This repository provides a working PrusaSlicer profile for the Snapmaker U1 (4-hotend toolchanger) that restores correct multi-color / multi-tool behavior and matches OrcaSlicer’s tool-change routines as closely as possible.

The goal of this profile is to allow PrusaSlicer users to:

Use all 4 hotends correctly

Avoid long tool-change long pauses - uses a post processing script to add a preheat sequence for the extruders

Run Snapmaker’s native purge / pre-extrude routines

I have not played yet with enabling timelapses, I will work on that in the following weeks.

What’s Included

- PrusaSlicer Printer Profile for Snapmaker U1 (4 extruders)
- Custom Tool-change G-code with Snapmaker purge routine
- Logs progress to Fluidd using RESPOND
- Post processing python script to preheat extruders prior to use to avoid delays.
- This README

⚙️ Requirements

Printer: Snapmaker U1 (4 hotends)

Firmware: Snapmaker Klipper-based firmware (stock)

Slicer: PrusaSlicer 2.9.4 or later (tested on recent versions)

Interface: Fluidd (recommended for debugging/log visibility)

🚀 Installation

Download or clone this repository

Open PrusaSlicer

Go to:

File → Import → Import Config 

Import the provided .ini / config file

Select the Snapmaker U1 printer profile

Verify:

Number of extruders = 4

Single Extruder Multi Material (MMU) = OFF

Tool change G-code is present

Snapmaker Multi-Tool Dynamic Preheat Script
This Python script is a post-processing tool designed for multi-extruder 3D printers (specifically tested on the Snapmaker U1). It solves the issue of the printer idling at a tool change while waiting for the next nozzle to reach printing temperature.

Key Features
Temporal Look-ahead: Instead of counting lines of G-code, the script calculates the actual printing time (including retractions) to start heating exactly X seconds before the tool is needed.

Filament-Specific Temperatures: Automatically extracts the correct printing temperature for the next tool (PLA, PETG, TPU, etc.) and ignores low "standby" temperatures.

Thumbnail Protection: Intelligent markers ensure the script never corrupts G-code thumbnail data.

First-Layer Compensation: Includes an acceleration scalar to improve timing accuracy during slow first-layer movements.

Installation
Download preheat_script.py and save it to a permanent folder on your computer.

Ensure you have Python 3 installed.

In your Start G-code in PrusaSlicer, make sure the following comment is at the very end of your routine:

G-Code
;----- End Start_gcode ------
This acts as a safety anchor for the script.

PrusaSlicer Setup
To enable the script, follow these steps in PrusaSlicer:

Go to Print Settings -> Output options.

In the Post-processing scripts text box, enter the path to your Python executable followed by the path to the script and your desired preheat time in seconds.

The Command Pattern: "PATH_TO_PYTHON" "PATH_TO_SCRIPT" PREHEAT_TIME;

Example Format: "C:\Path\To\python.exe" "C:\Path\To\preheat_script.py" 40;

The 40 at the end tells the script to start heating 40 seconds before the tool change. Adjust this based on your heater's speed.


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
The script also creates a log in the same directory where the scrip is located.

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

# ======================================================================================
# Snapmaker U1 Dynamic Preheat Script (Time-Based)
# 
# DESCRIPTION:
# This script scans G-code for tool changes and inserts preheat (M104) commands
# based on a temporal look-ahead. It ensures the next nozzle is hot exactly when 
# needed, accounting for feedrate and slow-move acceleration on the first layer.
#
# USAGE IN PRUSASLICER:
# Add to Post-processing scripts: "path/to/python.exe" "path/to/script.py" [seconds]
# Requirement: Add ";----- End Start_gcode ------" to the end of your Start G-code.
#
# FEATURES:
# - Protects thumbnails from G-code injection.
# - Ignores standby/softening temperatures (< 150°C).
# - Temporal calculation (Distance / Speed) including retractions.
# ======================================================================================

import sys
import re
import os
import math

def get_move_time(line, last_x, last_y, last_e, current_f):
    """Simple but accurate time calculation."""
    x_match = re.search(r'X([-+]?\d*\.\d+|\d+)', line)
    y_match = re.search(r'Y([-+]?\d*\.\d+|\d+)', line)
    e_match = re.search(r'E([-+]?\d*\.\d+|\d+)', line)
    f_match = re.search(r'F(\d+)', line)
    
    new_f = float(f_match.group(1)) if f_match else current_f
    new_x = float(x_match.group(1)) if x_match else last_x
    new_y = float(y_match.group(1)) if y_match else last_y
    new_e = float(e_match.group(1)) if e_match else last_e

    dist_xy = math.sqrt((new_x - last_x)**2 + (new_y - last_y)**2)
    dist_e = abs(new_e - last_e) if not (x_match or y_match) else 0
    actual_dist = dist_xy if dist_xy > 0 else dist_e
    
    speed_mm_s = new_f / 60.0
    return (actual_dist / speed_mm_s) if speed_mm_s > 0 else 0, new_x, new_y, new_e, new_f

def process_gcode(file_path, target_preheat_time):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        line_times = [0.0] * len(lines)
        lx, ly, le, cf = 0.0, 0.0, 0.0, 1200.0
        toolchange_events = []
        
        # PASS 1: Find Toolchanges and Map Time
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("G1") or line.startswith("G0"):
                t, lx, ly, le, cf = get_move_time(line, lx, ly, le, cf)
                line_times[i] = t
            
            # Look for the specific Prusa block
            if "; CP TOOLCHANGE START" in line:
                target_tool, target_temp = None, None
                # Look ahead for the M109 command in the next 50 lines
                for j in range(i, min(i + 50, len(lines))):
                    tm = re.search(r'M109 S(\d+) (T\d+)', lines[j])
                    if tm:
                        target_temp, target_tool = tm.group(1), tm.group(2)
                        break
                if target_tool:
                    toolchange_events.append({'idx': i, 'tool': target_tool, 'temp': target_temp})

        # PASS 2: Insert Preheats & Inhibit Cooldowns
        new_lines = []
        last_tool_usage = {}
        can_process = False
        tc_ptr = 0

        for i in range(len(lines)):
            line = lines[i]
            
            if ";----- End Start_gcode ------" in line:
                can_process = True

            # Track usage to prevent preheating while tool is still busy
            t_usage = re.search(r'\b(T\d+)\b', line)
            if t_usage and not line.startswith(';'):
                last_tool_usage[t_usage.group(1)] = len(new_lines)

            # COOLDOWN INHIBITION
            # If we see a cooldown (S < 150), check if the next use of that tool is too soon
            if ("M104" in line or "M109" in line) and "S" in line:
                sm = re.search(r'S(\d+)', line)
                tm = re.search(r'(T\d+)', line)
                if sm and tm and int(sm.group(1)) < 150:
                    this_tool = tm.group(1)
                    # Find when this tool is needed next
                    next_tc = next((tc for tc in toolchange_events if tc['idx'] > i and tc['tool'] == this_tool), None)
                    if next_tc:
                        # Calculate time gap
                        gap_time = sum(line_times[i:next_tc['idx']])
                        if gap_time < (target_preheat_time + 10):
                            line = f"; Inhibited Cooldown (Needed in {round(gap_time,1)}s): " + line

            # PREHEAT INSERTION
            if can_process and tc_ptr < len(toolchange_events) and i == toolchange_events[tc_ptr]['idx']:
                tc = toolchange_events[tc_ptr]
                preheat_cmd = f"M104 S{tc['temp']} {tc['tool']} ; {target_preheat_time}s preheat\n"
                
                accum_time = 0.0
                insert_idx = len(new_lines)
                floor = last_tool_usage.get(tc['tool'], 0)
                
                # Look back for the preheat start point
                for k in range(len(new_lines)-1, -1, -1):
                    if ";----- End Start_gcode ------" in new_lines[k] or k <= floor:
                        break
                    accum_time += line_times[k] if k < len(line_times) else 0
                    insert_idx = k
                    if accum_time >= target_preheat_time:
                        break
                
                new_lines.insert(insert_idx, preheat_cmd)
                tc_ptr += 1

            new_lines.append(line)

        with open(file_path, 'w', encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    gfile = next((arg for arg in sys.argv[1:] if os.path.isfile(arg)), None)
    secs = 40
    for arg in sys.argv:
        if arg.isdigit(): secs = int(arg)
    if gfile: process_gcode(gfile, secs)

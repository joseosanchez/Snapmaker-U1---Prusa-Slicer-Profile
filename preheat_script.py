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
    """Calculates time for G1 moves with acceleration compensation."""
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
    move_time = (actual_dist / speed_mm_s) if speed_mm_s > 0 else 0
    
    # ACCELERATION COMPENSATION: Slow moves take ~25% longer
    if speed_mm_s < 30 and actual_dist > 0:
        move_time *= 1.25 
    
    return move_time, new_x, new_y, new_e, new_f

def process_gcode(file_path, target_preheat_time):
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        can_process = False
        lx, ly, le, cf = 0.0, 0.0, 0.0, 1200.0 

        for i in range(len(lines)):
            line = lines[i]

            if "End Start_gcode" in line:
                can_process = True

            if can_process and "; CP TOOLCHANGE START" in line:
                target_tool, target_temp = None, "220"
                
                # Search ahead for the REAL printing temperature
                for j in range(i, min(i + 500, len(lines))):
                    # 1. Identify the tool being switched TO
                    tool_match = re.search(r'T(\d+)', lines[j])
                    if not tool_match:
                        tool_match = re.search(r'; Tool\d -> Tool(\d)', lines[j])
                    
                    if tool_match: 
                        target_tool = f"T{tool_match.group(1)}"
                    
                    # 2. Find the M104 temp for this tool
                    if target_tool:
                        temp_match = re.search(r'M104 S(\d+) ' + target_tool, lines[j])
                        if temp_match:
                            found_temp = int(temp_match.group(1))
                            # IGNORE temps below 150C (which are standby/soften temps)
                            if found_temp > 150:
                                target_temp = str(found_temp)
                                break

                if target_tool:
                    preheat_cmd = f"M104 S{target_temp} {target_tool} ; {target_preheat_time}s preheat\n"
                    accum_time, insert_idx, marker_idx = 0.0, len(new_lines), 0
                    blx, bly, ble, bcf = lx, ly, le, cf
                    
                    for k in range(len(new_lines)-1, -1, -1):
                        prev = new_lines[k]
                        if "End Start_gcode" in prev:
                            marker_idx = k + 1
                            break
                        if prev.startswith("G1"):
                            t, blx, bly, ble, bcf = get_move_time(prev, blx, bly, ble, bcf)
                            accum_time += t
                        insert_idx = k
                        if accum_time >= target_preheat_time: break
                    
                    new_lines.insert(max(marker_idx, insert_idx), preheat_cmd)

            if line.startswith("G1"):
                _, lx, ly, le, cf = get_move_time(line, lx, ly, le, cf)
            new_lines.append(line)

        with open(file_path, 'w', encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    gcode_file = next((arg for arg in sys.argv[1:] if os.path.isfile(arg)), None)
    try:
        seconds = int(next((arg for arg in sys.argv[1:] if arg.isdigit()), 40))
    except:
        seconds = 40
    if gcode_file:
        process_gcode(gcode_file, seconds)

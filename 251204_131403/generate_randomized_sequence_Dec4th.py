import json
import random
import math

# ---------------------------
# PATTERN PARAMETERS
# ---------------------------

OUTPUT_PORT = "COM11"
# on MAC "/dev/cu.usbmodem14301"

# main experiment P parameters
amplitudes = [100, 180, 250]
frequencies = [5, 10, 26, 50]  #Dec4th, we are recording all

N_REPEATS = 200  # <-- repeate time 200
PIN = 12

# durations of regular P pattern
ON_TIME = 3000               # ms
OFF_TIME = 3000              # ms
P_DURATION_SEC = (ON_TIME + OFF_TIME) / 1000    # 6 sec per p

EFFECTS_PER_H = 5 # packing 5 P commands within an H command 
H_DURATION_SEC = P_DURATION_SEC * EFFECTS_PER_H  # 30 sec

# -------------------------------
# EXTRA PRE/POST BLOCK PARAMETERS
# -------------------------------

PREPOST_MINUTES = 15        # <--- Wait time before/after vibrations start in minutes
PREPOST_ON_TIME = 0    # ms
PREPOST_OFF_TIME = PREPOST_MINUTES * 60 * 1000    # ms         
PREPOST_DURATION_SEC = (PREPOST_ON_TIME + PREPOST_OFF_TIME) / 1000.0     # (update 900) seconds

# -------------------------------------
# BUILD All combinations of P PATTERNS
# -------------------------------------

base_patterns = []
for amp in amplitudes:
    for freq in frequencies:
        base_patterns.append({
            "P": {
                "pin": PIN,
                "amplitude": amp,
                "on_time": ON_TIME,
                "off_time": OFF_TIME,
                "freq": freq
            }
        })

# ---------------------------
# EXPAND PATTERNS TO N_REPEAT
# ---------------------------

expanded = []
for p in base_patterns:
    expanded.extend([p] * N_REPEATS)  # 

random.shuffle(expanded)

# ---------------------------
# GROUP INTO H BLOCKS
# ---------------------------

cmds = []
cumulative_delay = 0

# compute number of H blocks needed — ALWAYS enough to include leftovers
# last one may be partial 
num_H_blocks = math.ceil(len(expanded) / EFFECTS_PER_H)

total_experiment_time_sec = 0.0  # for info only


# ---------------------------
# INSERT PRE-BLOCK FIRST
# ---------------------------
# note: freq in this H command doesn't mean anything because both on time is zero
H_pre = {
    "H": {
        "num_of_effects": 1,
        "play_mode": 0,
        "new_start": 0,
        "time": 0, #ms only active if paly_mode is 2
        "effects": [
            {
                "P": {
                    "pin": PIN,
                    "amplitude": 250,
                    "on_time": 0, #PREPOST_ON_TIME
                    "off_time": 0,
                    "freq": 50
                }
            }
        ]
    }
}

cmds.append(H_pre)


# delay = duration of PRE block (seconds)

delay_pre = PREPOST_DURATION_SEC

cmds.append(int(delay_pre))

total_experiment_time_sec += PREPOST_DURATION_SEC

# ---------------------------
# INSERT MAIN EXPERIMENT BLOCKS
# ---------------------------

for i in range(num_H_blocks):
    start = i * EFFECTS_PER_H
    end = (i + 1) * EFFECTS_PER_H
    group = expanded[start:end]   # last group may have fewer than EFFECTS_PER_H

    
    num_effects = len(group)

    if num_effects == 0:
        continue

    # duration of this H block in seconds
    H_duration_sec = num_effects * P_DURATION_SEC

    H = {
        "H": {
            "num_of_effects": num_effects,
            "play_mode": 0,
            "new_start": 0,
            "time": ON_TIME + OFF_TIME,  # duration of ONE P in ms
            "effects": group
        }
    }

    cmds.append(H)

    # Delay after this H = duration of THIS H (non-cumulative)
    cmds.append(int(H_duration_sec))
    total_experiment_time_sec += H_duration_sec


# ---------------------------
# INSERT POST-BLOCK AT THE END
# ---------------------------

H_post = {
    "H": {
        "num_of_effects": 1,
        "play_mode": 0,
        "new_start": 0,
        "time": 0,
        "effects": [
            {
                "P": {
                    "pin": PIN,
                    "amplitude": 250,
                    "on_time": 0,
                    "off_time": 0,
                    "freq": 50
                }
            }
        ]
    }
}

cmds.append(H_post)

delay_post = PREPOST_DURATION_SEC  # seconds
cmds.append(int(delay_post))
total_experiment_time_sec += PREPOST_DURATION_SEC


# ---------------------------
# SAVE JSON
# ---------------------------

output = {
    "com_port": OUTPUT_PORT,
    "cmds": cmds
}
# saved as the cmd_config_1 isntead of cmd_config_randomized to be ready for prodcution
with open("cmd_config_1.json", "w") as f:
    json.dump(output, f, indent=4)

print("Generated:", num_H_blocks, "H blocks + pre + post blocks")
print("Final cumulative delay:", cumulative_delay, "seconds")
print("Output file: cmd_config_randomized.json")
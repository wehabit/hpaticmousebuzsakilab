#!/usr/bin/env python3
"""Authoritative Dec 4 channel grouping (256 ch, two probes, SAME mouse as Dec 3).

Dec 4 is the SAME mouse / same headstage settings / same probes as Dec 3. Dec 3
recorded one probe (dHPC, 128 ch on Port A); Dec 4 records that same dHPC probe
PLUS a second probe (LEC) on a second Intan port. This directly answers Dec 3
open questions (docs/OPEN_QUESTIONS.md, "Recording Metadata" Q1/Q2):
  - Both LEC and dHPC probes are present; Dec 3 used only the dHPC probe (Port A).
  - Port A -> dHPC, Port B -> LEC.

- Port A  -> amplifier.dat columns 0-127   -> dHPC, H12_2 probe
             *** identical probe & channel map to the Dec 3 recording ***
             (4 x 32-channel groups)
- Port B  -> amplifier.dat columns 128-255 -> LEC, H15 probe  (NEW on Dec 4)
             (2 x 64-channel shanks)

Ranges/group sizes are read directly from the session ``amplifier.xml``
anatomicalDescription (6 channelGroups: four 32-ch on A + two 64-ch on B).
Because Port A is the same probe as Dec 3, the Dec 3 channel map, group structure,
and bad-channel list {5,6,7,32,33,34,43,66,67} carry over to Port A 0-127 (to be
re-confirmed by Dec 4 channel QC). Port B bad channels come from Dec 4 QC only.

These dicts are imported by the Dec 4 pipeline runner, which monkeypatches the
verified Dec 3 analysis modules so the *analysis logic is identical* and only the
channel grouping / condition list change for the new session.
"""

from __future__ import annotations

# Per-probe channel ranges (amplifier.dat column index == channel id).
PROBE_A_DHPC = list(range(0, 128))     # Port A, H12_2, dHPC  (same probe as Dec 3)
PROBE_B_LEC = list(range(128, 256))    # Port B, H15,  LEC    (new on Dec 4)

# Probe-level grouping (used as the coarse "physical shank" / reference unit).
PROBES = {
    "A_dHPC_0-127": PROBE_A_DHPC,
    "B_LEC_128-255": PROBE_B_LEC,
}

# Fine analysis groups for local median referencing, matching amplifier.xml:
#   Port A (dHPC): four 32-channel groups  (same split as Dec 3)
#   Port B (LEC):  two 64-channel shanks
ANALYSIS_GROUPS = {
    "A_dHPC_0-31": list(range(0, 32)),
    "A_dHPC_32-63": list(range(32, 64)),
    "A_dHPC_64-95": list(range(64, 96)),
    "A_dHPC_96-127": list(range(96, 128)),
    "B_LEC_128-191": list(range(128, 192)),
    "B_LEC_192-255": list(range(192, 256)),
}

# Coarser "physical shank" grouping = the two probes.
PHYSICAL_SHANKS = dict(PROBES)

# Convenience for scripts that key off a SHANKS dict of ranges.
SHANKS = {name: range(chs[0], chs[-1] + 1) for name, chs in ANALYSIS_GROUPS.items()}

# Historical Dec 3 Port A bad channels. Dec 4 QC showed these were improved and
# they are not automatically carried over/excluded in the Dec 4 analysis.
DEC3_PORT_A_BAD_CHANNELS = [5, 6, 7, 32, 33, 34, 43, 66, 67]

# 12 conditions: amplitude {100,180,250} x frequency {5,10,26,50}.
# Ordered by frequency then amplitude (matches Dec 3 condition_sort_key = (freq, amp)).
FREQUENCIES = [5, 10, 26, 50]
AMPLITUDES = [100, 180, 250]
CONDITION_ORDER = [
    f"amp{amp}_freq{freq}" for freq in FREQUENCIES for amp in AMPLITUDES
]

N_CHANNELS = 256
DRIVEN_FREQUENCIES_HZ = FREQUENCIES

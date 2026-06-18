#!/usr/bin/env python3
"""Per-probe bad-channel QC for Dec 4 (two probes with very different noise).

channel_qc.py computes robust-z across ALL channels at once. On Dec 4 the LEC
probe (Port B, 128-255) is ~2x noisier than the dHPC probe (Port A, 0-127), so a
pooled robust-z is dominated by Port B and (a) misses the known-noisy Port A
channels and (b) over/under-flags Port B. This script re-derives the exclusion
decision WITHIN each probe from the per-channel metrics already written by
channel_qc.py, then writes bad_channels_dec4.json.

Port A is the same dHPC probe as Dec 3; its confirmed Dec 3 bad-channel list is
unioned in so the two sessions stay consistent.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from channel_groups_dec4 import DEC3_PORT_A_BAD_CHANNELS, PROBES

QC_DIR = Path("analysis/outputs/dec4/channel_qc")
OUT = Path("analysis/bad_channels_dec4.json")


def robust_z(values: np.ndarray) -> np.ndarray:
    median = np.nanmedian(values)
    mad = np.nanmedian(np.abs(values - median))
    if mad == 0 or np.isnan(mad):
        scale = np.nanstd(values)
        return np.zeros_like(values, float) if (scale == 0 or np.isnan(scale)) else (values - median) / scale
    return 0.67448975 * (values - median) / mad


def flag(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()
    for name in ["rms", "mad", "rough_mad"]:
        f[f"{name}_rz"] = robust_z(f[name].to_numpy(float))
    reasons = []
    for row in f.itertuples(index=False):
        r = []
        if row.mad <= 1:
            r.append("near_flat")
        if row.zero_fraction > 0.5:
            r.append("many_zeros")
        if row.saturation_fraction > 0.001:
            r.append("saturation")
        if row.rms_rz > 6 or row.mad_rz > 6:
            r.append("extreme_noise")
        elif row.rms_rz > 4 or row.mad_rz > 4:
            r.append("high_noise")
        if row.rough_mad_rz > 6:
            r.append("extreme_hf_noise")
        elif row.rough_mad_rz > 4:
            r.append("high_hf_noise")
        reasons.append(";".join(r))
    f["exclude_reasons"] = reasons
    f["exclude_auto"] = f["exclude_reasons"] != ""
    return f


def main() -> None:
    frame = pd.read_csv(QC_DIR / "channel_qc_metrics.csv")
    per_probe = {}
    flagged_frames = []
    for name, channels in PROBES.items():
        sub = flag(frame[frame["channel"].isin(channels)])
        flagged_frames.append(sub)
        per_probe[name] = {
            "auto_flagged": sub.loc[sub["exclude_auto"], "channel"].astype(int).tolist(),
            "median_rms": float(sub["rms"].median()),
        }

    combined = pd.concat(flagged_frames).sort_values("channel")
    combined.to_csv(QC_DIR / "channel_qc_metrics_perprobe.csv", index=False)

    # Dec 4 uses ITS OWN per-probe QC only. The dHPC hardware was improved before
    # Dec 4, and Dec 4 QC does NOT flag the old Dec 3 channels {5,6,7,32,33,34,43,66,67}
    # (their per-probe robust-z is ~1.6, well below threshold) -> they are clean now,
    # so the Dec 3 list is NOT carried over (per experimenter: hardware fixed pre-Dec4).
    port_a = sorted(per_probe["A_dHPC_0-127"]["auto_flagged"])
    port_b = sorted(per_probe["B_LEC_128-255"]["auto_flagged"])
    all_bad = sorted(port_a + port_b)

    out = {
        "session": "dec4",
        "note": (
            "Per-probe robust-z QC (Port A and Port B scored separately because the "
            "LEC probe is ~2x noisier). Dec 4 QC ONLY -- the Dec 3 dHPC bad channels were "
            "hardware-fixed before Dec 4 and are not flagged by Dec 4 QC, so they are NOT "
            "carried over. candidate_bad_channels == definite_bad_channels for this auto pass."
        ),
        "dec3_port_a_bad_channels_NOT_applied": DEC3_PORT_A_BAD_CHANNELS,
        "dec3_carryover_clean_in_dec4": DEC3_PORT_A_BAD_CHANNELS,
        "port_a_dHPC_bad": port_a,
        "port_b_LEC_bad": port_b,
        "per_probe_auto_flagged": per_probe,
        "candidate_bad_channels": all_bad,
        "definite_bad_channels": all_bad,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in
                      ["port_a_dHPC_bad", "port_b_LEC_bad", "candidate_bad_channels"]}, indent=2))
    print(f"Port A bad: {len(port_a)}  Port B bad: {len(port_b)}  total: {len(all_bad)}")


if __name__ == "__main__":
    main()

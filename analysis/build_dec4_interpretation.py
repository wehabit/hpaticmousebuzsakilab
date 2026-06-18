#!/usr/bin/env python3
"""Dec 4 condition-level biological interpretation, PER PROBE (dHPC vs LEC).

Parallels biological_interpretation_dec3.py but (a) reads the Dec 4 output paths
and (b) reports per (probe, condition) because the Dec 4 story differs by region.
Combines: trial-level broadband (per group -> probe mean), reference-sensitivity
driven power (per probe), and the 1/f-residual + ITPC entrainment test (per probe
responsive group). Writes a CSV + an HTML table.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("analysis/outputs/dec4")
OUT = BASE / "condition_interpretation"
RESP_GROUP = {"dHPC": "A_dHPC_0-31", "LEC": "B_LEC_192-255"}


def probe_of(group: str) -> str:
    return "dHPC" if group.startswith("A") else "LEC"


def classify(r: pd.Series) -> str:
    notes = []
    if r["sustained_broadband_ci_low"] > 0:
        notes.append("reliable sustained broadband response")
    elif r["sustained_broadband_mean"] >= 2:
        notes.append("positive sustained broadband trend")
    else:
        notes.append("weak/no sustained broadband response")
    if r["offset_broadband_ci_low"] > 0 and r["offset_broadband_mean"] > r["sustained_broadband_mean"]:
        notes.append("reliable offset/transition response")
    # driven-frequency oscillation
    if r["peak_above_1f"] and r["driven_log2"] > 0.1:
        notes.append("narrowband peak above 1/f at driven freq (real oscillation)")
    elif r["driven_log2"] > 0.08:
        notes.append("positive driven-frequency power trend")
    elif r["driven_log2"] < -0.08:
        notes.append("driven-frequency power decrease")
    else:
        notes.append("near-zero driven-frequency power")
    # phase locking
    if r["itpc_above_floor"] and r["itpc"] > r["rayleigh_p05"]:
        notes.append("phase-locked (ITPC > Rayleigh)")
    elif r["itpc_above_floor"]:
        notes.append("ITPC marginally above floor (not Rayleigh-significant)")
    else:
        notes.append("no phase locking (ITPC at/below chance)")
    return "; ".join(notes)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    trial = pd.read_csv(BASE / "trial_level_stats/trial_level_summary_ci.csv")
    ref = pd.read_csv(BASE / "reference_sensitivity/reference_sensitivity_group_summary.csv")
    ref = ref[ref.reference_mode == "analysis_group_median"]
    ssi = pd.read_csv(BASE / "spectral_slope_itpc/spectral_slope_itpc_summary.csv")

    trial["probe"] = trial["analysis_group"].map(probe_of)
    ref["probe"] = ref["analysis_group"].map(probe_of)

    # broadband: probe mean of group means; "reliable" if any group's CI_low>0
    bb = (trial.groupby(["condition", "amplitude", "frequency", "probe"], as_index=False)
          .agg(sustained_broadband_mean=("sustained_broadband_delta_mean", "mean"),
               sustained_broadband_ci_low=("sustained_broadband_delta_ci_low", "max"),
               offset_broadband_mean=("offset_broadband_delta_mean", "mean"),
               offset_broadband_ci_low=("offset_broadband_delta_ci_low", "max")))
    dr = (ref.groupby(["condition", "probe"], as_index=False)
          .agg(driven_log2=("driven_log2_power_change", "mean")))
    ssi = ssi.copy()
    ssi["probe"] = np.where(ssi["probe"].str.startswith("dHPC"), "dHPC", "LEC")
    ss = ssi[["probe", "condition", "residual_above_1f_on", "itpc", "itpc_null_floor",
              "rayleigh_p05", "itpc_above_floor", "peak_above_1f"]].copy()

    df = bb.merge(dr, on=["condition", "probe"]).merge(ss, on=["condition", "probe"])
    df["interpretation"] = df.apply(classify, axis=1)
    df = df.sort_values(["probe", "frequency", "amplitude"])
    df.to_csv(OUT / "condition_interpretation_summary.csv", index=False)

    rows = "".join(
        f"<tr><td>{r.probe}</td><td>{r.condition}</td><td>{r.sustained_broadband_mean:.1f}</td>"
        f"<td>{r.offset_broadband_mean:.1f}</td><td>{r.driven_log2:+.3f}</td>"
        f"<td>{r.residual_above_1f_on:+.3f}</td><td>{r.itpc:.3f}</td><td>{r.interpretation}</td></tr>"
        for r in df.itertuples(index=False)
    )
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Dec 4 Condition Interpretation</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;max-width:1300px;line-height:1.4}}
table{{border-collapse:collapse;font-size:13px}}th,td{{border:1px solid #d9dee5;padding:6px 9px;vertical-align:top}}
th{{background:#f3f5f7}}td:nth-child(n+3):nth-child(-n+7){{text-align:right}}</style></head><body>
<h1>Dec 4 Condition-Level Interpretation (per probe)</h1>
<p>dHPC (Port A) = same probe as Dec 3; LEC (Port B) = new. Driven power = log2 change at the
drive frequency (group-median ref); residual = peak above the 1/f background (&gt;0.05 = real
oscillation); ITPC = inter-trial phase locking (null floor ~0.063, Rayleigh p&lt;.05 ~0.122).</p>
<table><tr><th>Probe</th><th>Condition</th><th>Sustained<br>broadband</th><th>Offset<br>broadband</th>
<th>Driven log2</th><th>Residual<br>above 1/f</th><th>ITPC</th><th>Interpretation</th></tr>{rows}</table>
<h2>Short read</h2>
<p><b>dHPC</b>: no frequency-following at any drive rate (replicates Dec 3 on the same probe); response is onset/transient broadband.</p>
<p><b>LEC</b>: a real, amplitude-graded narrowband <b>50 Hz</b> power peak above 1/f, but ITPC at chance &rarr; induced 50 Hz power, not onset-locked entrainment.</p>
</body></html>"""
    (OUT / "index.html").write_text(html)
    print(f"wrote {OUT}/condition_interpretation_summary.csv and index.html ({len(df)} rows)")


if __name__ == "__main__":
    main()

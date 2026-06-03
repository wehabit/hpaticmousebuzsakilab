#!/usr/bin/env python3
"""Create a condition-level biological interpretation summary for Dec 3."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUTPUT = Path("analysis/outputs/dec3/condition_interpretation")


def classify(row: pd.Series) -> str:
    notes = []
    if row["sustained_broadband"] >= 40:
        notes.append("large broadband LFP response")
    elif row["sustained_broadband"] >= 15:
        notes.append("moderate broadband LFP response")
    else:
        notes.append("small broadband LFP response")

    if row["offset_broadband"] > row["sustained_broadband"] * 1.5 and row["offset_broadband"] > 20:
        notes.append("offset/transition-heavy")

    if row["driven_power_analysis_group_median"] > 0.08:
        notes.append("clear driven-frequency power increase")
    elif row["driven_power_analysis_group_median"] > 0.02:
        notes.append("weak positive driven-frequency power")
    elif row["driven_power_analysis_group_median"] < -0.08:
        notes.append("driven-frequency power suppressed/negative")
    else:
        notes.append("near-zero driven-frequency power")

    if abs(row["sustained_minus_pre_plv"]) < 0.01:
        notes.append("no meaningful PLV increase")
    elif row["sustained_minus_pre_plv"] > 0:
        notes.append("tiny positive PLV change")
    else:
        notes.append("negative PLV change")

    return "; ".join(notes)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    base = Path("analysis/outputs/dec3")
    artifact = pd.read_csv(base / "artifact_aware_lfp" / "artifact_aware_lfp_summary.csv")
    ref = pd.read_csv(base / "provisional_final_pass" / "reference_sensitivity_lfp" / "reference_sensitivity_condition_summary.csv")
    tf = pd.read_csv(base / "time_frequency_lfp" / "time_frequency_summary.csv")
    plv = pd.read_csv(base / "provisional_final_pass" / "phase_locking_lfp" / "phase_locking_summary.csv")

    artifact_summary = (
        artifact.groupby(["condition", "amplitude", "frequency"], as_index=False)
        .agg(
            sustained_broadband=("sustained_minus_pre_abs_lfp", "mean"),
            offset_broadband=("offset_minus_pre_abs_lfp", "mean"),
        )
    )
    ref_summary = (
        ref.pivot_table(
            index=["condition", "amplitude", "frequency"],
            columns="reference_mode",
            values="driven_log2_power_change",
        )
        .reset_index()
        .rename(
            columns={
                "raw": "driven_power_raw",
                "physical_shank_median": "driven_power_physical_shank_median",
                "analysis_group_median": "driven_power_analysis_group_median",
            }
        )
    )
    tf_summary = (
        tf.groupby(["condition", "amplitude", "frequency"], as_index=False)
        .agg(
            sustained_timefreq=("sustained_driven_log2_power", "mean"),
            offset_timefreq=("offset_driven_log2_power", "mean"),
        )
    )
    plv_summary = (
        plv.groupby(["condition", "amplitude", "frequency"], as_index=False)
        .agg(sustained_minus_pre_plv=("sustained_minus_pre_plv", "mean"))
    )

    summary = artifact_summary.merge(ref_summary, on=["condition", "amplitude", "frequency"])
    summary = summary.merge(tf_summary, on=["condition", "amplitude", "frequency"])
    summary = summary.merge(plv_summary, on=["condition", "amplitude", "frequency"])
    summary["interpretation"] = summary.apply(classify, axis=1)
    summary = summary.sort_values(["frequency", "amplitude"])
    summary.to_csv(OUTPUT / "condition_interpretation_summary.csv", index=False)

    rows = []
    for row in summary.itertuples(index=False):
        rows.append(
            f"<tr><td>{row.condition}</td><td>{row.sustained_broadband:.2f}</td>"
            f"<td>{row.offset_broadband:.2f}</td><td>{row.driven_power_analysis_group_median:.3f}</td>"
            f"<td>{row.sustained_timefreq:.3f}</td><td>{row.sustained_minus_pre_plv:.3f}</td>"
            f"<td>{row.interpretation}</td></tr>"
        )

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Condition Interpretation</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1250px;line-height:1.45}"
        "table{border-collapse:collapse;font-size:14px}th,td{border:1px solid #d9dee5;padding:8px 10px;vertical-align:top}"
        "th{background:#f3f5f7}td:nth-child(n+2):nth-child(-n+6){text-align:right}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 Condition-Level Biological Interpretation</h1>",
        "<p>This page translates the current LFP metrics into condition-level language. It uses the provisional final-pass preprocessing where available.</p>",
        "<p><strong>What 'largest 26 Hz power candidate' means:</strong> among the 26 Hz stimulation conditions, it has the largest positive increase in 26 Hz-band power under the current preprocessing. It does not mean it is statistically proven, anatomically localized, or strongly phase-locked.</p>",
        "<table><tr><th>Condition</th><th>Sustained broadband</th><th>Offset broadband</th><th>Driven power<br>group median</th><th>Sustained TF<br>driven band</th><th>PLV delta</th><th>Interpretation</th></tr>",
        *rows,
        "</table>",
        "<h2>Short Biological Read</h2>",
        "<p><strong>amp180_freq26</strong>: largest overall LFP amplitude response, but this looks broadband/offset-heavy rather than clean sustained 26 Hz-following.</p>",
        "<p><strong>amp180_freq5</strong>: clearest driven-frequency power increase at 5 Hz.</p>",
        "<p><strong>amp100_freq26</strong>: largest positive 26 Hz-band power increase under the current referenced preprocessing, but PLV does not show strong phase-locking.</p>",
        "<p><strong>amp250_freq26</strong>: weak/negative in driven-frequency and time-frequency metrics, despite some broadband offset response.</p>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (OUTPUT / "index.html").write_text("\n".join(html))
    print({"output": str(OUTPUT / "index.html")})


if __name__ == "__main__":
    main()

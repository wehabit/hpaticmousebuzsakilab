#!/usr/bin/env python3
"""Create a condition-level biological interpretation summary for Dec 3."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


OUTPUT = Path("analysis/outputs/dec3/condition_interpretation")


def classify(row: pd.Series) -> str:
    notes = []
    if row.get("sustained_broadband_ci_low", 0) > 0:
        notes.append("reliable sustained broadband LFP response")
    elif row["sustained_broadband"] >= 2:
        notes.append("positive sustained broadband LFP trend")
    else:
        notes.append("weak/no sustained broadband LFP response")

    if row.get("offset_broadband_ci_low", 0) > 0 and row["offset_broadband"] > row["sustained_broadband"]:
        notes.append("reliable offset/recovery response")
    elif row["offset_broadband"] > row["sustained_broadband"] * 1.5 and row["offset_broadband"] > 4:
        notes.append("offset/transition-heavy trend")

    if row.get("driven_power_ci_low", 0) > 0:
        notes.append("reliable driven-frequency power increase")
    elif row.get("driven_power_ci_high", 0) < 0:
        notes.append("reliable driven-frequency power decrease")
    elif row["driven_power_analysis_group_median"] > 0.08:
        notes.append("positive driven-frequency power trend")
    elif row["driven_power_analysis_group_median"] > 0.02:
        notes.append("weak positive driven-frequency power")
    elif row["driven_power_analysis_group_median"] < -0.08:
        notes.append("negative driven-frequency power trend")
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
    trial = pd.read_csv(base / "trial_level_stats_equal_spectral_windows" / "condition_summary_ci.csv")
    ref = pd.read_csv(base / "provisional_final_pass" / "reference_sensitivity_lfp" / "reference_sensitivity_condition_summary.csv")
    tf = pd.read_csv(base / "time_frequency_lfp" / "time_frequency_summary.csv")
    plv = pd.read_csv(base / "provisional_final_pass" / "phase_locking_lfp" / "phase_locking_summary.csv")

    final_lfp_summary = (
        trial.rename(
            columns={
                "sustained_broadband_delta_mean": "sustained_broadband",
                "sustained_broadband_delta_ci_low": "sustained_broadband_ci_low",
                "sustained_broadband_delta_ci_high": "sustained_broadband_ci_high",
                "offset_broadband_delta_mean": "offset_broadband",
                "offset_broadband_delta_ci_low": "offset_broadband_ci_low",
                "offset_broadband_delta_ci_high": "offset_broadband_ci_high",
                "driven_power_log2_delta_mean": "driven_power_analysis_group_median",
                "driven_power_log2_delta_ci_low": "driven_power_ci_low",
                "driven_power_log2_delta_ci_high": "driven_power_ci_high",
            }
        )[
            [
                "condition",
                "amplitude",
                "frequency",
                "n_trials",
                "sustained_broadband",
                "sustained_broadband_ci_low",
                "sustained_broadband_ci_high",
                "offset_broadband",
                "offset_broadband_ci_low",
                "offset_broadband_ci_high",
                "driven_power_analysis_group_median",
                "driven_power_ci_low",
                "driven_power_ci_high",
            ]
        ]
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
                "raw": "reference_driven_power_raw",
                "physical_shank_median": "reference_driven_power_physical_shank_median",
                "analysis_group_median": "reference_driven_power_analysis_group_median",
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

    summary = final_lfp_summary.merge(ref_summary, on=["condition", "amplitude", "frequency"], how="left")
    summary = summary.merge(tf_summary, on=["condition", "amplitude", "frequency"])
    summary = summary.merge(plv_summary, on=["condition", "amplitude", "frequency"])
    summary["broadband_metric_note"] = "bad-channel-excluded analysis-group mean LFP amplitude"
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
        "<p>This page translates the current LFP metrics into condition-level language. It uses the bad-channel-excluded equal-window trial-level LFP table for broadband/driven metrics, with final-pass PLV/reference summaries where available.</p>",
        "<p><strong>What 'largest 26 Hz power candidate' means:</strong> among the 26 Hz stimulation conditions, it has the largest positive increase in 26 Hz-band power under the current preprocessing. It does not mean it is statistically proven, anatomically localized, or strongly phase-locked.</p>",
        "<table><tr><th>Condition</th><th>Sustained broadband</th><th>Offset broadband</th><th>Driven power<br>group median</th><th>Sustained TF<br>driven band</th><th>PLV delta</th><th>Interpretation</th></tr>",
        *rows,
        "</table>",
        "<h2>Short Biological Read</h2>",
        "<p><strong>amp180_freq26</strong>: strongest reliable broadband/recovery response, but not clean sustained 26 Hz-following.</p>",
        "<p><strong>amp180_freq5</strong>: positive 5 Hz driven-frequency trend, but the equal-window bootstrap CI remains compatible with zero.</p>",
        "<p><strong>amp100_freq26</strong>: positive 26 Hz driven-frequency trend, but PLV does not show strong phase-locking and the CI remains cautious.</p>",
        "<p><strong>amp250_freq26</strong>: offset/recovery-heavy response with weak/negative driven-frequency evidence.</p>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (OUTPUT / "index.html").write_text("\n".join(html))
    print({"output": str(OUTPUT / "index.html")})


if __name__ == "__main__":
    main()

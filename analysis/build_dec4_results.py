#!/usr/bin/env python3
"""Build the Dec 4 combined-explainer figure and the curated results/dec4/ tree.

Dec 4 produced a different set of steps than Dec 3 (two probes, four driven
frequencies, no TTL/movement/spike steps in this first pass), so this uses a
Dec 4-specific figure manifest rather than the Dec 3 MAP in build_results_folder.py.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from results_layout import CATEGORIES

BASE = Path("analysis/outputs/dec4")
RES = Path("results/dec4")
FREQS = [5, 10, 26, 50]
AMPS = [100, 180, 250]


def make_combined_explainer(out: Path) -> None:
    ref = pd.read_csv(BASE / "reference_sensitivity/reference_sensitivity_group_summary.csv")
    ref = ref[ref.reference_mode == "analysis_group_median"]
    ssi = pd.read_csv(BASE / "spectral_slope_itpc/spectral_slope_itpc_summary.csv")

    groups = ["A_dHPC_0-31", "A_dHPC_32-63", "A_dHPC_64-95", "A_dHPC_96-127",
              "B_LEC_128-191", "B_LEC_192-255"]
    conds = [f"amp{a}_freq{f}" for f in FREQS for a in AMPS]

    fig = plt.figure(figsize=(17, 9))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])

    # Panel A: driven log2 power change heatmap (condition x group)
    axA = fig.add_subplot(gs[0, :])
    M = ref.pivot_table(index="condition", columns="analysis_group",
                        values="driven_log2_power_change").reindex(index=conds, columns=groups)
    im = axA.imshow(M.values, aspect="auto", cmap="RdBu_r", vmin=-1.3, vmax=1.3)
    axA.set_xticks(range(len(groups)))
    axA.set_xticklabels([g.replace("_", " ") for g in groups], rotation=20, ha="right")
    axA.set_yticks(range(len(conds)))
    axA.set_yticklabels(conds, fontsize=8)
    axA.set_title("A. Driven-frequency power change (log2, group-median ref, bad ch excluded)\n"
                  "dHPC flat at every frequency; LEC lights up only at 50 Hz, growing with amplitude")
    for (i, j), v in np.ndenumerate(M.values):
        if np.isfinite(v):
            axA.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                     color="white" if abs(v) > 0.7 else "black")
    fig.colorbar(im, ax=axA, fraction=0.025, pad=0.01, label="log2 power change")

    # Panel B: 50 Hz amplitude grading, LEC vs dHPC responsive group
    axB = fig.add_subplot(gs[1, 0])
    for probe, key, color in [("dHPC (A 0-31)", "A_dHPC_0-31", "#2F6BBA"),
                              ("LEC (B 192-255)", "B_LEC_192-255", "#C43A31")]:
        d = ref[(ref.analysis_group == key) & (ref.frequency == 50)].sort_values("amplitude")
        axB.plot(d.amplitude, d.driven_log2_power_change, marker="o", color=color, label=probe)
    axB.axhline(0, color="k", lw=0.8)
    axB.set_title("B. 50 Hz power vs amplitude")
    axB.set_xlabel("drive amplitude"); axB.set_ylabel("log2 power change"); axB.set_xticks(AMPS)
    axB.legend(fontsize=8); axB.grid(alpha=0.2)

    # Panel C: oscillation test (residual above 1/f) at the driven freq
    axC = fig.add_subplot(gs[1, 1])
    fcolors = {5: "#2F6BBA", 10: "#54A24B", 26: "#E6A817", 50: "#C43A31"}
    lec = ssi[ssi.probe == "LEC (B 192-255)"]
    for f in FREQS:
        d = lec[lec.frequency == f].sort_values("amplitude")
        axC.plot(d.amplitude, d.residual_above_1f_on, marker="o", color=fcolors[f], label=f"{f} Hz")
    axC.axhline(0.05, color="gray", ls=":", lw=1)
    axC.axhline(0, color="k", lw=0.8)
    axC.set_title("C. LEC: narrowband peak above 1/f\n(>0.05 = real oscillation)")
    axC.set_xlabel("drive amplitude"); axC.set_ylabel("residual above 1/f"); axC.set_xticks(AMPS)
    axC.legend(fontsize=8); axC.grid(alpha=0.2)

    # Panel D: phase locking vs chance (ITPC), both probes at 50 Hz
    axD = fig.add_subplot(gs[1, 2])
    for probe, color in [("dHPC (A 0-31)", "#2F6BBA"), ("LEC (B 192-255)", "#C43A31")]:
        d = ssi[(ssi.probe == probe) & (ssi.frequency == 50)].sort_values("amplitude")
        axD.plot(d.amplitude, d.itpc, marker="o", color=color, label=probe)
    floor = float(ssi.itpc_null_floor.median())
    ray = float(ssi.rayleigh_p05.median())
    axD.axhline(floor, color="k", ls="--", lw=1.2, label=f"null floor {floor:.3f}")
    axD.axhline(ray, color="#27ae60", lw=1.4, label=f"Rayleigh p<.05 {ray:.3f}")
    axD.set_title("D. 50 Hz phase locking (ITPC) vs chance\nat/below floor -> induced, not entrained")
    axD.set_xlabel("drive amplitude"); axD.set_ylabel("sustained ITPC"); axD.set_xticks(AMPS)
    axD.legend(fontsize=7); axD.grid(alpha=0.2)

    fig.suptitle("Dec 4 in one figure: dHPC does NOT follow any drive frequency (replicates Dec 3 on the same probe); "
                 "LEC shows induced, amplitude-graded 50 Hz power that is NOT phase-locked",
                 fontweight="bold", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)


# Dec 4 figure manifest: category -> list of source figures (relative to BASE).
MAP = {
    "movement": [
        "movement/movement_raw.png",
        "movement/movement_sensitivity.png",
    ],
    "event_lfp": [
        "event_aligned_lfp/condition_average_lfp_collapsed.png",
        "event_aligned_lfp/condition_by_channel_lfp_response_heatmap.png",
        "artifact_aware_lfp/artifact_window_comparison.png",
        "artifact_aware_lfp/sustained_response_by_shank.png",
    ],
    "frequency": [
        "frequency_lfp/driven_power_change_by_analysis_group.png",
        "frequency_lfp/driven_power_change_by_channel.png",
        "frequency_lfp/driven_power_change_by_physical_shank.png",
        "frequency_lfp/frequency_specificity_by_group.png",
        "time_frequency_lfp/driven_frequency_timecourses.png",
        "time_frequency_lfp/time_frequency_condition_grid.png",
        "spectral_slope_itpc/spectral_slope_itpc_dec4.png",
        # aperiodic 1/f across states (baseline/ON/OFF/post): broad-shift vs real-bump
        ("../cross_dataset_spike_compare/lfp_aperiodic_states/dec4_aperiodic_states.png", "dec4_aperiodic_states.png"),
        ("../cross_dataset_spike_compare/lfp_aperiodic_states/dec4_bump_vs_broadshift.png", "dec4_bump_vs_broadshift.png"),
        ("../cross_dataset_spike_compare/lfp_aperiodic_states/state_spectra_loglog.png", "state_spectra_loglog.png"),
        # band power across states (broadband/theta/gamma + driven bands)
        ("../cross_dataset_spike_compare/lfp_bandpower_states/bandpower_general_states.png", "bandpower_general_states.png"),
        ("../cross_dataset_spike_compare/lfp_bandpower_states/bandpower_driven_states.png", "bandpower_driven_states.png"),
    ],
    "phase": [
        "phase_locking_lfp/plv_condition_summary.png",
        "phase_locking_lfp/plv_sustained_minus_pre.png",
        "phase_locking_lfp/plv_timecourses.png",
    ],
    "broadband": [
        "broadband_transition/broadband_window_group_heatmaps.png",
        "broadband_transition/broadband_windows_condition_ci.png",
        "broadband_transition/transition_index_condition.png",
        "off_control_broadband/off_control_condition_ci.png",
        "off_control_broadband/off_control_group_heatmaps.png",
        "trial_level_stats/driven_power_ci.png",
        "trial_level_stats/offset_broadband_ci.png",
        "trial_level_stats/sustained_broadband_ci.png",
    ],
    "reference": [
        "reference_sensitivity/reference_condition_summary.png",
        "reference_sensitivity/reference_group_heatmaps.png",
    ],
    "adaptation": [
        "adaptation_analysis/adaptation_epoch_summary.png",
        "adaptation_analysis/adaptation_slope_summary.png",
        "adaptation_analysis/adaptation_timecourses.png",
    ],
    "biological": [
        "biological_summary/combined_explainer.png",
        "biological_summary/broadband_perchannel_ci.png",
        "biological_summary/dHPC_amp180_freq26/sustained_vs_offset_explained.png",
        "biological_summary/LEC_amp250_freq50/sustained_vs_offset_explained.png",
    ],
    "spikes": [
        "spikeinterface_setup/spikeinterface_trace_sanity.png",
        # single-unit ON/OFF result (curated good units), cross-dataset (paths via ../)
        ("../cross_dataset_spike_compare/spike_onoff_cross_dataset.png", None),
        ("../cross_dataset_spike_compare/spike_50hz_interpretation.png", None),
        # per-probe ON/OFF PETH + heatmaps
        ("spike_peth_on_off_dhpc/condition_mean_on_minus_off.png", "dHPC_condition_mean_on_minus_off.png"),
        ("spike_peth_on_off_dhpc/unit_condition_on_minus_off_heatmap_ks_good.png", "dHPC_unit_condition_heatmap.png"),
        ("spike_peth_on_off_dhpc/peth_onset_ks_good_units.png", "dHPC_peth_onset_good_units.png"),
        ("spike_peth_on_off_lec/condition_mean_on_minus_off.png", "LEC_condition_mean_on_minus_off.png"),
        ("spike_peth_on_off_lec/unit_condition_on_minus_off_heatmap_ks_good.png", "LEC_unit_condition_heatmap.png"),
        ("spike_peth_on_off_lec/peth_onset_ks_good_units.png", "LEC_peth_onset_good_units.png"),
        # cross-region 50 Hz coordination + the soft-spot ACG/ISI artifact screen
        ("coordination_50hz/coordination_50hz.png", "coordination_50hz_pooled.png"),
        ("coordination_50hz_amp250/coordination_50hz.png", "coordination_50hz_amp250.png"),
        ("artifact_check_50hz/unit87_phy_view.png", "unit87_acg_artifact_screen.png"),
        # single-unit firing vs TRUE pre-experiment baseline & post-study (bootstrap CIs)
        ("../cross_dataset_spike_compare/baseline_poststudy/dec4_states_vs_baseline.png",
         "dec4_states_vs_baseline.png"),
        ("../cross_dataset_spike_compare/baseline_poststudy/dec4_freq50_vs_baseline.png",
         "dec4_freq50_vs_baseline.png"),
        # putative cell-type classification (CellExplorer-style) + 50 Hz response by type
        ("../cross_dataset_spike_compare/celltype/dec4_celltype.png", "dec4_celltype.png"),
        ("../cross_dataset_spike_compare/celltype/dec4_celltype_vs_50hz.png", "dec4_celltype_vs_50hz.png"),
        ("../cross_dataset_spike_compare/celltype/celltype_classification.png", "celltype_classification_pooled.png"),
        ("../cross_dataset_spike_compare/celltype/celltype_acg_examples.png", "celltype_acg_examples.png"),
        # sharp-wave ripples across states (exploratory, dHPC, CA1 provisional)
        ("../cross_dataset_spike_compare/ripples/ripple_rate_by_state.png", "ripple_rate_by_state.png"),
        ("../cross_dataset_spike_compare/ripples/ripple_participation_by_celltype.png", "ripple_participation_by_celltype.png"),
        ("../cross_dataset_spike_compare/ripples/ripple_examples.png", "ripple_examples.png"),
    ],
    "channelqc": [
        "channel_qc/channel_qc_metrics.png",
        # 50 Hz LFP artifact check (dead-channel pickup) + dHPC-vs-LEC gradient
        ("artifact_check_50hz/artifact_check_50hz.png", "50hz_artifact_check.png"),
        ("artifact_check_50hz/gradient_dhpc_vs_lec.png", "50hz_pickup_gradient_dhpc_vs_lec.png"),
    ],
    "teaching": [
        "methods/dHPC_amp180_freq26/margin_exclusion_test.png",
        "methods/LEC_amp250_freq50/margin_exclusion_test.png",
        # the 50 Hz "is it pickup?" explainers
        ("artifact_check_50hz/explainer_1_contamination.png", None),
        ("artifact_check_50hz/explainer_2_evidence.png", None),
    ],
}

BLURB = {
    "movement": "LFP-based movement proxy (no accelerometer this session) and the data-cleaning robustness check.",
    "adaptation": "How the response changes over the 200 repeats (early/middle/late + slope).",
    "spikes": "Kilosort4 + curation done (15 good units/probe). Single-unit ON/OFF (50 Hz/high-amp "
              "responders in both regions), cross-region 50 Hz coordination, and the unit-87 ACG/ISI "
              "artifact screen. See docs/DEC4_SPIKE_ONOFF_RESULT.md, DEC4_COORDINATION_50HZ.md.",
    "teaching": "Artifact-margin robustness test, plus the 50 Hz 'is it pickup or neural?' explainers "
                "(contamination + evidence). See docs/DEC4_50HZ_ARTIFACT_CHECK.md.",
    "event_lfp": "Event-aligned broadband LFP per condition, by channel and by probe (Port A dHPC, Port B LEC).",
    "frequency": "Power at the driven 5/10/26/50 Hz frequency, frequency specificity, time-frequency, and the 1/f + ITPC entrainment test.",
    "phase": "Phase locking (PLV/ITPC) per condition and probe vs the within-trial pre window.",
    "broadband": "Onset/sustained/offset broadband windows, OFF-control, and trial-level bootstrap CIs.",
    "reference": "Robustness of the driven-power result to the referencing scheme (raw / probe / group median).",
    "biological": "Dec 4 in one figure: dHPC null at all frequencies; LEC induced, amplitude-graded 50 Hz power without phase locking.",
    "channelqc": "Per-channel noise QC (pooled view; per-probe bad lists in analysis/bad_channels_dec4.json). "
                 "Plus the 50 Hz LFP artifact check: disconnected LEC electrodes pick up ~6x more 50 Hz than "
                 "tissue; dHPC is much cleaner (LEC: 82 good / 45 disconnected-dead / 1 hot-excluded ch142).",
}

HEADLINE = [
    ("10_Biological_Summary/combined_explainer.png",
     "the whole Dec 4 story: dHPC follows no frequency (same probe as Dec 3); LEC shows induced 50 Hz power that grows with amplitude but is not phase-locked"),
    ("11_Spikes/spike_onoff_cross_dataset.png",
     "the cleanest neural result: single-unit ON/OFF firing — Dec 3 null at 5/26 Hz, Dec 4 50 Hz/high-amp responders in BOTH dHPC and LEC"),
    ("11_Spikes/unit87_acg_artifact_screen.png",
     "the soft-spot unit 87 passes the ACG + ISI artifact screens: its 50 Hz rate increase is a real neuron, not pickup"),
    ("13_Teaching_and_Methods/explainer_2_evidence.png",
     "how we know the 50 Hz spike result is neural, not artifact: direction test + dose-response + the ACG resolution + the trust hierarchy"),
    ("05_Frequency_Spectral/spectral_slope_itpc_dec4.png",
     "entrainment test: a real narrowband 50 Hz peak above 1/f in LEC (amplitude-graded), but ITPC at chance"),
    ("05_Frequency_Spectral/driven_power_change_by_analysis_group.png",
     "driven-frequency power by probe-group across all 12 conditions"),
    ("09_Reference_Sensitivity/reference_condition_summary.png",
     "the 50 Hz LEC effect survives every reference scheme"),
]


def main() -> None:
    make_combined_explainer(BASE / "biological_summary/combined_explainer.png")

    if RES.exists():
        shutil.rmtree(RES)
    copied = missing = 0
    copied_files: dict[str, list[str]] = {}
    for cat, files in MAP.items():
        d = RES / CATEGORIES[cat]
        d.mkdir(parents=True, exist_ok=True)
        for entry in files:
            rel, dest = (entry, None) if isinstance(entry, str) else entry  # optional rename
            src = BASE / rel
            if src.exists():
                name = dest or src.name
                if (d / name).exists():  # collision (e.g. two sustained_vs_offset_explained.png)
                    name = f"{src.parent.name}_{Path(name).name}"
                shutil.copy2(src, d / name)
                copied_files.setdefault(cat, []).append(name)
                copied += 1
            else:
                print(f"  MISSING: {src}")
                missing += 1

    lines = ["# Results - dec4 haptic analysis (two probes: dHPC + LEC, freqs 5/10/26/50)\n",
             "Same mouse/probes as Dec 3, now with a second probe (LEC) and four drive",
             "frequencies. Curated, de-duplicated figures grouped by analysis type. Rebuild with",
             "`python analysis/build_dec4_results.py`.\n",
             "## Headline figures (start here)"]
    for path, label in HEADLINE:
        if (RES / path).exists():
            lines.append(f"- [{Path(path).name}]({path}) - {label}")
    lines.append("\n## All figures by category")
    for cat, folder in CATEGORIES.items():
        if cat not in copied_files:
            continue
        lines.append(f"\n### {folder}")
        if cat in BLURB:
            lines.append(f"_{BLURB[cat]}_\n")
        for name in copied_files[cat]:
            lines.append(f"- [{name}]({folder}/{name})")
    (RES / "README.md").write_text("\n".join(lines) + "\n")

    sessions = sorted(p.name for p in Path("results").iterdir() if p.is_dir())
    parent = ["# Results\n",
              "Curated result figures, **one folder per recording session**. Open a session's",
              "`README.md` for its per-figure index.\n"]
    for s in sessions:
        parent.append(f"- [`{s}/`]({s}/README.md)")
    Path("results/README.md").write_text("\n".join(parent) + "\n")

    print(f"results/dec4 built: {copied} figures copied, {missing} missing.")


if __name__ == "__main__":
    main()

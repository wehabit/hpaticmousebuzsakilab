#!/usr/bin/env python3
"""Build the curated Results/ deliverable tree from the raw dec3 pipeline outputs.

Copies each canonical figure into Results/<NN_Category>/ (the same grouping used in
the review). Raw outputs under analysis/outputs/dec3/<step>/ are left untouched so
downstream code keeps working; Results/ is the browsable view. Re-runnable and
idempotent. Duplicate / superseded copies (REPORT mirrors, provisional_final_pass)
are intentionally skipped and reported.
"""
from __future__ import annotations
import shutil
from pathlib import Path
from results_layout import RESULTS_ROOT, CATEGORIES, results_dir

BASE = Path("analysis/outputs/dec3")
MAX_MB = 50          # skip pathological oversized renders (e.g. a 1.75 GB spike_positions png)

# category key -> list of source paths (relative to BASE). Directories copy their *.png.
MAP = {
    "timeline": [
        "ttl_lfp_overview/session_timeline.png",
        "ttl_lfp_overview/ttl_lfp_context_and_trials.png",
    ],
    "ttl": [
        "ttl_lfp_overview/ttl_on_alignment_per_trial.png",
        "ttl_lfp_overview/accelerometer_active_threshold_examples.png",
        "ttl_on_off_audit/ttl_on_off_counts.png",
    ],
    "movement": [
        "movement/movement_raw.png",
        "movement/movement_emg.png",
        "movement/excluded_vs_kept_examples.png",
        "movement/movement_sensitivity.png",
    ],
    "event_lfp": [
        "event_aligned_lfp/condition_average_lfp_collapsed.png",
        "event_aligned_lfp/condition_by_channel_lfp_response_heatmap.png",
        "event_aligned_lfp/better_plots/lfp_by_shank_conditions.png",
        "event_aligned_lfp/better_plots/lfp_condition_envelopes.png",
        "event_aligned_lfp/better_plots/lfp_condition_panels_by_shank.png",
        "event_aligned_lfp/condition_summary_plots/lfp_condition_shank_heatmap_values.png",
        "event_aligned_lfp/condition_summary_plots/lfp_frequency_difference_by_shank.png",
        "event_aligned_lfp/condition_summary_plots/lfp_response_grouped_bars.png",
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
        "comprehensive/spectral_slope_decomposition.png",      # NEW (#1)
    ],
    "phase": [
        "phase_locking_lfp/plv_condition_summary.png",
        "phase_locking_lfp/plv_sustained_minus_pre.png",
        "phase_locking_lfp/plv_timecourses.png",
        "cohen_corrected/A_itpc_onset_vs_grid.png",
        "comprehensive/phase_locking_null_floor.png",          # NEW (#2)
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
        "cohen_corrected/B_broadband_rms.png",
    ],
    "adaptation": [
        "adaptation_analysis/adaptation_epoch_summary.png",
        "adaptation_analysis/adaptation_slope_summary.png",
        "adaptation_analysis/adaptation_timecourses.png",
    ],
    "reference": [
        "reference_sensitivity_lfp/reference_condition_summary.png",
        "reference_sensitivity_lfp/reference_group_heatmaps.png",
    ],
    "biological": [
        "biological_summary/amplitude_frequency_matrix.png",
        "biological_summary/broadband_vs_driven_power.png",
        "biological_summary/condition_fingerprint.png",
    ],
    "spikes": [
        "cluster_quality/cluster_quality_label_counts.png",
        "cluster_quality/cluster_quality_scatter.png",
        "modal_kilosort4_results/kilosort4_results/diagnostics.png",
        "modal_kilosort4_results/kilosort4_results/drift_amount.png",
        "modal_kilosort4_results/kilosort4_results/drift_scatter.png",
        "modal_kilosort4_results/kilosort4_results/spike_positions.png",
        "spike_positions_modal_kilosort4.png",
        "spikeinterface_setup/spikeinterface_trace_sanity.png",
        "spike_peth_on_off/condition_mean_on_minus_off.png",
        "spike_peth_on_off/peth_onset_ks_good_units.png",
        "spike_peth_on_off/peth_offset_ks_good_units.png",
        "spike_peth_on_off/unit_condition_on_minus_off_heatmap_all_units.png",
        "spike_peth_on_off/unit_condition_on_minus_off_heatmap_ks_good.png",
        "spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png",
        "spike_peth_high_confidence/high_confidence_unit_condition_heatmap.png",
        "spike_peth_high_confidence/peth_onset_high_confidence_units.png",
        "spike_peth_high_confidence/peth_offset_high_confidence_units.png",
    ],
    "channelqc": [
        "channel_qc/channel_qc_metrics.png",
        "channel_qc_baseline/channel_qc_metrics.png",
        "channel_qc_baseline/high_noise_review_traces.png",
    ],
    "teaching": [
        "REPORT/LEARN_real_vs_dec3.png",
        "REPORT/LEARN_results_at_a_glance.png",
        "methods/margin_exclusion_test.png",
        "REPORT/supp_provisional_probe_map_H12_UNRESOLVED.png",
    ],
}

# directory -> (category, subfolder): copy every *.png inside
DIR_MAP = {
    "channel_trace_pages": ("channelqc", "raw_trace_pages"),
    "lfp_trace_pages": ("channelqc", "lfp_trace_pages"),
}

# superseded copies we deliberately do NOT bring into Results/
SKIPPED = ["REPORT/1-7_*  (mirror of ttl_lfp_overview + movement)",
           "provisional_final_pass/*  (mirror of phase_locking + reference_sensitivity)"]


def main():
    if RESULTS_ROOT.exists():
        shutil.rmtree(RESULTS_ROOT)
    copied = missing = 0
    per_cat = {}
    too_large = []

    def copy_one(src, dest_dir, cat):
        nonlocal copied
        mb = src.stat().st_size / 1e6
        if mb > MAX_MB:
            too_large.append(f"{src}  ({mb:.0f} MB)"); print(f"  SKIP too large ({mb:.0f} MB): {src}")
            return
        shutil.copy2(src, dest_dir / src.name); copied += 1
        per_cat[cat] = per_cat.get(cat, 0) + 1

    for cat, files in MAP.items():
        d = results_dir(cat)
        for rel in files:
            src = BASE / rel
            if src.exists():
                copy_one(src, d, cat)
            else:
                print(f"  MISSING: {src}"); missing += 1
    for dirname, (cat, sub) in DIR_MAP.items():
        srcdir = BASE / dirname
        if not srcdir.exists():
            print(f"  MISSING DIR: {srcdir}"); continue
        d = results_dir(cat, sub)
        for png in sorted(srcdir.glob("*.png")):
            copy_one(png, d, cat)

    # index
    lines = ["# Results - Dec 3 haptic analysis (curated figure tree)\n",
             "Figures grouped by analysis type. Raw pipeline outputs remain under",
             "`analysis/outputs/dec3/<step>/`; this folder is the browsable deliverable,",
             "rebuilt by `python analysis/build_results_folder.py`.\n"]
    for cat, folder in CATEGORIES.items():
        n = per_cat.get(cat, 0)
        lines.append(f"- **{folder}** - {n} figure(s)")
    lines.append("\n_Skipped (duplicates / superseded):_")
    lines += [f"- {s}" for s in SKIPPED]
    if too_large:
        lines.append(f"\n_Skipped (> {MAX_MB} MB, regenerate at sane DPI):_")
        lines += [f"- {s}" for s in too_large]
    (RESULTS_ROOT / "README.md").write_text("\n".join(lines) + "\n")

    print(f"\nResults/ built: {copied} figures copied, {missing} missing, {len(too_large)} too-large skipped.")
    for cat, folder in CATEGORIES.items():
        print(f"  {folder}: {per_cat.get(cat, 0)}")


if __name__ == "__main__":
    main()

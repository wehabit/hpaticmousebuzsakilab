#!/usr/bin/env python3
"""Build the curated results/<session>/ deliverable tree from raw pipeline outputs.

Per session (default `dec3`): copies each canonical figure from
`analysis/outputs/<session>/<step>/` into `results/<session>/<NN_Category>/`
(the grouping used in the review), and writes a per-figure index plus a parent
`results/README.md` listing every session. Raw outputs are left untouched.
Re-runnable and idempotent.

    python analysis/build_results_folder.py --session dec3
    python analysis/build_results_folder.py --session dec4   # same pipeline, new session
"""
from __future__ import annotations
import shutil
from pathlib import Path
from results_layout import CATEGORIES

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
        # aperiodic 1/f across states (baseline/ON/OFF/post): broad-shift vs real-bump
        "../cross_dataset_spike_compare/lfp_aperiodic_states/dec3_aperiodic_states.png",
        "../cross_dataset_spike_compare/lfp_aperiodic_states/dec3_bump_vs_broadshift.png",
        "../cross_dataset_spike_compare/lfp_aperiodic_states/state_spectra_loglog.png",
        # band power across states (broadband/theta/gamma + driven bands)
        "../cross_dataset_spike_compare/lfp_bandpower_states/bandpower_general_states.png",
        "../cross_dataset_spike_compare/lfp_bandpower_states/bandpower_driven_states.png",
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
        "trial_level_stats_equal_spectral_windows/driven_power_ci.png",
        "trial_level_stats_equal_spectral_windows/offset_broadband_ci.png",
        "trial_level_stats_equal_spectral_windows/sustained_broadband_ci.png",
        "cohen_corrected/B_broadband_rms.png",
    ],
    "adaptation": [
        "adaptation_analysis/adaptation_epoch_summary.png",
        "adaptation_analysis/adaptation_slope_summary.png",
        "adaptation_analysis/adaptation_timecourses.png",
        # early/middle/late anchored to baseline (26 Hz habituation; OFF drift)
        "../cross_dataset_spike_compare/adaptation_states/lfp_adaptation_driven.png",
    ],
    "reference": [
        "reference_sensitivity_lfp/reference_condition_summary.png",
        "reference_sensitivity_lfp/reference_group_heatmaps.png",
    ],
    "biological": [
        "biological_summary/amplitude_frequency_matrix.png",
        "biological_summary/broadband_vs_driven_power.png",
        "biological_summary/condition_fingerprint.png",
        "biological_summary/combined_explainer.png",
        "biological_summary/sustained_vs_offset_explained.png",
    ],
    "spikes": [
        "cluster_quality/cluster_quality_label_counts.png",
        "cluster_quality/cluster_quality_scatter.png",
        "modal_kilosort4_results/kilosort4_results/diagnostics.png",
        "modal_kilosort4_results/kilosort4_results/drift_amount.png",
        "modal_kilosort4_results/kilosort4_results/drift_scatter.png",
        "modal_kilosort4_results/kilosort4_results/spike_positions.png",
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
        # Dec 3 single-unit negative control: no modulation at 5/26 Hz (0/174) — PSTH + raster
        "../cross_dataset_spike_compare/raster_psth/psth_dec3_null_control.png",
        "../cross_dataset_spike_compare/raster_psth/raster_psth_dec3_null.png",
        # single-unit firing vs TRUE pre-experiment baseline & post-study (bootstrap CIs)
        "../cross_dataset_spike_compare/baseline_poststudy/dec3_states_vs_baseline.png",
        # putative cell-type classification (CellExplorer-style)
        "../cross_dataset_spike_compare/celltype/dec3_celltype.png",
        "../cross_dataset_spike_compare/celltype/celltype_classification.png",
        "../cross_dataset_spike_compare/celltype/celltype_acg_examples.png",
        # full CellExplorer ACG-type classification (tau_rise; 3-way) + honest caveat
        "../cross_dataset_spike_compare/acg_type/acg_type_classification_plane.png",
        "../cross_dataset_spike_compare/acg_type/acg_type_fits.png",
        # sharp-wave ripples across states (exploratory, dHPC, CA1 provisional)
        "../cross_dataset_spike_compare/ripples/ripple_rate_by_state.png",
        "../cross_dataset_spike_compare/ripples/ripple_participation_by_celltype.png",
        "../cross_dataset_spike_compare/ripples/ripple_on_rate_by_stim_freq.png",
        "../cross_dataset_spike_compare/ripples/ripple_examples.png",
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
        "methods/trial_window_diagram.png",
        "REPORT/supp_provisional_probe_map_H12_UNRESOLVED.png",
    ],
}

# directory -> (category, subfolder): copy every *.png inside
DIR_MAP = {
    "channel_trace_pages": ("channelqc", "raw_trace_pages"),
    "lfp_trace_pages": ("channelqc", "lfp_trace_pages"),
}

# superseded copies we deliberately do NOT bring into results/
SKIPPED = ["REPORT/1-7_*  (mirror of ttl_lfp_overview + movement)",
           "provisional_final_pass/*  (mirror of phase_locking + reference_sensitivity)"]


def main(session="dec3"):
    base = Path("analysis/outputs") / session
    res_root = Path("results") / session

    def rdir(cat, sub=None):
        d = res_root / CATEGORIES[cat]
        if sub:
            d = d / sub
        d.mkdir(parents=True, exist_ok=True)
        return d

    if res_root.exists():
        shutil.rmtree(res_root)
    copied = missing = 0
    per_cat = {}
    too_large = []
    copied_files = {}                     # cat -> [actual filenames copied to the category folder]

    def copy_one(src, dest_dir, cat, record=True):
        nonlocal copied
        mb = src.stat().st_size / 1e6
        if mb > MAX_MB:
            too_large.append(f"{src}  ({mb:.0f} MB)"); print(f"  SKIP too large ({mb:.0f} MB): {src}")
            return
        name = src.name
        if (dest_dir / name).exists():    # avoid name collisions (e.g. two channel_qc_metrics.png)
            name = f"{src.parent.name}_{src.name}"
        shutil.copy2(src, dest_dir / name); copied += 1
        per_cat[cat] = per_cat.get(cat, 0) + 1
        if record:
            copied_files.setdefault(cat, []).append(name)

    for cat, files in MAP.items():
        d = rdir(cat)
        for rel in files:
            src = base / rel
            if src.exists():
                copy_one(src, d, cat)
            else:
                print(f"  MISSING: {src}"); missing += 1
    for dirname, (cat, sub) in DIR_MAP.items():
        srcdir = base / dirname
        if not srcdir.exists():
            print(f"  MISSING DIR: {srcdir}"); continue
        d = rdir(cat, sub)
        for png in sorted(srcdir.glob("*.png")):
            copy_one(png, d, cat, record=False)

    # ---- rich, per-figure index ----
    HEADLINE = [
        ("10_Biological_Summary/combined_explainer.png", "the whole story in one figure: strongest broadband/recovery response at 26 Hz / 180, weak driven-frequency evidence"),
        ("01_Session_Timeline/session_timeline.png", "the session at a glance: baseline / stimulation / post"),
        ("04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png", "which condition & channels respond (26 Hz / 180 strongest)"),
        ("05_Frequency_Spectral/spectral_slope_decomposition.png", "the response is a broadband shift, not a 5/26 Hz oscillation"),
        ("06_Phase_Locking/phase_locking_null_floor.png", "phase locking stays near the finite-trial floor, so this pass does not support strong entrainment"),
        ("11_Spikes/peth_onset_ks_good_units.png", "firing is flat ON vs OFF (provisional, pre-curation)"),
    ]
    BLURB = {
        "timeline": "Session at a glance: baseline -> stimulation -> post, with the accelerometer TTL and LFP.",
        "ttl": "Accelerometer-TTL vs commanded ON time: alignment, per-trial onset, and ON/OFF edge counts.",
        "movement": "Movement proxy (EMG-from-LFP) and the data-cleaning sensitivity check.",
        "event_lfp": "Event-aligned broadband LFP per condition, by channel and by shank (200 trials).",
        "frequency": "Power at the driven 5/26 Hz frequency, frequency specificity, and the 1/f spectral-slope test.",
        "phase": "Phase locking (PLV/ITPC) against chance, incl. the null-floor and onset-jitter checks.",
        "broadband": "Onset / sustained / offset broadband windows, OFF-control, and trial-level bootstrap CIs.",
        "adaptation": "How the response changes over the course of the trials.",
        "reference": "Robustness of the LFP results to the referencing scheme.",
        "biological": "Plain-language summary: does the brain react, and does it follow the buzz frequency? (with 95% CIs).",
        "spikes": "Kilosort cluster quality, drift, and ON-vs-OFF firing (PETH). Provisional until Phy curation.",
        "channelqc": "Per-channel noise QC plus raw/LFP trace-browsing pages.",
        "teaching": "Teaching/methods explainers: how to read the results, the +/-100 ms margin, and the probe map.",
    }
    lines = [f"# Results - {session} haptic analysis\n",
             "**Curated, de-duplicated set of every result figure for this session**, grouped by analysis type.",
             "Each figure here is the canonical copy; the raw per-step working files under",
             f"`analysis/outputs/{session}/<step>/` are inputs the scripts read from (not duplicates to browse).",
             f"Rebuild with `python analysis/build_results_folder.py --session {session}`.\n",
             "## Headline figures (start here)"]
    for path, label in HEADLINE:
        if (res_root / path).exists():
            lines.append(f"- [{Path(path).name}]({path}) - {label}")
    lines.append("\n## All figures by category")
    for cat, folder in CATEGORIES.items():
        lines.append(f"\n### {folder}")
        if cat in BLURB:
            lines.append(f"_{BLURB[cat]}_\n")
        for name in copied_files.get(cat, []):
            lines.append(f"- [{name}]({folder}/{name})")
        for dirname, (c, sub) in DIR_MAP.items():
            if c == cat:
                d = res_root / folder / sub
                k = len(list(d.glob("*.png"))) if d.exists() else 0
                if k:
                    lines.append(f"- `{sub}/` - {k} trace-browsing pages")
    lines.append("\n---")
    lines.append("_Not copied here (intentional):_")
    lines += [f"- {s}" for s in SKIPPED]
    if too_large:
        lines.append(f"\n_Skipped (> {MAX_MB} MB, regenerate at sane DPI):_")
        lines += [f"- {s}" for s in too_large]
    (res_root / "README.md").write_text("\n".join(lines) + "\n")

    # parent index of all sessions
    sessions = sorted(p.name for p in Path("results").iterdir() if p.is_dir())
    parent = ["# Results\n",
              "Curated result figures, **one folder per recording session**. Open a session's",
              "`README.md` for its per-figure index.\n"]
    for s in sessions:
        parent.append(f"- [`{s}/`]({s}/README.md)")
    Path("results/README.md").write_text("\n".join(parent) + "\n")

    print(f"\nresults/{session} built: {copied} figures copied, {missing} missing, {len(too_large)} too-large skipped.")
    for cat, folder in CATEGORIES.items():
        print(f"  {folder}: {per_cat.get(cat, 0)}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Build results/<session>/ from analysis/outputs/<session>/")
    ap.add_argument("--session", default="dec3", help="session id, e.g. dec3 or dec4")
    main(ap.parse_args().session)

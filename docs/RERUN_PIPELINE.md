# Reusable Analysis Pipeline

Use this checklist when adding a new recording or a new set of stimulation
conditions. Dec 3 is the template run.

## 1. Define The Session

Create a new output folder:

```bash
analysis/outputs/<session_id>
```

Record the key inputs:

- Intan session directory
- stimulus config or command log
- expected sample rate
- number of amplifier channels
- baseline duration
- ON/OFF timing
- condition list
- number of repeats
- known bad channels
- probe/channel map assumptions

For Dec 3, the study design used 3 s ON followed by 3 s OFF, with 200 repeats
per condition and at least 15 minutes of baseline.

## 2. Parse Intan Metadata, Schedule, And TTL QC

Template command:

```bash
python analysis/intan_haptic_summary.py \
  --session-dir "/path/to/intan/session" \
  --config "/path/to/stimulus_config.json" \
  --recording-start-offset-s 640 \
  --output-dir analysis/outputs/<session_id>
```

Outputs to check:

- `session_summary.json`
- `stimulus_config_schedule.csv`
- `dec3_condition_sequence.csv` or the session-equivalent condition sequence
- `stimulation_events.csv`
- `digital_edges_ch*.csv`

Use the schedule-derived condition sequence as the authoritative trial label and
ON/OFF window source. Treat `stimulation_events.csv` as a TTL QC table only when
there is any burst-count mismatch, pre/post/test TTL activity, or merged/missing
bursts.

Then audit ON/OFF timing:

```bash
python analysis/ttl_on_off_audit_dec3.py
```

For a new session, copy/update this script or parameterize it so it writes to
`analysis/outputs/<session_id>/ttl_on_off_audit`.

## 3. Confirm Channels And Bad Channels

Run channel QC:

```bash
python analysis/channel_qc.py
```

For Dec 3, the current confirmed bad channels are:

```text
5, 6, 7, 32, 33, 34, 43, 66, 67
```

Important: keep anatomy labels conservative until probe orientation and exact
site order are confirmed.

## 4. Extract And Analyze LFP

Main scripts used in the Dec 3 pass:

```bash
python analysis/extract_lfp.py
python analysis/event_aligned_lfp.py
python analysis/artifact_aware_lfp.py
python analysis/frequency_lfp.py
python analysis/time_frequency_lfp.py
python analysis/trial_level_stats_dec3.py
python analysis/off_control_broadband_dec3.py
python analysis/broadband_transition_stats_dec3.py
python analysis/adaptation_analysis_dec3.py
python analysis/phase_locking_lfp.py
python analysis/reference_sensitivity_lfp.py
```

For a new session, either parameterize these scripts or copy them to a
session-specific version and change:

- input/output folders
- condition names
- bad-channel list
- reference strategy
- trial-window definitions
- whether a figure is exploratory all-channel output or final
  bad-channel-excluded/referenced output

## 5. Spike Sorting Prep

Prepare metadata and trial windows:

```bash
python analysis/prepare_spike_sorting_dec3.py
python analysis/setup_spikeinterface_dec3.py
```

Optional smoke test:

```bash
python analysis/run_spikeinterface_test_sort_dec3.py
```

This verifies that the raw binary can be opened and that a sorter backend can
run on a small segment. It is not final spike sorting.

## 6. Kilosort / Modal

For GPU Kilosort on Modal:

```bash
bash analysis/stage_dec3_for_modal.sh
modal run analysis/modal_kilosort_dec3.py
```

For Phy/noVNC review:

```bash
modal run analysis/modal_phy_dec3.py
```

Large Kilosort arrays should stay local or in a data store. Commit only summary
tables, normal figures, and small metadata files.

## 7. Pynapple Exports

Export intervals:

```bash
python analysis/export_pynapple_dec3.py
```

After Kilosort, export spike trains:

```bash
python analysis/export_kilosort_pynapple_dec3.py
```

Pynapple is useful for interval-based spike counts and PETH-style analyses.

## 8. Spike ON/OFF Analysis

Run provisional Kilosort spike analysis:

```bash
python analysis/spike_peth_on_off_dec3.py
```

Run automated cluster-quality triage:

```bash
python analysis/cluster_quality_dec3.py
```

Run cleaner high-confidence spike subset:

```bash
python analysis/spike_peth_high_confidence_dec3.py
```

Final spike claims require Phy curation and rerunning the spike analysis on
curated good units.

## 9. Summarize Results

For each new session, create/update:

- supervisor summary
- major-images guide
- results dashboard
- open questions
- run log

For Dec 3 these are:

- `docs/DEC3_SUPERVISOR_SUMMARY.md`
- `docs/DEC3_MAJOR_IMAGES.md`
- `analysis/outputs/dec3/RESULTS_DASHBOARD.html`
- `docs/OPEN_QUESTIONS.md`
- `docs/DEC3_ANALYSIS_LOG.md`

## 10. What To Preserve In Git

Commit:

- scripts
- Markdown summaries
- CSV/JSON summary tables
- HTML report pages
- normal-sized PNG/JPG figures

Do not commit:

- raw `.dat` or `.rhd`
- large `.npy`/`.npz` arrays
- large Kilosort intermediates
- Phy cache folders
- full sorter working directories

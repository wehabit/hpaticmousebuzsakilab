# Haptic Mouse Analysis

This folder contains lightweight Python entry points for the Intan haptic stimulation
recordings. The first pass focuses on metadata, digital TTL pulse trains, and the
randomized stimulus schedule before loading the large `amplifier.dat` trace.

## Key Docs

For future sessions and reruns, start from:

- `../docs/RERUN_PIPELINE.md`

For Dec 3 presentation and interpretation, use:

For a supervisor-facing summary of findings, figures, tools, and pipeline, use:

- `docs/DEC3_SUPERVISOR_SUMMARY.md`
- `analysis/outputs/dec3/RESULTS_DASHBOARD.html`

For original study context and collaborator links, use:

- `../docs/STUDY_NOTES.md`
- `../docs/RESOURCES_AND_GUIDANCE.md`

## Dec 3 quick start

From the repository root:

```bash
python analysis/intan_haptic_summary.py \
  --session-dir "Haptic_Stim_session1_251203_143031" \
  --config "Haptic_Stim_session1_251203_143031/My log/cmd_config_1_Dec3rd.json" \
  --recording-start-offset-s 640 \
  --output-dir analysis/outputs/dec3
```

Outputs:

- `session_summary.json`: recording size, XML metadata, active digital channels, and
  stimulus alignment summary.
- `stimulus_config_schedule.csv`: one row per nonzero command from the randomized
  stimulus config.
- `stimulation_events.csv`: detected TTL pulse bursts with config columns joined by
  row order. For Dec 3 this is QC only; use `dec3_condition_sequence.csv` as the
  authoritative condition/trial table.
- `dec3_condition_sequence.csv`: authoritative schedule-derived ON/OFF trial
  table after applying the recording offset.
- `digital_edges_ch*.csv`: rising/falling sample indices for each parsed digital
  channel.

## Spike sorting and Pynapple

Kilosort/Pynapple setup notes are tracked in:

- `docs/KILOSORT_PYNAPPLE_PLAN.md`

Clean Kilosort4 environment files:

- `analysis/envs/kilosort4_dec3_gpu.yml`
- `analysis/envs/setup_kilosort4_dec3_gpu.sh`

Modal Kilosort files:

- `analysis/stage_dec3_for_modal.sh`
- `analysis/modal_kilosort_dec3.py`

Dec 3 trial timing can be exported as Pynapple intervals with:

```bash
python analysis/export_pynapple_dec3.py
```

Outputs go to:

- `analysis/outputs/dec3/pynapple_intervals/`

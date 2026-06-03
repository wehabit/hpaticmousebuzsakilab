# Haptic Mouse Analysis

This folder contains lightweight Python entry points for the Intan haptic stimulation
recordings. The first pass focuses on metadata, digital TTL pulse trains, and the
randomized stimulus schedule before loading the large `amplifier.dat` trace.

## Dec 3 quick start

From the repository root:

```bash
python analysis/intan_haptic_summary.py \
  --session-dir "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031" \
  --config "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_log/cmd_config_1_Dec3rd.json" \
  --recording-start-offset-s 640 \
  --output-dir analysis/outputs/dec3
```

Outputs:

- `session_summary.json`: recording size, XML metadata, active digital channels, and
  stimulus alignment summary.
- `stimulus_config_schedule.csv`: one row per nonzero command from the randomized
  stimulus config.
- `stimulation_events.csv`: detected TTL pulse bursts with config columns joined by
  row order. Check `alignment_warning` in the summary before treating labels as final.
- `digital_edges_ch*.csv`: rising/falling sample indices for each parsed digital
  channel.

## Spike sorting and Pynapple

Kilosort/Pynapple setup notes are tracked in:

- `analysis/KILOSORT_PYNAPPLE_PLAN.md`

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

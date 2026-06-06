# Dec 3 - TTL Timing & Data-Cleaning Report

Everything from the TTL/timing validation and the movement-based data-cleaning
decision, collected in one folder. Figures regenerate from:
`analysis/plot_ttl_lfp_overview_dec3.py`, `analysis/movement_from_raw_dec3.py`,
`analysis/movement_sensitivity_check_dec3.py` (and the preliminary
`movement_from_lfp_dec3.py`).

---

## 1. Study protocol & recording phases

| Phase | Recording time (s) | Time (min) | Duration |
|------|-------------------:|-----------:|---------:|
| Setup / pre-recording | 0 - 640 | 0.0 - 10.7 | ~10.7 min |
| **Baseline** | 640 - 1540 | 10.7 - 25.7 | **15 min** |
| **Stimulation** (1200 trials x 3s ON / 3s OFF) | 1540 - 8740 | 25.7 - 145.7 | **120 min** |
| **Post-experiment** | 8740 - 10540 | 145.7 - 175.7 | **30 min** |
| Tail | 10540 - 10644 | 175.7 - 177.4 | ~1.7 min |
| **Total recording** | | | **177.4 min** |

Stim start = **14:56:11 = 1540.0 s** (log-anchored, first main-stimulation command). Protocol = 15 + 120 + 30 = 165 min.

Figures: `1_session_timeline.png`, `2_ttl_lfp_context_and_trials.png`

---

## 2. TTL (accelerometer) <-> commanded ON-time alignment

1185 of 1200 trials (98%) have the accelerometer fire inside the commanded ON
window - i.e., TTL and ON time are aligned. Breakdown:

| Criterion | Count |
|---|---|
| First blip inside the 3 s ON window | 1185 / 1200 (98%) |
| First blip within 0.5 s of ON onset | 921 / 1200 (77%) |
| First blip within 0.2 s of ON onset | 636 / 1200 (53%) |
| No sensor blip at all (no detected vibration) | 15 / 1200 (1%) |

And alignment quality tracks the condition (tighter = stronger stimulation):

| Condition | aligned (blip in ON) | typical onset lag |
|---|---|---|
| amp250_freq26 | 200/200 | 58 ms (tightest) |
| amp180_freq26 | 200/200 | 124 ms |
| amp100_freq26 | 199/200 | 226 ms |
| amp250_freq5 | 195/200 | 298 ms |
| amp180_freq5 | 200/200 | 344 ms |
| amp100_freq5 | 191/200 | 326 ms |

## How precisely does the measured onset match the commanded ON start?

First sensor *toggle* in each ON window vs the commanded ON start. No trial is exactly aligned - there is always a physical delivery lag (median 175 ms), because the accelerometer only fires once the device actually vibrates. So the TTL is a delivery *validator*, not the onset clock.

| Tolerance | Trials |
|---|---|
| exactly 0 ms | 0 / 1200 |
| within 1 ms | 3 / 1200 |
| within 5 ms | 30 / 1200 |
| within 10 ms | 53 / 1200 |
| within 20 ms | 103 / 1200 |
| within 50 ms | 219 / 1200 |
| within 100 ms | 393 / 1200 |

Figure: `ttl_on_alignment_per_trial.png` · per-trial data: `ttl_onset_offset_alignment.csv`

Figures: `3_ttl_on_alignment_per_trial.png`, `4_accelerometer_active_threshold_examples.png`
(onset = first sensor *toggle*; the sensor toggles rapidly during vibration and is otherwise flat.)

---

## 3. Data cleaning - movement exclusion

**There is no real EMG or accelerometer signal in this recording** (the headstage
accelerometer was not saved). The "movement" measure is a **proxy** computed from
the neural data itself - buzcode's `EMGFromLFP` idea: when the animal moves, muscle
activity couples a common high-frequency (300-600 Hz) signal into all electrodes at
once, so the **cross-channel correlation of the high-frequency band** rises. It is a
surrogate for movement, not a measured EMG. Movement is read from each trial's
**OFF/rest window** (the ON window is contaminated by the vibration itself).
**121 / 1200 trials** were flagged (OFF-window proxy above the baseline "still" level).

`6_excluded_vs_kept_examples.png` shows the excluded vs kept trials: excluded trials
have large **synchronized** high-frequency bursts across all channels (movement-like);
kept trials are small and independent (still).

### Decision & caveats

- **It's a proxy, not ground truth.** Without a real accelerometer/EMG, we can't prove
  those 121 trials are animal movement (vs some other correlated high-frequency source).
  The example traces strongly suggest movement, but it's **unvalidated**.
- **It didn't match the other candidate signal** (the bit-7 stray toggles, r = 0.06) -
  so the two disagree, and neither is confirmed.
- That's why it's labeled a **"movement proxy" / "unvalidated,"** and why the real
  reassurance is the **sensitivity check**: excluding those trials **did not change the
  spike or LFP results** - so it doesn't actually matter whether the proxy is perfectly
  "movement," the conclusions hold either way.

Figures: `5_movement_proxy_raw.png`, `6_excluded_vs_kept_examples.png`
(`supp_movement_proxy_lfp_preliminary.png` = first attempt on the downsampled LFP; too
anti-aliased to trust, superseded by the raw-20kHz version.)

### Sensitivity check (the reassurance)

Headline results recomputed with the 121 movement-flagged trials removed. Spike
responsiveness stays **0/28 units (q<0.05)** either way; LFP ON-OFF pattern is preserved.

| condition | spike_delta_all | spike_delta_excl | spike_nResp_all | spike_nResp_excl | lfp_ONminusOFF_all | lfp_ONminusOFF_excl |
|---|---|---|---|---|---|---|
| amp250_freq26 | -0.199 | -0.175 | 0 | 0 | -1.069 | -1.791 |
| amp180_freq26 | -0.148 | -0.103 | 0 | 0 | -2.137 | -2.535 |
| amp100_freq26 | 0.041 | 0.047 | 0 | 0 | 1.055 | 0.632 |
| amp250_freq5 | -0.238 | -0.159 | 0 | 0 | -0.079 | -0.709 |
| amp180_freq5 | -0.141 | -0.129 | 0 | 0 | -2.014 | -2.766 |
| amp100_freq5 | -0.112 | -0.122 | 0 | 0 | -1.186 | -1.505 |

Figure: `7_movement_sensitivity.png`

---

## Files in this folder

- Figures: `1_*` ... `7_*` (+ `supp_*` preliminary)
- Tables (CSV): `ttl_on_alignment_condition_summary.csv`, `ttl_onset_offset_alignment_per_trial.csv`,
  `movement_per_trial.csv` (per-trial proxy + `moving` flag), `movement_sensitivity_by_condition.csv`

- `supp_provisional_probe_map_H12_UNRESOLVED.png` - PROVISIONAL probe geometry (built as ASSY-350-H12, 2x64). NOT confirmed: a surgery atlas figure says H7 (2x32, 250 um). Do not use for anatomy until Jun confirms the probe model. See `hpatic_analysis_review/`.

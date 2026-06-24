# Dec 3 + Dec 4 — LFP 1/f (aperiodic) slope across STATES

**Question:** is there a real bump at the stimulation frequency, or did the whole LFP
spectrum just broadly shift? The existing 1/f work tested only ON vs OFF trial
windows; it never compared the aperiodic fit against the **true pre-experiment
baseline** or **post-study** state. This adds that missing comparison and
decomposes each state's spectrum into:

- **aperiodic fit (slope + offset)** — a change here = *the whole spectrum broadly
  shifted* (state / E-I / broadband change);
- **residual above the fit at the driven frequency** — a peak here = *a real bump at
  the stimulation frequency.*

Script: [lfp_aperiodic_states_dec.py](../analysis/lfp_aperiodic_states_dec.py);
outputs in `analysis/outputs/cross_dataset_spike_compare/lfp_aperiodic_states/`.
Method (group-median reference, log-log `fit_aperiodic` over 3–120 Hz excluding
50/100 Hz line noise) matches [spectral_slope_itpc_dec4.py](../analysis/spectral_slope_itpc_dec4.py),
so the state slopes are comparable to the existing ON/OFF entrainment slopes.
Baseline/post are tiled into 3 s epochs (same windows as the spike state analysis);
PSDs are averaged per good channel per state; **95% bootstrap CIs over channels**.

## Answer: a narrowband bump, not a broad shift — and only in LEC at 50 Hz
### 1. The aperiodic 1/f does NOT shift across states
Slope and offset are flat from baseline through ON/OFF to post in **every**
region/session (CIs overlap; the log-log spectra superimpose —
`state_spectra_loglog.png`):

| region | aperiodic slope: baseline → ON → OFF → post |
|---|---|
| Dec 3 dHPC | −1.93 → −1.93 → −1.92 → −1.94 |
| Dec 4 dHPC | −1.92 → −1.91 → −1.94 → −1.94 |
| Dec 4 LEC | −1.49 → −1.50 → −1.52 → −1.50 |

Offset (broadband power level) is likewise unchanged. **So there is no sustained
broadband / spectral-tilt shift between the quiet state and stimulation.** Note this
also means the known Dec 3 broadband response is a **transition-weighted transient**
(onset/offset), not a sustained aperiodic-offset elevation across the 3 s ON window.

### 2. Endogenous rhythms are state-invariant
The hippocampal **~6–7 Hz theta** peak (dHPC) and the **~30–40 Hz gamma** shoulder
(LEC) are present *equally* at baseline and during stimulation — they are not
stimulus-driven.

### 3. The only stimulus-locked spectral feature: the LEC 50 Hz bump
The residual above the 1/f fit (log10 power) at the driven frequency, by state:

| Dec 4 region · freq | baseline | ON | OFF | post |
|---|---|---|---|---|
| **LEC · 50 Hz** | +0.13 | **+0.32** | +0.10 | +0.13 |
| dHPC · 50 Hz | +0.17 | +0.16 | +0.13 | +0.14 |
| dHPC · 26 Hz | +0.10 | +0.07 | +0.03 | +0.02 |

Only **LEC at 50 Hz** rises during ON (CI [+0.30, +0.34], clearly above the baseline
[+0.11, +0.15]) and **returns to baseline in OFF and post** — a genuine narrowband
peak that exists **only while the stimulus is on**. dHPC shows **no** ON-specific
bump at any driven frequency (its standing 50 Hz residual is identical across all
four states → not stimulus-driven). Figures: `dec4_bump_vs_broadshift.png`,
`dec3_bump_vs_broadshift.png`, `dec4_aperiodic_states.png`.

## What this means (and the caveat)
- **Dec 3:** broad/transient response, **no clean 5 or 26 Hz narrowband oscillation**
  — confirmed, now also against baseline/post (residuals flat across states).
- **Dec 4 LEC:** a **real narrowband 50 Hz peak above 1/f, locked to ON** — the new
  baseline/post comparison shows it is genuinely stimulus-state-locked (absent when
  the stimulator is off), not a hidden broad shift.
- **But treat the LEC 50 Hz LFP cautiously:** the dedicated artifact check
  ([DEC4_50HZ_ARTIFACT_CHECK.md](DEC4_50HZ_ARTIFACT_CHECK.md)) shows it is
  substantially stimulator **pickup** (disconnected channels carry ~6× tissue). So
  this is a "real narrowband peak during stimulation," **not** a proven neural
  oscillation. The standing baseline 50 Hz residual (~+0.13) is ambient/instrument;
  the ON jump is the stimulus-locked addition. Group-median referencing removes
  common-mode pickup, yet the ON bump persists — consistent with the existing
  residual>0 result.
- The **single-unit firing-rate** effect remains the cleaner neural evidence; this
  LFP analysis characterises the **spectral state**, and the within-trial ON/OFF
  remains the strongest stimulation-locked contrast.

## One-line takeaway
Across baseline/ON/OFF/post the aperiodic 1/f is **stable** (no broad shift); the
**only** state-locked spectral feature is the **LEC 50 Hz narrowband bump during ON**
(stimulus-locked, but artifact-suspect). dHPC follows no frequency.

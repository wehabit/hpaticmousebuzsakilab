# Dec 3 + Dec 4 — Single-Unit Firing vs TRUE Baseline & Post-Study

The ON/OFF analyses ([DEC4_SPIKE_ONOFF_RESULT.md](DEC4_SPIKE_ONOFF_RESULT.md))
contrast each 3 s ON window with the immediately-following 3 s OFF window. That
OFF window is the within-trial control — **not** a neutral baseline. This analysis
adds the two reference states that bracket the protocol and were always present in
the recording but never used:

- **PRE-experiment baseline** — quiet recording *before the first trial*
- **POST-study** — quiet recording *after the last trial*

Both are tiled into 3 s epochs (same length as ON/OFF) so rates are directly
comparable in Hz. Script:
[spike_baseline_poststudy_compare_dec.py](../analysis/spike_baseline_poststudy_compare_dec.py);
outputs in `analysis/outputs/cross_dataset_spike_compare/baseline_poststudy/`.
Tests are Mann-Whitney U (unpaired), BH-corrected within each dataset × comparison.

## The reference windows actually exist (and are large)
| dataset | pre-baseline | trials | post-study |
|---|---|---|---|
| Dec 3 dHPC | 0–1540 s (**25.7 min**) | 1540–8740 s | 8740–10644 s (**31.7 min**) |
| Dec 4 dHPC | 0–2787 s (**46.4 min**) | 2787–17187 s | 17187–18136 s (**15.8 min**) |
| Dec 4 LEC | 0–2787 s (**46.4 min**) | (same) | (same, **15.8 min**) |

(First 60 s and last 30 s trimmed for settling/end-of-file; a 30 s gap left around
the trial block. Baseline = 483–898 epochs, post = 296–614 epochs per dataset.)

## Headline
**Adding a true baseline does not overturn the ON/OFF results — it strengthens the
dHPC up-drive and exposes a session-long firing DRIFT (mild in dHPC, large in LEC).**

| dataset | baseline | ON (all) | OFF (all) | post | drift base→post |
|---|---|---|---|---|---|
| dataset | baseline | ON | OFF | post | drift base→post (95% boot CI) |
|---|---|---|---|---|---|
| Dec 3 dHPC | 6.46 Hz | 6.01 | 6.15 | 6.08 | −0.38 Hz / **−6 %** ([−0.88, +0.10] — n.s.) |
| Dec 4 dHPC | 5.58 Hz | 5.78 | 5.74 | 5.39 | −0.20 Hz / **−4 %** ([−0.68, +0.20] — n.s.) |
| Dec 4 LEC | 3.99 Hz | 3.38 | 3.38 | 2.96 | −1.03 Hz / **−26 %** ([−2.04, −0.20] — **CI excludes 0**) |

Population effects use **percentile bootstrap 95% CIs** over units (B=10 000); the
per-unit Mann-Whitney counts below are inflated by the large epoch n, so the CIs are
the honest population inference. The sharper read: **only LEC's drift (and its
below-baseline OFF) is significant**; dHPC's mild drift CIs span zero.

Figures (with bootstrap-CI error bars), copied to the results tree:
`results/dec3/11_Spikes/dec3_states_vs_baseline.png`,
`results/dec4/11_Spikes/dec4_states_vs_baseline.png`,
`results/dec4/11_Spikes/dec4_freq50_vs_baseline.png`.

## What the baseline reference adds

### 1. The within-trial ON/OFF contrast is drift-immune — so the original result stands
The drift is **slow** (hours-scale, baseline→post). ON and OFF are **adjacent 3 s
windows**, so the drift is negligible *within* a trial. The documented 50 Hz ON/OFF
effects are a local contrast and therefore unaffected by the drift. This is the
reassuring result: the missing baseline did **not** invalidate anything.

### 2. dHPC 50 Hz up-drive is confirmed ABOVE baseline, and is amplitude-graded
Referenced to the true baseline, dHPC ON rises with amplitude — the clean
dose-response the OFF-only contrast only hinted at:

| Dec 4 dHPC, 50 Hz | amp100 | amp180 | amp250 |
|---|---|---|---|
| ON − baseline | +0.01 | +0.22 | **+1.05 Hz** |
| OFF − baseline | +0.13 | +0.22 | +0.27 Hz |

So the strongest condition (amp250_freq50) drives dHPC units **~1 Hz above their own
pre-experiment baseline**, and the OFF window partially recovers toward baseline.
The up-drive is a genuine elevation, not an OFF-window artifact.

### 3. LEC 50 Hz: ON *and* OFF both sit below baseline — two consequences
At 50 Hz the LEC population is **suppressed below baseline in both ON and OFF**
(≈ −0.6 to −0.75 Hz, flat across amplitude):

| Dec 4 LEC, 50 Hz | amp100 | amp180 | amp250 |
|---|---|---|---|
| ON − baseline | −0.57 | −0.75 | −0.70 Hz |
| OFF − baseline | −0.58 | −0.55 | −0.65 Hz |

- **The ON/OFF contrast under-reports LEC modulation.** Because the OFF window is
  *also* suppressed, the ON−OFF delta (≈ −0.08 Hz) hides most of the effect — the
  LEC suppression is **sustained across the whole trial**, not confined to ON.
- **But LEC also drifts down −26 % over the session**, so the below-baseline level
  cannot be cleanly attributed to stimulation vs drift. Unlike dHPC's
  amplitude-graded up-drive, the LEC suppression is **flat across amplitude** —
  consistent with a drift-dominated offset plus a small within-trial component. For
  LEC, the **drift-immune local ON/OFF contrast remains the trustworthy measure**;
  the baseline analysis's value here is exposing the drift and the OFF contamination.

## The OFF window is provably not neutral — but only LEC's gap is significant
Two views agree. Per-unit (high-powered, ~500–900 epochs) Mann-Whitney finds OFF ≠
baseline in **most units** (Dec 3 dHPC 23/29; Dec 4 dHPC 13/15; Dec 4 LEC 13/15 at
q<0.05) — but those counts are inflated by epoch n. The **population bootstrap** is
the honest test: OFF − baseline = **−0.31 Hz [−0.70, +0.06] (dHPC, n.s.)**,
**+0.15 [−0.12, +0.40] (Dec 4 dHPC, n.s.)**, **−0.60 [−1.19, −0.13] (LEC, CI excludes
0)**. So at the population level **only LEC's OFF sits significantly below baseline**.
The per-unit gaps **share the sign of the drift** (post − baseline) in 24/29, 11/15,
10/15 units — i.e., the OFF≠baseline gap is largely the **slow drift**, not buzz
carry-over (LEC being the exception where
sustained suppression and drift are entangled).

## Bottom line / what changes
- **No prior conclusion is overturned.** The 50 Hz ON/OFF single-unit findings are a
  local contrast and survive the baseline check.
- **Strengthened:** dHPC's amplitude-graded up-drive is now anchored to true
  baseline (+1.05 Hz at amp250_freq50).
- **New caveat:** a **session-long downward firing drift** is present — mild in dHPC
  (−4 to −6 %), **substantial in LEC (−26 %)**. Any analysis that compares across
  distant timepoints (not ON/OFF) must regress out this drift. It also means the
  within-trial OFF window is **not** a neutral baseline, only a drift-immune local
  control.
- **For LEC specifically:** the OFF window is itself suppressed, so the true LEC
  50 Hz suppression is larger than the ON−OFF delta suggests — but is partly
  confounded with the drift until a stimulus-locked or drift-corrected measure is
  available (next-round recorded-stimulus reference).

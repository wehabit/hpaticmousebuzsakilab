# Dec 4 — Drift-Corrected Condition Model (dHPC + LEC)

Does the 50 Hz single-unit effect survive after explicitly removing the slow
session drift? The model (the one you proposed):

    firing rate  ~  slow time drift (degree-5 time polynomial)
                    + state(ON/OFF) + freq + amp + state:freq

fit per dataset with the rate **demeaned per unit**, coefficient CIs by **cluster
bootstrap over units** (resample units, refit), reported **with vs without** the
drift term. Script: [drift_corrected_model_dec.py](../analysis/drift_corrected_model_dec.py).

## Why this is identifiable: the design is fully interleaved
Every condition's 200 trials span the whole session, and
**corr(trial time, freq) = 0.01**, corr(time, amp) = 0.02. So the slow drift and the
condition factors are **statistically orthogonal** — the model can separate them
cleanly (a blocked design could not).

## Result: the 50 Hz effect is UNCHANGED by drift correction
Key coefficients (Hz), no-drift vs with-drift model:

| dataset | coefficient | no drift | with drift |
|---|---|---|---|
| dHPC | **freq50** (main) | +0.169 [0.075, 0.265] | **+0.164 [0.065, 0.267]** |
| dHPC | state:freq50 (ON−OFF) | +0.162 [−0.12, 0.50] | +0.165 [−0.12, 0.46] |
| LEC | **freq50** (main) | +0.043 [−0.003, 0.094] | **+0.050 [0.003, 0.108]** |
| LEC | state:freq50 (ON−OFF) | −0.182 [−0.46, 0.08] | −0.182 [−0.44, 0.09] |

The condition coefficients are **essentially identical with and without the drift
term** (e.g. dHPC freq50 0.169 → 0.164; LEC state:freq50 −0.182 → −0.182). That is the
proof: because the design is interleaved, **the 50 Hz effect is not a drift
artifact** — modeling the drift does not change it. The **freq50 main effect is
robust** (dHPC clearly, LEC marginally, CI excludes 0 with drift).

## But the drift is real and large — it just doesn't contaminate the conditions
Adding the drift term **increased the model R²** from 0.0016→0.0048 (dHPC) and
**0.0004→0.0067 (LEC, ~16×)** — the slow drift explains *more* structured
single-trial variance than the stimulation conditions do, especially in LEC. So the
drift must be modeled (it dominates the slow structure), but once it is, the
condition effects stand unchanged.

## Notes / caveats
- The `state:freq50` interaction is **pooled over amplitudes** here, which dilutes the
  headline **amp250_freq50** effect (the +0.79 Hz dHPC up-drive seen in the
  [single-unit ON/OFF](DEC4_SPIKE_ONOFF_RESULT.md)); pooled, its CI spans 0. The
  amplitude-resolved effect is the strong one.
- Single-trial spike-count variance is high, so model R² is small in absolute terms
  (expected); the point is coefficient **stability** and the **freq50 main effect**,
  not variance explained.

## Takeaway
The interleaved design makes drift and condition **orthogonal**, and the
drift-corrected model confirms the **50 Hz single-unit effect survives drift
correction unchanged** — directly answering the "is it just the LEC drift?" concern.
The drift is genuinely large (especially LEC) but separable; the **drift-immune
within-trial ON/OFF** and this drift-corrected model agree.

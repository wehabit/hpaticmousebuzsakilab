# Dec 3 + Dec 4 — Early / Middle / Late Adaptation (anchored to baseline)

Splits each condition's repeats into early/middle/late thirds (by trial order) and
answers three questions the static state analyses can't. Spike effects are
referenced to each unit's pre-experiment baseline; LFP driven power is dB vs the
baseline PSD; bootstrap 95% CIs (units for spikes, channels for LFP). Script:
[adaptation_states_dec.py](../analysis/adaptation_states_dec.py).

## 1. Does the 50 Hz single-unit response GROW or FADE? → it does not fade
Dec 4, amp250_freq50, firing change (Hz) by third:

| | early | middle | late |
|---|---|---|---|
| **dHPC ON − OFF** (drift-immune) | +1.12 | +0.43 | +0.81 |
| dHPC ON − baseline | +1.29 | +0.85 | +1.04 |
| **LEC ON − OFF** (drift-immune) | +0.07 | −0.18 | −0.04 |
| LEC ON − baseline | −0.35 | −0.75 | −0.99 |

- **dHPC up-drive is sustained** — ON−OFF stays positive across all thirds (no
  habituation of the single-unit drive).
- **LEC's growing below-baseline is the session DRIFT, not adaptation**: ON−baseline
  gets more negative (−0.35 → −0.99), but ON−OFF (drift-immune) is flat near 0. So the
  apparent "growing suppression" is the slow drift, confirmed by the local contrast
  being stable.

## 2. Does the OFF window drift TOWARD or AWAY from baseline? → away, in LEC
OFF − baseline by third: **LEC −0.42 → −0.58 → −0.96** (progressively further below
baseline) — the OFF window does **not** return toward baseline; it tracks the
monotonic downward drift. dHPC OFF stays near baseline throughout (+0.17 → +0.41 →
+0.23). This nails the drift as a genuine session-long, largely LEC phenomenon.

## 3. Does 26 Hz adaptation explain Dec 3? → yes, the LFP response habituates
Driven-band LFP power (dB vs baseline) by third:

| condition | early | middle | late |
|---|---|---|---|
| **Dec 3 dHPC · 26 Hz** | +0.06 | −0.32 | −0.39 |
| Dec 4 LEC · 50 Hz | +2.88 | +2.34 | +1.26 |
| Dec 4 dHPC · 50 Hz | −0.32 | −0.27 | −0.44 |

- **Dec 3 26 Hz habituates:** the response is at/above baseline early and falls *below*
  baseline by middle/late — a clear adaptation, consistent with the
  transition-weighted, non-sustained Dec 3 LFP response. So **26 Hz adaptation is a
  real contributor** to why Dec 3 shows a broad/transient rather than a sustained
  oscillatory response.
- **LEC 50 Hz also fades** (+2.9 → +1.3 dB) — habituation or a slowly declining
  artifact coupling — but stays **strongly elevated throughout**, so the ON-locked
  50 Hz peak is robust even as it adapts.
- dHPC 50 Hz never elevates (flat-negative = drift).

## Takeaway
The 50 Hz **single-unit** effect does **not** fade (dHPC up-drive sustained; LEC's
growing deficit is drift, not adaptation). The **LFP** driven responses **do** adapt —
Dec 3's 26 Hz habituates (helping explain its transient character), and LEC's 50 Hz
fades but stays large. The OFF window drifts **away** from baseline in LEC, confirming
the session-long drift and reinforcing that the **drift-immune within-trial ON/OFF**
is the measure to trust.

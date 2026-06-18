# Dec 3 — Curated Spike ON/OFF Result

Re-ran the ON-vs-OFF single-unit analysis on the **29 curated good units**
(19 automated high-confidence + 10 human/analysis-verified rescues), compared to
the original automated **19**. Control = each trial's following 3 s OFF window.
Script: [spike_peth_curated_dec3.py](../analysis/spike_peth_curated_dec3.py);
outputs in `analysis/outputs/dec3/spike_peth_curated/`.

## Headline
**Curation does not change the spike conclusion.** Both sets show **zero
BH-corrected significant ON-vs-OFF unit/condition effects** (q<0.05): 0/19 and
0/29. The cleaner, larger curated set did **not** rescue a hidden single-unit
firing effect. The pre-curation null is now confirmed *post*-curation.

## Directional observation (not significant)
Across the 29 curated units, mean ON−OFF firing trends **negative and grows more
negative with amplitude** — i.e. units fire *less* during ON than during the
following OFF window, increasingly so at high amplitude:

| condition | mean ON−OFF (Hz) | units ON>OFF | units ON<OFF |
|---|---|---|---|
| amp100_freq26 | +0.04 | 19 | 10 |
| amp100_freq5  | −0.12 | 9  | 20 |
| amp180_freq26 | −0.16 | 8  | 21 |
| amp180_freq5  | −0.15 | 12 | 17 |
| amp250_freq26 | −0.20 | 12 | 17 |
| amp250_freq5  | −0.25 | 6  | 23 |

## Interpretation (careful)
- None of this survives correction, so it is a *trend*, not a claim.
- "ON < OFF" must be read against the known caveat that the **3 s OFF window is
  not a neutral baseline** — for the high-amplitude conditions the OFF/recovery
  period is itself elevated (the broadband LFP recovery effect). So the negative
  deltas are consistent with the **population/recovery story** (activity carries
  into OFF), not necessarily active ON-suppression.

## Why this matters
The fear was that the "no single-unit effect" null was an artifact of using only
the conservative 19 pre-curation. It is not: with 29 curated single units the
null holds. So the Dec 3 story stands — a real **LFP/population broadband +
recovery** response with **no clean single-unit firing-rate modulation**, even
after curation.

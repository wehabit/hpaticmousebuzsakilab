# Dec 3 + Dec 4 — Sharp-Wave Ripples Across States (dHPC)

**Hippocampal physiology — secondary to the haptic 50 Hz result.** We make **no**
sharp-wave-ripple (SWR) memory/consolidation claims; this is a descriptive
characterization with explicit caveats. Script:
[ripple_states_dec.py](../analysis/ripple_states_dec.py); outputs in
`analysis/outputs/cross_dataset_spike_compare/ripples/`.

## Method
- **Data-driven ripple channel:** the dHPC good channel with the highest 100–250 Hz
  RMS over the quiet baseline (Dec 3 → ch 8; Dec 4 → ch 7). The presence of real
  ripples supports CA1/dHPC placement by Vöröslakos's criterion; exact laminar/site
  order is still not assigned.
- **Detection:** 100–250 Hz band-pass → Hilbert envelope → 8 ms smooth → robust z;
  peak > 5 SD, edges > 2 SD, 15–200 ms, merge < 30 ms apart.
- Assign each event to **baseline / ON / OFF / post**; report **rate / amplitude /
  duration** per state (bootstrap 95% CIs), plus single-unit **ripple participation**
  by putative cell type.

## The detector finds real ripples
| session | ripple ch | n ripples | median amp | median dur |
|---|---|---|---|---|
| Dec 3 dHPC | 8 | 5 854 | 6.3 z | 49.6 ms |
| Dec 4 dHPC | 7 | 10 393 | 6.3 z | 50.4 ms |

~50 ms duration and ~0.5 events/s are textbook SWR values.

## Headline: interneurons are strongly recruited — validating both detector & cell types
Single-unit **in-ripple / out-ripple firing ratio** by putative type:

| session | pyramidal-like | interneuron-like |
|---|---|---|
| Dec 3 | 1.28 [0.96, 1.60] | **2.50 [2.01, 2.90]** |
| Dec 4 | 1.50 [1.21, 1.83] | **2.55 [1.85, 3.00]** |

Interneuron-like units fire **~2.5×** more during ripples than outside, vs ~1.3–1.5×
for pyramidal-like — the canonical ripple signature (fast-spiking interneurons are
strongly engaged in SWRs). This **independently cross-validates two analyses**: the
ripple detection is finding real ripples, and the
[cell-type labels](DEC_CELLTYPE_CLASSIFICATION.md) behave as their type predicts.

## Stricter artifact control: ON ripples by stimulus frequency — the harmonic concern is refuted
50 Hz stimulus harmonics (100/150/200/250 Hz) fall in the ripple band, so a genuine
harmonic artifact would **inflate the 50 Hz-ON ripple rate specifically**. We split
the ON ripple rate by stimulus frequency (`ripple_on_rate_by_stim_freq.png`):

| Dec 4 dHPC | 5 Hz | 10 Hz | 26 Hz | **50 Hz** | ON excl. 50 | baseline |
|---|---|---|---|---|---|---|
| ON ripple rate (/s) | 0.61 | 0.64 | 0.56 | **0.37** | 0.60 | 0.45 |

The **50 Hz-ON rate is the *lowest*, not the highest** — the opposite of what a
harmonic artifact would produce. So the elevated ON ripple rate is **not** a 50 Hz
harmonic artifact. Two readings of the 50 Hz dip, both honest: 50 Hz stimulation may
**genuinely suppress ripples** (an active/aroused state suppresses SWRs), or the
strong 50 Hz pickup during freq50 raises the envelope floor and lowers detection
sensitivity. Either way, the harmonic-inflation concern is controlled — and the clean
**ON-excluding-50 Hz** rate (0.60/s) is the value to compare with baseline. (Dec 3
has no 50 Hz; its 5/26 Hz-ON rates both sit at baseline.)

## Ripple rate tracks session-long quiescence, not clearly stimulation
Ripple rate is **lowest at baseline and rises through the session**, peaking post
(Dec 3: 0.50 → 0.50 → 0.54 → **0.72**; Dec 4: 0.45 → 0.55 → 0.64 → 0.64 events/s,
baseline/ON/OFF/post). This parallels the **session-long firing drift toward
quiescence** found in [DEC_BASELINE_POSTSTUDY_STATES.md](DEC_BASELINE_POSTSTUDY_STATES.md)
(more SWRs as the animal settles), so it is best read as a **state / drift** effect,
not a stimulation effect. **ON is not suppressed** relative to baseline. Ripple
amplitude (~6.3 z) and duration (~50 ms) are flat across states.

## Caveats (state plainly)
- **CA1/dHPC placement is functionally supported** by ripple physiology, but exact
  CA1 pyramidal layer/contact assignment remains conservative. Layer-specific SWR
  claims need orientation/histology or equivalent site-order confirmation.
- **dHPC only** — ripples are a CA1 event; LEC is not the canonical ripple structure.
- **ON-state 50 Hz-harmonic caveat — now controlled** (see "Stricter artifact
  control" above): the 50 Hz-ON rate is the *lowest* of all frequencies, the opposite
  of harmonic inflation, so ON-state counts are not harmonic-faked. Use the
  ON-excluding-50 Hz rate for the clean ON comparison.
- The baseline→post rate rise is **confounded with the session drift** — we do not
  claim a stimulation-specific ripple effect.

## Takeaway
Real ripples are detected (interneuron recruitment confirms them), supporting the
dHPC/CA1 functional placement criterion; ripple **rate** follows the session-long
quiescence drift rather than stimulation, and ripple **amplitude/duration** are
state-stable. **No SWR/memory claims** beyond it.

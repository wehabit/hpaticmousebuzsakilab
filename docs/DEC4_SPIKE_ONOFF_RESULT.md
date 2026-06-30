# Dec 4 — Single-Unit ON/OFF Result (and cross-dataset comparison)

Curated single-unit ON-vs-OFF firing analysis on all three datasets. For each
**curated good** unit, ON-window vs the following OFF-window firing rate is
compared per condition (paired t over the 200 trials/condition; BH-corrected
*within* each dataset). Scripts:
[spike_curated_compare_dec.py](../analysis/spike_curated_compare_dec.py)
(engine: [spike_peth_on_off_dec3.py](../analysis/spike_peth_on_off_dec3.py));
outputs in `analysis/outputs/cross_dataset_spike_compare/`.

## Headline
**Dec 4 shows the interpretable single-unit effect at 50 Hz and high amplitude,
in BOTH regions.** Do not treat the 5, 10, or 26 Hz conditions as biological
negatives in this dataset; those delivered signals were not clean enough for
frequency-specific interpretation.

| dataset | curated good units | unit×condition tests | responsive (q<0.05) | where they concentrate |
|---|---|---|---|---|
| Dec 3 dHPC | 29 | 174 (6 cond) | **0** | — (only poor-delivery 5/26 Hz tested; do not interpret as biological null) |
| Dec 4 dHPC | 15 | 180 (12 cond) | **19** | **15/19 at 50 Hz** (peak amp250_freq50: 9 units) |
| Dec 4 LEC | 15 | 180 (12 cond) | **13** | **8/13 at 50 Hz** (amp180/amp250_freq50) |

Responsive counts by drive frequency:
- **dHPC** — 5 Hz: 0, 10 Hz: 0, 26 Hz: 4, **50 Hz: 15**
- **LEC** — 5 Hz: 1, 10 Hz: 0, 26 Hz: 4, **50 Hz: 8**

Important: the 5, 10, and 26 Hz count rows are bookkeeping only. Because the
delivered signals at those frequencies were not good, they should not be used to
argue that the brain "did not respond" at 5/10/26 Hz.

The strongest single condition is **dHPC amp250_freq50** (9 responsive units,
mean ON−OFF **+0.79 Hz**) — highest frequency × highest amplitude.

## Why this matters
- **It reframes the Dec 3/low-frequency result:** Dec 3 only delivered 5 and 26 Hz,
  and Dec 4's 5/10/26 delivery quality was poor. These conditions are therefore not
  valid biological nulls. The defensible positive statement is narrower: the cleanest
  interpretable response in the current dataset is at **50 Hz / high amplitude**.
- **It is coherent across levels and regions.** The LFP analysis found an
  amplitude-graded **50 Hz** power increase in LEC, although that LFP peak is
  pickup-contaminated and not proof of entrainment. Here the **single-unit** ON/OFF
  responses also pile up at 50 Hz / high amplitude — in LEC *and* dHPC. Different
  measurement (spikes vs LFP), same frequency/amplitude regime.

## Caveats
- It is a **modest fraction** of tests (≈7–11%), and BH controls FDR at 5%, so a
  few of those are expected false — but the **concentration at 50 Hz** (15/19 and
  8/13) is far from the uniform spread chance would give, so the *50 Hz signal*
  is real even if individual units aren't all real.
- **Stimulus-fidelity confound (low frequencies).** The delivered vibration was
  **not a clean sine wave at 5 / 10 / 26 Hz** (the actuator did not produce clean
  low-frequency sinusoids; 50 Hz was delivered more cleanly). So we should not claim
  that the brain prefers 50 Hz over 5/10/26 Hz from this dataset alone. The current
  result supports 50 Hz target engagement; it does **not** establish a clean
  frequency-response curve across 5, 10, 26, and 50 Hz.
- **Direction is mixed** (a subset of units go up, a subset down; e.g. amp250_freq50
  dHPC = 8 up / 7 down with a few strong up-units dominating the mean). This is
  *selective modulation of a subset*, not a uniform population drive.
- Dec 4 trial timing comes from the controller-log offset (no TTL); imprecise
  timing would *blur* effects, not create a frequency-specific concentration, so
  the 50 Hz pattern is trustworthy.
- Still an ON-vs-OFF contrast; the OFF window is the within-trial control, not a
  neutral baseline. We now checked this directly against the **true pre-experiment
  baseline and post-study** windows (25–46 min each, always in the recording; see
  [DEC_BASELINE_POSTSTUDY_STATES.md](DEC_BASELINE_POSTSTUDY_STATES.md)). The ON/OFF
  contrast is a *local* (adjacent 3 s) measure and is **immune to the slow,
  session-long firing drift** the baseline reference exposes — so this result
  stands. The baseline reference also **strengthens** the dHPC up-drive (ON sits
  **+1.05 Hz above baseline** at amp250_freq50, amplitude-graded) and shows the LEC
  50 Hz suppression is **sustained into the OFF window** (so ON−OFF *under*-reports
  it) — though LEC also drifts down ~26 % over the session, so its below-baseline
  level is partly drift.

## Interpretation: what the 50 Hz response actually means
Figure: `analysis/outputs/cross_dataset_spike_compare/spike_50hz_interpretation.png`.

The question is whether the 50 Hz "response" is just one identical passive
artifact/readout of the stimulus, or whether the brain is **actively responding**.
Walking the inference ladder:

1. **Not (simply) electrical/mechanical artifact.** Sorted single units change their
   firing *rate* during 50 Hz ON vs OFF. The ~300 Hz spike high-pass removes the slow
   50 Hz LFP pickup before detection, and a curated unit's *rate* change is much
   harder for pickup to fake; the ACG / ISI / waveform screens (see
   [DEC4_50HZ_ARTIFACT_CHECK.md](DEC4_50HZ_ARTIFACT_CHECK.md)) argue against
   pickup-manufactured spikes. So there is a genuine neural response.
2. **Not one identical passive readout across regions.** A simple passive artifact
   would look the **same everywhere**. Instead the two regions respond with
   **different distributions** — at 50 Hz,
   **LEC units are predominantly suppressed** (~67% fire less; mean −0.08 Hz) while
   **dHPC shows a driven-up subset** (mean +0.22 Hz, a few units strongly increased).
   The LFP 50 Hz peak is a stimulus-state power increase rather than proof of
   entrainment, and it is artifact-suspect. Together with the opposite spike-rate
   directions, this points to the input being *transformed differently by each
   circuit*, not mirrored.
3. **→ Active, region-specific processing** is the supported reading: the 50 Hz
   input is handled differently by hippocampus vs entorhinal cortex.

**Does it show "the regions working together"? — We tested this; the answer is no
clear coordination.** Follow-up analysis (spike–field locking + cross-region 50 Hz
coherence; see [DEC4_COORDINATION_50HZ.md](DEC4_COORDINATION_50HZ.md)) found that
the **harder-to-fake spike** test — whether sorted neurons in one region lock to the
*other* region's 50 Hz rhythm (much harder for an LFP artifact to fake than the LFP
itself) — shows only very weak coupling that **does not increase** with stimulation. Cross-region *LFP* coherence does rise during ON, but
that is best explained by a **shared 50 Hz signal** (plausibly stimulus artifact),
not coordination. So: each region responds, but they do **not** demonstrably
coordinate. True stimulus phase-locking still needs the recorded stimulus (next
round).

**Caveat:** part of the rate change could be a strong-stimulus arousal/state effect
(amp250_freq50 is the most intense buzz). The frequency-specificity and movement
controls argue against pure arousal, but a state component can't be fully excluded.

## One-line takeaway
High-frequency (50 Hz), high-amplitude haptic stimulation drives a
**region-specific** single-unit response (dHPC driven-up subset; LEC suppressed)
in a frequency regime Dec 3 never tested. The response is not consistent with one
identical passive readout across regions, and the separate coordination test found
no clear evidence that dHPC and LEC work together at 50 Hz.

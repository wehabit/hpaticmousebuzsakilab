# Dec 4 — Single-Unit ON/OFF Result (and cross-dataset comparison)

Curated single-unit ON-vs-OFF firing analysis on all three datasets. For each
**curated good** unit, ON-window vs the following OFF-window firing rate is
compared per condition (paired t over the 200 trials/condition; BH-corrected
*within* each dataset). Scripts:
[spike_curated_compare_dec.py](../analysis/spike_curated_compare_dec.py)
(engine: [spike_peth_on_off_dec3.py](../analysis/spike_peth_on_off_dec3.py));
outputs in `analysis/outputs/cross_dataset_spike_compare/`.

## Headline
**Dec 3 showed no single-unit ON/OFF effect; Dec 4 does — and it concentrates at
50 Hz and high amplitude, in BOTH regions.**

| dataset | curated good units | unit×condition tests | responsive (q<0.05) | where they concentrate |
|---|---|---|---|---|
| Dec 3 dHPC | 29 | 174 (6 cond) | **0** | — (only 5/26 Hz tested) |
| Dec 4 dHPC | 15 | 180 (12 cond) | **19** | **15/19 at 50 Hz** (peak amp250_freq50: 9 units) |
| Dec 4 LEC | 15 | 180 (12 cond) | **13** | **8/13 at 50 Hz** (amp180/amp250_freq50) |

Responsive counts by drive frequency:
- **dHPC** — 5 Hz: 0, 10 Hz: 0, 26 Hz: 4, **50 Hz: 15**
- **LEC** — 5 Hz: 1, 10 Hz: 0, 26 Hz: 4, **50 Hz: 8**

The strongest single condition is **dHPC amp250_freq50** (9 responsive units,
mean ON−OFF **+0.79 Hz**) — highest frequency × highest amplitude.

## Why this matters
- **It explains the Dec 3 null:** Dec 3 only delivered 5 and 26 Hz, and at those
  frequencies there is essentially no single-unit ON/OFF modulation (0/174). Dec 4
  *added 10 and 50 Hz* — and the single-unit effect appears specifically at 50 Hz.
  So "no single-unit effect" was frequency-limited, not absolute.
- **It is coherent across levels and regions.** The LFP analysis found an induced,
  amplitude-graded **50 Hz** power increase in LEC; here the **single-unit** ON/OFF
  responses also pile up at 50 Hz / high amplitude — in LEC *and* dHPC. Different
  measurement (spikes vs LFP), same frequency/amplitude regime.

## Honest caveats
- It is a **modest fraction** of tests (≈7–11%), and BH controls FDR at 5%, so a
  few of those are expected false — but the **concentration at 50 Hz** (15/19 and
  8/13) is far from the uniform spread chance would give, so the *50 Hz signal*
  is real even if individual units aren't all real.
- **Direction is mixed** (a subset of units go up, a subset down; e.g. amp250_freq50
  dHPC = 8 up / 7 down with a few strong up-units dominating the mean). This is
  *selective modulation of a subset*, not a uniform population drive.
- Dec 4 trial timing comes from the controller-log offset (no TTL); imprecise
  timing would *blur* effects, not create a frequency-specific concentration, so
  the 50 Hz pattern is trustworthy.
- Still an ON-vs-OFF contrast; the OFF window is the within-trial control, not a
  neutral baseline.

## Interpretation: what the 50 Hz response actually means
Figure: `analysis/outputs/cross_dataset_spike_compare/spike_50hz_interpretation.png`.

The question is whether the 50 Hz "response" is just the stimulus being **passively
relayed/echoed** into the brain, or whether the brain is **actively responding**.
Walking the inference ladder:

1. **Not electrical/mechanical artifact.** Sorted single units change their firing
   *rate* during 50 Hz ON vs OFF — electrical pickup cannot make a curated neuron
   fire more/less. So there is a genuine neural response.
2. **Not a simple passive echo.** A passive relay would look the **same everywhere**.
   Instead the two regions respond with **different distributions** — at 50 Hz,
   **LEC units are predominantly suppressed** (~67% fire less; mean −0.08 Hz) while
   **dHPC shows a driven-up subset** (mean +0.22 Hz, a few units strongly increased).
   And the LFP 50 Hz is **induced, not phase-locked**. Both point to the input being
   *transformed differently by each circuit*, not mirrored.
3. **→ Active, region-specific processing** is the supported reading: the 50 Hz
   input is handled differently by hippocampus vs entorhinal cortex.

**What this does NOT show: "the regions working together."** Coordination
(neurons synchronizing, the two regions becoming more coupled, spikes locking to a
shared rhythm) was **not measured**. We showed *each region responds* and *they
respond differently* — not that they *coordinate*. Testing that needs **spike–field
coupling** and **cross-region coherence** (runnable on existing data), and true
stimulus phase-locking (needs the recorded stimulus — next round).

**Caveat:** part of the rate change could be a strong-stimulus arousal/state effect
(amp250_freq50 is the most intense buzz). The frequency-specificity and movement
controls argue against pure arousal, but a state component can't be fully excluded.

## One-line takeaway
High-frequency (50 Hz), high-amplitude haptic stimulation drives an **active,
region-specific** single-unit response (dHPC driven-up subset; LEC suppressed) —
**not a passive echo** — in a frequency regime Dec 3 never tested, matching the
50 Hz LFP effect. Whether the regions *coordinate* ("work together") is the next
test, not yet answered.

# Dec 4 — Do dHPC and LEC "work together" at 50 Hz?

Tests whether the 50 Hz single-unit response reflects **cross-region coordination**
("working together"), or just each region responding on its own. During 50 Hz ON
windows vs the matched OFF windows:
1. **within-region spike–field** locking (spikes vs own-region 50 Hz LFP phase),
2. **cross-region spike–field** locking (one region's spikes vs the *other*
   region's 50 Hz phase — *artifact-robust*, because sorted spikes won't lock to a
   pure LFP artifact),
3. **cross-region LFP–LFP 50 Hz coherence**.

Script: [spike_field_coordination_dec4.py](../analysis/spike_field_coordination_dec4.py);
figure: `analysis/outputs/dec4/coordination_50hz/coordination_50hz.png`.

## Results (mean spike–field PLV; LFP coherence)
| measure | 50 Hz ON | OFF | read |
|---|---|---|---|
| within dHPC spike→dHPC phase | 0.064 (11/15 units) | 0.057 (12/15) | weak, barely ON>OFF |
| within LEC spike→LEC phase | 0.044 (6/15) | 0.037 (8/15) | weak, barely ON>OFF |
| **cross** dHPC spike→LEC phase | 0.025 (6/15) | 0.024 (4/15) | very weak, **not** ON>OFF |
| **cross** LEC spike→dHPC phase | 0.021 (2/15) | 0.020 (2/15) | very weak, **not** ON>OFF |
| **LFP–LFP 50 Hz coherence** | **0.162** | **0.092** | rises with ON (chance ≈ 0.003) |

## The verdict: **no clear evidence the regions coordinate at 50 Hz**
There's an apparent contradiction, and it resolves cleanly:
- **The LFP–LFP coherence *rises* during 50 Hz ON** (0.16 vs 0.09) — which *looks*
  like the two regions coupling.
- **But the artifact-robust test disagrees:** sorted neurons in one region show
  only **very weak** locking to the *other* region's 50 Hz rhythm, and that locking
  **does not increase** during stimulation (ON ≈ OFF).

If the regions were genuinely coordinating, the cross-region *spike–field* coupling
should rise with stimulation. It doesn't. So the increased **LFP coherence is most
parsimoniously a shared 50 Hz signal common to both probes** — plausibly the
stimulus's own 50 Hz (electrical/mechanical, volume-conducted) rather than neural
coordination. LFP coherence is exactly the measure such a shared artifact inflates;
sorted spikes are not.

**So:** each region *actively responds* at 50 Hz (rate changes — see
[DEC4_SPIKE_ONOFF_RESULT.md](DEC4_SPIKE_ONOFF_RESULT.md)), but we find **no clear
evidence they "work together" / coordinate.** This also **re-raises the artifact
caveat** for the 50 Hz LFP: the shared cross-region coherence is consistent with a
50 Hz artifact component, so the LFP 50 Hz effect still warrants a dedicated
artifact check (the single-unit *rate* effect remains the cleanest neural evidence).

## Amplitude check (does pooling hide it?)
The single-unit *rate* effect was strongest at **amp250**, so coordination — if
real — should be clearest there. Re-running on **amp250_freq50 alone** (200 trials,
`coordination_50hz_amp250/`): the decisive cross-region **spike** test shows only a
**faint, non-compelling hint** of ON-elevation that pooling had washed out
(dHPC spk→LEC ϕ: 0.043 ON vs 0.031 OFF, 3/15 vs 1/15 units significant; the reverse
direction is flat, 0/15). PLVs stay ~0.04 and the 200-trial CIs are wide. LFP
coherence is larger still (0.27 vs 0.17) but remains the artifact-prone measure.
**Conclusion unchanged:** no compelling coordination even at the strongest
amplitude — at most a weak hint that needs more data / the recorded stimulus.

## Caveats
- Spike–field PLVs are **low in absolute terms** (~0.02–0.06); many units pass the
  Rayleigh test only because spike counts are large. Within-region 50 Hz (gamma)
  spike–field coupling existing at baseline (ON ≈ OFF) is normal for these circuits.
- The OFF window is the post-stim control, not a neutral baseline.
- Single animal; true *stimulus* phase-locking still needs the recorded stimulus
  (next round).

## One-line takeaway
dHPC and LEC each respond at 50 Hz, but the **artifact-robust cross-region spike
test shows no coordination** — the rise in LFP coherence is best explained by a
**shared 50 Hz signal**, not the regions "working together."

# Dec 4 — Dedicated 50 Hz LFP Artifact Check

The coordination analysis ([DEC4_COORDINATION_50HZ.md](DEC4_COORDINATION_50HZ.md))
left one question open: **is the LEC 50 Hz LFP power increase a genuine neural
signal, or electrical/mechanical pickup from the actuator?** We cannot test true
phase entrainment without a recorded stimulus channel (not available this session),
but four signatures separate a tissue-local *neural* 50 Hz from a volume-conducted
*artifact*. This is the dedicated check.

Script: [artifact_check_50hz_dec4.py](../analysis/artifact_check_50hz_dec4.py);
figure: [`analysis/outputs/dec4/artifact_check_50hz/artifact_check_50hz.png`](../analysis/outputs/dec4/artifact_check_50hz/artifact_check_50hz.png);
numbers: `analysis/outputs/dec4/artifact_check_50hz/artifact_check_summary.json`
(600 freq50 trials, 50 Hz envelope = 45–55 Hz band-pass + Hilbert, ON vs OFF window).

## The decisive test: do *disconnected* electrodes pick up 50 Hz?
A QC-bad / disconnected electrode **cannot record neural LFP** but **will** act as
an antenna for a volume-conducted electrical (or microphonic/mechanical) artifact.
The LEC probe has **45/128 dead channels** (incl. the dead block 224–255) — a
built-in artifact probe.

| channel group | 50 Hz ON − OFF (mean ± 95% CI) | read |
|---|---|---|
| dHPC tissue (127 ch) | **−0.99** (−1.5, −0.5) | **no 50 Hz rise** at all |
| LEC tissue (83 ch) | **+4.9** (+3.6, +6.3) | modest rise |
| **LEC DEAD (45 ch)** | **+28.4** (+19.2, +37.8) | **largest rise — on electrodes that can't see neurons** |

The disconnected LEC electrodes show a **5.8× larger** 50 Hz ON-rise than the
in-tissue LEC electrodes. Since those electrodes are not recording tissue, that
50 Hz can only be **non-neural pickup**. So **a real 50 Hz electrical/mechanical
artifact is present in the LEC probe during ON.**

## Three supporting signatures
- **dHPC is clean.** dHPC tissue shows essentially **no** 50 Hz LFP rise (−0.99),
  matching its established *no frequency-following* result. The pickup is LEC-probe
  specific, and dHPC's amplitude scaling is ~0 except a small amp250 bump
  (−4.1 / −1.2 / +7.8 for amp100/180/250).
- **Cross-region lag ≈ 0.** dHPC↔LEC 50 Hz coupling is **near-zero-lag**
  (−4.8°, **−0.26 ms**; coherence 0.22). A genuine neural cross-region interaction
  carries a conduction/synaptic delay; ~0 ms is the signature of **one shared
  signal** seen by both probes — corroborating the coordination conclusion.
- **Harmonics weak.** 100/150 Hz line prominence during ON is only 1.4 / 2.4 dB
  (vs ~0 at OFF) — present but *not* a sharp high-Q comb, so the artifact is not a
  clean electrical square-wave drive line (consistent with microphonic / broadband
  EM coupling rather than direct stimulator current injection).

## What this does — and does NOT — change
**Tempered:** the **LEC 50 Hz LFP power increase is at least contaminated by, and
may be substantially explained by, non-neural pickup.** The in-tissue rise (+4.9)
cannot be cleanly partitioned into neural vs artifact, so we should **stop treating
the LEC 50 Hz *LFP* effect as clean neural evidence.** (Note the in-tissue *relative*
rise ≈12% slightly exceeds the dead-channel relative rise ≈6%, so a neural component
is not excluded — but it is no longer separable here.)

**Unchanged — the clean evidence:** **single-unit firing-rate changes are immune
to this.** A floating electrode picking up 50 Hz cannot make a **sorted neuron**
fire more or less. The Dec 4 single-unit ON/OFF result (50 Hz / high-amplitude
rate modulation in both regions; see
[DEC4_SPIKE_ONOFF_RESULT.md](DEC4_SPIKE_ONOFF_RESULT.md)) therefore **stands as the
cleanest neural signature**, exactly as argued. The artifact-robust cross-region
**spike** test was already flat — consistent with this finding.

## Channel-QC audit: are the dead channels otherwise accounted for?
A follow-up audit checked whether dead/marginal channels contaminate results
anywhere *else*. The structural safeguards hold, but two honest caveats remain.

**Accounted for:**
- **Sorting excluded the dead channels.** Kilosort ran on dHPC `channel_map`=127 and
  LEC=83 (global 136–223); the dead 128–135 / 224–255 blocks were removed *before*
  sorting, so KS whitening/CAR never saw them and no units sit on them.
- **References exclude bad channels** (group-median LFP ref "bad ch excluded";
  coordination/artifact region-means over good channels only).
- **50 Hz is below the spike band** — the sort's ~300 Hz high-pass removes it before
  detection, so pickup cannot *create* spikes. No good channel flatlines.

**Caveat 1 — the 50 Hz pickup is a spatial gradient, not confined to flagged-dead
channels.** ~28 of the 83 "good" LEC channels (the deep half, **173–223**) carry
extreme 50 Hz power (robust-z 7–10), rising toward both dead blocks. So even the
LEC *good-channel* 50 Hz region-mean is dominated by near-dead-block pickup —
reinforcing that the LEC 50 Hz **LFP** should not be read as neural.

**Caveat 2 — all 15 curated good LEC units sit in that pickup zone** (peak channels
173–214; **zero** in the clean shallow region 136–172). We therefore cannot
spatially separate "where the LEC units are" from "where the 50 Hz pickup is." This
does **not** invalidate the single-unit rate result, because (i) the ~300 Hz
high-pass removes 50 Hz before detection; (ii) LEC units predominantly **suppress**
during ON — the *opposite* of what pickup-driven false detections would add; and
(iii) the dHPC driven-up subset occurs with **zero** pickup. It is a disclosure, not
a refutation.

**Minor:** an independent robust-z RMS sweep flagged one extra hot LEC channel,
**ch142** (RMS ~3.5× median, z=4.6), that escaped the original auto pass; it hosts
no curated good unit and its own 50 Hz rise is ~0, so excluding it shifts the LEC
50 Hz region-mean by only +1.2% (4.90→4.96). It has been added to the exclusion
lists (`bad_channels_dec4.json` → `post_hoc_qc_2026_06`) for future LFP region-means;
sorts were not re-run (no unit on it). The Dec-3 "hardware-fixed" dHPC channels are
the noisiest dHPC channels (~2× median) but not dead.

## Why the next round fixes it
This is precisely what the **recorded analog stimulus** (PVDF force sensor on the
shared 20 kHz clock) buys: with a continuous copy of the delivered vibration you can
**measure the artifact directly and regress/subtract it** from the LFP, and run a
true phase-entrainment test. See
[HARDWARE_ENG_MESSAGE_NEXT_ROUND.md](HARDWARE_ENG_MESSAGE_NEXT_ROUND.md).

## One-line takeaway
Disconnected LEC electrodes pick up **more** 50 Hz during ON than tissue does, with
~0 ms cross-region lag → there is a **real non-neural 50 Hz component** in the LEC
LFP; rely on the **single-unit rate change**, not the LFP, as the neural readout.

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

**Channel partition (clean 3-way).** dHPC: **good 127 / disconnected-dead 1** (ch121).
LEC: **good 82 / disconnected-dead 45 / hot-excluded 1** (ch142 — broadband-hot but
*live*, its own 50 Hz rise ≈0; see "Channel-QC audit" below). 82+45+1 = 128.

## The decisive test: do *disconnected* electrodes pick up 50 Hz?
A QC-bad / disconnected electrode **cannot record neural LFP** but **will** act as
an antenna for a volume-conducted electrical (or microphonic/mechanical) artifact.
The LEC probe has **45 disconnected channels** (incl. the dead block 224–255) — a
built-in artifact probe.

| channel group | 50 Hz ON − OFF (µV) | read |
|---|---|---|
| dHPC tissue (127 ch) | **−0.19** | **no 50 Hz rise** at all |
| LEC tissue (82 ch, ch142 excluded) | **+0.97** | modest rise |
| **LEC disconnected-dead (45 ch)** | **+5.54** | **largest rise — on electrodes that can't see neurons** |

(50 Hz = 45–55 Hz Hilbert envelope, ON−OFF; µV via Intan 0.195 µV/bit; ≈ −0.99 /
+4.9 / +28.4 in raw ADC units, the values in `artifact_check_summary.json`.)

The disconnected LEC electrodes show a **5.7× larger** 50 Hz ON-rise than the
in-tissue LEC electrodes. Since those electrodes are not recording tissue, that
50 Hz can only be **non-neural pickup**. So **a real 50 Hz electrical/mechanical
artifact is present in the LEC probe during ON.** Side-by-side dHPC-vs-LEC and
amplitude-resolved views:
[`gradient_dhpc_vs_lec.png`](../analysis/outputs/dec4/artifact_check_50hz/gradient_dhpc_vs_lec.png),
[`explainer_1_contamination.png`](../analysis/outputs/dec4/artifact_check_50hz/explainer_1_contamination.png).

## Three supporting signatures
- **dHPC is much cleaner — but not perfectly pickup-free.** dHPC tissue shows
  essentially **no** pooled 50 Hz LFP rise (−0.19 µV), matching its *no
  frequency-following* result. But amplitude-resolved, dHPC is negative at
  amp100/180 and shows a small **amp250** bump — and its *dead* channel (ch121)
  shows a **larger** amp250 bump than tissue (+1.7 vs +1.3 µV), proving that bump is
  **pickup too**, just **~5× smaller** than LEC's. So "dHPC is clean" holds at
  amp100/180; at amp250 it leaks a little. The pickup is LEC-*dominant*, not
  LEC-exclusive.
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

**Unchanged — the clean evidence:** **single-unit firing-rate changes are much
harder for LFP pickup to fake**, and the ACG / ISI / waveform screens (below) argue
against pickup-manufactured spikes: a 50 Hz LFP component is removed by the ~300 Hz
spike high-pass, and a curated unit's *rate* change is not something a floating
electrode readily produces. The Dec 4 single-unit ON/OFF result (50 Hz /
high-amplitude rate modulation in both regions; see
[DEC4_SPIKE_ONOFF_RESULT.md](DEC4_SPIKE_ONOFF_RESULT.md)) therefore **stands as the
cleanest neural signature**. The cross-region **spike** test (harder for pickup to
fake than the LFP) was already flat — consistent with this finding.

## Channel-QC audit: are the dead channels otherwise accounted for?
A follow-up audit checked whether dead/marginal channels contaminate results
anywhere *else*. The structural safeguards hold, but two caveats remain.

**Accounted for:**
- **Sorting excluded the dead channels.** Kilosort ran on dHPC `channel_map`=127 and
  LEC=83 (global 136–223 — this is *pre*-ch142 exclusion, so it includes ch142, which
  hosts no good unit; the 50 Hz region-means use the 82-good partition); the
  disconnected 128–135 / 224–255 blocks were removed *before* sorting, so KS
  whitening/CAR never saw them and no units sit on them.
- **References exclude bad channels** (group-median LFP ref "bad ch excluded";
  coordination/artifact region-means over good channels only).
- **50 Hz is below the spike band** — the sort's ~300 Hz high-pass removes the slow
  50 Hz waveform before detection, so 50 Hz pickup is much harder to turn into spikes
  (sharp transients / broadband leakage are the residual route, closed by the
  ACG/ISI screens below). No good channel flatlines.

**Caveat 1 — the 50 Hz pickup is a spatial gradient, not confined to flagged-dead
channels.** **~30 of the 82** "good" LEC channels (the deep half, **173–223**) carry
elevated 50 Hz (31 by robust-z>4 on 50 Hz power; 28 by a µV threshold — metric-
dependent, hence "~30"), rising toward both dead blocks. So even the LEC
*good-channel* 50 Hz region-mean is dominated by near-dead-block pickup — reinforcing
that the LEC 50 Hz **LFP** should not be read as neural.

**Caveat 2 — all 15 curated good LEC units sit in that pickup zone** (peak channels
173–214; **zero** in the clean shallow region 136–172). We cannot spatially separate
"where the LEC units are" from "where the 50 Hz pickup is." This does **not**
invalidate the single-unit rate result, for three reasons: (i) the ~300 Hz high-pass
removes the slow 50 Hz before detection; (ii) the LEC population **leans down** at
50 Hz (10 of 15 units, mean −0.08 Hz) — additive pickup *adds*, not removes, apparent
spikes, so it does not naturally produce suppression; and (iii) the **autocorrelogram
+ ISI screens** below clear the up-going units directly. It is a disclosure, not a
refutation.

**Minor:** an independent robust-z RMS sweep flagged one extra hot LEC channel,
**ch142** (RMS ~3.5× median, z=4.6), that escaped the original auto pass; it hosts
no curated good unit and its own 50 Hz rise is ~0, so excluding it shifts the LEC
50 Hz region-mean by only ~1% (≈+4.90→+4.96 ADC). Added to the exclusion lists
(`bad_channels_dec4.json` → `post_hoc_qc_2026_06`) for future LFP region-means; sorts
were not re-run (no unit on it). The Dec-3 "hardware-fixed" dHPC channels are the
noisiest dHPC channels (~2× median) but not dead.

## The autocorrelogram screen: is unit 87 (the soft spot) a real neuron or pickup?
The up-going LEC units near the pickup zone — chiefly **unit 87** (rises
dose-dependently, +0.91 / +1.17 / +2.14 Hz at amp100/180/250, on global ch181) — are
the one place where "is this pickup-manufactured?" can't be answered by direction
alone. So we ran the strongest spike-level artifact test there is, the same one you
would read in Phy: the **autocorrelogram (ACG)**. Script:
[unit87_phy_view_dec4.py](../analysis/unit87_phy_view_dec4.py); figure:
[`unit87_phy_view.png`](../analysis/outputs/dec4/artifact_check_50hz/unit87_phy_view.png).

**Screen 1 — the 20 ms comb.** A 50 Hz fake-spike source fires every **20 ms**, so
it would grow a **20/40 ms comb** in the ACG **during ON**. Unit 87 does not — its
ACG 20 ms ratio is **0.80 ON / 0.81 OFF** (identical, no comb), with a clean
refractory period (**0.31 % ISI < 2 ms**) and a real spike waveform. **0 of 8**
up-going responsive units (both regions) develops an ON-specific 50 Hz comb.

**Screen 2 — the broadband loophole.** The ACG kills *periodic* pickup; a *broadband*
noise-floor rise during ON could instead add **randomly-timed** false spikes (no
comb). Those would land inside the refractory period, raising ISI < 2 ms violations
during ON. They don't: across all 8 up-units, **0/8** show an ON rise in refractory
violations (unit 87: **0.45 % ON vs 0.26 % OFF**, both ≪ 1 %). Both screens:
`up_unit_50hz_periodicity_screen.json`.

**Reading (the strong, defensible version):** unit 87 — and every up-going unit —
**passes the spike-artifact screens: clean refractory period, no ON-specific 50 Hz
ACG comb, and a stable ON/OFF refractory-violation rate.** The remaining caveats are
**n = 1, arousal/state, and indirect sensory-network effects** (direct 50 Hz circuit
modulation vs an indirect sensory/state cascade) — **not** evidence that 50 Hz pickup
manufactured the spikes.

## Why the next round fixes it
This is precisely what the **recorded analog stimulus** (PVDF force sensor on the
shared 20 kHz clock) buys: with a continuous copy of the delivered vibration you can
**measure the artifact directly and regress/subtract it** from the LFP, and run a
true phase-entrainment test. See
[HARDWARE_ENG_MESSAGE_NEXT_ROUND.md](HARDWARE_ENG_MESSAGE_NEXT_ROUND.md).

## One-line takeaway
Disconnected LEC electrodes pick up **~6× more** 50 Hz during ON than tissue, with
~0 ms cross-region lag → there is a **real non-neural 50 Hz component** in the LEC
LFP (LEC-dominant; dHPC leaks ~5× less, only at amp250). Rely on the **single-unit
rate change**, not the LFP — and that spike evidence survives a direct check: the
autocorrelogram screen clears **0/8** up-going units of pickup, so the residual
caveat is arousal/state, n=1, and indirect sensory-network effects, **not** 50 Hz
pickup manufacturing spikes.

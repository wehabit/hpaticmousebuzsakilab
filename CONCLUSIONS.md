# Conclusions — Haptic Stimulation Electrophysiology (Dec 3 + Dec 4)

A single-page synthesis across both sessions. For the figure-by-figure version see
the [README key findings](README.md#abstract) and the per-topic writeups linked
below.

## Bottom line
Body-surface haptic stimulation produces a **real, measurable cortical/hippocampal
response**, but it is **not** the brain "following" the vibration frequency, and the
two recorded regions do **not** demonstrably **coordinate**. The cleanest neural
signature is a **single-unit firing-rate change at 50 Hz / high amplitude**, present
in *both* dHPC and LEC; the LFP "50 Hz" signal is partly **non-neural pickup** and
should not be read as entrainment.

## The arc, in order
1. **There is a genuine response (Dec 3).** Haptic stimulation drives an
   amplitude-graded **broadband LFP** response, strongest at `amp180/250_freq26`.
   It is **transition-weighted** (onset/offset), statistically reliable on
   trial-level CIs at `amp250_freq26`. → broadband / transition-index figures.
2. **It is not frequency-following.** dHPC shows **no narrowband peak and no phase
   locking** at any tested frequency (5/10/26/50 Hz). This **replicates across Dec 3
   and Dec 4 on the same probe**. The brain is responding to the *stimulus events*,
   not oscillating at the drive frequency.
3. **A 50 Hz LFP appears in LEC — but it is contaminated.** Dec 4's LEC probe shows
   an amplitude-graded, *induced* (not phase-locked) 50 Hz LFP power increase. A
   **dedicated artifact check** ([DEC4_50HZ_ARTIFACT_CHECK.md](docs/DEC4_50HZ_ARTIFACT_CHECK.md))
   shows disconnected LEC electrodes pick up **~6× more** 50 Hz than tissue and the
   cross-region lag is **~0 ms** → a real **non-neural pickup component**. So the
   LEC 50 Hz *LFP* is not clean neural evidence.
4. **The clean neural result is single-unit (Dec 4).** Sorted, curated units change
   their **firing rate** during 50 Hz / high-amplitude ON vs OFF, in **both** regions
   (dHPC 19/180 unit-conditions, LEC 13/180; concentrated at 50 Hz: 15/19 and 8/13).
   Electrical pickup cannot change a sorted neuron's rate, so this is genuine. It
   also explains the Dec 3 single-unit null: Dec 3 only tested 5/26 Hz, where there
   is no effect. → [DEC4_SPIKE_ONOFF_RESULT.md](docs/DEC4_SPIKE_ONOFF_RESULT.md).
5. **The response is active & region-specific, not a passive echo.** A passive relay
   would look identical everywhere; instead **LEC is predominantly suppressed**
   (~67% of modulated units fire less) while **dHPC has a driven-up subset**. The
   50 Hz input is *transformed differently by each circuit*.
6. **But the regions do not demonstrably coordinate.** The artifact-robust
   cross-region **spike–field** test (do one region's neurons lock to the *other*
   region's rhythm?) is weak and **does not rise** during stimulation. The LFP
   coherence rise is the foolable measure (inflated by the shared 50 Hz pickup from
   #3). → [DEC4_COORDINATION_50HZ.md](docs/DEC4_COORDINATION_50HZ.md).

## What is genuinely supported
- A real, amplitude-graded, **event-/transition-driven** haptic response (LFP).
- **No frequency-following** (no entrainment by power *or* phase), replicated.
- A genuine, frequency-specific (**50 Hz**), region-specific **single-unit rate**
  modulation at high amplitude — the headline neural finding.

## What is NOT supported / explicitly negative
- The brain does **not** oscillate at the drive frequency.
- The LEC **50 Hz LFP** is **not** clean neural signal (pickup-contaminated).
- The two regions do **not** demonstrably **work together** at 50 Hz.

## Honest limits
- **Single animal**, single session per region pairing.
- **No recorded stimulus phase** → a true entrainment (phase-following) test is
  impossible this session; "no entrainment" is partly a *measurement* limit.
- ON-vs-OFF is a within-trial contrast (OFF = post-stim, not neutral baseline); a
  strong-stimulus arousal/state component can't be fully excluded.
- Probe geometry / channel order not yet confirmed for laminar/anatomical claims.

## What the next recording must add (external, can't be done on this data)
1. **Continuous analog copy of the delivered vibration** (thin PVDF force sensor in
   the tactor→skin path → Intan analog input on the shared 20 kHz clock). Enables a
   true **phase-entrainment** test *and* lets you **regress out the 50 Hz artifact**.
2. **Per-cycle + per-trial digital sync lines** for exact stimulus timing (no TTL
   this session; timing came from the controller log).
3. Confirm probe geometry / channel map.

→ Hardware spec: [HARDWARE_ENG_MESSAGE_NEXT_ROUND.md](docs/HARDWARE_ENG_MESSAGE_NEXT_ROUND.md),
[PVDF_CHARGE_AMP_SPEC.md](docs/PVDF_CHARGE_AMP_SPEC.md).

## Detailed writeups
- [DEC4_SPIKE_ONOFF_RESULT.md](docs/DEC4_SPIKE_ONOFF_RESULT.md) — single-unit headline
- [DEC4_50HZ_ARTIFACT_CHECK.md](docs/DEC4_50HZ_ARTIFACT_CHECK.md) — the LFP artifact test
- [DEC4_COORDINATION_50HZ.md](docs/DEC4_COORDINATION_50HZ.md) — do the regions coordinate?
- [DEC4_SUPERVISOR_SUMMARY.md](docs/DEC4_SUPERVISOR_SUMMARY.md) /
  [DEC3_SUPERVISOR_SUMMARY.md](docs/DEC3_SUPERVISOR_SUMMARY.md)

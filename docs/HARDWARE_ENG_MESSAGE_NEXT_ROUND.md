# Message to hardware engineer (Volodymyr) — stimulus recording for next round

Final, ready-to-send version. Full wiring/firmware detail is in
[STIMULUS_SYNC_RECORDING_SPEC.md](STIMULUS_SYNC_RECORDING_SPEC.md), and the PVDF
front-end design is in [PVDF_CHARGE_AMP_SPEC.md](PVDF_CHARGE_AMP_SPEC.md). The key
change from last round: capture the delivered vibration as a **continuous analog
waveform** on the Intan clock, so stimulus **phase** is recoverable.

---

**Subject: Stimulus sync + delivered-vibration recording for the next study**

Hi Volodymyr,

I want to frame the next firmware/sensor changes around what the data actually
showed, so this is diagnostic context rather than fault-finding.

In the last study, we recorded no usable copy of the delivered stimulus. The
accelerometer/sync signal that was recorded did not capture the carrier vibration.
One digital channel was completely dead, and the other toggled slowly and
irregularly: it gave about the same ~6 pulses per trial regardless of whether the
commanded stimulus was 5 Hz or 26 Hz. A real per-cycle marker should have given
~15 cycles in a 3 s, 5 Hz trial and ~78 cycles in a 3 s, 26 Hz trial. In the
best-case 26 Hz check, the longest run of near-26 Hz intervals was only 3 cycles.

Scientifically, this means we can still analyze coarse stimulus responsiveness
using ON/OFF timing from the controller log, for example whether firing rate or
LFP power changes during the buzz. But we cannot test whether neurons lock to the
phase of the vibration, because the vibration phase was never recorded. That is
the main limitation of the previous dataset.

That is why I am being specific this round. I think we need three signals recorded
on the Intan:

**1) Per-cycle sync pin from the firmware.** This is now implemented in
`actuator.cpp` as `SYNC_CYCLE_PIN`: one clean edge per carrier cycle, emitted by
the waveform engine itself. This fixes the specific failure mode where the
recorded digital line was not actually the carrier. Because the pin is generated
from the same waveform/timer logic that drives the tactor, it is the command-side
phase reference.

**2) Trial gate pin from the firmware.** This is `TRIAL_GATE_PIN`: HIGH for the
whole 3 s ON window and LOW during the 3 s OFF. This gives precise trial timing
on the same clock as the neural data, instead of reconstructing timing only from
the controller log.

**3) Delivered-vibration sensor as a continuous analog signal.** This is the most
important piece scientifically. The firmware sync pin tells us what the firmware
commanded, but it cannot prove the tactor actually moved, had the right amplitude,
or had the expected mechanical phase. A dead or mechanically disconnected tactor
would still produce a perfect firmware sync pin. So we need a transduced analog
copy of the vibration delivered to the body: ideally a thin PVDF piezo film in the
tactor-to-contact force path, with a small charge-amp front end, recorded into an
Intan analog input. If you think a tiny accelerometer is mechanically better, I am
open to that, but the key requirement is that the signal be analog and continuous,
not thresholded TTL.

The reason for recording everything on the Intan is that the digital inputs,
analog input, and neural data all share the same 20 kHz clock. That removes
cross-device drift and lets us compare neural phase directly against the measured
stimulus phase.

Before the real study, I also want to do a short verification recording and check
the data directly. For each test frequency/amplitude, we should confirm:

1. The per-cycle sync pin has the right edge rate, e.g. ~5 edges/s at 5 Hz and
   ~26 edges/s at 26 Hz.
2. The trial gate is HIGH for the full ON window and LOW during OFF.
3. The analog delivered-vibration sensor shows the commanded carrier frequency,
   with no clipping and enough signal at the lowest amplitude.
4. The firmware sync pin and the delivered-vibration sensor are phase-consistent.

This verification step is what keeps us from discovering months later, during
analysis, that a line was dead or was not the carrier.

My concrete asks:

1. Please confirm the two free GPIOs and wiring to Intan digital inputs. Current
   firmware labels are `SYNC_CYCLE_PIN` and `TRIAL_GATE_PIN`; proposed board labels
   are `P1.04 / OUT1` for cycle sync and `P1.06 / OUT2` for trial gate, if those are
   correct for this board.
2. Please review the PVDF/analog sensor plan and tell me the best mechanical
   integration: thin sensor in the tactor-to-contact path, minimal added mass,
   rigid enough to measure transmitted vibration, and a front-end scaled to the
   Intan 0-3.3 V analog input.
3. Please help run or enable a short pre-session verification recording before we
   collect neural data.

I am happy to share the diagnostic plots from the previous recording if useful.
The main point is not that "the sync was bad" in a vague way; it is that the
recorded line demonstrably never captured the carrier, and each fix above is
aimed at one specific failure mode.

Thanks!

---

## Why — what the Dec 3 digital sync actually recorded (context for Volodymyr)

This is where the requirements above come from. I went back and analyzed the Dec 3
`digitalin.dat` to see if we could recover the stimulus phase after the fact. We
can't, and the reason drives every item below.

Two digital channels were active:
- **ch15 — completely dead** (0 edges in the entire ~3 h recording).
- **ch7 — ~9,000 edges, but it does not track the tactor.** It toggles slowly and
  irregularly (median interval ~231 ms ≈ 4 Hz, HIGH ~58 % of the time). The actuator
  ran at 5 and 26 Hz, but ch7 fired the **same ~6 pulses per trial regardless of
  frequency**. A real per-cycle marker would give ~78 edges per 3 s trial at 26 Hz
  and ~15 at 5 Hz; ch7 gave ~6 either way — so it is not the carrier.

Best-case checks confirm it: across the whole session the longest run of consecutive
~38.5 ms (26 Hz) intervals is **3** — it never sustains even three tactor cycles in a
row; even the single densest 1 s window is irregular, nothing like a 26 Hz square
wave; and ch7's edges don't line up with the trial schedule (0 edges inside the first
20 scheduled 26 Hz windows), so it wasn't reliable for trial timing either. Put
concretely: between two ch7 edges the tactor completed ~6 full up/down cycles — far
too coarse to see the motion at all.

**Net result: we recorded no usable copy of the stimulus.** We can still show the
brain's firing *rate* changes during the buzz (that only needs coarse ON/OFF timing,
which we reconstructed from the controller log) — but we **cannot** test whether
neurons phase-lock to the vibration (entrainment), because the vibration's phase was
never recorded. That one missing signal is the main scientific limitation of the
study, which is why I'm being specific now:
- the **per-cycle sync pin** (now in firmware) fixes "ch7 wasn't the carrier" — it's
  emitted by the waveform engine itself, so it can't be the wrong signal;
- the **transduced analog sensor** gives the *delivered* phase **and proves the tactor
  actually moved** — the firmware pin alone can't tell us a tactor was dead, the same
  way nobody noticed ch15 was dead until now;
- **shared clock + a pre-session verification recording** means we confirm each line
  shows the right edges/sec at each frequency *before* we trust it — instead of
  finding out in analysis, months later, that it was useless.

(Diagnostic plots: `analysis/outputs/dec3/ttl_diagnostic/`. Happy to walk through them.)

## Hardware-readiness: firmware ✓ vs wiring ☐ (internal prep)

**What the firmware already does (verified in `firmware/actuator.cpp`).** Two
**digital** references, generated deterministically and sample-accurately — the
marker is written in the *same* timer ISR as each PWM sample, off the same
`g_sine_index`, so it **cannot drift from the carrier** (it *is* the carrier):
- **`SYNC_CYCLE_PIN`** — one clean rising edge per carrier cycle (currently anchored
  at sine index 0; that's the **trough** for the start-at-zero table or the **rising
  zero-crossing** for mid-rise — i.e. the phase-zero convention follows the Q3
  sine-table decision). Fires only while delivering (`g_pwm_active && output>0`),
  parked LOW when idle.
- **`TRIAL_GATE_PIN`** — HIGH for the whole ON window, LOW otherwise.

**The catch — these are *command-side*.** They report what the firmware *intends*,
not what the tactor *delivers*. A dead, mis-amplitude, or mechanically phase-lagged
actuator would still emit a perfect sync pin. So they're necessary but **not
sufficient**: the delivered signal and an independent cross-check are **wiring, not
firmware**.

**Why redundancy (the Dec-3 lesson).** Last round we had a single digital line that
(a) never actually captured the carrier and (b) was unverified — so we only found out
it was useless during analysis, months later. Recording **2–3 independent references
on the shared Intan 20 kHz clock** and cross-checking them removes that single point
of failure: if one is wrong, the others disagree and you catch it *before* the
session.

## What to ask Volodymyr to wire in (checklist)
1. **Both firmware digital lines → Intan DIGITAL inputs**, on the Intan's own 20 kHz
   clock: `SYNC_CYCLE_PIN` and `TRIAL_GATE_PIN` (assign the two free GPIOs — Q1).
2. **Analog copy of the drive signal → Intan ANALOG input.** A buffered/divided copy
   of the actual tactor drive voltage, scaled to the input range. A near-free *second*
   phase reference — continuous, command-side — that cross-checks the sync pin.
3. **Delivered-vibration sensor → Intan ANALOG input.** PVDF in the tactor→skin force
   path + charge-amp ([PVDF_CHARGE_AMP_SPEC.md](PVDF_CHARGE_AMP_SPEC.md)), **or** a
   small accelerometer on the tactor (26/50 Hz is well in-band). This is the delivery
   ground-truth and catches mechanical phase lag. **Analog & continuous, never a TTL.**
4. **Everything on the shared Intan clock** — no separate logger. If anything must live
   on another device, also record a common sync line on both to re-align offline.
5. **Acceptance test BEFORE the neural session (the step Dec 3 skipped).** In a short
   test recording, verify *in the data*: (a) the sync pin shows the **right number of
   edges per second** at each frequency (e.g. ~26/s at 26 Hz — the exact check ch7
   failed in Dec 3), (b) the gate is HIGH for the full ON window, (c) the analog
   sensor shows the carrier, (d) the sync pin and the delivered sensor are
   phase-consistent. Fix any disagreement before recording brain data.

**Minimum viable:** items **1 + 3** (digital sync + one transduced analog sensor) make
entrainment testable. Items **2 + 5** are the cheap insurance that turns "we hope it
worked" into "we verified it worked" — exactly what was missing last round.

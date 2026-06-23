# Message to hardware engineer (Volodymyr) — stimulus recording for next round

Final, ready-to-send version. Full wiring/firmware detail is in
[STIMULUS_SYNC_RECORDING_SPEC.md](STIMULUS_SYNC_RECORDING_SPEC.md). The key change
from last round: capture the delivered vibration as a **continuous analog
waveform** (not a 1-bit TTL), so stimulus **phase** is recoverable.

---

**Subject: Firmware + sensor changes for the next study (recording the actuator's phase & delivery)**

Hi Volodymyr,

For the next study I need an updated firmware, plus one added sensor, so we can record exactly what the actuator is doing — time-aligned with the brain electrodes in the human or animal. Context: we drive the tactor in trials (3 s ON at a set frequency + amplitude, then 3 s OFF), and we want to align the recorded brain signal against the actual stimulus — both its timing and its phase. That needs three signals: **two digital lines** into our neural recording system (Intan), and **one analog sensor**.

**1) Per-cycle phase pin (digital).** A GPIO that gives one clean edge per sine cycle (a square wave at the drive frequency). This is our phase reference — it lets us recover where in the sine cycle the stimulus is at any instant.

**2) Trial ON/OFF pin (digital).** A GPIO that's HIGH for the whole 3 s ON window and LOW during the 3 s OFF. This marks trial timing precisely (right now we infer it from logs).

Both come from the nRF52 firmware. I've drafted a modified `actuator.cpp` that implements both, with the two pin numbers left as placeholders (`SYNC_CYCLE_PIN`, `TRIAL_GATE_PIN`) for you to assign to free GPIOs and wire to the Intan digital inputs. I'll attach the file. (These two are genuinely digital, so TTL is correct here.)

**3) Delivered-vibration sensor (the important one — analog, not digital).** An ADXL335 / chip-on-board can't mount cleanly on the moving tactor and would mass-load it. Better idea: a thin **PVDF piezo film** (e.g. piezopvdf.com) sandwiched between the tactor and the contact point. It's thin and light, so it barely loads the actuator, and sitting in the force path it measures the vibration actually transmitted to the subject — the ground truth of what they feel, which is what we compare against the brain signal. Three key points:

- **Analog and continuous.** It must be recorded as a continuous analog waveform, *not* a TTL. A 1-bit threshold discards the waveform and makes phase unrecoverable — that's exactly what bit us last round (we logged a comparator version of the sensor). We need the full analog waveform to extract instantaneous phase offline.
- **It needs a small front-end board.** PVDF is a high-impedance charge source, so it needs a tiny charge-amp board (op-amp + feedback cap `Cf` and resistor `Rf`) that outputs a clean analog voltage scaled into the recording system's input range. Two phase-critical constraints: keep the high-pass corner well below our lowest carrier (≤0.5 Hz — e.g. `Rf·Cf` of 1 GΩ × 1 nF ≈ 0.16 Hz), and set the gain so the loudest amplitude condition fills the input range without clipping while the quietest stays above the noise floor. I'll send a schematic + component table.
- **Clock and storage.** I'd record it on an Intan analog input so it shares the Intan's 20 kHz clock — that's what keeps it sample-aligned to the brain data — and it never goes through the actuator MCU, so it can't add delay or jitter to the stimulus. Storage is small: one analog channel over a 5 h session is only ~0.7 GB (1–3 GB for a few channels), so it fits on the existing recording — no separate disk needed. (If we ever have to log it on a standalone board/disk instead, we can, but then we'd need to record a shared sync line on both systems to re-align them offline — happy to discuss.)

**The two sine tables — your call.** While editing I found two 256-point sine tables in `actuator.cpp`: a standard mid-rise one (starts at the midpoint / rising zero-crossing) and a "start-at-zero" one (starts at the minimum). The start-at-zero one was active. In the draft I switched to the standard mid-rise table, for two reasons: (a) for our phase pin, index 0 then lands on the rising zero-crossing — the conventional definition of phase 0° and the steepest, most precise marker; and (b) I'd rather not ship a leftover "test" table in a real study. For a free-running oscillator we never reset, the starting point doesn't change the vibration itself, so I don't think start-at-zero was doing anything for us — but you know the driver: was it there for a reason, e.g. a soft-start to avoid an inrush/click when the driver enables? If so, let's keep it; otherwise I'll go with standard mid-rise. Either way, please confirm and explain the tradeoff so I understand it.

**Questions back to you:**

1. Which free GPIOs should the two digital pins use?
2. PVDF sensor: best way to integrate it in the tactor→contact path (rigid in the force path, minimal added mass) and build the charge-amp front end so its **analog** output lands in the recording system's input range. Confirm it won't load or delay the actuator.
3. Sine table: standard mid-rise vs start-at-zero — your call + reasoning.

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

# Stimulus Sync & Delivery-Recording Spec (for the hardware engineer)

**Goal:** record the *actual* haptic stimulus alongside the neural data so we can
(a) test whether brain activity phase-locks to the stimulus and (b) verify the
stimulus was delivered cleanly at each commanded frequency.

## Why this is needed (background)

The actuator firmware (`wehabit/FAR2.0`, `Firmware/refactor-version/actuator.cpp`)
generates vibration from a **continuously free-running sine oscillator**: a 50-point
sine table is stepped by a hardware-timer ISR (`TIMER2_IRQHandler`) that starts once
at boot and never stops; an ON command only gates the **amplitude**, never resets the
**phase**:

```c
volatile uint8_t sine_index1 = 0;
void TIMER2_IRQHandler(){ if(++sine_index1 == 50) sine_index1 = 0; }   // free-runs all session
NRF_TIMER2->CC[0] = 20000/freq;                                        // sets frequency only
HwPWM0.writePin(PWMPin, sine[sine_index1]*OutputLevel/255, 0);         // phase free-running, amplitude gated
```

Consequence: each trial's vibration starts at a *random* phase ("a fan spinning behind
a shutter"). The Dec 4 recording also saved **no** stimulus copy (no `digitalin.dat`,
and `auxiliary.dat` was all `0xFF` = nothing connected). With a free-running stimulus
**and** no recording of it, we cannot test entrainment from the LFP at all. The fix is
not to change the stimulus — it is to **record it**.

## What to add — ranked

| Priority | Signal | Records into | Gives us |
|---|---|---|---|
| **MUST #1** | **Per-trial ON/OFF TTL** | Intan **digital-in** | jitter-free trial timing (when each 3 s buzz starts/stops) |
| **MUST #2** | **In-line PIEZO** between tactor tip & mouse (analog; used in a prior study) | Intan **analog-in (ADC)** via charge-amp | true *transmitted force* = what the body receives: phase to phase-lock against + delivery QC (amplitude, frequency purity, harmonics, dropouts) |
| **NICE** | **Zero-crossing TTL** (1 pulse per sine cycle) | Intan **digital-in** | exact, drift-free phase clock; lets us measure the mechanical lag (accelerometer vs command) |
| **SKIP** | buffered copy of the electrical drive/PWM | analog-in | electrical command only (not what the animal feels); needs anti-alias filter + isolation; redundant with the accelerometer |

Rationale: the brain responds to what it physically **feels**, so the analog sensor is
both the phase reference and the delivery monitor. **Decided: an in-line PIEZO**
sandwiched between the tactor tip and the mouse (the approach used in a prior study) — it
measures the *transmitted force* (closest to what the body receives) and, unlike a MEMS
accelerometer, needs **no chip bonded to the tiny actuator** (a thin piezo just sits in the
contact/load path, so it is far more feasible to mount). It feeds a small **charge-amp →
Intan ADC** (passive, no MCU): bias to mid-rail, gain so the strongest amplitude doesn't
clip, low-frequency corner ≤0.5 Hz so the 5 Hz condition isn't phase-distorted, clamp to
protect the ADC. The two TTLs are cheap, exact digital markers (trial timing + phase
clock). The electrical drive-tap is fussiest/least informative — skip it.

Minimum viable = **MUST #1** alone (fixes trial timing). Ideal = #1 + #2 + the
zero-crossing TTL.

## Channel / wiring spec (Intan)

Assign free channels and **enable + save** these signal types in the Intan recording
software (one-file-per-signal-type). Confirm the exact channel numbers and note them in
the session log.

- **Digital inputs** (3.3 V logic, sampled at the 20 kHz amplifier rate):
  - `DIN-A` = **per-trial ON/OFF**: HIGH for the whole 3 s ON window, LOW during OFF
    (or a short pulse at each onset — see firmware below). One edge per trial → ~2400
    ON events for the 12×200 design.
  - `DIN-B` = **zero-crossing**: toggles once per sine cycle (rate = the commanded
    frequency).
  - Share a common ground between the stimulator controller and the Intan digital
    ground. If you see stimulus artifact riding into the ephys, use an **opto-isolator**
    on the TTL lines.
- **Analog input** (match your Intan model's ADC range — commonly 0–3.3 V on RHD eval
  boards, ±5/±10.24 V on the RHX controller; sampled at 20 kHz):
  - `AIN-0` = **accelerometer** output (1 axis aligned with the vibration direction is
    enough; 3-axis is fine). Scale/level-shift so the signal sits **mid-range with
    headroom** (no clipping at max amplitude). Sensor bandwidth must resolve **≥200 Hz**
    (to capture 50 Hz + its first 2–3 harmonics). A small analog MEMS part
    (ADXL335-class) is sufficient; mount it rigidly on the actuator/contact piece.

## Capturing PHASE — and why the Dec 3 accelerometer-TTL did NOT

**What "phase" is:** the vibration goes up and down N times per second; *phase* is
where in that up/down cycle it is at a given instant — an angle that cycles 0→360°
once per wave. To phase-lock brain activity to the stimulus you need that angle at
every instant.

**How to actually get it:** record the stimulus as a **continuous ANALOG waveform,
sampled fast** — the accelerometer into an Intan **ADC at 20 kHz** (~400 samples per
50 Hz cycle, plenty). Phase is then computed offline (bandpass at the drive
frequency → Hilbert transform → instantaneous phase at every sample). This is the
only thing that gives phase at every instant.

**Why a TTL cannot do this:** a TTL is **1 bit** (high/low). A "device is vibrating"
TTL carries the ON/OFF *envelope* and **zero phase**. Even a perfect zero-crossing
comparator only marks the 0°/180° crossings and only if the edges are clean.

**The Dec 3 lesson (from this session's `digitalin` bit-7 data):** the accelerometer
was **thresholded into a TTL**. Measured: its edges fire irregularly at **~2–6 Hz
(median ~4 Hz), not the commanded 5/26 Hz**, and the per-burst "frequency" ranges
0.5–107 Hz — so the edges **do not track the vibration cycles** and carry no usable
phase. The bursts also don't map one-per-trial (extra pre/post/test bursts), so
burst→trial alignment **drifts** badly. A thresholded accelerometer TTL therefore
loses the waveform **and** drifts → **record the accelerometer as ANALOG, not as a
TTL.** (Keep a *separate* clean digital line for trial ON/OFF timing — that's a
different job; see the table.)

**No cross-clock drift if it's recorded by the Intan:** the digital-in and analog-in
are sampled by the **same 20 kHz clock as the neural amplifier**, so any sync recorded
*through the Intan* cannot drift relative to the neural data. Drift only appears when
you try to line up an external controller's timeline to the Intan after the fact —
which is the no-TTL problem on Dec 4 and the burst-enumeration problem on Dec 3. The
whole point of these channels is to put the stimulus on the neural clock.

## Firmware changes (FAR2.0, `actuator.cpp` — current 256-point/ISR version)

Context for the current firmware: a **256-point** `sine_table` is stepped by a
free-running `g_sine_index` in `TIMER2_IRQHandler`, and the PWM sample is now written
**inside the ISR** (`HwPWM0.writePin(... sine_table[g_sine_index]*g_output_level/255 ...)`).
Frequency is set by `timer2_set_sine_frequency()` (`CC[0] ≈ 1e6/(freq*256)`); the loop
only publishes `g_output_level`. Phase is **never reset** at ON, so it free-runs.

Pick two free nRF52 GPIOs (11/12/13 are taken by LED/PWM/BST_SHDN) and wire them to Intan
digital-in. Use `nrf_gpio_*` (single-register) ops in the ISR, not Arduino `digitalWrite`.

```c
#define SYNC_CYCLE_PIN  <free_gpio>   // per-carrier-cycle phase marker
#define TRIAL_GATE_PIN  <free_gpio>   // HIGH during the ON window
```

1. **Per-cycle phase pulse (Ask #2)** — in `TIMER2_IRQHandler`, right after the index
   update, emit a square (HIGH at index 0, LOW at the half-cycle), gated by
   `g_pwm_active && g_output_level > 0u` so edges appear **only while actually delivering**
   (each rising edge = one delivered cycle; parked LOW during OFF/idle). With the standard
   table, index 0 = rising zero-crossing => rising edge = stimulus phase 0 deg.
   *(Implemented in `firmware/actuator.cpp`.)*

2. **Per-trial ON/OFF gate (Ask #3)** — mirror the amplitude. In the ISR's
   `if (g_pwm_active)` block (sample-accurate):
   ```c
   nrf_gpio_pin_write(TRIAL_GATE_PIN, (g_output_level > 0u) ? 1u : 0u);
   ```
   (or, simpler/loop-rate, set `digitalWrite(TRIAL_GATE_PIN, OutputLevel>0)` in
   `Actuator::UpdateLevel()` and clear it in the `Effects.isEmpty()` branch of
   `Update()` and in `drv_dis()`).

3. **Pin init** — in `actuator_init()`:
   ```c
   nrf_gpio_cfg_output(SYNC_CYCLE_PIN);  nrf_gpio_pin_clear(SYNC_CYCLE_PIN);
   nrf_gpio_cfg_output(TRIAL_GATE_PIN);  nrf_gpio_pin_clear(TRIAL_GATE_PIN);
   ```

(Add a level shifter if the nRF52 3.3 V logic doesn't match the Intan digital-in; common
ground required, or opto-isolate.)

**Do NOT add a phase reset** (`g_sine_index = 0` at ON). It would inject an onset
discontinuity/click every trial and entangle the evoked edge with entrainment; recording
the phase (above) is the better fix. (Note there is a commented "phase-shifted table for
startup transient experiments," which is the same idea — leave it off.)

**Sine table — decided:** use the **standard mid-rise table** (index 0 = rising
zero-crossing), not the leftover "starts at 0 / ends at 0" test table. Reasons: don't ship
a test waveform; and index 0 = rising zero-crossing is the conventional phase-0 reference
and the max-slope point, so the per-cycle marker is a clean, precise phase-0 mark. This is
implemented in `firmware/actuator.cpp` (standard table active; test table disabled under
`#if 0`).

## Pre-session verification (do NOT skip — this is why Dec 4 has no sync data)

Before the real recording, run a ~30 s test capture and confirm **each** sync channel is
**live and non-flat**:
- Buzz the actuator and watch `AIN-0` (accelerometer) move and show the commanded
  frequency.
- Confirm `DIN-A` toggles once per trial and `DIN-B` toggles at the drive frequency.
- Confirm the Intan software is actually **writing and you will share** `digitalin.dat`
  and `analogin.dat` (Dec 4 only shared `amplifier/auxiliary/time`, and `auxiliary` was
  empty — that mistake cost us the entrainment test entirely).

## Acceptance criteria (what "done right" looks like)

- `digitalin.dat` present and non-empty; `DIN-A` shows ~2400 ON windows; `DIN-B` rate
  matches the commanded frequency per trial.
- `analogin.dat` present and non-empty; the accelerometer shows clear 5 / 10 / 26 / 50 Hz
  during the corresponding trials, with sane amplitude scaling (no clipping) and no
  unexpected harmonics/dropouts.
- All four signal-type files (`amplifier`, `digitalin`, `analogin`, `time`) saved **and
  shared** for analysis.

## What this unlocks in analysis

- **Trial timing** without the no-TTL jitter problem (we currently estimate onsets from
  the controller log; see DEC4 summary).
- **True entrainment test:** LFP/spike phase-locking to the recorded accelerometer (and
  cross-checked against the zero-crossing TTL) — free-running becomes irrelevant.
- **Delivery QC:** confirm the stimulus was actually clean at 5/10/26/50 Hz (the original
  Dec 3 caveat was that 5/26 Hz delivery could not be verified).

_See `docs/DEC4_SUPERVISOR_SUMMARY.md` (“Stimulus is FREE-RUNNING (firmware)”) for the
finding that motivated this spec._

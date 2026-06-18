# Message to hardware engineer — stimulus recording for the next round

Hey — for the next recording I need to change how we capture the stimulus. Goal: recover
the **instantaneous phase of the delivered vibration** and verify delivery, **time-aligned
to the neural data on the Intan's own clock**. Full wiring/firmware detail is in
`STIMULUS_SYNC_RECORDING_SPEC.md`; this is the summary.

## What went wrong last round
We logged a **comparator/threshold (1-bit) version of the accelerometer**. That discards
the waveform, so phase is unrecoverable. And the edges were ragged — they fired at
~2–6 Hz (median ~4 Hz), not at the commanded 5/26 Hz carrier — and didn't enumerate
trials 1:1 (extra pre/post bursts), so any burst→trial alignment drifted by hundreds of
seconds. Net: no phase, unreliable timing. Fix is to capture the **analog waveform** plus
clean digital sync lines, all sampled by the Intan.

## The three asks

**1) (MUST) Accelerometer raw analog → Intan ADC, continuous, full bandwidth.**
- Gives us instantaneous phase (bandpass + Hilbert offline) **and** delivery QC
  (amplitude per condition, spectral purity at 5/10/26/50 Hz, harmonics, dropouts).
- Conditioning: 1 axis along the drive axis is the minimum. DC-bias to mid-scale and set
  gain so peak deflection at max drive amplitude uses most of the input range without
  clipping. Match the Intan ADC input range for our board (RHD eval ≈ 0–3.3 V
  single-ended; RHX controller ±5/±10.24 V — confirm which we're on). Sensor analog
  bandwidth ≥ ~200 Hz; Intan samples at 20 kHz so the sensor BW is well under Nyquist —
  no extra anti-alias network needed. **No comparator/threshold — we want the analog.**

**2) (NICE) Per-cycle digital sync from firmware → Intan digital-in.**
- Toggle a spare GPIO on the sine-table wrap (`sine_index1` → 0); one edge per carrier
  cycle. Drift-free reference of the *commanded* phase. Lets us measure the
  electromechanical lag (accelerometer phase − command phase) and validate the
  analog phase extraction. Keep the ISR write to a single register/`digitalToggle`.

**3) (MUST) Per-trial ON/OFF digital line → Intan digital-in.**
- GPIO high for the ON window (`OutputLevel > 0`), low otherwise (or a short pulse at each
  onset). Gives sample-accurate trial onsets/offsets. Last round we inferred trial timing
  from the controller log, which is imprecise and what forced us to *estimate* the
  recording offset.

(The current Intan config already exposes spare analog-in and digital-in channels, so
there's room for all three.)

## Watch-outs
- **Acquire everything through the Intan** so the stimulus shares the 20 kHz acquisition
  clock — this removes clock-domain drift between stimulus and ephys (last round the only
  timing reference was the controller's clock, which drifts vs Intan). Phase/timing are
  only meaningful on a common clock.
- **Grounding/coupling:** common ground for the digital lines; keep the tactor drive
  return away from the ADC/return, and opto-isolate the TTLs if we see drive coupling into
  the ephys ground. The accelerometer being galvanically separate is a plus.
- **Verify before the session.** Last round `auxiliary.dat` came back all `0xFF` (sensor
  not connected/enabled) and no digital-in file was saved/shared. Do a 30 s test capture,
  confirm each channel is live (non-flat), and make sure we **save and send `digitalin`
  and `analogin`** (one-file-per-signal-type), not just amplifier/aux/time.

## TL;DR
Accelerometer **analog → Intan ADC** (no threshold), plus a **per-cycle sync pulse** and a
**per-trial ON/OFF** digital line, all **acquired by the Intan**, and **verified live
before recording**. That gives us recoverable stimulus phase + delivery QC, clock-aligned
to the neural data.

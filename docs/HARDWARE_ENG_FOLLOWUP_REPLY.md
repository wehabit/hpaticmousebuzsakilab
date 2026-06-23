# Follow-up reply to Volodymyr

**Subject: Re: stimulus sync + delivered-vibration recording**

Hi Volodymyr,

I analyzed the accelerometer/sync data from the previous study, and the main
lesson is that we did not record a usable copy of the delivered stimulus. We can
still analyze coarse ON/OFF effects, such as whether firing rate or LFP power
changes during the buzz, because that only needs trial timing. But we cannot test
phase-locking or entrainment to the vibration, because the vibration phase itself
was not captured.

For the next setup, I would like to record **two digital signals and two analog
signals**, all on the Intan clock:

**1) Firmware cycle sync: `SYNC_CYCLE_PIN = 36` (`P1.04 / OUT1`)**

Digital signal from the nRF52 firmware into an Intan digital input. This should
give one clean edge per carrier cycle, so it is the command-side phase reference.

**2) Trial gate: `TRIAL_GATE_PIN = 38` (`P1.06 / OUT2`)**

Digital signal from the nRF52 firmware into an Intan digital input. This should
be HIGH during the full 3 s ON window and LOW during the OFF period. This is for
trial timing, not phase.

**3) Delivered-vibration signal: PVDF + charge amp**

Analog signal into an Intan analog input. This is the most important scientific
signal: it gives the phase of the delivered mechanical vibration and confirms
that the tactor actually moved. The PVDF should sit in the tactor-to-contact
force path, with minimal added mass and without acting like a soft spacer.

I checked the Intan metadata: we are using the RHD2000 USB evaluation board, so
the analog input is `0-3.3 V`, single-ended/unipolar. For the PVDF front end, my
understanding is that the output should be biased around `1.65 V`, scaled so the
largest condition does not clip, and filtered so the high-pass corner is well
below our lowest carrier frequency. The attached PVDF spec suggests `Rf = 1 GΩ`
and `Cf = 1 nF` as a starting point, giving about `0.16 Hz`, but please review
and adjust the circuit values as needed.

**4) Electrical drive-signal copy**

Analog signal into another Intan analog input. This would be a buffered/divided
copy of the actual voltage driving the tactor, scaled and protected for the Intan
`0-3.3 V` input range. This gives us a redundant command-side analog phase
reference and lets us compare the firmware sync pin against the real electrical
drive signal. It should not load or disturb the tactor driver.

Please also confirm that the board/core really maps `36` to `P1.04` and `38` to
`P1.06`. If the board variant uses different Arduino pin numbers, please replace
them with the correct board pin constants. Also please confirm the Intan digital
inputs are compatible with the nRF52 logic level, and that ground/reference or
isolation is handled properly.

For the sine table, I agree with keeping the start-at-zero table if that avoids
the startup click. Please confirm that the cycle sync rising edge fires at
`sine_index == 0`. With the start-at-zero table, we will define that rising edge
as the fixed phase reference, meaning phase zero corresponds to the waveform
minimum/trough.

After wiring, could you please run a short Intan test recording and verify the
saved signals?

- `SYNC_CYCLE_PIN` should show the correct edge rate at each frequency, e.g.
  about 5 edges/s at 5 Hz and 26 edges/s at 26 Hz.
- `TRIAL_GATE_PIN` should be HIGH for the full ON window and LOW during OFF.
- The PVDF analog channel should show the carrier waveform without clipping.
- The drive-signal copy should show the electrical carrier waveform without
  clipping.
- The firmware sync, drive-signal copy, and PVDF signal should have a stable
  phase relationship.

So the requested recorded signals are:

| Signal | Type | Intan input | What it tells us |
|---|---|---|---|
| `SYNC_CYCLE_PIN = 36` (`P1.04 / OUT1`) | Digital | Digital input | Command-side phase: one edge per carrier cycle |
| `TRIAL_GATE_PIN = 38` (`P1.06 / OUT2`) | Digital | Digital input | Trial timing: ON vs OFF |
| PVDF delivered-vibration signal | Analog | Analog input | Delivered mechanical phase + proof of motion |
| Buffered drive-signal copy | Analog | Analog input | Electrical drive phase, redundant command-side reference |

I will send the updated `actuator.cpp` and the PVDF charge-amp spec. I can also
share the diagnostic plots from the previous recording if useful.

Thanks again.

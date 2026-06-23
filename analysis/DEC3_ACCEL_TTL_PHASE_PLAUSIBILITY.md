# Dec 3 Accelerometer TTL Phase-Locking Plausibility Check

Question: can the Dec 3 accelerometer/digital signal be used as a cycle-by-cycle phase reference for 26 Hz stimulation, especially `amp100_freq26` and `amp250_freq26`?

Short answer: no, not for a strong stimulus-phase-locking analysis. It is useful for delivery/timing QC, but it does not behave like a 26 Hz phase clock.

## Available Stimulus Signal

The Dec 3 session folder contains:

- `amplifier.dat`
- `digitalin.dat`
- `time.dat`
- `info.rhd`

There is no saved `analogin.dat` or continuous accelerometer waveform in the Dec 3 folder.

The available accelerometer-like signal is therefore the thresholded digital signal on channel 7. This is a 1-bit TTL/comparator signal, not the analog vibration waveform.

## What A Usable 26 Hz Phase Signal Would Look Like

For a 3 s ON window:

- A one-pulse-per-cycle marker should show about 78 rising edges.
- A zero-crossing square wave should show about 156 total edges, or about 52 edges/s.
- Edges should be regular, with cycle spacing near 38.5 ms or half-cycle spacing near 19.2 ms.

## What Dec 3 Actually Shows

### `amp100_freq26`

- Median rising edges during ON: 4
- Median all edges during ON: 8
- Maximum rising edges in any trial: 20
- Maximum all edges in any trial: 39
- Median rising-edge frequency: about 2.17 Hz
- Trials with at least 60 rising edges: 0/200
- Trials with at least 120 total edges: 0/200
- Trials with median rising-edge interval near 26 Hz and enough edges: 0/200

Interpretation: `amp100_freq26` is not usable for stimulus phase. It is far too sparse.

### `amp250_freq26`

- Median rising edges during ON: 15.5
- Median all edges during ON: 31
- Maximum rising edges in any trial: 47
- Maximum all edges in any trial: 94
- Median rising-edge frequency: about 6.78 Hz
- Median all-edge rate: about 18.6 Hz
- Trials with at least 60 rising edges: 0/200
- Trials with at least 120 total edges: 0/200
- Trials with median rising-edge interval near 26 Hz and enough edges: 1/200

Best-looking examples still fail as phase references:

- Trial 1113 had 47 rising edges and 94 total edges, but median rising-edge frequency was about 18.3 Hz, not 26 Hz.
- Its all-edge rate was about 45.8 Hz, not the expected 52 Hz zero-crossing rate.
- Only about 7.5% of all-edge intervals were near a 26 Hz cycle interval.

Interpretation: `amp250_freq26` is the best delivery-QC condition, but still not reliable enough for cycle-by-cycle phase.

## What This Means

The Dec 3 TTL can answer:

> Did the actuator/sensor become active during the commanded ON window?

It cannot cleanly answer:

> What was the vibration phase at each moment?

So it cannot support the strongest steady-state test:

> Is dHPC/LEC LFP phase locked to the actual 26 Hz vibration cycle?

## What We Can Still Do With It

Reasonable Dec 3 uses:

- delivery QC
- onset-lag estimates by condition
- excluding trials with no detected sensor activity
- maybe aligning to first detected sensor toggle instead of commanded onset for an evoked-response sensitivity check
- comparing "good delivery" trials versus weak/no-blip trials

Not reasonable:

- Hilbert phase of the stimulus
- cycle-by-cycle LFP-to-stimulus PLV
- spike phase relative to actual vibration phase
- claiming stimulus-phase entrainment from this TTL alone

## Practical Next Analysis

The best Dec 3 follow-up is not true stimulus phase-locking. It is:

1. Select trials with good detected delivery, especially `amp250_freq26`.
2. Re-align LFP to first sensor toggle instead of commanded onset.
3. Re-run event-aligned LFP, driven-frequency power, and trial-onset PLV.
4. Compare against all trials.

If results strengthen after sensor-toggle alignment, that supports better stimulus timing/delivery. It still does not prove cycle-by-cycle steady-state entrainment.

For true steady-state phase-locking, the next recording needs a continuous analog actuator/force signal or a clean per-cycle phase TTL.

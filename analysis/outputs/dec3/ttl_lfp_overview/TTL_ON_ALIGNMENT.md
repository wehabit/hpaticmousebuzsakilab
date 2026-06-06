# TTL (accelerometer) vs commanded ON-time alignment - Dec 3

1185 of 1200 trials (98%) have the accelerometer fire inside the commanded ON
window - i.e., TTL and ON time are aligned. Breakdown:

| Criterion | Count |
|---|---|
| First blip inside the 3 s ON window | 1185 / 1200 (98%) |
| First blip within 0.5 s of ON onset | 921 / 1200 (77%) |
| First blip within 0.2 s of ON onset | 636 / 1200 (53%) |
| No sensor blip at all (no detected vibration) | 15 / 1200 (1%) |

And alignment quality tracks the condition (tighter = stronger stimulation):

| Condition | aligned (blip in ON) | typical onset lag |
|---|---|---|
| amp250_freq26 | 200/200 | 58 ms (tightest) |
| amp180_freq26 | 200/200 | 124 ms |
| amp100_freq26 | 199/200 | 226 ms |
| amp250_freq5 | 195/200 | 298 ms |
| amp180_freq5 | 200/200 | 344 ms |
| amp100_freq5 | 191/200 | 326 ms |

## How precisely does the measured onset match the commanded ON start?

First sensor *toggle* in each ON window vs the commanded ON start. No trial is exactly aligned - there is always a physical delivery lag (median 175 ms), because the accelerometer only fires once the device actually vibrates. So the TTL is a delivery *validator*, not the onset clock.

| Tolerance | Trials |
|---|---|
| exactly 0 ms | 0 / 1200 |
| within 1 ms | 3 / 1200 |
| within 5 ms | 30 / 1200 |
| within 10 ms | 53 / 1200 |
| within 20 ms | 103 / 1200 |
| within 50 ms | 219 / 1200 |
| within 100 ms | 393 / 1200 |

Figure: `ttl_on_alignment_per_trial.png` · per-trial data: `ttl_onset_offset_alignment.csv`

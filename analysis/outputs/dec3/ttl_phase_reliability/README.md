# Dec 3 TTL Phase Reliability Scan

This scan tests whether digital channel 7 can be used as a cycle-by-cycle phase marker.

| Condition | Expected cycles | Expected half-edges | Median rising | Max rising | Median all edges | Max all edges | Rising-cycle candidates | All-edge half-cycle candidates | Good delivery <=500 ms | Tight delivery <=200 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| amp100_freq26 | 78 | 156 | 4.0 | 20 | 8.0 | 39 | 0 | 0 | 155 | 87 |
| amp100_freq5 | 15 | 30 | 2.0 | 11 | 5.0 | 21 | 0 | 0 | 122 | 65 |
| amp180_freq26 | 78 | 156 | 9.0 | 23 | 17.0 | 45 | 0 | 0 | 179 | 142 |
| amp180_freq5 | 15 | 30 | 3.0 | 11 | 7.0 | 21 | 0 | 0 | 132 | 80 |
| amp250_freq26 | 78 | 156 | 15.5 | 47 | 31.0 | 94 | 0 | 0 | 197 | 189 |
| amp250_freq5 | 15 | 30 | 3.0 | 9 | 5.0 | 17 | 0 | 0 | 136 | 73 |

Interpretation:

- No condition produced reliable cycle-marker candidates under the strict criteria.
- The TTL is useful for delivery/onset QC, especially high-amplitude 26 Hz.
- It is not a continuous analog stimulus waveform and should not be used for true stimulus-phase PLV.

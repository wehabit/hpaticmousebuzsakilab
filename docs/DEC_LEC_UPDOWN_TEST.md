# Dec 4 — LEC UP/DOWN-state test (cortical-confirmation attempt)

Vöröslakos's anatomy criterion has two halves: **ripples confirm CA1 (dHPC)**, and
**UP/DOWN states + slow oscillations confirm cortex (LEC)**. The ripple half works
([DEC_RIPPLE_STATES.md](DEC_RIPPLE_STATES.md)). This is the LEC half — and the honest
answer is that **it does not work on this awake recording.** Script:
[lec_updown_states_dec4.py](../analysis/lec_updown_states_dec4.py).

## Method
In the quiet pre-experiment baseline, per region (LEC and dHPC as contrast):
- **DOWN states** = population-silence periods — the good+MUA population rate drops
  below 15 % of its median for ≥ 50 ms;
- **slow oscillation** = the 0.3–2 Hz peak in the region-mean LFP PSD;
- example LFP (broadband + 0.5–2 Hz) and population rate with DOWN shading.

## Result: no stereotyped cortical UP/DOWN in either region
| region | "DOWN" periods | rate | median dur | slow-osc "peak" |
|---|---|---|---|---|
| LEC | 437 | 0.16 /s | 60 ms | 2.0 Hz (band edge) |
| dHPC | 591 | 0.22 /s | 60 ms | 1.8 Hz (band edge) |

LEC and dHPC look **the same** — both show only generic quiet-period rate
fluctuations, **not** the stereotyped, bistable UP↔DOWN alternation with synchronous
population silence and a stereotyped slow-wave LFP. The "slow-osc peak" sits at the
analysis-band edge in both, i.e. there is **no genuine <1 Hz slow oscillation**.

## Why — and what it means
Classic cortical **UP/DOWN states and the slow oscillation are a NREM-sleep /
anesthesia phenomenon**; this was an **awake** haptic experiment, so the baseline
lacks them. So **UP/DOWN cannot confirm LEC = cortex on these data** — that would
need a sleep or anesthetized recording.

This does **not** weaken the LEC identification, which rests on:
- the **surgical targeting** (AP −3.8 / ML 3.8 / 10°; [DEC_PROBE_METADATA_VOROSLAKOS.md](DEC_PROBE_METADATA_VOROSLAKOS.md)), and
- the **now-confirmed channel map** (the `amplifier.xml` channelGroups = verified
  per-shank order; Cambridge ASSY-350 H15).

The dHPC = CA1 half **is** functionally confirmed, because **ripples occur in awake
quiet rest** and we detect them. The LEC = cortex functional check is simply deferred
to a future NREM/anesthesia recording — a clean, zero-cost addition next round.

## Takeaway
Honest negative: the awake baseline shows no cortical UP/DOWN or slow oscillation in
either region, so this route can't functionally confirm LEC = cortex here (it needs
sleep/anesthesia). Ripples confirm dHPC = CA1; LEC = cortex rests on targeting + the
confirmed channel map.

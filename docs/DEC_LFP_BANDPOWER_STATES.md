# Dec 3 + Dec 4 — LFP Band Power Across States

Companion to the aperiodic 1/f state analysis
([DEC_LFP_APERIODIC_STATES.md](DEC_LFP_APERIODIC_STATES.md)): band-limited LFP power
from the true pre-experiment baseline through ON / OFF / post-study. Bands:
**broadband** (1–100 Hz, line-excluded), **theta** (6–10), **gamma** (30–80), and the
**driven bands** (5/10/26/50 Hz ±1.5, with ON taken from the **matched-frequency**
trials). Each band is expressed as **dB change from that channel's own baseline**
(baseline = 0 dB; cross-channel scale cancels), bootstrap 95% CIs over channels.
Script: [lfp_bandpower_states_dec.py](../analysis/lfp_bandpower_states_dec.py).

## General bands: small, drift-tracking changes (no big state shift)
All broadband/theta/gamma changes are **< ~1 dB** (< ~25 % power) — consistent with
the stable aperiodic offset. The notable, modest patterns:

- **dHPC gamma is suppressed during ON** and recovers in OFF (Dec 3: ON −0.43 dB →
  OFF −0.07; Dec 4: ON −0.15 → OFF +0.07 dB) — a small stimulation-related gamma dip.
- **dHPC theta dips in ON, rises in OFF** (Dec 4: ON −0.12 → OFF +0.28 dB).
- **LEC gamma declines across the session** (ON −0.05 → OFF −0.26 → post −0.74 dB) —
  the same session drift seen in the spike rates and ripple analysis.
- Broadband power is near baseline throughout (±0.5 dB), confirming no broad shift.

## Driven bands: the only strong ON-specific elevation is LEC 50 Hz
| Dec 4, driven band | ON | OFF | post |
|---|---|---|---|
| **LEC · 50 Hz** | **+1.1 dB** | −0.35 | −0.90 |
| dHPC · 50 Hz | −0.15 | +0.22 | −0.28 |
| dHPC · 26 Hz | −0.48 | −0.27 | −0.79 |

**LEC 50 Hz-band power jumps +1.1 dB above baseline during ON**, and is *below*
baseline in OFF/post — a large, stimulus-locked, ON-specific elevation. It is the
**same artifact-suspect peak** flagged everywhere
([DEC4_50HZ_ARTIFACT_CHECK.md](DEC4_50HZ_ARTIFACT_CHECK.md)): treat as a real
narrowband peak during stimulation, not a proven neural rhythm. **dHPC shows no
driven-band elevation** at 26 or 50 Hz (its small 5 Hz ON bump is not ON-specific —
OFF/post are similarly elevated, i.e. drift). Dec 3 dHPC likewise shows no narrowband
following.

## Takeaway
Band power is broadly **stable / drift-tracking** across states (small theta/gamma
modulation, no broadband shift). The single robust, stimulus-locked LFP feature is
the **LEC 50 Hz +1.1 dB ON elevation** (pickup-suspect). This agrees with the
aperiodic-residual result and keeps the **single-unit rate effect** as the cleaner
neural evidence; within-trial ON/OFF remains the strongest stimulation-locked
contrast.

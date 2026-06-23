# Independent Inference: Steady-State Response vs Entrainment

Created: 2026-06-22

This note is based on numeric outputs in `analysis/outputs/` and `results/`, not on prior interpretive `.md` summaries.

## Question

Are the Dec3/Dec4 haptic mouse results showing:

1. Evoked responses?
2. Steady-state responses?
3. Native brain entrainment?
4. A broader brain state change?

## Short Answer

The current results support **stimulus-locked / evoked responses** and some **frequency-specific spectral/phase-following evidence**, especially around stimulation frequencies. They do **not yet prove native entrainment**.

The strongest current biological-looking effect is not a clean "the brain entrained at the driven frequency" story. It is more consistent with:

- sensory/haptic evoked responses,
- stimulus-frequency-following / steady-state-like responses in some analyses,
- broad on/off state modulation that depends on frequency and amplitude,
- possible suppression during stronger 26 Hz / 50 Hz stimulation in Dec4,
- and artifact/common-pickup concerns, especially for 50 Hz.

## Evidence For Evoked Response

Evoked response means the LFP changes time-locked to stimulus onset or offset.

Evidence:

- Event-aligned LFP summaries show condition-dependent changes in absolute LFP during stimulation and recovery.
- Dec3 raw event-aligned mean `stim - pre` across channels is positive for all conditions:
  - 5 Hz: about +15 to +17 absolute LFP units.
  - 26 Hz: about +15 to +46, strongest at amp180/freq26.
- Dec4 raw event-aligned mean `stim - pre` is positive for most 5/10/26 Hz conditions, but negative at 50 Hz high amplitudes.
- Broadband transition summaries show onset/offset/sustained windows are not flat relative to pre.

Inference:

The preparation is responding to the haptic stimulus. That is the minimum claim we can make.

## Evidence For Steady-State-Like Response

Steady-state response means the neural signal follows the rhythmic stimulus frequency while stimulation is ON.

Evidence:

- Trial-level driven-frequency power in Dec3 is strongly positive across all 5 Hz and 26 Hz conditions in `analysis/outputs/dec3/trial_level_stats/condition_summary_ci.csv`.
- Dec4 driven-frequency power is much weaker overall, with most confidence intervals crossing zero; 250/26 and 180/50 are negative in the condition-level summary.
- Dec4 `spectral_slope_itpc_summary.csv` shows some ITPC above null floor and some peaks above the 1/f background at driven frequencies, especially in parts of dHPC for 26/50 Hz. However, this is not uniform across probes/groups.
- Phase-locking summaries show small PLV values. Dec4 has modest positive delta-PLV for some conditions such as amp100/freq5 and amp180/freq10, but other conditions are flat or negative.

Important caveat:

The Dec3 trial-level driven-power statistic averages channels before computing power. That can inflate a common phase-locked stimulus response or artifact. The channel-wise frequency summaries are more conservative and show much smaller/mixed driven-power changes.

Inference:

We can say there is **some evidence for stimulus-frequency following / steady-state-like activity**, but it is not uniformly strong across sessions, frequencies, amplitudes, and analysis methods. The safest wording is "steady-state-like evoked response" or "stimulus-locked frequency-following response," not "entrainment."

## Evidence Against A Clean Entrainment Claim

Native entrainment would require evidence that the external haptic rhythm modulates an endogenous brain oscillator, not merely that the LFP contains stimulus-frequency energy.

Current weaknesses:

- PLV increases are small and inconsistent.
- Dec4 trial-level driven-frequency power is weak or negative for several conditions.
- Some 50 Hz results carry artifact risk: dead channels show stronger 50 Hz pickup, dHPC/LEC cross-region lag is near zero, and 50/100/150 Hz harmonic checks complicate interpretation.
- Spike modulation is sparse and mixed:
  - Dec3 dHPC: 0 responsive unit-condition tests at q < 0.05.
  - Dec4 dHPC: 19 / 180 responsive unit-condition tests.
  - Dec4 LEC: 13 / 180 responsive unit-condition tests.
  - Mean unit firing-rate changes are small and not clearly frequency-specific in a way that proves entrainment.
- ON vs OFF broadband controls show the stronger Dec4 effects are broad state changes/suppression at higher frequencies/amplitudes, not simply increased driven-frequency oscillation.

Inference:

These data do **not** currently demonstrate native oscillatory entrainment.

## Evidence For Broader State Change

Dec4 has strong frequency/amplitude-dependent broadband ON-minus-OFF effects:

- 26 Hz:
  - amp180/freq26: ON minus OFF about -4.22, CI excludes zero.
  - amp250/freq26: ON minus OFF about -9.21, CI excludes zero.
- 50 Hz:
  - amp100/freq50: ON minus OFF about -8.88, CI excludes zero.
  - amp180/freq50: ON minus OFF about -9.74, CI excludes zero.
  - amp250/freq50: ON minus OFF about -11.02, CI excludes zero.

This looks more like a stimulation-induced state shift or suppression than a clean steady-state entrainment effect.

Inference:

The most interesting current result may be **frequency/amplitude-dependent broadband state modulation**, especially suppression at stronger 26/50 Hz in Dec4. That is biologically interesting, but it is not the same as entrainment.

## What Would Need To Be Present To Claim Entrainment

To claim native entrainment, we would need at least several of the following:

1. Clear frequency-specific power increase at the stimulation frequency, above 1/f background, across relevant channels/probes.
2. Strong phase-locking/ITPC to the stimulus rhythm during stimulation, clearly above a shuffled/null floor.
3. Evidence that the response is not electrical/mechanical artifact:
   - absent or much smaller on dead channels,
   - plausible spatial gradient/localization,
   - plausible inter-region phase lags,
   - no suspicious common-mode zero-lag pickup,
   - harmonics consistent with biology rather than device artifact.
4. Evidence that an endogenous rhythm is being modulated:
   - pre-existing oscillatory peak shifts or locks to stimulus,
   - intrinsic-frequency dependence,
   - phase reset of ongoing rhythm,
   - persistence/carryover after stimulation stops,
   - interaction with native theta/gamma/ripple structure.
5. Spike-field evidence:
   - neurons phase-lock more strongly during stimulation than OFF/pre,
   - locking is frequency-specific,
   - firing-rate changes are not only broadband arousal/suppression.
6. Frequency controls:
   - 5/10/26/50 Hz produce different responses in ways matching circuit hypotheses.
   - Effects are not simply amplitude or movement.
7. State controls:
   - attention/arousal/movement/anesthesia/sleep state are measured or controlled.

## Current Best Wording

Use:

- "haptic stimulation evokes LFP responses"
- "stimulus-frequency-following response"
- "steady-state-like response"
- "frequency/amplitude-dependent broadband modulation"
- "possible target engagement"

Avoid for now:

- "native gamma entrainment"
- "entrainment of hippocampal/entorhinal oscillations"
- "40/50 Hz restores gamma"
- "cross-region entrainment"

## Immediate Next Analyses

1. Recompute driven-frequency power per channel/probe without channel averaging first.
2. Add explicit stimulus-phase ITPC using actual actuator/TTL pulse timing, not only trial onset.
3. Compare ON, OFF, and pre for the exact same frequency band and exact same channels.
4. Quantify dead-channel and reference-mode sensitivity for every frequency, not only 50 Hz.
5. Plot spatial gradients across probe depth for driven-frequency amplitude and phase.
6. Add shuffle/null tests:
   - trial-label shuffle,
   - phase-randomized surrogate,
   - off-window pseudo-stimulation,
   - frequency-mismatched controls.
7. Test carryover:
   - does phase/power persist after stimulus offset?
   - does repeated stimulation change later trials?
8. For 50 Hz specifically, treat all cross-region coherence as suspicious until artifact controls are stronger.


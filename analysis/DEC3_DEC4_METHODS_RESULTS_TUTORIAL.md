# Dec 3 and Dec 4 Haptic Ephys: Methods, Results, and Conservative Inference

This note is meant to be a teaching map. It ignores the older interpretation prose and reads the pipeline outputs directly.

The central question is:

> Did haptic stimulation merely evoke responses, did it produce a steady-state/frequency-following response, or did it entrain a native brain rhythm?

My short answer:

- Dec 3: clear evoked LFP response; possible weak/method-dependent steady-state-like signal; no convincing entrainment.
- Dec 4: clear evoked/state response; strongest result is broadband suppression during high-amplitude 26/50 Hz stimulation; no clean entrainment; 50 Hz has artifact concerns.

## Vocabulary First

### LFP

LFP means local field potential. Think of it as a local electrical field microphone. It does not record one neuron. It mostly reflects summed synaptic/transmembrane currents from nearby neural tissue, plus reference effects, volume conduction, movement, and possible stimulation pickup.

This is why Buzsaki-style caution matters: a big LFP effect is real as a signal, but it is not automatically a native brain rhythm.

Relevant local note:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/buzsaki-008-the-origin-of-extracellular-fields-and-currents-eeg-ecog-lfp-and-spikes.md`

### Evoked response

An evoked response means the brain/electrode signal changes after the stimulus starts.

It answers:

> Did the stimulus cause any time-locked response?

It does not answer:

> Did the brain follow the stimulus rhythm?

In this repo, event-aligned LFP is the main evoked-response test.

### Steady-state response

A steady-state response means repeated stimulation creates a repeated brain/electrode response at the same frequency as the stimulus.

Example: a 26 Hz vibration produces a 26 Hz component in the LFP.

It answers:

> Is there frequency-following at the driven frequency?

It still does not prove:

> The external rhythm captured a native oscillator.

Buzsaki's local inventory says this is the key trap: sensory steady-state responses are easy to induce, but they are not automatically native gamma entrainment.

Relevant local note:

- `/Users/paris/Documents/LitretureReview_Github/buzsaki_entrainment_steady_state_inventory.md`

### Entrainment

Entrainment is the stronger claim. It means an external rhythm changes the timing of an endogenous brain oscillator.

For a strong entrainment claim, we would want several of these:

- A native rhythm exists before stimulation.
- During stimulation, its phase or frequency locks to the external drive.
- The effect survives reasonable referencing, movement exclusion, and artifact checks.
- It appears in good tissue channels more than dead/noisy channels.
- Spikes participate, not just LFP.
- There is phase carryover or a post-stimulus signature after the stimulus ends.
- Controls show frequency specificity, not just "any rhythmic stimulus makes a line."

Our Dec 3 and Dec 4 outputs do not yet meet that bar.

### Broadband in this pipeline

This is the part that can be confusing.

In this repo, "broadband" mostly means:

> Overall absolute LFP size in a time window, after baseline correction and referencing.

It is not the same as:

> Power at exactly 26 Hz or 50 Hz.

It is also not automatically:

> High-gamma broadband spiking proxy.

Here, broadband tells us whether the stimulation changed the overall field state. A broadband increase or decrease could reflect neural population state, sensory response, suppression/desynchronization, arousal, movement, reference effects, or artifact. It is important, but it is not entrainment by itself.

## What Each Pipeline Method Did

### 1. Session summary and TTL alignment

Files:

- `analysis/outputs/dec3/session_summary.json`
- `analysis/outputs/dec3/dec3_condition_sequence.csv`
- `analysis/outputs/dec4/session_summary.json`
- `analysis/outputs/dec4/stimulus_config_schedule.csv`

What it does:

It figures out the recording metadata and the timing of stimulation trials.

Why it matters:

Before interpreting brain data, we need to know exactly when stimulation started and which condition each trial used.

### 2. Event-aligned LFP

Script:

- `analysis/event_aligned_lfp.py`

Outputs:

- `analysis/outputs/dec3/event_aligned_lfp/condition_channel_lfp_summary.csv`
- `analysis/outputs/dec4/event_aligned_lfp/condition_channel_lfp_summary.csv`

What it does:

For each trial, it cuts out a window around stimulus onset: before stimulation, during stimulation, and recovery after stimulation. It baseline-corrects the segment and asks whether mean absolute LFP is larger or smaller during stimulation than before.

Why it matters:

This is the simplest evoked-response test.

Important caveat:

The script says this is exploratory and does not remove stimulation artifacts or median-subtract channels. So it is good for "something happened," but not enough for mechanism.

### 3. Artifact-aware LFP

Script:

- `analysis/artifact_aware_lfp.py`

What it does:

It avoids immediate onset and offset margins, then looks at the more sustained portion of the response.

Why it matters:

The first and last moments of stimulation can be contaminated by mechanical/electrical transients.

### 4. Frequency-specific LFP power

Script:

- `analysis/frequency_lfp.py`

Outputs:

- `analysis/outputs/dec3/frequency_lfp/frequency_lfp_group_summary.csv`
- `analysis/outputs/dec4/frequency_lfp/frequency_lfp_group_summary.csv`

What it does:

It compares power at the driven frequency during stimulation versus before stimulation.

Example:

- For a 26 Hz condition, it asks whether 26 Hz power increased during stimulation.
- For a 5 Hz condition, it asks whether 5 Hz power increased during stimulation.

Why it matters:

This is the first steady-state/frequency-following test.

Important caveat:

This method computes per-channel power first and then summarizes across channels. That makes it more conservative than averaging channels first.

### 5. Time-frequency analysis

Script:

- `analysis/time_frequency_lfp.py`

Outputs:

- `analysis/outputs/dec3/time_frequency_lfp/`
- `analysis/outputs/dec4/time_frequency_lfp/`

What it does:

It makes spectrogram-like views: how power at different frequencies changes over time around stimulation.

Why it matters:

It helps separate onset transients, sustained responses, offset responses, and recovery/carryover.

### 6. Phase-locking LFP

Script:

- `analysis/phase_locking_lfp.py`

Outputs:

- `analysis/outputs/dec3/phase_locking_lfp/phase_locking_summary.csv`
- `analysis/outputs/dec4/phase_locking_lfp/phase_locking_summary.csv`

What it does:

It bandpasses the LFP around the driven frequency, extracts phase with a Hilbert transform, and computes PLV across trials.

PLV means phase-locking value. If the phase is consistent across trials, PLV is high. If phase is random across trials, PLV is low.

Why it matters:

This is closer to an entrainment test than power alone.

Important caveat:

Stimulus-locked PLV can still be produced by repeated evoked responses. It is necessary for entrainment-like claims, but not sufficient for native entrainment.

### 7. Trial-level stats

Script:

- `analysis/trial_level_stats_dec3.py`

Outputs:

- `analysis/outputs/dec3/trial_level_stats/condition_summary_ci.csv`
- `analysis/outputs/dec4/trial_level_stats/condition_summary_ci.csv`

What it does:

For each trial and analysis group, it computes:

- sustained broadband delta: sustained ON absolute LFP minus pre absolute LFP
- offset broadband delta: offset window absolute LFP minus pre absolute LFP
- driven power log2 delta: driven-frequency power during stimulation divided by pre power

Then it bootstraps confidence intervals across trials.

Why it matters:

It tells us whether condition effects are reliable across trials.

Important caveat:

For driven power, this script averages channels within a group first, then computes power. That can amplify common phase-locked signals, including shared evoked responses or artifact. So if this method is positive but channel-wise power is weak, I trust the conclusion less.

### 8. Broadband transition stats

Script:

- `analysis/broadband_transition_stats_dec3.py`

Outputs:

- `analysis/outputs/dec3/broadband_transition/`
- `analysis/outputs/dec4/broadband_transition/`

What it does:

It splits the trial into windows:

- onset
- sustained
- offset
- recovery

Why it matters:

This asks whether the response is a brief onset event, a sustained state change, an offset rebound, or a recovery/carryover effect.

### 9. OFF-control broadband

Script:

- `analysis/off_control_broadband_dec3.py`

Outputs:

- `analysis/outputs/dec3/off_control_broadband/off_control_condition_summary_ci.csv`
- `analysis/outputs/dec4/off_control_broadband/off_control_condition_summary_ci.csv`

What it does:

It compares the ON period to the following OFF period inside the same trial.

Why it matters:

This is a strong sanity check. If ON and OFF both look elevated versus pre, the effect may be slow drift, recovery, carryover, or state change rather than the stimulation ON period specifically.

### 10. Reference sensitivity

Script:

- `analysis/reference_sensitivity_lfp.py`

Outputs:

- `analysis/outputs/dec3/reference_sensitivity_lfp/`
- `analysis/outputs/dec4/reference_sensitivity/`

What it does:

It asks whether effects survive different referencing choices.

Why it matters:

LFP can be dominated by common signals. A robust biological effect should not disappear or flip under reasonable referencing.

### 11. Movement checks

Scripts:

- `analysis/movement_from_lfp_dec3.py`
- `analysis/movement_proxy_dec4.py`

Outputs:

- `analysis/outputs/dec3/movement/`
- `analysis/outputs/dec4/movement/movement_summary.json`

What it does:

It estimates whether high-movement trials explain the LFP results.

Why it matters:

Movement can create large LFP-like signals.

Dec 4 note:

The Dec 4 movement summary says the driven-power results are highly correlated before and after excluding high-movement trials, so the driven-power pattern is probably not explained only by the highest-movement trials.

### 12. Dec 4 50 Hz artifact check

Script:

- `analysis/artifact_check_50hz_dec4.py`

Output:

- `analysis/outputs/dec4/artifact_check_50hz/artifact_check_summary.json`

What it does:

It asks whether the 50 Hz signal looks neural or artifact-like by checking:

- good channels versus dead/noisy channels
- harmonics at 100/150 Hz
- cross-region phase lag
- amplitude scaling

Why it matters:

50 Hz is especially vulnerable to electrical/mechanical pickup and shared signal contamination.

### 13. Spikes

Outputs:

- `analysis/outputs/cross_dataset_spike_compare/overview.csv`
- `analysis/outputs/dec3/spike_peth_on_off/`
- `analysis/outputs/dec4/spike_peth_on_off_dhpc/`
- `analysis/outputs/dec4/spike_peth_on_off_lec/`

What it does:

It asks whether sorted units change firing rate during stimulation and whether spikes lock to LFP phase.

Why it matters:

Spikes are stronger biological evidence than LFP alone. If LFP shows a huge "rhythm" but spikes do not care, be cautious.

## Dec 3: Step-by-Step

### Setup

Dec 3 has 128 channels and 6 conditions:

- 5 Hz at amplitudes 100, 180, 250
- 26 Hz at amplitudes 100, 180, 250

Each condition has about 200 configured trials.

### Dec 3 evoked response

Event-aligned mean absolute LFP changed during stimulation.

Mean stim minus pre across channels:

| Condition | Mean stim-pre abs LFP |
|---|---:|
| amp100_freq5 | +16.83 |
| amp180_freq5 | +15.58 |
| amp250_freq5 | +14.74 |
| amp100_freq26 | +27.69 |
| amp180_freq26 | +46.39 |
| amp250_freq26 | +15.28 |

Interpretation:

There is a real evoked response. The biggest raw event-aligned effect is 26 Hz at amplitude 180.

Conservative language:

> Dec 3 haptic stimulation evokes LFP responses.

Not yet:

> Dec 3 entrains the brain.

### Dec 3 driven-frequency power

Channel-wise frequency-specific power is small and mixed.

Mean driven log2 power change across analysis groups:

| Condition | Channel-wise driven log2 change |
|---|---:|
| amp100_freq5 | -0.083 |
| amp180_freq5 | +0.135 |
| amp250_freq5 | -0.057 |
| amp100_freq26 | -0.015 |
| amp180_freq26 | -0.059 |
| amp250_freq26 | -0.147 |

Interpretation:

The conservative channel-wise method does not show a clean, strong frequency-following increase.

But the trial-level method reports large positive driven-power deltas around +1.6 to +1.7 log2 units for all conditions. That is a warning sign, because the trial-level method averages channels before computing power. A shared phase-locked evoked signal or artifact can look strong in that calculation.

Conservative language:

> Dec 3 has method-dependent driven-frequency evidence. The conservative channel-wise result is weak.

### Dec 3 phase locking

PLV sustained minus pre is tiny and inconsistent.

Mean PLV sustained-pre across analysis groups:

| Condition | PLV change |
|---|---:|
| amp100_freq5 | -0.0131 |
| amp180_freq5 | +0.0052 |
| amp250_freq5 | -0.0006 |
| amp100_freq26 | -0.0042 |
| amp180_freq26 | -0.0007 |
| amp250_freq26 | -0.0105 |

Interpretation:

This argues against strong phase locking during sustained stimulation.

Conservative language:

> Dec 3 does not show consistent sustained phase-locking increases.

### Dec 3 broadband

Trial-level sustained broadband showed one positive-looking condition:

| Condition | Sustained broadband delta | 95% CI |
|---|---:|---|
| amp180_freq26 | +6.65 | +2.93 to +10.71 |

But the OFF-control test weakens this. ON minus OFF confidence intervals crossed zero for every Dec 3 condition.

Example:

| Condition | ON minus OFF broadband | 95% CI |
|---|---:|---|
| amp180_freq26 | -2.14 | -5.40 to +1.09 |

Interpretation:

There may be broadband state/recovery effects, especially around 26 Hz amplitude 180, but the ON period is not cleanly larger than the following OFF period.

Conservative language:

> Dec 3 broadband effects are not robust against within-trial OFF control.

### Dec 3 spikes

Cross-dataset spike comparison:

| Dataset | Curated good units | Responsive q<0.05 | Mean ON-OFF Hz |
|---|---:|---:|---:|
| dec3_dHPC | 29 | 0 | -0.1399 |

Interpretation:

No reliable spike response was detected in Dec 3 curated units.

### Dec 3 bottom line

Dec 3 supports:

- evoked response: yes
- steady-state/frequency-following: possible, but weak and method-dependent
- native entrainment: no convincing evidence
- broadband state effect: possible, but not robust versus OFF control
- spike support: no

Best one-sentence interpretation:

> Dec 3 shows haptic-evoked LFP responses, but the stronger entrainment-style evidence is missing.

## Dec 4: Step-by-Step

### Setup

Dec 4 has 256 channels and 12 conditions:

- 5, 10, 26, and 50 Hz
- amplitudes 100, 180, 250
- about 200 trials per condition
- two probe/region groups: dHPC and LEC

### Dec 4 evoked/state response

Event-aligned mean absolute LFP changed during stimulation.

Mean stim minus pre across channels:

| Condition | Mean stim-pre abs LFP |
|---|---:|
| amp100_freq5 | +45.96 |
| amp180_freq5 | +43.03 |
| amp250_freq5 | +21.94 |
| amp100_freq10 | +33.95 |
| amp180_freq10 | +50.76 |
| amp250_freq10 | +30.56 |
| amp100_freq26 | +23.36 |
| amp180_freq26 | +18.21 |
| amp250_freq26 | +3.84 |
| amp100_freq50 | +12.07 |
| amp180_freq50 | -28.51 |
| amp250_freq50 | -32.15 |

Interpretation:

There is a strong evoked/state response. Low-frequency and moderate conditions tend to increase raw absolute LFP. High-amplitude 50 Hz decreases it.

This already tells us Dec 4 is not a simple "more frequency means more response" story. It looks like stimulation can push the system into different field states depending on frequency and amplitude.

### Dec 4 driven-frequency power

Channel-wise driven-frequency power is weak and mixed.

Mean driven log2 power change across analysis groups:

| Condition | Channel-wise driven log2 change |
|---|---:|
| amp100_freq5 | +0.049 |
| amp180_freq5 | -0.002 |
| amp250_freq5 | -0.060 |
| amp100_freq10 | -0.004 |
| amp180_freq10 | +0.036 |
| amp250_freq10 | -0.054 |
| amp100_freq26 | -0.067 |
| amp180_freq26 | -0.052 |
| amp250_freq26 | -0.093 |
| amp100_freq50 | -0.224 |
| amp180_freq50 | -0.070 |
| amp250_freq50 | +0.057 |

Trial-level driven power also does not show a broad clean increase. Some conditions are slightly negative, and only a few confidence intervals exclude zero.

Interpretation:

The strongest Dec 4 result is not narrow driven-frequency power.

Conservative language:

> Dec 4 does not show a robust, broad driven-frequency power increase.

### Dec 4 phase locking

Mean PLV sustained minus pre across groups:

| Condition | PLV change |
|---|---:|
| amp100_freq5 | +0.0205 |
| amp180_freq5 | -0.0001 |
| amp250_freq5 | +0.0016 |
| amp100_freq10 | +0.0046 |
| amp180_freq10 | +0.0107 |
| amp250_freq10 | -0.0352 |
| amp100_freq26 | -0.0034 |
| amp180_freq26 | -0.0175 |
| amp250_freq26 | -0.0095 |
| amp100_freq50 | -0.0045 |
| amp180_freq50 | -0.0128 |
| amp250_freq50 | +0.0128 |

Interpretation:

The phase-locking changes are small and inconsistent.

Conservative language:

> Dec 4 does not show consistent sustained phase-locking increases.

### Dec 4 broadband is the clearest effect

Trial-level sustained broadband:

| Condition | Sustained broadband delta | 95% CI |
|---|---:|---|
| amp180_freq10 | +5.84 | +2.00 to +9.59 |
| amp180_freq26 | -4.25 | -7.39 to -1.13 |
| amp250_freq26 | -8.66 | -12.26 to -5.09 |
| amp180_freq50 | -13.94 | -17.36 to -10.26 |
| amp250_freq50 | -15.38 | -18.51 to -12.37 |

Interpretation:

Dec 4 shows a strong broadband suppression pattern for higher-amplitude 26 and 50 Hz stimulation.

This means:

> The overall LFP field amplitude became smaller during these stimulation conditions.

It does not mean:

> The brain entrained at 26 or 50 Hz.

Possible explanations include neural suppression/desynchronization, altered state, sensory adaptation, reference/common-mode effects, or artifact. The OFF-control and artifact checks help separate these.

### Dec 4 OFF-control broadband

ON minus OFF broadband is strongly negative for 26 and 50 Hz:

| Condition | ON minus OFF broadband | 95% CI |
|---|---:|---|
| amp180_freq26 | -4.22 | -6.52 to -1.83 |
| amp250_freq26 | -9.21 | -11.45 to -6.98 |
| amp100_freq50 | -8.88 | -11.59 to -6.22 |
| amp180_freq50 | -9.74 | -12.17 to -7.46 |
| amp250_freq50 | -11.02 | -13.32 to -8.68 |

Interpretation:

This is stronger than Dec 3. It says the broadband suppression is specific to the ON period relative to nearby OFF, especially for 26/50 Hz.

Conservative language:

> Dec 4 shows robust ON-period broadband suppression for 26/50 Hz stimulation, strongest at higher amplitudes.

### Dec 4 movement check

The movement proxy excluded the top 25% highest-movement trials. The driven-power pattern before versus after exclusion had correlation 0.903.

Interpretation:

The driven-power pattern is probably not explained only by the highest-movement trials.

Caveat:

This is an LFP-only proxy, not a perfect body movement measurement.

### Dec 4 50 Hz artifact check

Important values:

| Check | Result |
|---|---|
| LEC good channels 50 Hz ON-OFF | +4.90 |
| LEC dead channels 50 Hz ON-OFF | +28.40 |
| LEC dead/good pickup ratio | 5.796 |
| Cross-region 50 Hz phase lag | about -0.264 ms |
| Artifact flag | dead-channel pickup high |

Interpretation:

The 50 Hz LFP coordination/coherence result is suspicious. Dead/noisy LEC channels pick up much more 50 Hz than good channels, and dHPC/LEC lag is close to zero. That can happen with shared electrical/mechanical pickup.

Important nuance:

This does not mean every Dec 4 effect is artifact. It means any 50 Hz narrowband/coherence claim needs heavy caution.

### Dec 4 spikes

Cross-dataset spike comparison:

| Dataset | Curated good units | Responsive q<0.05 | Mean ON-OFF Hz | Percent ON>OFF |
|---|---:|---:|---:|---:|
| dec4_dHPC | 15 | 19/180 tests | +0.0431 | 46.1% |
| dec4_LEC | 15 | 13/180 tests | -0.0070 | 46.7% |

Interpretation:

Some unit-condition tests are responsive, but the population effect is tiny and mixed. The percent ON>OFF is below 50% in both dHPC and LEC.

Conservative language:

> Dec 4 has some unit-level responses, but not a clean population firing-rate signature of entrainment.

### Dec 4 bottom line

Dec 4 supports:

- evoked/state response: yes
- broadband ON-period suppression at 26/50 Hz: yes, strongest result
- narrow driven-frequency power increase: not robust
- phase-locking increase: weak/inconsistent
- 50 Hz coherence/coordination: artifact-concerning
- spike support: small/mixed
- native entrainment: not proven

Best one-sentence interpretation:

> Dec 4 shows robust stimulation-dependent broadband state modulation, especially suppression during 26/50 Hz ON periods, but it does not yet show clean native entrainment.

## What The Local Papers Add

### Buzsaki steady-state inventory

Local file:

- `/Users/paris/Documents/LitretureReview_Github/buzsaki_entrainment_steady_state_inventory.md`

Use it for:

- distinguishing steady-state sensory responses from native entrainment
- avoiding overclaiming "40 Hz entrainment"
- defining what stronger evidence would require

How it applies here:

Our data have evoked responses and some possible frequency-following hints, but we should not call that entrainment.

### Soula/Buzsaki 40 Hz caution paper

Local file:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/ad-016-forty-hertz-light-stimulation-does-not-entrain-native-gamma-oscillations-in-alzheimers-dis.md`

Use it for:

- the strongest caution that 40 Hz sensory stimulation can fail to entrain native gamma
- separating stimulus-locked response from native gamma engagement

How it applies here:

Even if we saw a 40 or 50 Hz LFP line, that alone would not prove native gamma entrainment.

### Buzsaki LFP origin paper

Local file:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/buzsaki-008-the-origin-of-extracellular-fields-and-currents-eeg-ecog-lfp-and-spikes.md`

Use it for:

- explaining why LFP is summed field activity and must be interpreted carefully
- grounding the broadband caveat

How it applies here:

Broadband LFP changes are meaningful, but they are not one-to-one readouts of spikes or cognition.

### Buzsaki gamma coherence paper

Local file:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/buzsaki-002-what-does-gamma-coherence-tell-us-about-inter-regional-neural-communication.md`

Use it for:

- caution around coherence and inter-region communication claims

How it applies here:

The Dec 4 50 Hz dHPC/LEC coherence result should not be overread, especially with artifact flags.

### Vibrotactile coding papers

Local file:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/vibro-028-periodicity-and-firing-rate-as-candidate-neural-codes-for-the-frequency-of-vibrotactile-st.md`

Use it for:

- showing that 5 to 50 Hz tactile flutter can drive somatosensory neurons
- explaining periodicity and firing-rate coding of vibrotactile frequency

How it applies here:

It supports the idea that haptic stimulation can evoke or drive somatosensory responses. It does not by itself prove hippocampal/entorhinal native entrainment.

### Direct iEEG theta-burst stimulation paper

Local file:

- `/Users/paris/Documents/LitretureReview_Github/notes/papers/direct-006-theta-burst-stimulation-entrains-frequency-specific-oscillatory-responses.md`

Use it for:

- an example of stronger human direct-stimulation evidence
- thinking about frequency, target, state, and direct circuit engagement

How it applies here:

It shows the kind of evidence we would want: frequency-specific responses in intracranial recordings with stimulation parameters and neural readouts. Our haptic data are peripheral sensory stimulation, so the evidentiary bar is harder.

## What We Should Do Next Analytically

To separate evoked response, steady-state response, and possible entrainment, the next analyses should ask:

### 1. Evoked versus induced power

Compute two versions of driven-frequency power:

- total power: normal single-trial power
- induced/residual power: subtract the trial-average evoked waveform first, then compute power

Why:

If the 26/50 Hz signal disappears after subtracting the trial-average waveform, it was mostly evoked/phase-locked response. If it remains, that is stronger evidence for induced oscillatory activity.

### 2. Stimulus-phase locking, if actuator phase is available

Compare LFP phase to actual actuator/stimulus phase, not just trial onset.

Why:

True frequency following should have a stable phase relationship to the physical stimulus.

### 3. Post-stimulus carryover

Ask whether phase or power persists after stimulation stops.

Why:

Carryover is one of the differences between externally imposed response and altered native oscillator.

### 4. Dead-channel and reference robustness for every frequency

Especially for 50 Hz, repeat artifact logic across conditions.

Why:

Good tissue channel specificity matters.

### 5. Spike timing at driven frequency

Ask whether spikes lock to the stimulus rhythm or LFP phase during ON more than OFF.

Why:

LFP-only rhythm is weaker evidence than LFP plus spikes.

### 6. Frequency specificity curve

Ask whether responses are truly special at a frequency or just scale with amplitude/intensity/discomfort/movement.

Why:

Entrainment should have frequency structure, not just "stronger stimulus makes a bigger field change."

## Working Claims We Can Safely Use

Safe:

> Haptic stimulation evoked measurable LFP responses in Dec 3 and Dec 4.

Safe:

> Dec 4 showed robust broadband suppression during 26/50 Hz ON periods, strongest at higher amplitudes.

Safe:

> The narrow driven-frequency and PLV evidence is weak or inconsistent, so native entrainment is not established.

Safe:

> The 50 Hz Dec 4 LFP coordination result is artifact-concerning and should not be used alone as evidence of neural entrainment.

Not safe yet:

> The haptic device entrained native gamma.

Not safe yet:

> The Dec 4 50 Hz coherence proves dHPC-LEC communication.

Not safe yet:

> Broadband suppression is definitely beneficial or disease-relevant.

## Final Mental Model

Think of the evidence ladder like this:

1. Evoked response: "the signal changed when stimulation happened."
2. Steady-state response: "the signal followed the stimulation frequency."
3. Native entrainment: "an existing brain rhythm was captured or modulated by the external rhythm."
4. Mechanistic/therapeutic relevance: "that rhythm/state change matters for memory, sleep, glymphatic flow, pathology, or behavior."

Dec 3 is mostly level 1, with weak/method-dependent hints of level 2.

Dec 4 is level 1 plus a strong broadband state/suppression effect. It is not clean level 2 across the board, and it is not level 3 yet.

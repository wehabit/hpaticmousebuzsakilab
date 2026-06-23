# Follow-Up Work Proposal: Haptic Stimulation And Glymphatic-Relevant Brain State

## Working Title

Can haptic stimulation shift the mouse brain toward a glymphatic-clearance-permissive state?

## Motivation

Our Dec 3 / Dec 4 recordings show that haptic stimulation affects the brain,
with the cleanest current result being a 50 Hz high-amplitude single-unit
firing-rate effect in memory-relevant regions, especially dHPC. However, this
does not yet show glymphatic clearance, native entrainment, or CSF/ISF flow.

The glymphatic literature suggests that clearance is strongly state-dependent.
Natural sleep, slow-wave/delta activity, vascular pulsatility, autonomic state,
and coordinated neural population dynamics are all relevant. Jiang-Xie et al.
2024 adds an important mechanistic bridge: synchronized neural activity can
generate large extracellular ionic/field waves that may help organize
CSF-to-ISF perfusion and brain clearance.

The realistic follow-up should therefore avoid the overclaim:

> Haptic stimulation entrains gamma and clears amyloid.

The stronger and more testable hypothesis is:

> Haptic stimulation may improve glymphatic-relevant physiology if it shifts
> neural, autonomic, vascular, or CSF/ISF dynamics toward a
> clearance-permissive state.

## Practical Constraint

Stimulating a naturally sleeping mouse is probably not the best first
experiment. Vibration may wake the animal, disrupt sleep scoring, and make the
result hard to interpret. The first-pass study should therefore test awake or
quiet-wake stimulation and then ask whether it changes target engagement,
state, and offline tracer movement.

## Central Hypothesis

Haptic stimulation can engage the somatosensory pathway and downstream
memory-relevant circuits. If the stimulation also shifts the animal toward a
clearance-permissive state, we should observe one or more of the following:

- clean sensory target engagement in S1;
- replicated dHPC firing-rate or field-potential modulation;
- increased slow-wave/delta activity or altered theta dynamics;
- reduced movement/arousal or calmer autonomic state;
- increased CSF tracer influx into brain tissue;
- improved tracer clearance/efflux in a later-stage experiment.

## Specific Aim 1: Establish Clean Haptic Target Engagement

### Question

Does the haptic stimulus reliably enter the mouse brain through the
somatosensory pathway and reach downstream dHPC circuits?

### Recording Targets

Minimum preferred targets:

1. Contralateral S1 matched to the stimulated body region.
2. dHPC, ideally with CA1/DG coverage if anatomy allows.

Optional third target:

- LEC/MEC if the question is memory-circuit propagation.
- VPL/VPM thalamus if the question is sensory relay and target engagement.

### Required Non-Neural Channels

- actual actuator motion: PVDF or accelerometer time-locked to Intan;
- digital trial ON/OFF;
- stimulus phase or cycle marker if possible;
- cortical EEG/LFP for state;
- EMG and video/accelerometer for movement;
- heart rate or respiration if feasible.

### Frequencies

Use a small, interpretable panel:

- 50 Hz: strongest current Dec 4 single-unit candidate;
- 40 Hz: literature/GENUS comparator;
- 1 Hz or 8 Hz: Jiang-Xie-inspired slow/theta comparator;
- 26 Hz: continuity with Dec 3 / Dec 4;
- sham/no stimulation.

If time is limited, use:

- sham;
- 50 Hz;
- 1 Hz or 8 Hz;
- 40 Hz.

### Primary Readouts

- S1 firing-rate modulation and LFP/field response;
- dHPC firing-rate modulation and slow/theta/ripple changes;
- stimulus-phase locking if the stimulus phase is recorded;
- movement/EMG changes;
- delta/theta power before, during, and after stimulation.

### Interpretation

Positive result:

> Haptic stimulation has clean target engagement and reaches memory-relevant
> circuits.

Negative result:

> If S1 is weak or inconsistent, downstream dHPC/LEC effects are difficult to
> interpret as meaningful haptic target engagement.

## Specific Aim 2: Test Awake/Quiet-Wake CSF Tracer Influx Offline

### Question

Does haptic stimulation increase CSF-to-ISF tracer influx under runnable mouse
conditions?

### Design

Use an offline endpoint tracer assay:

1. Deliver tracer into CSF, preferably through cisterna magna access.
2. Deliver stimulation while the animal is awake or quietly resting.
3. Record EEG/EMG/movement during the stimulation window.
4. Allow a fixed tracer circulation period.
5. Perfuse/fix the brain.
6. Quantify fluorescent tracer distribution in brain tissue.

### Groups

Minimum:

- sham/no stimulation;
- 50 Hz haptic;
- slow/theta comparator: 1 Hz or 8 Hz.

Better:

- sham;
- 1 Hz;
- 8 Hz;
- 40 Hz;
- 50 Hz.

Optional:

- 26 Hz for continuity with existing data.

### Regions To Quantify

- S1 matched to stimulation site;
- dHPC;
- entorhinal cortex;
- cortex broadly;
- perivascular spaces if histology supports it;
- whole-brain or section-level tracer burden.

### Primary Readout

Amount and distribution of tracer entering brain tissue.

### Secondary Readouts

- delta/theta power during stimulation;
- movement/EMG;
- sleep/wake state;
- heart rate/respiration if available.

### Interpretation Matrix

**Tracer increases + sleep/delta increases**

Interpretation:

> Supports a sleep-state or slow-wave-mediated glymphatic route.

**Tracer increases without sleep/delta increase**

Interpretation:

> Supports an awake neurovascular/CSF-flow mechanism.

**Neural engagement without tracer increase**

Interpretation:

> Haptic stimulation affects circuits but does not measurably alter
> glymphatic-relevant fluid movement in this condition.

**Tracer increases only with movement/arousal**

Interpretation:

> Ambiguous. Could reflect physiology, stress, vascular change, or movement
> artifact. Requires stronger controls.

## Specific Aim 3: Test Post-Stimulation Sleep Carryover

### Question

Can awake haptic stimulation change the following sleep period in a way that
improves clearance?

This avoids vibrating a sleeping mouse directly.

### Design

1. Stimulate during an awake/pre-sleep period.
2. Stop stimulation.
3. Allow undisturbed natural sleep.
4. Score sleep with EEG/EMG.
5. Measure CSF tracer influx or clearance during the subsequent sleep window.

### Positive Result

- more NREM sleep;
- higher 0.5-4 Hz slow-wave/delta power;
- lower EMG/movement;
- increased tracer influx or improved tracer clearance.

### Why This Is Useful

It preserves the biological sleep/glymphatic hypothesis while avoiding the
practical problem of vibrating the animal during sleep.

## Specific Aim 4: Use Anesthesia Only As A Positive Control

Ketamine/xylazine is not natural NREM sleep, but it can create a
clearance-permissive, slow-wave-like state. It should be used as an assay
positive control, not as the therapeutic claim.

### Question

Can our tracer protocol detect a known high-glymphatic state?

### Interpretation

Positive under ketamine/xylazine:

> The tracer assay is capable of detecting enhanced CSF/ISF movement.

Negative under ketamine/xylazine:

> The assay may not be sensitive enough, or the surgical/tracer protocol needs
> optimization.

Do not conclude:

> Haptic stimulation works under ketamine, therefore it will work in awake
> animals.

That would overstate the result.

## Minimal Practical Experiment

If resources are limited, run this first:

1. Record awake/quiet haptic target engagement with S1 + dHPC + EEG/EMG +
   stimulus sensor.
2. Pick two stimulation frequencies based on target engagement, likely 50 Hz
   and either 1 Hz or 8 Hz.
3. Run an offline tracer influx experiment:
   - sham;
   - 50 Hz;
   - 1 Hz or 8 Hz.
4. Quantify tracer entry into S1, dHPC, entorhinal cortex, and whole brain.
5. Interpret tracer effects together with sleep/wake, movement, and delta/theta
   state.

This gives a realistic first answer:

> Does haptic stimulation affect both brain circuits and CSF-entry markers
> under practical mouse conditions?

## What This Study Can Claim

If positive:

> Haptic stimulation engages somatosensory and memory-relevant circuits and is
> associated with increased glymphatic-relevant tracer influx or clearance
> markers under defined mouse-state conditions.

If negative:

> Haptic stimulation may still engage neurons, but under these conditions it
> does not measurably improve glymphatic tracer movement.

## What This Study Should Not Claim

Do not claim:

- native gamma entrainment unless stimulus phase and native oscillator evidence
  are present;
- glymphatic clearance from electrophysiology alone;
- disease modification without amyloid/tau/pathology or behavioral outcomes;
- that ketamine/xylazine results equal natural sleep results;
- that 40 or 50 Hz is the "clearance frequency" without tracer/flow evidence.

## Key Risks And Mitigations

### Risk: stimulation causes movement or stress

Mitigation:

- record EMG/video/accelerometer;
- use amplitude titration;
- include sham and low-frequency controls;
- interpret tracer changes alongside arousal markers.

### Risk: stimulation does not engage S1

Mitigation:

- record S1 first;
- verify actual actuator motion;
- adjust body site, amplitude, or device coupling.

### Risk: tracer assay is noisy

Mitigation:

- include ketamine/xylazine positive control;
- standardize tracer volume, rate, circulation time, and perfusion;
- quantify blinded;
- predefine regions of interest.

### Risk: 50 Hz LFP artifact repeats

Mitigation:

- record actual stimulus phase;
- include dead/noisy channel checks;
- rely on S1/dHPC single units and artifact screens;
- do not interpret LFP peaks alone as entrainment.

## Proposal Summary

The next realistic step is not to vibrate a sleeping mouse. The next step is to
separate three questions:

1. Does the haptic stimulus cleanly engage somatosensory cortex?
2. Does that engagement reach dHPC or entorhinal memory circuits?
3. Does stimulation alter CSF tracer influx/clearance or state markers related
   to glymphatic physiology?

A defensible first proposal is therefore:

> Record awake S1 + dHPC target engagement, then run an offline CSF tracer
> experiment comparing sham, 50 Hz, and a slow/theta comparator. Use sleep/state
> and movement measures to decide whether any tracer effect reflects a
> sleep-like route, an awake neurovascular route, or neural engagement without
> measurable glymphatic impact.

## Core References

- Jiang-Xie et al. 2024, *Nature*. Neuronal dynamics direct cerebrospinal fluid
  perfusion and brain clearance. DOI: https://doi.org/10.1038/s41586-024-07108-6
- Xie et al. 2013, *Science*. Sleep drives metabolite clearance from the adult
  brain. DOI: https://doi.org/10.1126/science.1241224
- Hablitz et al. 2019, *Science Advances*. Increased glymphatic influx is
  correlated with high EEG delta power and low heart rate in mice under
  anesthesia. DOI: https://doi.org/10.1126/sciadv.aav5447
- Iliff et al. 2012, *Science Translational Medicine*. A paravascular pathway
  facilitates CSF flow through the brain parenchyma and clearance of
  interstitial solutes, including amyloid beta. DOI:
  https://doi.org/10.1126/scitranslmed.3003748
- Murdock et al. 2024, *Nature*. Multisensory gamma stimulation promotes
  glymphatic clearance of amyloid. DOI: https://doi.org/10.1038/s41586-024-07132-6

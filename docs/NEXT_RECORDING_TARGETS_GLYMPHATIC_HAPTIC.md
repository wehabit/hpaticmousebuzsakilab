# Next Recording Targets For The Glymphatic-Haptic Hypothesis

This is a planning note, not a final protocol. The goal is to decide where to
record next if the question is:

> Can external haptic stimulation push the mouse brain toward a state that is
> relevant to glymphatic clearance?

## Core Principle

Do not only record where we hope to see a disease-relevant effect. Record the
chain:

1. Did the body actually receive the vibration?
2. Did the somatosensory pathway receive it?
3. Did memory/clearance-relevant circuits change?
4. Did the animal's brain state shift toward a clearance-permissive state?
5. Did any direct CSF/ISF or vascular readout change?

Electrophysiology can answer points 2-4. It cannot, by itself, prove
glymphatic clearance.

## Best Next Recording Design

### First priority: contralateral primary somatosensory cortex

Record from the S1 body map that matches the stimulation site.

Why:

- Haptic stimulation first enters the brain through somatosensory pathways.
- Without S1, we do not know whether a weak dHPC/LEC effect means "no brain
  engagement" or just "the effect stayed upstream."
- Mouse vibrotactile literature, especially Hayashi et al. 2018, directly
  shows frequency-selective responses in mouse S1.

What it tells us:

- whether the delivered vibration produces clean sensory target engagement;
- whether S1 follows 5, 10, 20, 40, 50 Hz, etc.;
- whether responses are stimulus-locked, broadband, or state-dependent;
- whether S1 response strength predicts hippocampal/entorhinal effects.

### Second priority: dorsal hippocampus

Keep dHPC.

Why:

- dHPC was the cleanest Dec 4 neural result: little 50 Hz pickup and the
  strongest single-unit evidence.
- Jiang-Xie et al. recorded hippocampal field potentials and linked
  hippocampal ionic waves to CSF perfusion and clearance.
- dHPC is memory-relevant and AD-relevant.

What it tells us:

- whether the haptic signal reaches memory circuits;
- whether 50 Hz changes spikes again in a cleaner, replicated experiment;
- whether stimulation changes slow-wave/delta, theta, ripple, or
  spike-field organization;
- whether S1 activity predicts dHPC activity.

### Third priority: entorhinal cortex, if hardware allows

Record LEC or MEC only after S1 + dHPC are covered.

Why:

- Entorhinal cortex is the gateway between cortex and hippocampus.
- Dec 4 LEC showed population suppression and up/down single-unit responses,
  but the LFP was pickup-contaminated.
- A cleaner entorhinal recording could test propagation into the hippocampal
  memory system.

How to treat it:

- Useful as a downstream memory-circuit node.
- Not the first place to record if we still lack S1 target engagement.
- Must have stronger artifact controls than Dec 4.

### Fourth priority: cortical EEG/LFP plus EMG

Add state channels even if they are not a full probe target.

Minimum:

- cortical EEG or surface LFP for slow waves;
- neck EMG for sleep/wake scoring;
- accelerometer/video for movement;
- ideally heart rate or respiration if available.

Why:

- Glymphatic clearance is state-dependent.
- Hablitz et al. links glymphatic influx to high delta power and low heart
  rate in mice.
- Fultz et al. links human NREM slow waves, hemodynamics, and CSF oscillations.
- Jiang-Xie et al. argues that synchronized sleep/anesthesia-like ionic waves
  organize CSF-to-ISF perfusion.

## Practical Ranking

If we can record from two neural targets:

1. contralateral S1 for the stimulated body region;
2. dHPC, ideally CA1/DG coverage if anatomy allows.

If we can record from three neural targets:

1. contralateral S1;
2. dHPC;
3. LEC/MEC or somatosensory thalamus.

Choose the third target based on the main question:

- **LEC/MEC** if the question is memory-circuit propagation.
- **VPL/VPM thalamus** if the question is sensory relay and haptic target
  engagement.

If we can record from only one deep target:

> Choose dHPC, but add cortical EEG/EMG and a stimulus sensor. If the next
> paper/presentation hinges on haptic target engagement, choose S1 instead.

## What To Record Alongside The Brain

The next experiment must record the actual stimulus:

- analog accelerometer or PVDF signal time-locked to Intan;
- digital trial ON/OFF;
- digital cycle marker or phase reference if firmware supports it.

This is necessary for true phase locking and entrainment tests.

## What Would Be A Convincing Positive Result

For the sleep-state route:

- haptic stimulation increases NREM or quiet-state time;
- 0.5-4 Hz cortical/hippocampal slow-wave power increases;
- EMG/movement decrease;
- dHPC/S1 show coordinated slow waves;
- tracer or vascular readouts improve.

For the awake neurovascular route:

- animal remains awake;
- S1 and dHPC are engaged;
- vascular/CSF/ISF readouts improve;
- the effect is frequency- or pattern-specific and not just intensity/arousal.

For the current 50 Hz route:

- 50 Hz single-unit modulation replicates in dHPC;
- S1 confirms clean haptic sensory input;
- stimulus phase is recorded;
- no dead-channel/artifact gradient explains the effect;
- slow-wave/state or CSF/ISF measures show whether it matters for clearance.

## What Not To Claim Without Extra Measurements

Do not claim glymphatic clearance from electrophysiology alone.

Do not claim native entrainment from an LFP peak alone.

Do not claim 40 or 50 Hz is the clearance frequency unless CSF/ISF or
sleep-state markers support it.

## References

- Jiang-Xie et al. 2024, Nature: neuronal dynamics direct CSF perfusion and
  brain clearance. DOI: https://doi.org/10.1038/s41586-024-07108-6
- Hayashi et al. 2018: mouse S1 vibrotactile frequency responses. DOI:
  https://doi.org/10.3389/fncir.2018.00109
- Hablitz et al. 2019: glymphatic influx correlates with high EEG delta and
  low heart rate in mice. DOI: https://doi.org/10.1126/sciadv.aav5447
- Fultz et al. 2019: human NREM slow waves, hemodynamics, and CSF oscillations.
  DOI: https://doi.org/10.1126/science.aax5440
- Murdock et al. 2024: multisensory gamma stimulation and glymphatic amyloid
  clearance in 5xFAD mice. DOI: https://doi.org/10.1038/s41586-024-07132-6

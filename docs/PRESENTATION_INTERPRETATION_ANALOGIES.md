# Presentation Interpretation Analogies

This is a slide-prep / self-teaching note. It is not a formal result file. Use
it when explaining the Dec 3 / Dec 4 conclusions to yourself or to a
non-neuroscience audience.

## Single Units vs LFP vs Entrainment

The key result wording:

> 50 Hz high-amplitude haptic stimulation produced the strongest clean
> single-unit firing-rate modulation, but it did not prove LFP entrainment.

Plain meaning:

> Some individual neurons changed how often they fired during 50 Hz
> stimulation, but we did not prove that the brain's population rhythm locked
> its timing to the 50 Hz vibration.

## The Crowd-Clapping Analogy

Think of the recording like a room full of people.

- **Single-unit firing rate** = how often one person claps.
- **LFP** = the total crowd noise in the room.
- **Entrainment** = the whole crowd claps in sync with the beat.

Our result says:

> Some people changed how much they clapped.

It does **not** prove:

> The whole crowd synchronized to the beat.

That is the difference between single-unit firing-rate modulation and LFP
entrainment.

## Why Single Units Are The Cleaner Result Here

LFP is like a local electrical field microphone. It can include:

- real summed neural currents,
- reference effects,
- movement,
- electrical or mechanical pickup,
- signals spreading through tissue or wires.

So a 50 Hz line in the LFP is not automatically a brain rhythm. In this dataset,
the LEC 50 Hz LFP is contaminated because disconnected LEC channels picked up
strong 50 Hz. Dead channels cannot record neurons, so that LFP signal cannot be
treated as clean neural evidence.

Single units are different. A single unit is a sorted neuron, or our best
estimate of one neuron. The single-unit analysis asks:

> During stimulation ON, did this neuron fire more or less often than during OFF?

Example:

- OFF: a neuron fires 5 spikes/second.
- ON: the same neuron fires 7 spikes/second.
- Difference: +2 Hz.

That is a firing-rate increase.

In this study, 50 Hz high-amplitude stimulation changed single-unit firing rates
more than 5, 10, or 26 Hz. The spike-artifact screens also argue against the
up-going units being pickup-manufactured spikes.

## What To Infer

Supported:

> The haptic stimulus affected real neurons in memory-related brain regions,
> especially at 50 Hz / high amplitude.

Not supported:

> The stimulus entrained hippocampal or entorhinal gamma rhythms.

Better presentation wording:

> 50 Hz stimulation produced the strongest single-unit firing-rate modulation,
> with a driven-up subset in dHPC and net suppression in LEC. The LEC 50 Hz LFP
> is pickup-contaminated, so the spike-rate result is the cleaner neural readout.

Avoid:

> 50 Hz entrained the brain.

## Native Rhythm vs External Drive

Use this vocabulary:

- **Native rhythm** = a rhythm the brain generates on its own.
- **External drive** = the vibration/light/sound/electrical stimulation we apply.
- **Entrainment** = the external drive changes the timing of a native rhythm.

Clean phrase:

> The external stimulus entrains a native brain rhythm.

Risky phrase:

> Native entrainment.

The stimulus can create a rhythm in the recording without controlling a native
brain rhythm. A repeated stimulus can create a repeated response at 50 Hz. That
is a steady-state or stimulus-locked response. It is not automatically
entrainment.

## Four Possible Effects Of Stimulation

1. **Added response**
   The stimulus adds a rhythm on top of whatever the brain was already doing.

2. **True entrainment**
   The brain already had a rhythm, and the stimulus pulls its timing into
   alignment.

3. **Masking**
   The external response is so strong that it hides the native rhythm in the
   recording.

4. **Suppression / disruption**
   The stimulation weakens or desynchronizes the native rhythm.

So stimulation might not entrain the native rhythm. It might dilute, mask,
suppress, or override it.

## What Would Prove Real Entrainment

We would want evidence that:

- a native rhythm exists before stimulation,
- during stimulation, that same rhythm shifts phase/frequency toward the
  stimulus,
- the effect is stronger in real neural channels than dead channels,
- spikes participate, not just LFP,
- there is carryover or phase reset after stimulation stops,
- other frequencies do not produce the same effect,
- and the actual delivered stimulus phase was recorded.

In this study, the last point is the major blocker: we did not record a
continuous stimulus phase signal.

## Final Slide-Safe Summary

> Haptic stimulation affects the brain. Dec 3 showed a broadband,
> transition-weighted dHPC response but no clean entrainment. Dec 4's clean
> readout is single-unit firing: 50 Hz high-amplitude stimulation produces the
> strongest frequency-specific rate effect, with a driven-up subset in dHPC and
> net suppression in LEC. The LEC 50 Hz LFP is pickup-contaminated, so spikes are
> the trustworthy measure. We do not yet show entrainment because no stimulus
> phase was recorded, and we do not show cross-region coordination.

## Glymphatic Flow And Ionic Waves

Use this section when explaining why the glymphatic hypothesis is not the same
as "make gamma."

Slide-safe hypothesis:

> Haptic stimulation may affect glymphatic clearance if it pushes the brain
> toward a clearance-permissive state, where neural synchrony, vascular/CSF
> movement, and interstitial-fluid exchange become coordinated.

The key paper here is Jiang-Xie et al. 2024, *Nature*:

> Neuronal dynamics direct cerebrospinal fluid perfusion and brain clearance.

Their "ionic waves" are not literal waves of CSF sloshing back and forth. They
are large, rhythmic extracellular field-potential waves measured in the
interstitial fluid around neurons.

Plain meaning:

> When many neurons coordinate their firing and recovery, their tiny ionic
> currents line up. That creates a large rhythmic field fluctuation in the
> fluid space outside cells. Jiang-Xie argues that this kind of wave can help
> organize CSF-to-ISF perfusion and waste clearance.

The important distinction:

- **Neural ionic wave** = synchronized extracellular voltage/current wave.
- **CSF/ISF flow** = physical movement of fluid and molecules.
- **Glymphatic clearance** = CSF enters tissue, mixes/exchanges with ISF, and
  waste molecules leave through clearance routes.

So the ionic wave is not the fluid itself. It is a neural/electrical pattern
that may help organize the fluid movement.

## The Tiny Pumps Analogy

Imagine each neuron is a tiny pump.

If every pump works randomly, their pushes cancel out. That is like awake,
desynchronized activity: useful for processing information, but not ideal for
large coordinated fluid movement.

If many pumps pulse together, their small pushes add up. That is like sleep or
ketamine-like synchronized activity: less information-rich, but better for
large rhythmic waves in the extracellular space.

The slide version:

> Awake brain: many tiny pumps firing randomly.
>
> Sleep-like brain: many tiny pumps pulsing together.
>
> Glymphatic hypothesis: coordinated pulsing may help move CSF/ISF and clear
> waste.

## What This Means For Our Haptic Project

Our Dec 4 data support target engagement:

> 50 Hz haptic stimulation changes single-unit firing in dHPC and LEC.

But they do not yet support glymphatic clearance.

The next scientific question is:

> Does haptic stimulation change the animal's brain state or fluid-flow
> machinery in a way that should matter for glymphatic clearance?

What would support the glymphatic version:

- more NREM-like slow-wave activity, especially 0.5-4 Hz;
- larger coordinated field waves in hippocampus/cortex;
- lower movement/arousal/EMG and calmer autonomic state;
- better CSF tracer influx or ISF efflux;
- vascular pulsatility or AQP4/meningeal-lymphatic changes;
- the effect survives controls for stimulus artifact and movement.

What would not be enough:

> A 40 or 50 Hz LFP line by itself.

Better final wording:

> Our haptic stimulus engages memory-relevant circuits. The glymphatic
> hypothesis asks whether that engagement can shift the brain toward a
> clearance-permissive state, either by promoting NREM-like slow-wave dynamics
> or by recruiting awake neurovascular/CSF-flow mechanisms.

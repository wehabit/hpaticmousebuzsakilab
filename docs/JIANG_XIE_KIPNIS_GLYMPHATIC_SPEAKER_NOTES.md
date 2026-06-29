# Jiang-Xie / Kipnis Glymphatic Speaker Notes

Purpose: slide-ready notes for the Jiang-Xie et al. 2024 Nature paper, especially the hippocampal ionic-wave frequency, where the recordings were made, where the optogenetic 1 Hz and 8 Hz stimulation was induced, and what figures to cite while speaking.

Primary paper:

- Jiang-Xie et al. 2024, Nature, "Neuronal dynamics direct cerebrospinal fluid perfusion and brain clearance." DOI: https://doi.org/10.1038/s41586-024-07108-6
- Local lit-review PDF: `/Users/paris/Documents/LitretureReview_Github/papers/alzheimers_nonpharm/2024_Neuronal_dynamics_direct_cerebrospinal_fluid_perfusion_and_brain_clearance.pdf`

## One-Sentence Takeaway

Jiang-Xie/Kipnis showed in mice that synchronized hippocampal field-potential or "ionic" waves, especially NREM-like slow waves, can causally regulate CSF-to-ISF perfusion and brain clearance.

CSF means cerebrospinal fluid. ISF means interstitial fluid inside brain tissue.

## Exact Frequencies

| Condition | Frequency in the paper | What they said / did | Slide-safe wording |
|---|---:|---|---|
| Native NREM sleep | 0.5-4 Hz slow waves | Large-amplitude ionic waves appeared in hippocampus during NREM sleep, while EEG showed slow oscillations and EMG was low. | "The sleep-related hippocampal clearance waves were slow, around 0.5-4 Hz." |
| Native REM sleep | 6-10 Hz theta | REM showed rhythmic theta originating in hippocampus and propagating to cortical EEG. | "REM was the theta condition, around 6-10 Hz." |
| Ketamine/xylazine anesthesia | 0.5-4 Hz slow oscillations plus 10-50 Hz high-frequency ionic waves | Slow oscillations were interleaved with 10-50 Hz ionic waves in hippocampal recordings. | "Under ketamine, slow waves and faster 10-50 Hz components were coupled." |
| Synthetic optogenetic slow-wave pattern | 1 Hz light pulses, 50 ms on / 950 ms off | Designed to mimic high-energy NREM/anesthesia-like slow oscillation. It entrained hippocampal 0.5-4 Hz field-potential power. | "They imposed a 1 Hz pattern to create slow-wave-like hippocampal activity." |
| Synthetic optogenetic theta pattern | 8 Hz light pulses, 6.25 ms on / 118.75 ms off | Designed to mimic REM/theta-like rhythm. It entrained hippocampal 6-10 Hz field-potential power. | "They imposed an 8 Hz pattern to create theta-like hippocampal activity." |

Important: this paper does not say 40 Hz is the glymphatic clearance frequency. For the sleep-linked mechanism, the strongest native wave is slow-wave/delta-range, 0.5-4 Hz.

## Where The Hippocampal Recording Was

They recorded with a linear silicon probe inserted through cortex into the hippocampus.

Method details:

- Electrophysiology craniotomy: approximately AP -2.5, ML 2.0.
- The probe slowly penetrated cortex and was inserted into hippocampus.
- The authors say the probe covered the entire dorsal-ventral axis of hippocampus.
- Figure labels use D for dorsal and V for ventral.
- They analyzed about 28 hippocampal recording channels spanning top to bottom of the hippocampus.

Speaker-note wording:

> They did not record from one tiny named hippocampal subfield. They inserted a linear probe into hippocampus and sampled across the dorsal-to-ventral axis. So I would call this "hippocampal" recording, not only dHPC, CA1, CA3, or dentate gyrus.

dHPC means dorsal hippocampus. CA1, CA3, and dentate gyrus are hippocampal subfields; the paper does not make the key claim at that subfield level.

## Where The Optogenetic 1 Hz And 8 Hz Were Induced

They expressed ChRmine, a red-light-sensitive optogenetic activator, unilaterally in the hippocampus.

Method details:

- Viral injection target: hippocampus.
- Coordinates: AP -2.7, ML 2.5, depth 1.5 mm below brain surface.
- Viral vectors for optogenetic activation: CaMKIIa-ChRmine-mScarlet or CaMKIIa-mScarlet control.
- Light delivery: 635 nm red light through a 400 micrometer optical fiber anchored on top of the cranium.
- The optical fiber was not inserted into the hippocampus for the main glymphatic perfusion experiment; they call this transcranial optogenetics.

Speaker-note wording:

> The 1 Hz and 8 Hz patterns were induced in ChRmine-expressing hippocampal neurons on one side of the mouse brain, using red light delivered through the skull. The target was hippocampus, not a specified CA1/CA3/dentate subfield.

The stimulated side showed more CSF-to-ISF tracer perfusion than the contralateral side in ChRmine animals. That asymmetry was not present in control RFP animals.

## Figures To Use Or Mention

- Figure 1b: wake versus ketamine versus ketamine plus chemogenetic silencing. Shows hippocampal ionic waves and how silencing flattens them.
- Extended Data Fig. 1: power spectra and coupling under ketamine; shows slow and 10-50 Hz components.
- Figure 2a: wake, NREM, and REM raw traces. This is the best image for showing what the hippocampal waves looked like during natural sleep.
- Figure 2e-g: sleep increased tracer infiltration, and hippocampal neuronal inhibition reduced local tracer perfusion.
- Extended Data Fig. 5: natural sleep-wake traces and power spectra with chemogenetic inhibition.
- Extended Data Fig. 10: filtered wave phase progression across hippocampal recording channels; shows 0.5-4 Hz NREM traces and 6-10 Hz REM theta traces.
- Figure 5: synthetic 1 Hz and 8 Hz optogenetic stimulation increased CSF-to-ISF tracer infiltration in the hippocampus.
- Extended Data Fig. 9b-c: validates that optogenetic 1 Hz and 8 Hz patterns entrained hippocampal slow/theta field-potential power.

## What This Paper Proves

- Hippocampal ionic/field-potential waves change with brain state.
- Local chemogenetic flattening of hippocampal waves reduces local CSF tracer perfusion and clearance.
- Synthetic 1 Hz slow-wave-like and 8 Hz theta-like hippocampal patterns can increase CSF-to-ISF perfusion.
- The strongest causal evidence is in mice and is local to the manipulated hippocampal side.

## What This Paper Does Not Prove

- It does not prove that 40 Hz or 50 Hz haptic stimulation increases glymphatic clearance.
- It does not prove that a 40/50 Hz LFP line equals native gamma entrainment.
- It does not identify CA1 versus CA3 versus dentate gyrus as the unique driver.
- It does not show direct ISF fluid flow in behaving animals; it uses field potentials as a proxy for ionic dynamics and tracer/MRI readouts for perfusion and clearance.

## How To Connect This To Our Haptic Slides

Good wording:

> The glymphatic literature does not simply point to gamma. Jiang-Xie/Kipnis suggests that sleep-like synchronized hippocampal ionic waves, especially 0.5-4 Hz slow-wave activity, can organize CSF-to-ISF perfusion. For our haptic project, 40/50 Hz tests sensory and unit-response target engagement, while slow-wave, theta, sleep-state, and tracer readouts test whether we are moving toward a clearance-permissive state.

Good experimental implication:

- Keep 40 Hz because it tests the GENUS literature.
- Keep 50 Hz because it is our strongest clean unit-response frequency.
- Add or retain slow/theta comparators if the question is glymphatic mechanism: 1-2 Hz, 5 Hz, 8-10 Hz, or a patterned slow/theta protocol.
- Measure state: EEG or cortical LFP, hippocampal LFP, EMG, movement, and ideally CSF tracer influx/clearance.

## Slide-Safe Language

Short version:

> In Jiang-Xie/Kipnis, the relevant sleep-linked hippocampal waves were slow, around 0.5-4 Hz. Their optogenetic rescue used 1 Hz and 8 Hz patterns in hippocampus, not 40 Hz. This keeps our glymphatic hypothesis separate from a simple gamma-entrainment claim.

Longer version:

> Jiang-Xie/Kipnis recorded hippocampal field-potential or ionic waves across the dorsal-ventral hippocampal axis. During NREM sleep, large slow waves appeared in the 0.5-4 Hz range; during REM, hippocampal theta appeared around 6-10 Hz. They then expressed ChRmine in one hippocampus and used transcranial red-light optogenetics to impose either 1 Hz slow-wave-like or 8 Hz theta-like activity. Both increased CSF-to-ISF perfusion on the stimulated hippocampal side.

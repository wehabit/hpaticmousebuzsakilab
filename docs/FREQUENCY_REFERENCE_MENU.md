# Frequency Reference Menu

Purpose: a clear planning sheet for which stimulation frequencies are worth
checking, why each one is included, which references justify it, and what those
references actually studied or showed.

Important distinction:

- **Haptic/vibrotactile frequency** = mechanical vibration delivered to the body.
- **iEEG/direct electrical stimulation frequency** = electrical pulses delivered
  directly through intracranial electrodes.
- **Theta-burst frequency** = the rhythm at which bursts are repeated, often with
  much faster pulses inside each burst.
- These are related but not interchangeable.

For the Jiang-Xie/Kipnis glymphatic details behind the slow/theta comparison,
see `docs/JIANG_XIE_KIPNIS_GLYMPHATIC_SPEAKER_NOTES.md`.

## Short Recommendation

For the next haptic mouse experiment, the strongest practical panel is:

**5, 10, 20, 26, 40, 50 Hz**

If there is room for more, add:

**2, 32, 64, 100, 128, 200/250 Hz**

The central comparison should be:

**40 Hz**, because that is the AD/GENUS literature claim frequency, versus
**50 Hz**, because that is the strongest clean single-unit effect in our current
Dec 4 data.

## Clear Frequency Table With Links

| Frequency | Why choose it? | Paper link(s) | What was shown or studied at/around this frequency | How to use it in our project |
|---|---|---|---|---|
| **1 Hz** | Very-low-frequency stimulation control. It is mainly useful as a contrast against higher-frequency stimulation. | [Keller et al. 2018](https://doi.org/10.1523/JNEUROSCI.1088-17.2018); [Mohan et al. 2020](https://doi.org/10.1016/j.brs.2020.05.009) | Keller frames low-frequency stimulation as a regime that can decrease excitability, in contrast to higher-frequency protocols. Mohan shows human direct electrical stimulation effects depend on frequency, amplitude, and white/gray matter proximity. | Optional. Not a core haptic frequency. Use only if we want a very slow control or a stimulation-literature comparison. |
| **2 Hz** | Slow mechanical/tactile control below the main flutter range. Helps ask whether any periodic touch changes the brain. | [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109) | Mouse hind-limb S1 was tested with 2, 5, 10, 20, 50, 100, and sometimes 200 Hz vibration. The paper showed cell-type-specific, frequency-selective responses in mouse S1. | Optional low mechanical-frequency control, especially if we record somatosensory cortex in the future. |
| **3-8 Hz** | Theta-burst timing range. Important because hippocampal/entorhinal memory circuits are theta-linked, and human iEEG theta-burst studies show frequency-specific responses. | [Solomon et al. 2021](https://doi.org/10.1016/j.brs.2021.08.014); [Huang/Keller/Paulk et al. 2024](https://doi.org/10.1038/s41467-024-51443-1) | Solomon delivered intracranial theta-burst stimulation with bursts repeated at 3-8 Hz and found frequency-specific theta responses. Huang/Keller used human iEEG theta-burst direct electrical stimulation and found distributed responses and short-term plasticity shaped by baseline connectivity. | Do not treat this as simple 6 Hz vibration. Use it as a patterned-stimulation idea: bursts repeated in the theta range. |
| **5 Hz** | Lower edge of classic tactile flutter and already used in our Dec 3/Dec 4 experiments. | [Salinas/Romo et al. 2000](https://doi.org/10.1523/JNEUROSCI.20-14-05503.2000); [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109) | Salinas/Romo describe flutter as mechanical skin vibration in the 5-50 Hz range and studied primate somatosensory coding of vibrotactile frequency. Hayashi tested mouse S1 responses including 5 Hz. | Keep. It tells us whether the brain responds broadly to vibration or preferentially to higher frequencies. |
| **10 Hz** | Low/flutter and theta/alpha-adjacent comparator. Also important because 10 Hz appears in human direct-stimulation/plasticity work. | [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109); [Keller et al. 2018](https://doi.org/10.1523/JNEUROSCI.1088-17.2018); [Ezzyat et al. 2019](https://doi.org/10.1523/JNEUROSCI.3553-18.2019) | Mountcastle/Romo trained monkeys on tactile flutter discrimination and used examples including 10, 30, and 50 Hz. Hayashi tested 10 Hz mouse S1 vibration. Keller used 10 Hz direct electrical stimulation and found lasting excitability changes in connected human cortical regions. Ezzyat used 10 Hz stimulation to study connectivity changes predicted by intracortical dynamics. | Keep. It is a bridge frequency across tactile coding, theta/alpha-adjacent biology, and human iEEG stimulation. |
| **20 Hz** | Mid-flutter / beta-range comparator. Critical because AD sensory papers compare 20 Hz against 40 Hz. | [Salinas/Romo et al. 2000](https://doi.org/10.1523/JNEUROSCI.20-14-05503.2000); [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109); [Singer group 5xFAD flicker paper](https://doi.org/10.1063/5.0249833) | Tactile papers place 20 Hz inside the flutter range. Hayashi tested mouse S1 at 20 Hz. The 5xFAD flicker paper studied frequency/duration effects, including 20 vs 40 Hz audiovisual flicker, and reported frequency-dependent transcriptional programs. | Add. It helps us avoid only testing "gamma" and asks whether mid-frequency stimulation has its own biological effect. |
| **25/26 Hz** | Continuity with our data. 26 Hz was used in Dec 3/Dec 4 and Dec 3 had a large gross LFP transient here. Also near beta/high-flutter. | [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Mohan et al. 2020](https://doi.org/10.1016/j.brs.2020.05.009); [Papasavvas et al. 2020](https://doi.org/10.1088/1741-2552/abbecf); our Dec 3/Dec 4 data | Mountcastle/Romo included nearby flutter comparisons. Mohan and Papasavvas used parameter sweeps including 25 Hz direct electrical stimulation. Our data show 26 Hz can produce strong LFP transients, but not the strongest clean single-unit effect. | Keep. It protects us from cherry-picking 50 Hz and helps explain why the Dec 3 26 Hz LFP result differs from the Dec 4 50 Hz spike result. |
| **30/32 Hz** | Upper flutter / low-gamma boundary. Also relevant to fast-adapting tactile afferent stimulation and Tass coordinated-reset design. | [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Tass 2017](https://doi.org/10.7759/cureus.1535) | Mountcastle/Romo studied discrimination around 30 Hz. Tass discusses 30-60 Hz vibration as effective for FA-I tactile afferents and notes 32 Hz in mechanoreceptor/thalamic-response contexts. | Optional. Useful if we want a smoother frequency-response curve between 26 and 40 Hz. |
| **40 Hz** | Required. This is the central AD/GENUS/gamma-stimulation claim frequency. | [Iaccarino/Singer/Tsai et al. 2016](https://doi.org/10.1038/nature20587); [Martorell/Tsai et al. 2019](https://doi.org/10.1016/j.cell.2019.02.014); [Suk et al. 2023 tactile 40 Hz](https://doi.org/10.3389/fnagi.2023.1129510); [Mlinaric et al. 2025 human iEEG 40 Hz](https://doi.org/10.1038/s42003-025-08766-6); [Soula/Voroslakos/Buzsaki et al. 2023 counterpaper](https://doi.org/10.1101/2023.03.14.532608) | Iaccarino/Tsai launched the 40 Hz sensory stimulation AD claim. Martorell extended to multisensory 40 Hz. Suk tested 40 Hz whole-body vibrotactile stimulation in mouse neurodegeneration models. Mlinaric studied human iEEG target engagement with visual 40 Hz. Soula/Buzsaki argues 40 Hz sensory responses do not prove native gamma entrainment. | Must include. But phrase carefully: 40 Hz can test sensory target engagement and neural response, not automatically native gamma entrainment. |
| **50 Hz** | Required because our Dec 4 clean single-unit result is strongest at 50 Hz. Also upper classic flutter and common human direct-stimulation frequency. | [Salinas/Romo et al. 2000](https://doi.org/10.1523/JNEUROSCI.20-14-05503.2000); [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109); [Kucewicz/Kahana et al. 2018](https://doi.org/10.1523/ENEURO.0369-17.2018); [Jacobs et al. 2016](https://doi.org/10.1016/j.neuron.2016.07.032); [Mohan et al. 2020](https://doi.org/10.1016/j.brs.2020.05.009); [Papasavvas et al. 2020](https://doi.org/10.1088/1741-2552/abbecf); our Dec 4 data | Tactile papers place 50 Hz at/near the upper flutter range; Hayashi tested mouse S1 at 50 Hz. Kahana/Jacobs/Mohan/Papasavvas show 50 Hz direct electrical stimulation can modulate high-gamma, memory, and band power, often depending on target/state. Our Dec 4 data show strongest frequency-specific single-unit firing-rate modulation at 50 Hz. | Must include. This is our strongest current candidate, but 50 Hz LFP needs strict artifact controls. |
| **60/64 Hz** | Boundary between flutter/gamma and higher-frequency Pacinian-like vibration. Tests whether the effect continues above 50 Hz or falls off. | [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Tass 2017](https://doi.org/10.7759/cureus.1535) | Mountcastle/Romo included 60 Hz vibration comparisons. Tass discusses 32/64 Hz vibration for tactile afferent/human thalamic response contexts. | Optional high-frequency haptic control. Good if actuator can deliver cleanly. |
| **80 Hz** | Specificity control against the 40 Hz claim. If 40 Hz is special, 80 Hz should not produce the same pattern. | [Iaccarino/Singer/Tsai et al. 2016](https://doi.org/10.1038/nature20587); [Martorell/Tsai et al. 2019](https://doi.org/10.1016/j.cell.2019.02.014); [Suk et al. 2023](https://doi.org/10.3389/fnagi.2023.1129510) | GENUS papers compare 40 Hz against other frequencies such as 20 or 80 Hz to argue frequency specificity. Suk summarizes this logic in the tactile-gamma context. | Optional. Strong control for the "is 40 Hz special?" question. |
| **100 Hz** | High-frequency mechanical/electrical comparator. Tests whether high-frequency vibration recruits a different tactile receptor regime. | [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109); [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Mohan et al. 2020](https://doi.org/10.1016/j.brs.2020.05.009); [Papasavvas et al. 2020](https://doi.org/10.1088/1741-2552/abbecf); [Solomon et al. 2021](https://doi.org/10.1016/j.brs.2021.08.014); [Huang/Keller/Paulk et al. 2024](https://doi.org/10.1038/s41467-024-51443-1) | Hayashi tested mouse S1 responses at 100 Hz. Mohan/Papasavvas used 100 Hz in human direct-stimulation parameter sweeps. Solomon/Huang use high-frequency pulses inside theta-burst paradigms. | Optional. Useful as a high-frequency receptor/hardware control, not a primary AD-gamma target. |
| **128 Hz** | Pacinian/FA-II-style vibration reference. More receptor/hardware biology than AD-gamma biology. | [Tass 2017](https://doi.org/10.7759/cureus.1535) | Tass discusses high-frequency FA-II/Pacinian-related vibration and cites 128 Hz as a stimulus used in human thalamic Vc tactile-response contexts. | Optional. Use if we want to test high-frequency tactile afferent activation rather than gamma entrainment. |
| **145 Hz** | Clinical DBS comparator, not a haptic target. Included to understand real clinical stimulation parameters. | [Fisher/SANTE Study Group 2010](https://doi.org/10.1111/j.1528-1167.2010.02536.x) | The SANTE epilepsy DBS trial used anterior thalamus stimulation at 145 pulses/s, 90 microsecond pulses, 1 min ON / 5 min OFF. | Do not prioritize for haptic mouse work. Mention only as clinical stimulation context. |
| **185 Hz** | Clinical DBS parameter-adjustment comparator, not a haptic target. | [Fisher/SANTE Study Group 2010](https://doi.org/10.1111/j.1528-1167.2010.02536.x) | SANTE allowed changes including 185 Hz, but this was not a systematic haptic-style frequency experiment and was not the main effective parameter claim. | Do not prioritize. Context only. |
| **200 Hz** | High-frequency mechanical/electrical comparator. Mouse S1 tested it; iEEG uses it in parameter sweeps and theta-burst pulses. | [Hayashi et al. 2018](https://doi.org/10.3389/fncir.2018.00109); [Mountcastle/Romo et al. 1990](https://doi.org/10.1523/JNEUROSCI.10-09-03032.1990); [Mohan et al. 2020](https://doi.org/10.1016/j.brs.2020.05.009); [Papasavvas et al. 2020](https://doi.org/10.1088/1741-2552/abbecf); [Solomon et al. 2021](https://doi.org/10.1016/j.brs.2021.08.014); [Huang/Keller/Paulk et al. 2024](https://doi.org/10.1038/s41467-024-51443-1) | Hayashi tested 200 Hz in some mice. Mohan/Papasavvas used 200 Hz in human direct-stimulation parameter sweeps. Solomon/Huang use 100/200 Hz pulses within theta-burst stimulation. | Optional. Use only if actuator and sensor confirm clean delivery. Not a core AD-gamma frequency. |
| **250 Hz** | Tass vibrotactile coordinated-reset carrier frequency. Important for comparing simple rhythmic vibration against patterned multi-site CR-style stimulation. | [Tass 2017](https://doi.org/10.7759/cureus.1535); [Pfeifer/Tass et al. 2021 vCR benefits](https://doi.org/10.3389/fphys.2021.624317); [Pfeifer/Tass et al. 2021 vCR protocol](https://doi.org/10.3389/fneur.2021.758481) | Tass/Pfeifer vCR uses 250 Hz fingertip vibration bursts with a slow coordinated-reset cycle around 1.5 Hz. The target is Parkinsonian beta desynchronization/plasticity, not AD gamma entrainment. | Optional, but important for a different question: "Can patterned tactile CR-style stimulation modulate circuits?" Not the same as testing 40/50 Hz haptic gamma. |

## What This Means For The Next Experiment

### Minimum defensible haptic panel

Use this if time or animal tolerance is limited:

**10, 20, 40, 50 Hz**

This gives:

- **10 Hz**: low/theta-alpha comparator
- **20 Hz**: mid-frequency/beta comparator
- **40 Hz**: AD/GENUS claim frequency
- **50 Hz**: our current strongest single-unit response frequency

### Better haptic panel for this project

Use this if we can run more conditions:

**5, 10, 20, 26, 40, 50 Hz**

This gives:

- continuity with Dec 3/Dec 4
- direct 40 vs 50 comparison
- low/mid/high controls
- ability to argue frequency specificity instead of intensity/arousal alone

### Expanded mechanistic panel

Use only if we have enough trials, clean stimulus measurement, and preferably S1
recording:

**2, 5, 10, 20, 26, 32, 40, 50, 64, 80, 100, 128, 200/250 Hz**

This asks a broader question:

> How does the brain respond across tactile receptor regimes, from slow texture-like
> stimulation through flutter, gamma-range vibration, and high-frequency Pacinian/
> coordinated-reset style stimulation?

## Guardrails For Interpretation

- **40 Hz** tests the AD/GENUS literature claim.
- **50 Hz** tests our strongest current mouse haptic finding.
- **20/26 Hz** protect against cherry-picking 50 Hz and help explain the Dec 3 LFP
  result.
- **5/10 Hz** are low-frequency controls.
- **100/128/200/250 Hz** are not primary AD-gamma frequencies; they test high-frequency
  tactile receptor recruitment, hardware behavior, or Tass-style coordinated reset.
- Human iEEG/direct stimulation papers show that stimulation effects are causal but
  parameter-sensitive. They raise the bar for our haptic claims; they do not prove
  that haptic stimulation has the same mechanism.

## Source Files In The Lit Review Folder

- `/Users/paris/Documents/LitretureReview_Github/paper_inventory/vibrotactile_animal_all_papers.md`
- `/Users/paris/Documents/LitretureReview_Github/parvizi_ieeg_direct_stimulation_inventory.md`
- `/Users/paris/Documents/LitretureReview_Github/stanford_patterned_ieeg_interventions_inventory.md`
- `/Users/paris/Documents/LitretureReview_Github/tass_coordinated_reset_inventory.md`
- `/Users/paris/Documents/LitretureReview_Github/downloaded_literature_synthesis.md`

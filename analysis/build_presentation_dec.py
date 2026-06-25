#!/usr/bin/env python
"""Build the ~35-min program talk (mixed-researcher audience) in TWO formats:
  - presentation/haptic_brain_talk.pptx  (editable; PowerPoint/Keynote, or Google Slides)
  - presentation/haptic_brain_talk.pdf   (renders images everywhere)

Structure: Part 1 vision -> Part 2 literature & parameters -> Part 3 current study
-> Part 4 limits & next -> Part 5 fit. Register: scientifically literate, not
neuroscience-specialist; lead with precise terms, analogies as intuition, and keep
the 'mechanism != proven' discipline the lit review insists on. Narration in .pptx notes.
Vision/lit content grounded in ~/Documents/LitretureReview_Github (papers by handle).
"""
from __future__ import annotations
from pathlib import Path
import textwrap

OUT = Path("presentation"); OUT.mkdir(exist_ok=True)
F = "results/dec4"
CF = "presentation/concept_figs"
TTL = "analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png"
TRIAL = "results/dec3/13_Teaching_and_Methods/trial_window_diagram.png"
LOGO_W = "presentation/som_logo_white.png"       # Stanford School of Medicine, white
MOUSE = "presentation/concept_figs/mouse_white.png"
EVIDENCE = "presentation/concept_figs/evidence_ladder.png"
NAVY, TEAL, GREY, PANEL = "#2E2D29", "#8C1515", "#53565A", "#DAD7CB"   # Stanford: Black, Cardinal, Cool Grey, Fog
STONE, STONE_LIGHT, STONE_DARK, FOG_LIGHT, FOG_DARK = "#7F7776", "#D4D1D1", "#544948", "#F4F4F4", "#B6B1A9"

SLIDES = [
    dict(kind="title", title="Can vibrotactile stimulation drive brain clearance?",
         sub="Wearable vibrotactile stimulation, brain rhythms, and glymphatic clearance — rationale, plan, and first electrophysiology (in the mouse)",
         footer="a Snyder Lab (Stanford) × Buzsáki Lab (NYU) collaboration",
         footer2="Pardis Miri, PhD  ·  June 30, 2026",
         notes="The program question: can a wearable, vibrotactile stimulus engage brain rhythms in a way that helps the brain clear waste (the glymphatic system), with Alzheimer's relevance? I'll motivate it from the literature, lay out what to test, then show a first electrophysiology study testing the premise. I separate 'plausible mechanism' from 'proven' throughout. ~35 min — please interrupt."),

    # ===================== PART 1 — VISION =====================
    dict(kind="section", title="Part 1 · The vision — clearing the brain with vibrotactile stimulation",
         sub="Where clearance biology could matter: Alzheimer's amyloid/tau · stroke recovery/inflammation · Parkinson's α-synuclein",
         refs="Refs: Iliff 2012; Xie 2013; Murdock 2024 · Gaberel 2014; Mestre 2020; JCI 2026 · Cui 2021; Zhang 2023; Lopes 2025",
         sub_y=5.35,
         notes="Disease examples for the vision slide. Keep this as mechanism motivation, not a treatment claim. Alzheimer's: the glymphatic idea starts with clearance of interstitial solutes including amyloid-beta (Iliff 2012), sleep-dependent metabolite clearance (Xie 2013), and 40 Hz multisensory stimulation increasing glymphatic Aβ clearance in mouse models (Murdock 2024). Stroke: glymphatic perfusion is impaired after several stroke models (Gaberel et al., Stroke 2014); acutely, glymphatic CSF influx can also worsen edema (Mestre et al., Science 2020), so timing matters; a new mouse chronotherapy study reports increased glymphatic function, reduced cytokine burden, and improved post-stroke recovery (JCI 2026). Parkinson's: the relevant waste species is α-synuclein; AQP4/glymphatic disruption worsens α-syn pathology in mouse studies (Cui 2021; Zhang 2023), and a 2025 Brain paper links glymphatic function to α-syn propagation. Bottom line to say out loud: if a wearable can shape brain state safely, the broader long-term application space may include diseases where clearance/inflammation/protein propagation matter, but our present data only test neural target engagement."),
    dict(kind="content", kicker="the problem", title="Alzheimer's resists drugs — non-invasive neuromodulation is an open frontier", fig=f"{CF}/landscape.png",
         take="Pharmacology is real but incomplete: modest slowing with BBB/safety burden. Multidomain lifestyle has the largest human-scale evidence; Hosseini's Stanford work adds a relevant cognitive-training branch. Neuromodulation is promising but still early.",
         notes=("Framing the gap. The three boxes are the landscape in one glance. Pharmacology: do not say 'dead end' - say 'incomplete.' Anti-amyloid antibodies now show real but modest slowing, and the blood-brain barrier plus safety monitoring still make this a hard drug-delivery problem. Lecanemab evidence: van Dyck et al., 'Lecanemab in Early Alzheimer's Disease,' New England Journal of Medicine, 2023; about 27% slower clinical decline over 18 months, with infusion, amyloid-confirmation, MRI, and ARIA monitoring burden. Donanemab evidence: Sims et al., 'Donanemab in Early Symptomatic Alzheimer Disease: The TRAILBLAZER-ALZ 2 Randomized Clinical Trial,' JAMA, 2023; about 29-36% slowing depending on outcome/population, also with ARIA and monitoring burden. "
                "Lifestyle/multidomain: 'multidomain' means several risk pathways are targeted together, not one habit alone. The domains include exercise, diet, cognitive challenge/training, social engagement, and cardiovascular/metabolic monitoring. FINGER evidence: Ngandu et al., 'A 2 year multidomain intervention of diet, exercise, cognitive training, and vascular risk monitoring versus control to prevent cognitive decline in at-risk elderly people (FINGER): a randomised controlled trial,' The Lancet, 2015; NTB total score improved 0.20 vs 0.16 over 2 years, a modest but positive signal. U.S. POINTER evidence: Baker et al., 'Structured vs Self-Guided Multidomain Lifestyle Interventions for Global Cognitive Function: The US POINTER Randomized Clinical Trial,' JAMA, 2025; structured improved 0.243 SD/year vs 0.213 SD/year for self-guided, difference +0.029 SD/year, p=.008. "
                "Hadi Hosseini belongs here, but carefully: his work is not the same broad lifestyle package as FINGER/U.S. POINTER. It is a Stanford cognitive-training / neurocognitive-rehabilitation branch of the multidomain prevention space. Gozdas et al., including S. M. Hadi Hosseini, 'Long-term cognitive training enhances fluid cognition and brain connectivity in individuals with MCI,' Translational Psychiatry, 2024; 6-month multi-domain computerized cognitive training in amnestic MCI, 34 completers; Fluid Cognition improved 10.9% in the cognitive-training group, Cohen's d=0.70, but the sample is small, so call it promising rather than definitive. Related Hosseini background I checked but did not make the main impact anchor: Hosseini, Kramer, and Kesler, 'Neural correlates of cognitive intervention in persons at risk of developing Alzheimer's disease,' Frontiers in Aging Neuroscience, 2014, a review/methods framing paper; and Bruno, Shaw, and Hosseini, 'Toward Personalized Cognitive Training in Older Adults: A Pilot Investigation of the Effects of Baseline Performance and Age on Cognitive Training Outcomes,' Journal of Alzheimer's Disease, 2024 volume / online first 2023, a small healthy-aging pilot about personalization. Single-domain caution: Barnes et al., 'Trial of the MIND Diet for Prevention of Cognitive Decline in Older Persons,' New England Journal of Medicine, 2023; MIND diet plus caloric restriction did not significantly beat control diet with caloric restriction, difference 0.035 standardized units, p=.23. "
                "Non-invasive neuromodulation: latest human methods include personalized precuneus rTMS, home gamma tACS, and 40 Hz audiovisual sensory stimulation. rTMS evidence: Koch et al., 'Effects of 52 weeks of precuneus rTMS in Alzheimer's disease patients: a randomized trial,' Alzheimer's Research & Therapy, 2025; CDR-SB worsened +1.36 rTMS vs +2.45 sham at 52 weeks, but only 48 enrolled and 31-32 reached the long follow-up. Gamma tACS evidence: Cantoni et al., 'Home-Based Gamma Transcranial Alternating Current Stimulation in Patients With Alzheimer Disease: A Randomized Clinical Trial,' JAMA Network Open, 2025; n=50, home gamma tACS showed small clinical differences and EEG engagement, but this is still proof-of-concept. GENUS human sensory evidence: Chan et al., 'Gamma frequency sensory stimulation in mild probable Alzheimer's dementia patients: Results of feasibility and pilot studies,' PLOS ONE, 2022; feasibility/pilot studies suggest safety and target engagement, not definitive efficacy. Bottom line to say out loud: lifestyle has the strongest human-scale evidence but modest effects; Stanford/Hosseini supports the cognitive-training branch; neuromodulation is exciting because it may be targetable/wearable, but it still has to prove durable clinical and biomarker impact.")),
    dict(kind="content", kicker="why clearance", title="A leading hypothesis: failing glymphatic clearance lets amyloid build up", fig=f"{CF}/glymphatic.png",
         take="The brain clears amyloid-β / tau via CSF–interstitial exchange (the glymphatic system), boosted by sleep and vascular pulsation. Impaired clearance is a leading — but still-unsettled — explanation for AD (Iliff 2012; Xie 2013; DTI-ALPS, ADNI 2024).",
         notes="The mechanistic bridge — why stimulating the brain might help at all. One leading hypothesis is that AD is partly a clearance failure. The glymphatic system (Iliff 2012) moves CSF along perivascular spaces to wash amyloid-β and tau out toward the cervical lymph nodes; it is strongly boosted during sleep (Xie 2013) and by vascular pulsation, and depends on the AQP4 water channel. In AD, amyloid is cleared more slowly (Mawuenyega 2010), and impaired glymphatic flow on DTI-ALPS imaging appears to precede amyloid deposition (ADNI 2024). Important caveat for this audience: it remains contested — DTI-ALPS may index vascular rather than glymphatic function (Mayo 2025), and some studies find clearance reduced rather than increased in sleep. So present it as an active, plausible contributor, not the proven sole cause."),
    dict(kind="content", kicker="why rhythms", title="Neural waves can organize CSF perfusion and clearance", fig=f"{CF}/csf_wave_evidence.png",
         take="Jiang-Xie et al. 2024 (Nature) is the cleanest causal anchor: flatten neural/ionic waves and CSF infiltration/clearance drops; generate synthetic waves with transcranial optogenetics and CSF-to-ISF perfusion increases. Sleep, neuromodulator, vascular, and 40 Hz sensory papers support the broader state-control story.",
         notes=("This is the dedicated mechanism slide. Say it simply: the glymphatic pathway is not just plumbing; brain state and brain waves can organize the flow. The strongest causal paper is Jiang-Xie et al., 'Neuronal dynamics direct cerebrospinal fluid perfusion and brain clearance,' Nature, 2024. Their method was not vibrotactile stimulation. They measured large rhythmic ionic waves in brain tissue, then did two causal manipulations: chemogenetically flattening those waves impaired CSF infiltration and molecular clearance, while synthetic waves generated by transcranial optogenetic stimulation increased CSF-to-interstitial-fluid perfusion. That is why I call it the causal anchor. "
                "Then make the evidence ladder clear. Fultz et al., 'Coupled electrophysiological, hemodynamic, and cerebrospinal fluid oscillations in human sleep,' Science, 2019, showed in humans that NREM slow neural waves, blood oxygenation waves, and CSF flow oscillations are coupled. Hablitz et al., 'Increased glymphatic influx is correlated with high EEG delta power and low heart rate in mice under anesthesia,' Science Advances, 2019, showed glymphatic influx tracks slow cortical activity/state in mice. Hauglund et al., 'Norepinephrine-mediated slow vasomotion drives glymphatic clearance during sleep,' Cell, 2025, adds a sleep-pump mechanism: norepinephrine-linked slow vasomotion during NREM sleep drives clearance. Chuang et al., 'Cholinergic basal forebrain neurons regulate vascular dynamics and cerebrospinal fluid flux,' Nature Communications, 2025, shows neuromodulatory control of BOLD-CSF coupling and glymphatic flux, with human imaging plus mouse lesion/pharmacology. Broggini et al., 'Long-wavelength traveling waves of vasomotion modulate the perfusion of cortex,' Neuron, 2024, supports the vascular-wave side: vasomotion waves modulate cortical perfusion, though it is more blood/perfusion than direct glymphatic clearance. Murdock et al., 'Multisensory gamma stimulation promotes glymphatic clearance of amyloid,' Nature, 2024, connects external 40 Hz light+sound to increased CSF influx/ISF efflux and amyloid clearance in AD-model mice. Bottom line: Jiang-Xie is the strongest direct wave-to-clearance causal paper; the others support the broader idea that neural state, neuromodulators, and vascular waves regulate CSF/glymphatic flow. This motivates our open question, but it does not prove vibrotactile stimulation will do the same.")),
    dict(kind="content", kicker="and it can be driven", title="And clearance can be driven non-invasively — preclinical evidence", fig=f"{CF}/driving_clearance.png",
         take="This slide is animal proof-of-principle, not human clinical proof. 40 Hz sensory stimulation increased glymphatic flow and reduced amyloid in AD-model mice (Murdock 2024). Focused ultrasound increased CSF influx/clearance in rodents (Aryal 2022; Azadian 2025). Open question: can vibrotactile stimulation enhance glymphatic clearance?",
         notes="The proof-of-principle that motivates the program. Be very clear: this slide is mostly preclinical animal evidence, not human efficacy. The previous slide made the mechanism point that neural and vascular dynamics can organize CSF perfusion. This slide asks: can an outside intervention move that biology? Murdock et al. 2024, Nature, gives the directly relevant sensory-stimulation result: 40 Hz multisensory light + sound in 5XFAD AD-model mice increased CSF tracer influx, increased ISF efflux, lowered frontal-cortex amyloid by about 30%, and blocking the AQP4 water channel abolished the amyloid-clearance effect, tying it to the glymphatic route. Separately, Stanford's focused-ultrasound work is also preclinical: Aryal 2022 used transcranial ultrasound to increase CSF influx and intrathecal drug delivery in rats; Azadian 2025 used low-intensity focused ultrasound to clear debris and improve outcomes in mouse hemorrhagic-stroke models. Together they do not prove a wearable haptic treatment works in humans. They support the narrower claim: clearance biology can be modulated from outside the skull in animal models, so it is reasonable to ask whether vibrotactile stimulation can enhance glymphatic clearance."),
    dict(kind="content", kicker="the thesis", title="The proposal: use vibrotactile stimulation to engage brain rhythms and drive clearance", fig=f"{CF}/vision_chain.png",
         take="Wearable vibrotactile stimulation → entrain brain rhythms → engage glymphatic clearance of amyloid-β / tau. A mechanism hypothesis — explicitly not yet a treatment claim.",
         notes="The core chain. The glymphatic system is the brain's waste-clearance pathway — CSF/interstitial-fluid exchange that removes amyloid-β and tau. The hypothesis: if we can drive the right rhythms or brain-states from the skin, we may enhance that clearance. This is a mechanism hypothesis to test, not a clinical claim — I'll be explicit about that distinction the whole way through."),
    dict(kind="content", kicker="why vibrotactile", title="Why vibrotactile, and why wearable: the white space next to light and sound", fig=f"{CF}/whitespace.png",
         take="40 Hz light/sound (GENUS) is the developed approach but hard to wear daily. Vibrotactile stimulation is the open frontier — wearable, sleep-compatible, and pairs naturally with sensing.",
         notes="The niche. The established sensory-stimulation approach is audiovisual 40 Hz (GENUS). Its practical limits are daily wearability, comfort, and sleep use — exactly when clearance peaks. Vibrotactile stimulation is comparatively unexplored, is wearable, can run during sleep, and integrates with the wearable-sensing ecosystem (the Snyder-lab angle). That combination is the white space this program targets."),

    # ===================== PART 2 — LITERATURE & PARAMETERS =====================
    dict(kind="section", title="Part 2 · What the literature says — and what to test"),
    dict(kind="content", kicker="evidence · 40 Hz gamma", title="40 Hz sensory stimulation lowers amyloid and drives clearance — animals, and early humans",
         take="GENUS / Tsai 2016: 40 Hz light/sound lowers amyloid. Murdock 2024 (Nature): 40 Hz gamma drives glymphatic Aβ clearance. Human gamma-sensory is safe with target engagement (Chan 2022).",
         notes="The anchor evidence chain. In mice, 40 Hz visual/auditory stimulation (GENUS, Tsai lab 2016) reduces amyloid and engages microglia; Murdock 2024 in Nature shows 40 Hz gamma drives CSF influx and amyloid clearance, AQP4-dependent — the gamma-to-glymphatic bridge. Early human trials (Chan 2022) report safety, neural entrainment, and good compliance. This is why 40 Hz is the canonical frequency to start from."),
    dict(kind="content", kicker="the key caveat", title="But a steady-state response is not the same as entraining the brain's own rhythm",
         take="A driven 40 Hz response ≠ engaging native gamma (Buzsáki/Soula; some studies find 40 Hz light fails to entrain native gamma in AD-model mice). We separate target engagement from disease modification.",
         notes="Essential for credibility — especially at Stanford. The Buzsáki lab and others caution that an evoked steady-state response at the stimulus frequency is not the same as entraining the brain's endogenous oscillator; some studies find 40 Hz light does not entrain native gamma in AD models. So the program holds two questions apart: did we engage the circuit, versus did we change the disease. Building that discipline in is part of the design, not a footnote."),
    dict(kind="content", kicker="evidence · clearance", title="Clearance is actively driven by neural, vascular & sleep dynamics — so 'brain-state' stimulation is plausible",
         take="CSF flow tracks NREM slow waves (Fultz 2019) and EEG delta (Hablitz 2019); neuronal dynamics actively direct CSF perfusion (Jiang-Xie et al. 2024, Nature); human sleep clearance moves plasma Aβ/tau (Dagum 2026).",
         notes="Why targeting clearance via brain-state is reasonable. Glymphatic/CSF flow isn't passive: it's driven by neural activity, vascular pulsation, and especially sleep slow waves — Fultz 2019 (human, NREM slow waves drive CSF oscillations), Hablitz 2019 (influx tracks EEG delta), Mestre 2018 (arterial pulsation), and Jiang-Xie et al. 2024 in Nature, from the Kipnis group (neuronal ionic waves actively direct CSF perfusion). In humans, sleep clearance raises morning plasma Aβ/tau (Dagum 2026). So if stimulation can shape brain state, engaging clearance is mechanistically plausible — and this points to slow / sleep-band stimulation, not only 40 Hz."),
    dict(kind="content", kicker="evidence · vibrotactile", title="The vibrotactile anchor: 40 Hz vibration helps in mouse AD models, and cortex codes vibration frequency",
         take="40 Hz whole-body vibration reduces pathology and improves function in AD-model mice (Suk 2023). Somatosensory cortex faithfully encodes vibration frequency (Romo, Mountcastle) — vibrotactile input can carry a frequency code.",
         notes="The vibrotactile-specific evidence. Suk 2023 (Tsai lab) showed 40 Hz whole-body vibration reduces pathology and improves motor function in mouse AD models — the central vibrotactile anchor, though not yet a human AD trial. And classic somatosensory physiology (Romo, Mountcastle flutter coding) shows primary somatosensory cortex faithfully encodes vibration frequency — so a frequency-specific tactile drive is biologically grounded, not wishful."),
    dict(kind="content", kicker="→ what to test", title="So which vibrotactile parameters should we test?",
         take="40 Hz (gamma) · ~50 Hz (our electrophysiology, Part 3) · slow ~1 Hz / sleep-band (clearance biology) · steady vs coordinated-reset patterning · controls: 20 Hz, sham, matched salience.",
         notes="The payoff of Part 2. The literature defines a parameter space: 40 Hz (the GENUS anchor); ~50 Hz (where our own single-unit data peak — coming in Part 3); slow ~1 Hz / sleep-band (because clearance tracks slow waves); patterning — steady single-site versus spatiotemporal 'coordinated reset', which produces lasting plasticity rather than transient entrainment in Parkinson's (Tass vibrotactile glove); and rigorous controls — a non-40 frequency like 20 Hz, sham, and perceptually matched salience to exclude pure arousal. This is the experimental program the current study begins to ground."),

    # ===================== PART 3 — CURRENT STUDY =====================
    dict(kind="section", title="Part 3 · Does vibrotactile stimulation reach the brain? A first study",
         sub="Foundational electrophysiology in the mouse — before any clearance claim"),
    dict(kind="content", title="Design: parametric vibrotactile stimulation with simultaneous electrophysiology", fig=TRIAL,
         take="3 s ON / 3 s OFF blocks across four carrier frequencies (5/10/26/50 Hz) and three amplitudes; ~200 repeats/condition; dual-region linear-probe recording (hippocampus + entorhinal cortex).",
         notes="A tactor delivers a sinusoidal vibration in 3 s ON / 3 s OFF blocks (figure: trial structure + analysis windows). We vary carrier frequency (5, 10, 26, 50 Hz) and amplitude, ~200 trials/condition, recording extracellularly with linear silicon probes in two connected regions at once: hippocampus (spatial/memory) and entorhinal cortex (its principal cortical input). Each window is referenced to the 1 s pre-stimulus baseline; 100 ms margins isolate onset/offset transients."),
    dict(kind="content", kicker="key methodological distinction", title="One electrode yields two readouts: LFP and single-unit activity", fig=f"{CF}/stadium.png",
         take="LFP = low-frequency aggregate field (many cells). A single unit = one individual neuron's firing (spikes), isolated by spike sorting. They differ in what can fake them — spikes are the conservative readout.",
         notes="The crux of the whole study. An extracellular electrode captures two regimes. The local field potential (LFP) is the low-frequency aggregate of synaptic/transmembrane currents from many neurons — large, but non-specific and susceptible to volume-conducted or instrumental noise. A 'single unit' is one individual neuron's spiking, isolated by spike sorting (clustering spikes by waveform). Stadium intuition: the crowd's roar (LFP) versus one identified shout (a single unit). The asymmetry that matters: an electrical artifact can add power to the LFP, but it cannot make a sorted neuron fire — so single-unit rate changes are the conservative, artifact-resistant evidence."),
    dict(kind="content", kicker="how to read the evidence", title="Evidence ladder: from 'the brain noticed' to 'the rhythm captured it'",
         fig=EVIDENCE, full_fig=True,
         notes="Teaching slide. Use the clapping/body analogy: one clap makes you flinch = evoked response. Different clap speeds make you react differently = frequency-specific response. Louder/stronger claps make a bigger response = dose-response or amplitude-graded response. A steady sequence of claps appears as a spectral peak at the clap rate = steady-state or frequency-following. But an LFP peak alone can be mechanical or electrical pickup; spike sorting asks whether real neurons changed, and a true frequency-following spike claim would need spikes aligned to the vibration cycle. Phase locking means activity lands at the same point in each cycle, which needs the actual vibration phase. Entrainment is the strongest claim: the outside beat captures an internal rhythm, usually including phase alignment plus a change in the native rhythm. Amplitude or power can grow during entrainment, but size is not the definition; timing/frequency capture is. Our result reaches response plus 50 Hz/high-amplitude single-unit rate modulation; it does not prove phase locking or entrainment."),
    dict(kind="content", kicker="finding 1", title="A robust LFP response — transition-weighted, not a sustained oscillation",
         fig=f"{F}/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png",
         take="The broadband LFP responds at stimulus onset/offset (an evoked transient), not as a sustained rhythm at the carrier frequency.",
         notes="The broadband LFP shows a clear, amplitude-graded response — but concentrated at the ON and OFF transitions: an evoked transient, not a sustained oscillation at the drive frequency. The difference between responding to the event of stimulation versus tracking its rhythm. So there is a response — but not yet frequency-following."),
    dict(kind="content", kicker="finding 2", title="No frequency-following in hippocampus at any carrier",
         fig=f"{F}/05_Frequency_Spectral/spectral_slope_itpc_dec4.png",
         take="No narrowband spectral peak above the 1/f background, and inter-trial phase consistency at chance — across 5/10/26/50 Hz, replicated across sessions.",
         notes="The entrainment test (recall Part 2's definition). Frequency-following predicts a narrowband peak at the carrier above the 1/f background plus above-chance inter-trial phase consistency. We see neither, at any carrier, replicated across two sessions — no power- or phase-based frequency-following in hippocampus."),
    dict(kind="content", kicker="finding 3", title="Entorhinal cortex shows an amplitude-graded 50 Hz LFP increase",
         fig=f"{F}/05_Frequency_Spectral/driven_power_change_by_analysis_group.png",
         take="A narrowband 50 Hz LFP power increase, scaling with amplitude — the candidate entrainment signal. But the LFP is exactly the readout most vulnerable to artifact.",
         notes="In entorhinal cortex there is a narrowband 50 Hz LFP power increase that scales with amplitude — superficially the entrainment signal we want. But the LFP is precisely the readout electrical pickup can mimic, so before interpreting it as neural we must exclude a stimulator-coupled artifact."),
    dict(kind="content", kicker="the confound", title="The confound: stimulator-coupled 50 Hz electrical artifact", fig=f"{CF}/trap.png",
         take="An electromechanical actuator can inject a 50 Hz electrical artifact directly into the recording — indistinguishable from a neural 50 Hz in the LFP alone.",
         notes="The actuator and its drive electronics can couple a 50 Hz signal into the recording — volume-conducted or via wiring. In the LFP that's indistinguishable from a neural 50 Hz. We need a discriminator the artifact can't fool."),
    dict(kind="content", kicker="finding 3, controlled", title="Disconnected channels carry the 50 Hz — so it is largely pickup",
         fig=f"{F}/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png",
         take="Disconnected electrodes (which cannot record neural signal) show ~6× more 50 Hz than in-tissue channels. The entorhinal 50 Hz LFP is substantially artifact.",
         notes="The discriminator: broken/disconnected channels cannot record neurons but still act as antennas for pickup. If they carry the 50 Hz, it's instrumental. They do — ~6× the in-tissue channels — so the entorhinal 50 Hz LFP is largely stimulator artifact. The headline LFP result is mostly the machine. This is the central twist, and exactly the 'steady-state response ≠ real engagement' caution from Part 2, caught in our own data."),
    dict(kind="content", kicker="finding 4 — the robust result", title="Frequency-specific single-unit rate modulation at 50 Hz",
         fig=f"{F}/11_Spikes/spike_onoff_cross_dataset.png",
         take="Sorted single units change firing rate during 50 Hz / high-amplitude stimulation, in both regions — an effect electrical pickup cannot produce.",
         notes="The artifact-resistant readout: sorted single units change firing rate during the high-amplitude 50 Hz condition, in both regions, and far more than at lower carriers. Pickup cannot drive a sorted neuron's spike train, so this is the clean evidence — and it answers the program's hardest objection: vibrotactile stimulation does reach and frequency-specifically drive these neurons."),
    dict(kind="content", kicker="controls", title="Controls: high-pass separation + autocorrelogram / ISI screens",
         fig=f"{F}/11_Spikes/unit87_acg_artifact_screen.png",
         take="Spikes are detected >~300 Hz (50 Hz pickup is removed pre-detection); units show no stimulus-locked 50 Hz periodicity and no ON-rise in refractory violations.",
         notes="Two controls. Spike detection operates above ~300 Hz, so 50 Hz pickup is filtered out before a spike is detected. And were pickup injecting spurious spikes at 50 Hz, the autocorrelogram would develop 20 ms periodicity during stimulation — it does not, and is identical ON vs OFF; refractory-violation rates don't rise either. So the rate modulation is genuine single-unit activity."),
    dict(kind="content", kicker="finding 5", title="Region-specific, bidirectional modulation — not a passive relay",
         fig=f"{F}/11_Spikes/spike_50hz_interpretation.png",
         take="Hippocampus: a driven-up subset. Entorhinal cortex: net-suppressed. Opposite transformations of identical input argue for active, circuit-specific processing.",
         notes="The two regions transform the same input in opposite directions: a hippocampal subset increases firing while entorhinal cortex is net-suppressed. Opposite-signed responses to identical input are inconsistent with a passive relay and consistent with circuit-specific processing — and the suppression is itself artifact-resistant (pickup adds, it can't remove, spikes)."),
    dict(kind="content", kicker="finding 6", title="No clear cross-regional coordination at 50 Hz",
         fig=f"{F}/11_Spikes/coordination_50hz_pooled.png",
         take="LFP–LFP coherence rises, but the artifact-resistant cross-region spike–field measure does not — parsimoniously a shared signal, not interaction.",
         notes="LFP–LFP coherence increases, but a shared pickup inflates coherence. The spike–field measure (one region's spikes vs the other's LFP phase), which a shared artifact can't fake as easily, does not increase — so the apparent coupling is most parsimoniously a shared signal, not genuine coordination."),

    # ===================== PART 4 — LIMITS & NEXT =====================
    dict(kind="section", title="Part 4 · Limits, and the next study"),
    dict(kind="content", kicker="the limitation", title="Entrainment was untestable — a measurement gap, not a null",
         take="Our acquisition was not equipped to test entrainment: no time-aligned stimulus-phase reference was recorded — so phase-following is untestable here, not negative.",
         notes="Testing entrainment (phase-locking) requires a time-aligned reference for the stimulus phase. We didn't record a usable one — so 'no entrainment shown' is a measurement gap, not evidence of absence. The power/periodicity negatives are real; only the phase-locking claim is gated by the missing reference. Separately, we found post hoc that the lower-frequency stimuli (5/10/26 Hz) were not clean sine waves — so the 50 Hz frequency-specificity is partly confounded with stimulus quality; recording the delivered waveform fixes that too."),
    dict(kind="content", kicker="diagnosis", title="The digital sync channel never captured the carrier", fig=TTL,
         take="The recorded sync line updated at ~4 Hz, independent of carrier (identical pulse counts at 5 vs 26 Hz; ~78 expected at 26 Hz). No phase reference exists in the data.",
         notes="Verified from the raw digital stream: the sync channel updated at ~4 Hz irrespective of carrier (same ~6 pulses/trial for 5 and 26 Hz; ~78 expected at 26 Hz), never sustained a run at the carrier period, and was misaligned with the schedule. Undersampled and decoupled — phase unrecoverable. A ~4 Hz observer can't resolve a 26 Hz oscillation."),
    dict(kind="content", kicker="the fix", title="Fix: redundant, clock-shared stimulus references", fig=f"{CF}/fix.png",
         take="Firmware per-cycle sync + a transduced force/accelerometer signal + a drive-signal copy, all on the acquisition clock — cross-checked, with pre-session verification.",
         notes="Design, not analysis: record the stimulus three ways on the acquisition clock — a firmware per-cycle marker (implemented), a transduced measurement of the delivered vibration (PVDF or accelerometer, which also verifies delivery), and a drive-signal copy — then cross-validate, plus a short verification recording before the session. With redundancy on a shared clock, a failed reference is caught immediately rather than months later. This is what makes entrainment — and eventually clearance readouts — testable."),

    # ===================== PART 5 — HOW IT FITS =====================
    dict(kind="section", title="Part 5 · How it fits the program"),
    dict(kind="content", kicker="the role of this study", title="This study de-risks the program's core premise",
         take="It shows peripheral vibration reaches AD-relevant medial-temporal circuits and that those neurons are frequency-tuned (peak ~50 Hz) — directly answering the 'steady-state ≠ engagement' objection.",
         notes="How it fits. The program's hardest objection (Part 2) is whether sensory stimulation engages the relevant circuits or just produces a surface steady-state. This study answers it for vibrotactile stimulation: peripheral vibration drives frequency-specific single-unit responses in hippocampus and entorhinal cortex — AD-relevant medial-temporal circuits — and they're frequency-tuned, peaking near 50 Hz. That converts 'vibrotactile 40 Hz' from an assumption into a measured, tunable target-engagement parameter — the prerequisite before any clearance or clinical claim, and it sharpens the parameter list (40 vs 50 vs slow) for the next studies."),
    dict(kind="content", kicker="key references", title="Key references",
         take="Lifestyle: Ngandu 2015 · Baker 2025 · Livingston 2024 · Barnes 2023.  Clearance/waves: Iliff 2012 · Xie 2013 · Fultz 2019 · Hablitz 2019 · Jiang-Xie 2024 · Murdock 2024 · Hauglund 2025 · Chuang 2025 · Broggini 2024.  Disease-space examples: Gaberel 2014 · Mestre 2020 · JCI 2026 · Cui 2021 · Zhang 2023 · Lopes 2025.  Guardrail: Buzsáki / Soula.",
         notes="Grouped anchors. Lifestyle bar — FINGER (Ngandu, Lancet 2015), U.S. POINTER (Baker, JAMA 2025), the Lancet Commission synthesis (Livingston 2024, ~45% modifiable risk), and the single-domain counterpoint (MIND diet alone null; Barnes, NEJM 2023). Clearance hypothesis & drivers — glymphatic discovery (Iliff, Sci Transl Med 2012), sleep clearance (Xie, Science 2013), slowed Aβ clearance in AD (Mawuenyega, Science 2010), human sleep CSF coupling (Fultz, Science 2019), delta/glymphatic state coupling (Hablitz, Science Advances 2019), the direct neural/ionic-wave causal paper (Jiang-Xie et al., Nature 2024, Kipnis group), 40 Hz → glymphatic clearance, AQP4-dependent (Murdock, Nature 2024), norepinephrine-mediated sleep vasomotion (Hauglund, Cell 2025), cholinergic neurovascular control of CSF/glymphatic flux (Chuang, Nature Communications 2025), vascular-wave perfusion (Broggini, Neuron 2024), and Stanford focused ultrasound (Aryal, J Control Release 2022; Azadian, Nat Biotech 2025). Stimulation — origin of sensory-gamma (Tsai 2016), the vibrotactile anchor (Suk 2023). Disease-space examples — stroke: impaired glymphatic perfusion after stroke (Gaberel, Stroke 2014), acute ischemic edema driven by CSF/glymphatic influx so timing matters (Mestre, Science 2020), and chronotherapy improving glymphatic function and recovery in mice (JCI 2026). Parkinson's: AQP4/glymphatic disruption aggravates α-syn pathology (Cui 2021; Zhang 2023), and a Brain 2025 paper links glymphatic function to α-syn propagation. Guardrail — Buzsáki/Soula: a steady-state response is not entrainment. Full lit-review repository available on request."),
    dict(kind="closing", title="Thank you — questions",
         sub="Happy to go into any figure, the artifact controls, the parameter plan, or the next-round instrumentation.",
         notes="Anticipated questions. 'Is 50 Hz special or just strongest?' — strongest clean single-unit effect of the carriers tested; the LFP transient was largest at 26 Hz but that's the artifact-prone measure. 'Could it be arousal?' — possible, but frequency-specific (50 ≫ 26 at matched amplitude); an indirect sensory/state pathway isn't excluded. 'Why distrust the 50 Hz LFP?' — disconnected channels carry it at ~6× tissue. 'Is this a treatment?' — no; this is target-engagement evidence for a mechanism hypothesis, deliberately separated from any clinical claim."),
]


# ---------------------------------------------------------------- generated teaching figures
def build_evidence_ladder_figure(out: str | Path) -> None:
    """One-slide visual glossary for evoked, stimulus-specific, following, phase locking, entrainment."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    cardinal = TEAL
    navy = NAVY
    grey = GREY
    fog = PANEL
    stone = STONE
    stone_dark = STONE_DARK
    stone_light = STONE_LIGHT

    fig = plt.figure(figsize=(16, 9), dpi=220)
    fig.patch.set_facecolor("white")
    fig.text(0.04, 0.980, "Evidence ladder: from response to entrainment",
             fontsize=19, weight="bold", color=navy, va="top")
    fig.text(0.04, 0.940,
             "Memory hook: claps and body movement. The farther down the ladder, the stronger the claim.",
             fontsize=11.5, color=grey, va="top")

    rows = [
        ("1", "Evoked response",
         "One clap happens; your body reacts.",
         "Data: signal changes at stimulation ON/OFF.",
         "one clap -> flinch"),
        ("2", "LFP amplitude clue at 50 Hz",
         "The field signal can grow when the buzz gets stronger.",
         "Data: compare amp100 -> amp250 at 50 Hz; LFP can include pickup.",
         "LFP clue: 50 Hz, stronger buzz"),
        ("3", "Single-unit frequency x amplitude tuning",
         "Neuron clusters react differently to clap speed and strength.",
         "Data: Kilosort units change most at 50 Hz + high amplitude.",
         "cleaner neural readout:\n50 Hz high amp"),
        ("4", "Steady-state / frequency-following",
         "A steady clap sequence shows up as a peak at that rate.",
         "Data: 50 Hz peak can be machine noise; Kilosort checks neuron-cluster firing.",
         "the beat appears as a peak"),
        ("5", "Phase locking",
         "Your movement lands at the same beat-position again and again.",
         "Data: spikes/LFP line up to the same vibration phase across trials.",
         "same beat-position, every trial"),
        ("6", "Entrainment",
         "The outside beat captures an internal rhythm.",
         "Data: native rhythm shifts into the external rhythm's timing.",
         "phase-locked + rhythm captured"),
    ]

    y0 = 0.830
    row_h = 0.124
    chart_x = 0.70
    chart_w = 0.245
    for idx, (num, term, plain, data, hook) in enumerate(rows):
        y = y0 - idx * row_h
        if idx % 2 == 0:
            fig.add_artist(Rectangle((0.03, y - 0.089), 0.94, 0.103, transform=fig.transFigure,
                                     facecolor=fog, edgecolor="none", alpha=0.72))

        fig.text(0.045, y, num, fontsize=16, weight="bold", color="white", ha="center", va="center",
                 bbox=dict(boxstyle="circle,pad=0.29", facecolor=cardinal, edgecolor=cardinal))
        fig.text(0.085, y + 0.031, term, fontsize=13.0, weight="bold", color=navy, va="top")
        fig.text(0.085, y + 0.003, plain, fontsize=10.1, color=navy, va="top")
        fig.text(0.085, y - 0.025, data, fontsize=9.3, color=grey, va="top")
        fig.text(0.485, y + 0.010, hook, fontsize=11.0, weight="bold", color=cardinal, va="center")

        ax = fig.add_axes([chart_x, y - 0.043, chart_w, 0.078])
        ax.set_facecolor("white")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

        if idx == 0:
            t = np.linspace(-1, 4, 600)
            sig = 0.05 * np.sin(2 * np.pi * 1.5 * t)
            sig += 0.95 * np.exp(-((t - 0.05) / 0.15) ** 2)
            sig += 0.55 * np.exp(-((t - 3.0) / 0.18) ** 2)
            ax.axvspan(0, 3, color=cardinal, alpha=0.11)
            ax.axvline(0, color=cardinal, lw=1.5)
            ax.axvline(3, color=cardinal, lw=1.5)
            ax.plot(t, sig, color=navy, lw=2)
            ax.text(0.03, 0.84, "ON", transform=ax.transAxes, fontsize=8, color=cardinal)
            ax.text(0.72, 0.84, "OFF", transform=ax.transAxes, fontsize=8, color=cardinal)
            ax.set_xlim(-0.7, 3.7)
            ax.set_ylim(-0.35, 1.2)
        elif idx == 1:
            amps = [100, 180, 250]
            vals = [0.20, 0.48, 0.88]
            ax.bar(range(3), vals, color=["#D8D8D8", "#AAAAAA", cardinal], width=0.58, alpha=0.78)
            ax.plot(range(3), vals, color=cardinal, lw=1.3, marker="o", ms=3)
            ax.set_xticks(range(3), [f"amp{a}" for a in amps], fontsize=8)
            ax.set_ylim(0, 1.0)
            ax.text(0.42, 0.82, "50 Hz", transform=ax.transAxes, fontsize=8, color=cardinal)
            ax.text(0.42, 0.08, "can include pickup", transform=ax.transAxes, fontsize=7.3, color=grey)
        elif idx == 2:
            ax.set_position([chart_x, y - 0.050, chart_w, 0.090])
            vals = np.array([
                [0.05, 0.03, 0.18, 0.96],
                [0.04, 0.02, 0.12, 0.55],
                [0.06, 0.02, 0.08, 0.24],
            ])
            ax.imshow(vals, cmap="Reds", vmin=0, vmax=1, aspect="auto")
            ax.set_xticks(range(4), ["5", "10", "26", "50"], fontsize=7.2)
            ax.set_yticks(range(3), ["amp250", "amp180", "amp100"], fontsize=6.8)
            ax.tick_params(length=0, pad=1)
            for col in range(4):
                for row in range(3):
                    ax.add_patch(plt.Rectangle((col - 0.5, row - 0.5), 1, 1,
                                               fill=False, edgecolor="white", lw=0.7))
            ax.text(0.50, -0.28, "single units: frequency x amplitude", transform=ax.transAxes,
                    fontsize=7.2, color=stone_dark, ha="center", va="top", weight="bold",
                    clip_on=False, zorder=40)
            ax.text(3, 0, "biggest", fontsize=7.4, color="white",
                    ha="center", va="center", weight="bold")
            ax.set_xlabel("frequency (Hz)", fontsize=6.8, labelpad=0)
        elif idx == 3:
            ax.set_position([chart_x, y - 0.043, chart_w * 0.61, 0.078])
            freq = np.linspace(5, 95, 600)
            background = 1.25 / np.sqrt(freq)
            peak = 0.48 * np.exp(-0.5 * ((freq - 50) / 2.8) ** 2)
            power = background + peak
            ax.plot(freq, background, color="#B8B8B8", lw=1.4, ls="--")
            ax.plot(freq, power, color=stone, lw=2)
            ax.axvline(50, color=cardinal, lw=1.5)
            ax.fill_between(freq, background, power, where=(freq > 45) & (freq < 55),
                            color=cardinal, alpha=0.18)
            ax.text(0.50, 0.86, "50 Hz peak", transform=ax.transAxes, fontsize=8, color=cardinal,
                    ha="center")
            ax.text(0.58, 0.53, "LFP can\nfool us", transform=ax.transAxes, fontsize=7.2,
                    color=grey, ha="left", va="center")
            ax.text(0.04, 0.12, "1/f background", transform=ax.transAxes, fontsize=7.3, color=grey)
            ax.set_xlim(5, 95)
            ax.set_ylim(0, 0.86)
            ax.set_xticks([10, 50, 90])
            ax.set_xticklabels(["10", "50", "90 Hz"], fontsize=7.2)
            ax.set_yticks([])

            ax2 = fig.add_axes([chart_x + chart_w * 0.66, y - 0.043, chart_w * 0.32, 0.078])
            ax2.set_facecolor("white")
            for spine in ax2.spines.values():
                spine.set_visible(False)
            ax2.set_xticks([])
            ax2.set_yticks([])
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.text(0.38, 0.98, "Kilosort:\ncluster spikes", transform=ax2.transAxes,
                     fontsize=7.1, color=stone_dark, ha="center", va="top", weight="bold")
            cluster_specs = [
                (0.20, 0.55, stone_dark),
                (0.36, 0.32, cardinal),
                (0.49, 0.62, stone),
            ]
            offsets = np.array([
                [-0.035, -0.010], [-0.020, 0.030], [0.000, 0.000],
                [0.018, -0.026], [0.034, 0.018], [-0.006, -0.038],
            ])
            for cx, cy, col in cluster_specs:
                pts = offsets + np.array([cx, cy])
                ax2.scatter(pts[:, 0], pts[:, 1], s=10, color=col, alpha=0.78, edgecolors="none")
            ax2.annotate("", xy=(0.67, 0.50), xytext=(0.56, 0.50),
                         arrowprops=dict(arrowstyle="->", color=grey, lw=1.2))
            firing_x = [0.72, 0.77, 0.82, 0.87, 0.92]
            for i, xval in enumerate(firing_x):
                height = 0.16 + 0.06 * (i % 2)
                ax2.vlines(xval, 0.34, 0.34 + height, color=stone_dark, lw=2.0)
            ax2.text(0.82, 0.24, "neuron-cluster\nfiring", transform=ax2.transAxes,
                     fontsize=6.6, color=navy, ha="center", va="top")
        elif idx == 4:
            t = np.linspace(0, 1.0, 800)
            wave = 0.24 * np.sin(2 * np.pi * 3 * t)
            ax.plot(t, wave + 0.76, color="#4F565A", lw=1.8)
            lock_times = np.array([0.08, 0.42, 0.76])
            for p in lock_times:
                ax.axvline(p, ymin=0.10, ymax=0.88, color=stone_dark, lw=1.3, alpha=0.32, zorder=1)
                ax.plot([p], [1.02], marker="v", color=stone_dark, ms=5, zorder=3)
            trial_ys = [0.30, 0.12, -0.06, -0.24]
            for trial, ydot in enumerate(trial_ys):
                ax.hlines(ydot, 0.0, 1.0, color="#D9D9D9", lw=1.0, zorder=0)
                jitter = np.array([-0.004, 0.003, -0.002])
                for p, j in zip(lock_times, jitter):
                    ax.vlines(p + j + trial * 0.001, ydot - 0.065, ydot + 0.065,
                              color=stone_dark, lw=3.4, zorder=4)
                ax.text(-0.035, ydot, f"trial {trial + 1}", fontsize=7.0, color=navy,
                        ha="right", va="center")
            ax.text(0.50, -0.145, "spike ticks line up = same phase", transform=ax.transAxes,
                    fontsize=7.7, color=stone_dark, ha="center", va="bottom", weight="bold",
                    clip_on=False, bbox=dict(facecolor="white", edgecolor="none", alpha=0.72, pad=0.7))
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.42, 1.10)
        else:
            t = np.linspace(0, 1.0, 800)
            stim_on = 0.38
            external = 0.34 * np.sin(2 * np.pi * 4.5 * (t - stim_on))
            native_pre = 0.18 * np.sin(2 * np.pi * 2.4 * t + 1.1)
            native_post = 0.58 * np.sin(2 * np.pi * 4.5 * (t - stim_on) - 0.05)
            native = np.where(t < stim_on, native_pre, native_post)
            ax.axvspan(stim_on, 1.0, color=cardinal, alpha=0.08)
            ax.plot(t[t >= stim_on], external[t >= stim_on] + 0.62, color=cardinal, lw=1.5)
            beat_times = stim_on + np.arange(0, 0.70, 1 / 4.5)
            for b in beat_times:
                ax.axvline(b, ymin=0.55, ymax=0.94, color=cardinal, lw=0.7, alpha=0.35)
            ax.plot(t, native - 0.30, color=stone_dark, lw=2.0)
            ax.axvline(stim_on, color=navy, lw=1, alpha=0.45)
            ax.text(0.02, 0.17, "own pace", transform=ax.transAxes, fontsize=8, color=stone_dark)
            ax.text(0.54, 0.16, "captured + bigger", transform=ax.transAxes, fontsize=8, color=stone_dark)
            ax.text(0.50, 0.80, "external beat ON", transform=ax.transAxes, fontsize=8, color=cardinal)
            ax.annotate("", xy=(0.52, -0.30), xytext=(0.40, -0.30),
                        arrowprops=dict(arrowstyle="->", color=navy, lw=1.4))
            ax.set_xlim(0, 1)
            ax.set_ylim(-1.08, 1.18)

    fig.add_artist(Rectangle((0.03, 0.030), 0.94, 0.062, transform=fig.transFigure,
                             facecolor=FOG_LIGHT, edgecolor=stone_light, linewidth=1.0))
    fig.text(0.05, 0.068,
             "Our current result: 50 Hz/high-amplitude stimulation gives the strongest single-unit rate changes; the LFP 50 Hz peak alone is artifact-suspect.",
             fontsize=11.7, weight="bold", color=navy, va="center")
    fig.text(0.05, 0.042,
             "Not proven here: stimulus-phase locking or native entrainment, because the continuous vibration phase was not recorded.",
             fontsize=10.1, color=grey, va="center")
    fig.savefig(out, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ---------------------------------------------------------------- PPTX
def build_pptx(slides, out):
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
    from PIL import Image

    def rgb(h):
        return RGBColor(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))
    NV, TL, GR, PN, WH = rgb(NAVY), rgb(TEAL), rgb(GREY), rgb(PANEL), RGBColor(255, 255, 255)
    SW, SH = 13.333, 7.5
    prs = Presentation(); prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)
    BL = prs.slide_layouts[6]

    def txt(s, x, y, w, h, text, size, *, bold=False, color=NV, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
        for i, line in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line; p.alignment = align
            r = p.runs[0]; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = "Calibri"

    def bar(s, x, y, w, h, color):
        sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background()

    def img(s, path, x, y, width):
        if Path(path).exists():
            w, h = Image.open(path).size
            s.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(width), height=Inches(width * h / w))

    def pic(s, path, maxw, maxh, top):
        if not Path(path).exists():
            txt(s, 1, top, SW - 2, 1, f"[missing: {path}]", 14, color=GR); return
        w, h = Image.open(path).size; ar = w / h
        iw, ih = maxw, maxw / ar
        if ih > maxh:
            ih, iw = maxh, maxh * ar
        s.shapes.add_picture(str(path), Inches((SW - iw) / 2), Inches(top), width=Inches(iw), height=Inches(ih))

    for i, sl in enumerate(slides):
        s = prs.slides.add_slide(BL); k = sl["kind"]
        if k in ("title", "closing"):
            bar(s, 0, 0, SW, SH, NV); bar(s, 0, 5.0, SW, 0.08, TL); img(s, LOGO_W, 0.55, 0.5, 3.6)
            if k == "title":
                img(s, MOUSE, SW - 2.9, SH - 1.7, 2.2)
            txt(s, 1, 2.0 if k == "title" else 3.0, SW - 4.0, 1.6, sl["title"], 34, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                txt(s, 1, 3.7 if k == "title" else 4.2, SW - 4.0, 1.2, sl["sub"], 17, color=rgb("#D7D2CB"))
            if sl.get("footer"):
                txt(s, 1, 5.25, SW - 4.0, 0.35, sl["footer"], 15.5, color=rgb("#9A958C"))
            if sl.get("footer2"):
                txt(s, 1, 5.68, SW - 4.0, 0.35, sl["footer2"], 15.5, color=rgb("#D7D2CB"))
        elif k == "section":
            bar(s, 0, 0, SW, SH, TL); img(s, LOGO_W, 0.55, 0.5, 2.9)
            txt(s, 1, 2.7, SW - 2, 1.5, sl["title"], 34, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                sub_y = sl.get("sub_y", 4.1)
                txt(s, 1, sub_y, SW - 2, 0.65, sl["sub"], 17, color=rgb("#EDDDDD"))
            if sl.get("refs"):
                txt(s, 1, sl.get("refs_y", sl.get("sub_y", 4.1) + 0.55), SW - 2, 0.5,
                    sl["refs"], 10.5, color=rgb("#D7D2CB"))
        elif sl.get("full_fig"):
            if Path(sl["fig"]).exists():
                s.shapes.add_picture(str(sl["fig"]), Inches(0.15), Inches(0.10), width=Inches(SW - 0.30))
            else:
                txt(s, 1, 2, SW - 2, 1, f"[missing: {sl['fig']}]", 16, color=GR)
        else:
            bar(s, 0, 0, SW, 0.18, TL); y = 0.45
            if sl.get("kicker"):
                txt(s, 0.6, y, SW - 1.2, 0.4, sl["kicker"].upper(), 14, bold=True, color=TL); y += 0.45
            txt(s, 0.6, y, SW - 1.2, 1.1, sl["title"], 24, bold=True, color=NV)
            if sl.get("fig"):
                if sl.get("full_fig"):
                    pic(s, sl["fig"], SW - 0.7, SH - (y + 0.95) - 0.28, top=y + 0.75)
                else:
                    pic(s, sl["fig"], SW - 1.6, SH - (y + 1.4) - 0.9, top=y + 1.25)
            if sl.get("take"):
                bar(s, 0, SH - 0.9, SW, 0.9, PN)
                txt(s, 0.6, SH - 0.87, SW - 1.2, 0.85, sl["take"], 15, bold=True, color=TL, anchor=MSO_ANCHOR.MIDDLE)
        if sl.get("notes"):
            s.notes_slide.notes_text_frame.text = sl["notes"]
        if k != "title" and not sl.get("full_fig"):
            txt(s, SW - 1.8, 0.27, 1.4, 0.4, f"{i + 1} / {len(slides)}", 11,
                color=(WH if k in ("section", "closing") else GR), align=PP_ALIGN.RIGHT)
    prs.save(out)


# ---------------------------------------------------------------- PDF
def build_pdf(slides, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    from matplotlib.backends.backend_pdf import PdfPages
    slide_h = 7.5

    def wrap(t, w):
        return "\n".join(textwrap.fill(line, w) for line in t.split("\n"))

    def place(fig, path, box):
        if not Path(path).exists():
            fig.text(0.5, box[1] + box[3] / 2, f"[missing: {path}]", ha="center", color=GREY); return
        im = mpimg.imread(path); ar = im.shape[1] / im.shape[0]
        fw, fh = fig.get_size_inches()
        bw_in, bh_in = box[2] * fw, box[3] * fh
        dw_in = min(bw_in, bh_in * ar); dh_in = dw_in / ar
        wf, hf = dw_in / fw, dh_in / fh
        ax = fig.add_axes([box[0] + (box[2] - wf) / 2, box[1] + (box[3] - hf) / 2, wf, hf])
        ax.imshow(im); ax.axis("off")

    def imgbox(fig, path, x, top, w):
        if not Path(path).exists():
            return
        im = mpimg.imread(path); ar = im.shape[1] / im.shape[0]
        fw, fh = fig.get_size_inches(); hf = (w * fw / ar) / fh
        ax = fig.add_axes([x, top - hf, w, hf]); ax.imshow(im); ax.axis("off")

    with PdfPages(out) as pdf:
        for i, sl in enumerate(slides):
            fig = plt.figure(figsize=(13.333, 7.5)); k = sl["kind"]
            if k in ("title", "closing"):
                fig.patch.set_facecolor(NAVY); imgbox(fig, LOGO_W, 0.05, 0.93, 0.30)
                if k == "title":
                    imgbox(fig, MOUSE, 0.80, 0.22, 0.16)
                fig.text(0.07, 0.58, wrap(sl["title"], 30), fontsize=32, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    fig.text(0.07, 0.36, wrap(sl["sub"], 74), fontsize=15, color="#D7D2CB")
                if sl.get("footer"):
                    fig.text(0.07, 0.16, sl["footer"], fontsize=13, color="#9A958C")
                if sl.get("footer2"):
                    fig.text(0.07, 0.105, sl["footer2"], fontsize=13, color="#D7D2CB")
            elif k == "section":
                fig.patch.set_facecolor(TEAL); imgbox(fig, LOGO_W, 0.05, 0.93, 0.24)
                fig.text(0.08, 0.56, wrap(sl["title"], 34), fontsize=33, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    sub_y = 0.40 if "sub_y" not in sl else max(0.13, 1.0 - (sl["sub_y"] / slide_h))
                    fig.text(0.08, sub_y, wrap(sl["sub"], 78), fontsize=15, color="#EDDDDD")
                if sl.get("refs"):
                    refs_y = max(0.08, 1.0 - (sl.get("refs_y", sl.get("sub_y", 4.1) + 0.55) / slide_h))
                    fig.text(0.08, refs_y, wrap(sl["refs"], 102), fontsize=9.2, color="#D7D2CB")
            elif sl.get("full_fig"):
                fig.patch.set_facecolor("white")
                place(fig, sl["fig"], (0.01, 0.01, 0.98, 0.98))
            else:
                fig.patch.set_facecolor("white")
                fig.add_artist(plt.Rectangle((0, 0.975), 1, 0.025, color=TEAL, transform=fig.transFigure))
                yt = 0.93
                if sl.get("kicker"):
                    fig.text(0.05, 0.945, sl["kicker"].upper(), fontsize=12, color=TEAL, weight="bold"); yt = 0.90
                fig.text(0.05, yt, wrap(sl["title"], 70), fontsize=21, color=NAVY, weight="bold", va="top")
                if sl.get("fig"):
                    if sl.get("full_fig"):
                        place(fig, sl["fig"], (0.025, 0.035, 0.95, 0.78))
                    else:
                        place(fig, sl["fig"], (0.05, 0.18, 0.90, 0.60))
                if sl.get("take"):
                    fig.add_artist(plt.Rectangle((0, 0), 1, 0.12, color=PANEL, transform=fig.transFigure))
                    fig.text(0.05, 0.06, wrap(sl["take"], 120), fontsize=13, color=TEAL, weight="bold", va="center")
            if k != "title" and not sl.get("full_fig"):
                fig.text(0.955, 0.955, f"{i + 1} / {len(slides)}", ha="right", va="top", fontsize=11,
                         color=("white" if k in ("section", "closing") else GREY))
            pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def main():
    pptx = OUT / "haptic_brain_talk.pptx"; pdf = OUT / "haptic_brain_talk.pdf"
    build_evidence_ladder_figure(EVIDENCE)
    build_pptx(SLIDES, pptx); print("wrote", pptx)
    build_pdf(SLIDES, pdf); print("wrote", pdf)
    print(f"{len(SLIDES)} slides")


if __name__ == "__main__":
    main()

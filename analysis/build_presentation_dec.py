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
NAVY, TEAL, GREY, PANEL = "#2E2D29", "#8C1515", "#53565A", "#F4F4F4"   # Stanford: Black, Cardinal, Cool Grey, Fog

SLIDES = [
    dict(kind="title", title="Can vibrotactile stimulation drive brain clearance?",
         sub="Wearable vibrotactile stimulation, brain rhythms, and glymphatic clearance — rationale, plan, and first electrophysiology (in the mouse)",
         footer="Pardis Miri  ·  a Snyder Lab (Stanford) × Buzsáki Lab (NYU) collaboration",
         notes="The program question: can a wearable, vibrotactile stimulus engage brain rhythms in a way that helps the brain clear waste (the glymphatic system), with Alzheimer's relevance? I'll motivate it from the literature, lay out what to test, then show a first electrophysiology study testing the premise. I separate 'plausible mechanism' from 'proven' throughout. ~35 min — please interrupt."),

    # ===================== PART 1 — VISION =====================
    dict(kind="section", title="Part 1 · The vision — clearing the brain with vibrotactile stimulation"),
    dict(kind="content", kicker="the problem", title="Alzheimer's resists drugs — non-invasive neuromodulation is an open frontier", fig=f"{CF}/landscape.png",
         take="The strongest non-drug clinical evidence today is multidomain lifestyle (FINGER, US POINTER). Non-invasive stimulation is largely unproven — which is the opportunity.",
         notes="Framing the gap. Pharmacology for Alzheimer's has struggled; the most credible non-drug clinical evidence is multidomain lifestyle intervention (FINGER, US POINTER). Non-invasive neuromodulation — light, sound, touch — is an emerging but mostly unproven frontier. The question is what a wearable, vibrotactile approach could add, and we should hold it to the bar those lifestyle trials set."),
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
         take="CSF flow tracks NREM slow waves (Fultz 2019) and EEG delta (Hablitz 2019); neuronal dynamics actively direct CSF perfusion (Jiang-Xie–Kipnis 2024, Nature); human sleep clearance moves plasma Aβ/tau (Dagum 2026).",
         notes="Why targeting clearance via brain-state is reasonable. Glymphatic/CSF flow isn't passive: it's driven by neural activity, vascular pulsation, and especially sleep slow waves — Fultz 2019 (human, NREM slow waves drive CSF oscillations), Hablitz 2019 (influx tracks EEG delta), Mestre 2018 (arterial pulsation), and Jiang-Xie–Kipnis 2024 in Nature (neuronal ionic waves actively direct CSF perfusion). In humans, sleep clearance raises morning plasma Aβ/tau (Dagum 2026). So if stimulation can shape brain state, engaging clearance is mechanistically plausible — and this points to slow / sleep-band stimulation, not only 40 Hz."),
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
         take="GENUS / Tsai 2016 · Murdock 2024 (gamma → glymphatic) · Suk 2023 (40 Hz tactile) · Jiang-Xie–Kipnis 2024 (neural dynamics → CSF) · + Buzsáki / Soula (steady-state ≠ entrainment).",
         notes="The five anchors: the origin of sensory-gamma (Tsai 2016); the gamma→glymphatic bridge (Murdock 2024); the vibrotactile anchor (Suk 2023); the mechanism legitimizing brain-state stimulation of clearance (Jiang-Xie–Kipnis 2024); and the guardrail that keeps us rigorous (Buzsáki/Soula: a steady-state response is not entrainment). Full lit-review repository available on request."),
    dict(kind="closing", title="Thank you — questions",
         sub="Happy to go into any figure, the artifact controls, the parameter plan, or the next-round instrumentation.",
         notes="Anticipated questions. 'Is 50 Hz special or just strongest?' — strongest clean single-unit effect of the carriers tested; the LFP transient was largest at 26 Hz but that's the artifact-prone measure. 'Could it be arousal?' — possible, but frequency-specific (50 ≫ 26 at matched amplitude); an indirect sensory/state pathway isn't excluded. 'Why distrust the 50 Hz LFP?' — disconnected channels carry it at ~6× tissue. 'Is this a treatment?' — no; this is target-engagement evidence for a mechanism hypothesis, deliberately separated from any clinical claim."),
]


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
                txt(s, 1, 5.3, SW - 2, 0.8, sl["footer"], 16, color=rgb("#9A958C"))
        elif k == "section":
            bar(s, 0, 0, SW, SH, TL); img(s, LOGO_W, 0.55, 0.5, 2.9)
            txt(s, 1, 2.7, SW - 2, 1.5, sl["title"], 34, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                txt(s, 1, 4.1, SW - 2, 1.0, sl["sub"], 19, color=rgb("#EDDDDD"))
        else:
            bar(s, 0, 0, SW, 0.18, TL); y = 0.45
            if sl.get("kicker"):
                txt(s, 0.6, y, SW - 1.2, 0.4, sl["kicker"].upper(), 14, bold=True, color=TL); y += 0.45
            txt(s, 0.6, y, SW - 1.2, 1.1, sl["title"], 24, bold=True, color=NV)
            if sl.get("fig"):
                pic(s, sl["fig"], SW - 1.6, SH - (y + 1.4) - 0.9, top=y + 1.25)
            if sl.get("take"):
                bar(s, 0, SH - 0.9, SW, 0.9, PN)
                txt(s, 0.6, SH - 0.87, SW - 1.2, 0.85, sl["take"], 15, bold=True, color=TL, anchor=MSO_ANCHOR.MIDDLE)
        if sl.get("notes"):
            s.notes_slide.notes_text_frame.text = sl["notes"]
        if k != "title":
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
                    fig.text(0.07, 0.15, sl["footer"], fontsize=13, color="#9A958C")
            elif k == "section":
                fig.patch.set_facecolor(TEAL); imgbox(fig, LOGO_W, 0.05, 0.93, 0.24)
                fig.text(0.08, 0.56, wrap(sl["title"], 34), fontsize=33, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    fig.text(0.08, 0.40, wrap(sl["sub"], 64), fontsize=17, color="#EDDDDD")
            else:
                fig.patch.set_facecolor("white")
                fig.add_artist(plt.Rectangle((0, 0.975), 1, 0.025, color=TEAL, transform=fig.transFigure))
                yt = 0.93
                if sl.get("kicker"):
                    fig.text(0.05, 0.945, sl["kicker"].upper(), fontsize=12, color=TEAL, weight="bold"); yt = 0.90
                fig.text(0.05, yt, wrap(sl["title"], 70), fontsize=21, color=NAVY, weight="bold", va="top")
                if sl.get("fig"):
                    place(fig, sl["fig"], (0.05, 0.18, 0.90, 0.60))
                if sl.get("take"):
                    fig.add_artist(plt.Rectangle((0, 0), 1, 0.12, color=PANEL, transform=fig.transFigure))
                    fig.text(0.05, 0.06, wrap(sl["take"], 120), fontsize=13, color=TEAL, weight="bold", va="center")
            if k != "title":
                fig.text(0.955, 0.955, f"{i + 1} / {len(slides)}", ha="right", va="top", fontsize=11,
                         color=("white" if k in ("section", "closing") else GREY))
            pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def main():
    pptx = OUT / "haptic_brain_talk.pptx"; pdf = OUT / "haptic_brain_talk.pdf"
    build_pptx(SLIDES, pptx); print("wrote", pptx)
    build_pdf(SLIDES, pdf); print("wrote", pdf)
    print(f"{len(SLIDES)} slides")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Build the ~35-min talk (mixed-researcher audience) in TWO formats from one source:
  - presentation/haptic_brain_talk.pptx  (editable; open in PowerPoint/Keynote, or
    upload to Google Drive -> 'Open with Google Slides')
  - presentation/haptic_brain_talk.pdf   (renders images everywhere; safe fallback)

Register: scientifically literate but not neuroscience-specialist. Lead with precise
terminology, define only the neuro-specific terms, keep analogies as intuition.
Full narration is in the .pptx speaker notes; the PDF is the visual deck.
Uses real figures from results/ where they exist; schematics only for concepts.
"""
from __future__ import annotations
from pathlib import Path
import textwrap

OUT = Path("presentation"); OUT.mkdir(exist_ok=True)
F = "results/dec4"
CF = "presentation/concept_figs"   # schematic illustrations (build_concept_figures.py)
TTL = "analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png"
TRIAL = "results/dec3/13_Teaching_and_Methods/trial_window_diagram.png"
NAVY, TEAL, GREY, PANEL = "#2E2D29", "#8C1515", "#53565A", "#F4F4F4"   # Stanford: Black, Cardinal, Cool Grey, Fog

# ---------------------------------------------------------------- content
SLIDES = [
    dict(kind="title", title="Can we drive the brain through the skin?",
         sub="Single-unit and LFP responses to amplitude- and frequency-varied haptic stimulation in hippocampus & entorhinal cortex",
         footer="Pardis Miri  ·  Buzsáki Lab  ·  haptic-stimulation electrophysiology",
         notes="The question: does peripheral haptic stimulation produce a measurable, frequency-specific response in central circuits, and can it entrain neural activity? I'll define the few neuroscience-specific terms (LFP, single units, entrainment, spike sorting) as they come up; everything else assumes general research literacy. ~35 min — please interrupt."),
    dict(kind="content", title="Motivation: peripheral routes to non-invasive neuromodulation",
         take="Before targeting brain states via the skin, we need to know whether — and how — a cutaneous stimulus is represented centrally.",
         notes="There's growing interest in modulating brain state non-invasively through the periphery — the skin is the most accessible, lowest-risk interface. But the foundational, under-characterized question is whether peripheral haptic input produces a reliable, frequency-specific central response, and whether it can entrain endogenous activity (the precondition for 'driving' a rhythm). This study characterizes that response at two levels — field potentials and single neurons — and, importantly, the controls needed to interpret it."),
    dict(kind="content", title="Design: parametric haptic stimulation with simultaneous electrophysiology",
         fig=TRIAL,
         take="3 s ON / 3 s OFF blocks across four carrier frequencies (5/10/26/50 Hz) and three amplitudes; ~200 repeats/condition; dual-region linear-probe recording.",
         notes="A tactor delivers a sinusoidal vibration in 3 s ON / 3 s OFF blocks (figure shows the trial structure and the analysis windows we use). We vary carrier frequency — 5, 10, 26, 50 Hz — and amplitude, ~200 trials per condition, while recording extracellularly with linear silicon probes in two regions simultaneously. Each analysis window is referenced to the 1 s pre-stimulus baseline; 100 ms margins isolate onset/offset transients from sustained activity."),
    dict(kind="content", title="Three questions, increasing in strength of claim",
         take="(1) Is there a central response?   (2) Is it frequency-specific?   (3) Does it entrain neural activity (phase-locking)?",
         notes="Three levels: detection (any response?), tuning (specific to stimulus frequency/amplitude?), and entrainment (do neural signals phase-lock to the stimulus waveform?). Entrainment is the strongest claim and the one that would justify peripheral rhythm-driving — and, as you'll see, the one we could not test, for an instructive instrumentation reason."),

    dict(kind="section", title="Part 1 — Two readouts, two regions", sub="The minimum background, with the key methodological distinction"),
    dict(kind="content", title="Recording sites: hippocampus and entorhinal cortex", fig=f"{CF}/two_regions.png",
         take="Entorhinal cortex = principal cortical input to hippocampus; hippocampus = spatial/mnemonic processing. A connected circuit, recorded simultaneously.",
         notes="For non-neuroscientists: the hippocampus supports spatial navigation and episodic memory; the entorhinal cortex is its principal cortical input/output interface. They form a tightly coupled circuit, so recording both lets us ask not only whether each responds but whether they interact."),
    dict(kind="content", kicker="key methodological distinction", title="One electrode yields two readouts: LFP and single-unit activity", fig=f"{CF}/stadium.png",
         take="LFP = low-frequency aggregate field (synaptic/transmembrane currents of many cells). Spikes = action potentials of individual, sorted neurons. They differ in what can fake them.",
         notes="An extracellular electrode captures two regimes. The local field potential (LFP) is the low-frequency aggregate of synaptic and transmembrane currents from many neurons — large and easy to measure, but spatially non-specific and susceptible to volume-conducted or instrumental noise. Single-unit activity is the spiking of individual neurons, isolated by spike sorting — sparser and harder to extract, but each spike is a discrete, unambiguous biological event. Intuition: a stadium microphone hears both the crowd's aggregate roar (LFP) and individual shouts (spikes); the roar is loud but can be contaminated by, say, a PA hum, whereas an identified shout is real. This LFP-vs-single-unit distinction is the crux of the entire talk."),
    dict(kind="content", kicker="why it matters", title="Single units are the more conservative readout",
         take="A sorted action potential is a discrete biological event; the LFP can be mimicked by volume-conducted electrical artifact. Spikes constrain interpretation far more tightly.",
         notes="The asymmetry that drives the whole analysis: an electrical artifact can add power to the LFP at the stimulus frequency, but it cannot make a waveform-isolated, sorted neuron emit an action potential. So when we want to claim a genuine neural effect — rather than instrumental pickup — single-unit firing-rate changes are the evidence that survives scrutiny. Keep this asymmetry in mind; it resolves the central twist of the results."),

    dict(kind="section", title="Part 2 — Results"),
    dict(kind="content", kicker="finding 1", title="A robust LFP response — transition-weighted, not a sustained oscillation",
         fig=f"{F}/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png",
         take="The broadband LFP responds at stimulus onset/offset (an evoked transient), not as a sustained rhythm at the carrier frequency.",
         notes="The broadband LFP shows a clear, amplitude-graded response — but it is concentrated at the ON and OFF transitions: an evoked transient, not a sustained oscillation at the drive frequency. Conceptually it's the difference between responding to the event of stimulation versus tracking its rhythm. So 'there is a response' — but not yet frequency-following."),
    dict(kind="content", kicker="definition", title="Entrainment, defined: phase-locking of neural activity to the stimulus", fig=f"{CF}/entrainment.png",
         take="Entrainment = endogenous activity aligns to the stimulus phase (a driven-oscillator relationship). The strong claim — and the most useful, if true.",
         notes="Entrainment here means neural activity phase-locks to the periodic stimulus — a driven-oscillator relationship, analogous to resonantly pumping a pendulum. If these circuits entrained to a 50 Hz drive, we'd see neural power and spike timing organized at 50 Hz. That is the result that would justify driving a brain rhythm from the periphery. So: is there frequency-following?"),
    dict(kind="content", kicker="finding 2", title="No frequency-following in hippocampus at any carrier",
         fig=f"{F}/05_Frequency_Spectral/spectral_slope_itpc_dec4.png",
         take="No narrowband spectral peak above the 1/f background, and inter-trial phase consistency at chance — across 5/10/26/50 Hz, replicated across sessions.",
         notes="The test: frequency-following predicts a narrowband peak at the carrier above the 1/f aperiodic background, and above-chance inter-trial phase clustering (ITPC). We see neither, at any carrier, replicated across two sessions on the same probe. So no power- or phase-based frequency-following in hippocampus."),
    dict(kind="content", kicker="finding 3", title="Entorhinal cortex shows an amplitude-graded 50 Hz LFP increase",
         fig=f"{F}/05_Frequency_Spectral/driven_power_change_by_analysis_group.png",
         take="A narrowband 50 Hz LFP power increase, scaling with amplitude — the candidate entrainment signal. But the LFP is exactly the readout most vulnerable to artifact.",
         notes="In entorhinal cortex there is a narrowband 50 Hz LFP power increase that scales with stimulus amplitude — superficially the entrainment signal we want. But recall the asymmetry: the LFP is precisely the readout that electrical pickup can mimic. So before interpreting it as neural, we have to exclude a stimulator-coupled artifact."),
    dict(kind="content", kicker="the confound", title="The confound: stimulator-coupled 50 Hz electrical artifact", fig=f"{CF}/trap.png",
         take="An electromechanical actuator can inject a 50 Hz electrical artifact directly into the recording — indistinguishable from a neural 50 Hz in the LFP alone.",
         notes="The actuator and its drive electronics can couple a 50 Hz signal into the recording — volume-conducted through tissue or via the wiring. In the LFP that is indistinguishable from a neural 50 Hz oscillation (the PA-hum case of the stadium analogy). We need a discriminator the artifact cannot fool."),
    dict(kind="content", kicker="finding 3, controlled", title="Disconnected channels carry the 50 Hz — so it is largely pickup",
         fig=f"{F}/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png",
         take="QC-failed/disconnected electrodes (which cannot record neural signal) show ~6× more 50 Hz than in-tissue channels. The entorhinal 50 Hz LFP is substantially artifact.",
         notes="The discriminator: broken/disconnected channels cannot record neural activity but still act as antennas for electrical pickup. If they carry the 50 Hz, it is instrumental, not neural. They do — ~6× the in-tissue channels — so the entorhinal 50 Hz LFP is largely (not necessarily entirely) stimulator artifact. The headline LFP result is mostly the machine. This is the central twist."),
    dict(kind="content", kicker="finding 4 — the robust result", title="Frequency-specific single-unit rate modulation at 50 Hz",
         fig=f"{F}/11_Spikes/spike_onoff_cross_dataset.png",
         take="Sorted single units change firing rate during 50 Hz / high-amplitude stimulation, in both regions — an effect electrical pickup cannot produce.",
         notes="Now the artifact-resistant readout: sorted single units change firing rate during the high-amplitude 50 Hz condition, in both regions, and far more than at lower carriers. Because pickup cannot drive a sorted neuron's spike train, this is the clean evidence. Question 2 — frequency specificity — is answered: 50 Hz is privileged, and the Dec-3 single-unit null is explained (Dec 3 only tested 5/26 Hz, where there is no effect)."),
    dict(kind="content", kicker="controls", title="Controls: high-pass separation + autocorrelogram / ISI screens",
         fig=f"{F}/11_Spikes/unit87_acg_artifact_screen.png",
         take="Spikes are detected >~300 Hz (50 Hz pickup is removed pre-detection); units show no stimulus-locked 50 Hz periodicity and no ON-rise in refractory violations.",
         notes="Two controls against residual artifact. (1) Spike detection operates on the >~300 Hz band, so the 50 Hz LFP/pickup is filtered out before a spike is detected. (2) Were pickup nonetheless injecting spurious spikes at 50 Hz, the spike-train autocorrelogram would develop 20 ms periodicity during stimulation — it does not, and is identical ON vs OFF; refractory-violation rates also do not rise during ON. So the rate modulation is genuine single-unit activity. (Unit 87, the most exposed up-going unit, passes both screens.)"),
    dict(kind="content", kicker="finding 5", title="Region-specific, bidirectional modulation — not a passive relay",
         fig=f"{F}/11_Spikes/spike_50hz_interpretation.png",
         take="Hippocampus: a driven-up subset. Entorhinal cortex: net-suppressed. Opposite transformations of identical input argue for active, circuit-specific processing.",
         notes="The two regions transform the same input in opposite directions: a hippocampal subset increases firing (a few strongly driven units carry the positive mean), while entorhinal cortex is net-suppressed (~10/15 units down). Opposite-signed responses to identical input are inconsistent with a passive, volume-conducted relay and consistent with circuit-specific processing. The suppression is also intrinsically artifact-resistant — additive pickup adds, it cannot remove, spikes."),
    dict(kind="content", kicker="finding 6", title="No clear cross-regional coordination at 50 Hz",
         fig=f"{F}/11_Spikes/coordination_50hz_pooled.png",
         take="LFP–LFP coherence rises, but the artifact-resistant cross-region spike–field measure does not — parsimoniously a shared signal, not interaction.",
         notes="Do the regions interact at 50 Hz? LFP–LFP coherence increases — but a shared pickup inflates coherence, so that's the artifact-prone measure. The spike–field measure (one region's spikes vs the other region's LFP phase), which a shared LFP artifact cannot fake as easily, does not increase with stimulation. So the apparent coupling is most parsimoniously a shared signal, not genuine coordination."),

    dict(kind="section", title="Part 3 — The entrainment question, and an instrumentation limit"),
    dict(kind="content", kicker="the limitation", title="Entrainment was untestable — a measurement gap, not a null",
         take="Phase-locking to the stimulus requires a recorded, time-aligned stimulus-phase reference. We lacked one — so entrainment is untestable here, not negative.",
         notes="Critically: testing entrainment (phase-locking) requires a time-aligned reference for the stimulus phase. We did not record a usable one — so 'no entrainment shown' is a measurement gap, not evidence of absence. Distinguishing 'untestable' from 'tested-and-negative' is essential for honest claims. (Note: the power/periodicity negatives above are real and testable; only the phase-locking claim is gated by the missing reference.)"),
    dict(kind="content", kicker="diagnosis", title="The digital sync channel never captured the carrier",
         fig=TTL,
         take="The recorded sync line updated at ~4 Hz, independent of carrier (identical pulse counts at 5 vs 26 Hz; ~78 expected at 26 Hz). No phase reference exists in the data.",
         notes="I verified this directly from the raw digital stream: the channel intended as a sync updated at ~4 Hz irrespective of carrier (the same ~6 pulses/trial for 5 and 26 Hz; ~78 expected at 26 Hz), never sustained a run at the carrier period anywhere in the 3 h session, and was misaligned with the trial schedule. It is undersampled and decoupled from the stimulus — so phase is unrecoverable. Sampling intuition: a ~4 Hz observer cannot resolve a 26 Hz oscillation."),
    dict(kind="content", kicker="the fix", title="Fix: redundant, clock-shared stimulus references", fig=f"{CF}/fix.png",
         take="Firmware per-cycle sync + a transduced force/accelerometer signal + a drive-signal copy, all on the acquisition clock — cross-checked, with pre-session verification.",
         notes="The fix is design, not analysis: record the stimulus three ways on the acquisition clock — a firmware-emitted per-cycle marker (now implemented), a transduced measurement of the delivered vibration (PVDF or accelerometer, which also verifies delivery and captures mechanical phase), and a copy of the drive signal — then cross-validate, plus a short verification recording before the session. With redundancy on a shared clock, any single failed reference is caught immediately rather than months later in analysis."),

    dict(kind="content", kicker="summary", title="Summary",
         take="Genuine central response to haptic stimulation; cleanest evidence is frequency-specific, region-specific single-unit modulation at 50 Hz; the 50 Hz LFP is largely artifact; entrainment untestable here.",
         notes="To summarize: (1) peripheral haptic stimulation produces a genuine central response; (2) the most rigorous evidence is frequency-specific, region-specific single-unit rate modulation at 50 Hz / high amplitude — driven-up subset in hippocampus, net suppression in entorhinal cortex; (3) the entorhinal 50 Hz LFP is largely stimulator artifact, established by the disconnected-channel control; (4) entrainment was untestable for want of a stimulus-phase reference — a fixable instrumentation gap, not a biological null. Caveats: single animal; modest responder fraction; an arousal/indirect-pathway contribution can't be fully excluded."),
    dict(kind="content", kicker="implications", title="Implications & next step",
         take="Establishes a measurable central readout of peripheral haptic input and the controls to interpret it; with the instrumentation fix, entrainment becomes directly testable.",
         notes="Implications: this establishes that peripheral haptic stimulation has a measurable, frequency-specific central signature — and, equally important, the methodological controls needed to separate neural signal from stimulator artifact (the disconnected-channel test, the high-pass/ACG/ISI spike screens). With the shared-clock stimulus recording, entrainment becomes directly testable — the gateway question for closed-loop peripheral neuromodulation."),
    dict(kind="closing", title="Thank you — questions",
         sub="Happy to go into any figure, the artifact controls, or the next-round instrumentation.",
         notes="Anticipated questions. 'Is 50 Hz special or just strongest?' — strongest clean single-unit effect of the carriers tested; the LFP transient was largest at 26 Hz but that's the artifact-prone/non-specific measure. 'Could it be arousal?' — possible, but it's frequency-specific (50 ≫ 26 at matched amplitude), which argues against pure intensity-driven arousal; an indirect sensory/state pathway is not excluded. 'Why distrust the 50 Hz LFP?' — disconnected channels carry it at ~6× tissue levels."),
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

    def pic(s, path, maxw, maxh, top):
        if not Path(path).exists():
            txt(s, 1, top, SW - 2, 1, f"[missing: {path}]", 14, color=GR); return
        w, h = Image.open(path).size; ar = w / h
        iw, ih = maxw, maxw / ar
        if ih > maxh:
            ih, iw = maxh, maxh * ar
        s.shapes.add_picture(str(path), Inches((SW - iw) / 2), Inches(top), width=Inches(iw), height=Inches(ih))

    for sl in slides:
        s = prs.slides.add_slide(BL); k = sl["kind"]
        if k in ("title", "closing"):
            bar(s, 0, 0, SW, SH, NV); bar(s, 0, 5.0, SW, 0.08, TL)
            txt(s, 1, 2.0 if k == "title" else 3.0, SW - 2, 1.6, sl["title"], 34, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                txt(s, 1, 3.7 if k == "title" else 4.2, SW - 2, 1.2, sl["sub"], 18, color=rgb("#D7D2CB"))
            if sl.get("footer"):
                txt(s, 1, 5.3, SW - 2, 0.8, sl["footer"], 16, color=rgb("#9A958C"))
        elif k == "section":
            bar(s, 0, 0, SW, SH, TL)
            txt(s, 1, 2.7, SW - 2, 1.5, sl["title"], 36, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
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
        img = mpimg.imread(path); ar = img.shape[1] / img.shape[0]
        fw, fh = fig.get_size_inches()
        bw_in, bh_in = box[2] * fw, box[3] * fh
        dw_in = min(bw_in, bh_in * ar); dh_in = dw_in / ar
        wf, hf = dw_in / fw, dh_in / fh
        ax = fig.add_axes([box[0] + (box[2] - wf) / 2, box[1] + (box[3] - hf) / 2, wf, hf])
        ax.imshow(img); ax.axis("off")

    with PdfPages(out) as pdf:
        for sl in slides:
            fig = plt.figure(figsize=(13.333, 7.5)); k = sl["kind"]
            if k in ("title", "closing"):
                fig.patch.set_facecolor(NAVY)
                fig.text(0.07, 0.58, wrap(sl["title"], 34), fontsize=32, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    fig.text(0.07, 0.38, wrap(sl["sub"], 78), fontsize=15, color="#D7D2CB")
                if sl.get("footer"):
                    fig.text(0.07, 0.16, sl["footer"], fontsize=13, color="#9A958C")
            elif k == "section":
                fig.patch.set_facecolor(TEAL)
                fig.text(0.08, 0.56, wrap(sl["title"], 32), fontsize=33, color="white", weight="bold", va="center")
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
            pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def main():
    pptx = OUT / "haptic_brain_talk.pptx"; pdf = OUT / "haptic_brain_talk.pdf"
    build_pptx(SLIDES, pptx); print("wrote", pptx)
    build_pdf(SLIDES, pdf); print("wrote", pdf)
    print(f"{len(SLIDES)} slides")


if __name__ == "__main__":
    main()

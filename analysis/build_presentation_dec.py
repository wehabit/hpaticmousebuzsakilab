#!/usr/bin/env python
"""Build the 35-min non-neuroscientist talk in TWO formats from one source of truth:
  - presentation/haptic_brain_talk.pptx  (editable; open in PowerPoint/Keynote, or
    upload to Google Drive -> 'Open with Google Slides')
  - presentation/haptic_brain_talk.pdf   (renders images everywhere; safe fallback)

Assertion-evidence style; full narration (with analogies) is in the .pptx speaker
notes. The PDF is the visual deck only.
"""
from __future__ import annotations
from pathlib import Path
import textwrap

OUT = Path("presentation"); OUT.mkdir(exist_ok=True)
F = "results/dec4"
CF = "presentation/concept_figs"   # schematic illustrations (build_concept_figures.py)
TTL = "analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png"
NAVY, TEAL, GREY, PANEL = "#1A1A2E", "#1C6E8C", "#555555", "#F2F5F7"

# ---------------------------------------------------------------- content
SLIDES = [
    dict(kind="title", title="Can we talk to the brain through the skin?",
         sub="What happens in the brain when we buzz the body at different rhythms",
         footer="Pardis Miri  ·  Buzsáki Lab  ·  haptic-stimulation electrophysiology",
         notes="Welcome. Today: a simple-sounding question with a surprisingly subtle answer. If you buzz someone's skin, does it actually change what their brain is doing — and can the brain 'tune in' to the rhythm of the buzz? No neuroscience background needed; I'll build up every idea with an analogy. (~35 min, stop me with questions.)"),
    dict(kind="content", title="The dream: wearables that gently 'nudge' the brain through touch",
         take="To build that, we first have to answer a basic question: does a buzz on the body actually reach and change the brain?",
         notes="Big picture first. There's huge interest in wearables that touch your skin to shift a brain state — to help you sleep, focus, calm down, or aid therapy after injury. The skin is the easiest, safest door to the nervous system. But before any of that, we need the unglamorous groundwork: if I buzz the body, (1) does the brain even notice, (2) does it matter how FAST I buzz, and (3) can the brain lock onto the rhythm of the buzz? That third one — 'marching in step' with the stimulus — is the holy grail, because that's how you'd drive a brain rhythm on purpose."),
    dict(kind="content", title="The experiment, in one picture", fig=f"{CF}/experiment.png",
         take="Buzz the body in 3-second bursts at different speeds; listen to the brain at the same time; repeat 200×.",
         notes="Here's the whole setup in plain terms. We put a little vibrating motor — a 'tactor', like the buzz in your phone — on the body. We buzz it for 3 seconds, then rest 3 seconds, over and over. We try different buzz SPEEDS: 5, 10, 26, and 50 buzzes per second. And different strengths. While that happens, we listen to the brain with fine electrodes. Then we ask: what changed in the brain during the buzz versus the rest? [Tip: drop a setup photo here.]"),
    dict(kind="content", title="Three questions",
         take="(1) Does the brain notice?    (2) Does the buzz SPEED matter?    (3) Does the brain march in step with the buzz?",
         notes="Keep these three questions in your head — the whole talk answers them. One: does the brain register the buzz at all? Two: does it care how fast we buzz — is 50/sec different from 26/sec? Three, the big one: does the brain 'entrain' — literally oscillate in lockstep with the buzz, like marching to a drumbeat? Spoiler: yes, yes-ish, and 'we couldn't fully test it' — and WHY we couldn't is one of the most useful things we learned."),

    dict(kind="section", title="Part 1 — How do you 'listen' to a brain?", sub="Two ideas you need, both with analogies"),
    dict(kind="content", title="We listened in two neighboring brain regions", fig=f"{CF}/two_regions.png",
         take="Hippocampus = the brain's inner GPS & memory.   Entorhinal cortex = its main input hub. Two listening posts.",
         notes="We recorded from two spots that talk to each other: the hippocampus — think of it as the brain's inner GPS and memory-maker — and right next to it the entorhinal cortex, which is the hippocampus's main inbox, where a lot of sensory information arrives. So: two listening posts in a circuit that handles where-you-are and what-just-happened. Don't worry about the names; just 'two connected regions.'"),
    dict(kind="content", kicker="concept · analogy", title="THE key idea: a brain recording has two very different signals", fig=f"{CF}/stadium.png",
         take="Stadium analogy → the CROWD MURMUR (the field potential) vs. INDIVIDUAL VOICES (single neurons firing).",
         notes="This is the single most important idea in the talk. Imagine a microphone over a packed stadium. You hear TWO things. First, the low ROAR of the whole crowd — that's the 'field potential' (LFP): the blended, slow electrical hum of thousands of cells. Second, individual people SHOUTING — sharp, brief, distinct. Those are 'spikes': single neurons firing, each a crisp ~1-millisecond blip. The crowd murmur is easy to hear but vague; the individual voices are harder to pick out but tell you exactly who said what. We use BOTH — and the difference between them is the whole plot."),
    dict(kind="content", kicker="concept", title="Why single neurons are the gold standard",
         take="A real neuron firing is unambiguous — much harder for noise or equipment to fake than the crowd hum.",
         notes="Why care about the hard-to-hear individual voices? Because they're trustworthy. The crowd murmur can be contaminated by background noise — a passing truck, a buzzing speaker. But an identified shout is a real event from a real person. Same in the brain: a sorted single-neuron spike is a genuine cell, and it's much harder for the equipment's electrical noise to fake one. Hold that thought; it becomes the hero of the story."),

    dict(kind="section", title="Part 2 — What the brain actually did"),
    dict(kind="content", kicker="finding 1 · analogy", title="Yes — the brain notices the buzz. But it reacts to the START and STOP",
         fig=f"{F}/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png",
         take="Like a doorbell: the brain responds to the EVENT of the buzz turning on/off — not by humming along with it.",
         notes="First result. The crowd-murmur signal clearly changes when we buzz — so yes, the brain notices. But HOW: it mostly reacts to the buzz turning ON and OFF, not by settling into its rhythm. Analogy: a doorbell. Your attention spikes when it RINGS and when it STOPS, but you don't start vibrating at the doorbell's pitch. So the brain registers the event, but isn't obviously 'tuning in.'"),
    dict(kind="content", kicker="concept · analogy", title="'Marching in step' has a name: entrainment", fig=f"{CF}/entrainment.png",
         take="Pushing a swing in rhythm → if the brain entrains, its own waves line up with the buzz's beat.",
         notes="The dream is 'entrainment': the brain's own waves locking onto the buzz's rhythm. Analogy: pushing a swing. If you push exactly in time, it goes higher and higher — your rhythm drives its rhythm. If the brain entrained to a 50-per-second buzz, we'd see brain activity ticking at 50 per second. That would mean you can DIAL IN a brain rhythm from the skin. So: does the brain hum along at the buzz frequency?"),
    dict(kind="content", kicker="finding 2", title="The hippocampus does NOT hum along — at any buzz speed",
         fig=f"{F}/05_Frequency_Spectral/spectral_slope_itpc_dec4.png",
         take="No matter the buzz speed (5–50/sec), we see no matching brain rhythm above the normal background.",
         notes="If the brain hummed at the buzz speed, we'd see a sharp spike of energy at that exact frequency, above the brain's normal background. We don't — at any speed. So in the hippocampus, no frequency-following: it notices the buzz but doesn't oscillate in step. And this replicated across two sessions. The swing isn't catching the push."),
    dict(kind="content", kicker="finding 3", title="Plot twist: the OTHER region shows a 50-per-second signal",
         fig=f"{F}/05_Frequency_Spectral/driven_power_change_by_analysis_group.png",
         take="In the entorhinal region a 50 Hz signal appears in the crowd murmur — and it grows with buzz strength. Exciting!",
         notes="Now it gets interesting. In the entorhinal inbox, a signal at exactly 50 per second DOES show up in the crowd murmur, and it grows as we buzz harder. We were excited — maybe THIS region entrains at 50! But there's a trap, and a careful scientist has to check it. Let me teach you the trap."),
    dict(kind="content", kicker="concept · analogy", title="The trap: the machine has its OWN electrical hum", fig=f"{CF}/trap.png",
         take="A microphone can pick up the speaker's buzz, not just the crowd. Electrical equipment leaks its own signal.",
         notes="Analogy: you're recording the crowd, but the stadium PA speaker hums at 50 Hz and your mic picks up THAT. Now your recording shows a clean 50 Hz — but it's the speaker, not the crowd. Same risk: the buzzing motor and its electronics can leak a 50-per-second electrical signal into our wires. That would look like a '50 Hz brain signal' but be pure equipment artifact. How do you tell brain from machine? We found a clean test."),
    dict(kind="content", kicker="finding 3b · the killer test", title="That 50 Hz is mostly the machine — the dead-electrode test proves it",
         fig=f"{F}/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png",
         take="Broken electrodes that CAN'T hear neurons still pick up the 50 Hz — ~6× more than the live ones. So it's pickup.",
         notes="The trick: some electrodes were broken/disconnected — they physically can't hear neurons. Dead microphones. If a dead mic still records a loud 50 Hz, that CANNOT be the brain — only the machine's hum leaking in. And that's what we saw: the dead electrodes picked up about SIX TIMES MORE 50 Hz than the live, in-brain ones (right panel, red). Verdict: the entorhinal '50 Hz brain wave' is largely equipment pickup. The crowd murmur fooled us — good thing we checked."),
    dict(kind="content", kicker="finding 4 · the headline", title="The real result: individual neurons change their firing at 50 Hz",
         fig=f"{F}/11_Spikes/spike_onoff_cross_dataset.png",
         take="Single neurons fire differently during the 50 Hz buzz — in BOTH regions. Equipment hum can't fake a neuron firing.",
         notes="Now the hero arrives: the individual voices. Tracking single, identified neurons, they genuinely change how much they fire during the strong 50-per-second buzz — in BOTH regions. Why trustworthy when the crowd murmur wasn't? The machine's hum can make a recording wiggle, but it can't make a real, identified neuron decide to fire. This is the clean result: 50 Hz, strong buzz, is where the brain's actual cells respond — far more than at slower speeds. So question 2 — does speed matter? — yes: 50 is special."),
    dict(kind="content", kicker="concept · analogy", title="How do we KNOW it's neurons and not the machine? Two filters",
         fig=f"{F}/11_Spikes/unit87_acg_artifact_screen.png",
         take="(1) Strip out the slow hum to find the sharp spikes.   (2) Check the neuron isn't 'ticking like a clock' at 50 Hz.",
         notes="Two safeguards. First: to find spikes we throw away the slow part and keep only the fast, sharp blips — like turning up the treble to hear finger-snaps over a rumble. The 50 Hz hum is a slow rumble, so it's gone before we ever count a spike. Second: if the hum WERE sneaking in as fake spikes, the neuron would look like a metronome — ticking exactly every 1/50th of a second. We checked: NO such 50 Hz ticking, and it looks the same during buzz and rest. So these are real neurons. (This was the unit we scrutinized hardest; it passed.)"),
    dict(kind="content", kicker="finding 4b · analogy", title="Same buzz, opposite reactions — the brain is PROCESSING, not echoing",
         fig=f"{F}/11_Spikes/spike_50hz_interpretation.png",
         take="One region revs a subset of cells UP; the other quiets DOWN. A passive echo would look the same everywhere.",
         notes="The satisfying part: the two regions react to the SAME buzz in OPPOSITE directions — hippocampus revs a subset up, entorhinal mostly quiets down. Analogy: two people hearing the same news, one excited, one goes quiet. That difference means they're actively PROCESSING the input, not passively echoing it. (Bonus: the quieting-down is itself strong evidence it's real — equipment pickup can only ADD fake blips, it can't make a neuron go silent.)"),
    dict(kind="content", kicker="finding 5 · analogy", title="Do the two regions 'work together' at 50 Hz? Not clearly",
         fig=f"{F}/11_Spikes/coordination_50hz_pooled.png",
         take="Two orchestras can SOUND synced because of a hallway metronome (a shared hum) — not because they play together.",
         notes="Do they coordinate, like partners in a conversation? The crowd murmur made them look in sync. But analogy: two orchestras in separate rooms can SEEM synchronized just because both hear the same metronome in the hallway — not because they listen to each other. The trustworthy test is whether the actual MUSICIANS (neurons) time to the other room — they don't, not more during the buzz. So the apparent 'sync' is the shared hum (that 50 Hz pickup again), not teamwork. Honest answer: no clear coordination."),

    dict(kind="section", title="Part 3 — The one thing we couldn't test (and how we fix it)"),
    dict(kind="content", kicker="the honest limit · analogy", title="We could NOT test 'marching in step' — and it's not the brain's fault",
         take="It's like judging whether a dancer is on-beat when you forgot to record the music. The reference was missing.",
         notes="Back to the holy-grail question — does the brain entrain? We genuinely could not test it, for an honest reason. Analogy: to judge whether a dancer is on the beat, you need to have recorded the MUSIC. We recorded the dancer (the brain) beautifully — but never properly recorded the music (the exact timing of the buzz). No beat, no scoring. So 'we didn't show entrainment' is NOT 'the brain failed to entrain' — it's 'we were missing the measurement.'"),
    dict(kind="content", kicker="the diagnosis", title="Why: the wire meant to record the buzz never captured it",
         fig=TTL,
         take="It updated ~4×/sec while the tactor buzzed 26×/sec — like checking a hummingbird's wings 4 times a second.",
         notes="I proved this from the data. The signal that should have marked each buzz cycle updated only ~4 times a second — but the tactor buzzed 26 times a second. Analogy: tracking a hummingbird's wingbeats by glancing 4 times a second — between glances the wings flapped 6 times; you can't recover the motion. (Top: the actual recorded line, slow and irregular. Middle: what a real 26-per-second buzz looks like. Bottom: the gaps are ~6× too long.) So the 'music track' was effectively blank. That one missing signal is the main limitation of the study."),
    dict(kind="content", title="The fix is concrete — next round records the buzz properly", fig=f"{CF}/fix.png",
         take="A per-cycle marker from the firmware + a tiny force sensor that measures the ACTUAL vibration, on the same clock.",
         notes="The good news: a wiring problem, not a dead end, and we've designed the fix. Next round we record the music three ways at once, all on the brain's clock: (1) a clean marker the buzzer's software emits once per cycle; (2) a tiny force sensor between tactor and skin measuring the ACTUAL vibration — proving the buzz happened and giving its exact beat; (3) a copy of the drive signal as backup. Plus a 2-minute test recording to CONFIRM it works before real data — the check that would have caught this. Then entrainment is directly testable."),

    dict(kind="content", kicker="takeaways", title="The big picture, in plain words",
         take="Buzzing the body DOES change the brain — most clearly as single-neuron activity at 50 Hz — but 'driving a brain rhythm' isn't shown yet.",
         notes="Three plain-language takeaways. ONE: a buzz on the body really does change the brain — real, not trivial. TWO: the most trustworthy effect is at the level of individual neurons, specifically at the fast 50-per-second buzz, and the two regions handle it differently — active processing, not a passive echo. THREE: the flashy 'brain wave at 50 Hz' was mostly the machine's hum, and whether the brain truly 'marches in step' we couldn't test yet — because the stimulus timing wasn't recorded. We know exactly how to fix that."),
    dict(kind="content", kicker="the road ahead", title="Why it matters",
         take="If we can verify entrainment, we move toward wearables that gently and non-invasively steer brain states through touch.",
         notes="Why should a non-neuroscientist care? If the next round shows the brain CAN be entrained through the skin, that's a foundation for safe, non-invasive wearables that nudge brain states — for sleep, focus, calm, rehabilitation — without surgery or drugs. This study did the honest groundwork: found a real neural effect, caught itself when a result was actually equipment noise, and pinpointed the one measurement we must add to ask the biggest question properly."),
    dict(kind="closing", title="Thank you — questions?",
         sub="Happy to dig into any figure, the analogies, or the next-round design.",
         notes="Likely questions: 'Is 50 Hz special or just strongest?' (strongest clean single-unit effect of the speeds tested). 'Could it be arousal — they just felt a strong buzz?' (possible; but it's frequency-specific — 50 beats 26 at the same strength — which argues against pure arousal). 'Why not trust the 50 Hz brain wave?' (dead electrodes picked it up → largely machine pickup)."),
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
            txt(s, 1, 2.0 if k == "title" else 3.0, SW - 2, 1.6, sl["title"], 36, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                txt(s, 1, 3.6 if k == "title" else 4.2, SW - 2, 1.0, sl["sub"], 19, color=rgb("#BFD0DA"))
            if sl.get("footer"):
                txt(s, 1, 5.3, SW - 2, 0.8, sl["footer"], 16, color=rgb("#9AA8B5"))
        elif k == "section":
            bar(s, 0, 0, SW, SH, TL)
            txt(s, 1, 2.7, SW - 2, 1.5, sl["title"], 38, bold=True, color=WH, anchor=MSO_ANCHOR.MIDDLE)
            if sl.get("sub"):
                txt(s, 1, 4.1, SW - 2, 1.0, sl["sub"], 20, color=rgb("#D8E8EE"))
        else:
            bar(s, 0, 0, SW, 0.18, TL); y = 0.45
            if sl.get("kicker"):
                txt(s, 0.6, y, SW - 1.2, 0.4, sl["kicker"].upper(), 14, bold=True, color=TL); y += 0.45
            txt(s, 0.6, y, SW - 1.2, 1.1, sl["title"], 26, bold=True, color=NV)
            if sl.get("fig"):
                pic(s, sl["fig"], SW - 1.6, SH - (y + 1.4) - 0.9, top=y + 1.25)
            if sl.get("take"):
                bar(s, 0, SH - 0.85, SW, 0.85, PN)
                txt(s, 0.6, SH - 0.82, SW - 1.2, 0.8, sl["take"], 16, bold=True, color=TL, anchor=MSO_ANCHOR.MIDDLE)
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

    def place(fig, path, box):  # box = (x0,y0,w,h) fig-fraction
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
                fig.text(0.07, 0.58, wrap(sl["title"], 34), fontsize=34, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    fig.text(0.07, 0.40, wrap(sl["sub"], 70), fontsize=17, color="#BFD0DA")
                if sl.get("footer"):
                    fig.text(0.07, 0.18, sl["footer"], fontsize=13, color="#9AA8B5")
            elif k == "section":
                fig.patch.set_facecolor(TEAL)
                fig.text(0.08, 0.56, wrap(sl["title"], 30), fontsize=34, color="white", weight="bold", va="center")
                if sl.get("sub"):
                    fig.text(0.08, 0.40, wrap(sl["sub"], 60), fontsize=18, color="#E2F0F4")
            else:
                fig.patch.set_facecolor("white")
                fig.add_artist(plt.Rectangle((0, 0.975), 1, 0.025, color=TEAL, transform=fig.transFigure))
                yt = 0.93
                if sl.get("kicker"):
                    fig.text(0.05, 0.945, sl["kicker"].upper(), fontsize=12, color=TEAL, weight="bold"); yt = 0.90
                fig.text(0.05, yt, wrap(sl["title"], 64), fontsize=22, color=NAVY, weight="bold", va="top")
                if sl.get("fig"):
                    place(fig, sl["fig"], (0.05, 0.17, 0.90, 0.62))
                if sl.get("take"):
                    fig.add_artist(plt.Rectangle((0, 0), 1, 0.11, color=PANEL, transform=fig.transFigure))
                    fig.text(0.05, 0.055, wrap(sl["take"], 110), fontsize=14, color=TEAL, weight="bold", va="center")
            pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)


def main():
    pptx = OUT / "haptic_brain_talk.pptx"; pdf = OUT / "haptic_brain_talk.pdf"
    build_pptx(SLIDES, pptx); print("wrote", pptx)
    build_pdf(SLIDES, pdf); print("wrote", pdf)
    print(f"{len(SLIDES)} slides")


if __name__ == "__main__":
    main()

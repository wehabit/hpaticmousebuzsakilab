#!/usr/bin/env python
"""Build a 35-min, non-neuroscientist presentation (.pptx) from the project figures.

Assertion-evidence style: each slide's title is a plain-language claim, the body is
one figure, and the full narration (with analogies) lives in the speaker notes.
Output: presentation/haptic_brain_talk.pptx  (open/edit in PowerPoint/Keynote/Slides)
"""
from __future__ import annotations
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

OUT = Path("presentation"); OUT.mkdir(exist_ok=True)
NAVY = RGBColor(0x1A, 0x1A, 0x2E)
ACCENT = RGBColor(0x1C, 0x6E, 0x8C)   # teal
GOLD = RGBColor(0xB5, 0x86, 0x00)
GREY = RGBColor(0x55, 0x55, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
SW, SH = 13.333, 7.5
BLANK = prs.slide_layouts[6]


def txt(slide, x, y, w, h, text, size, *, bold=False, color=NAVY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.alignment = align
        r = p.runs[0]; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
        r.font.name = "Calibri"
    return tb


def bar(slide, x, y, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background()
    return s


def picture_fit(slide, path, max_w, max_h, top):
    """center a picture horizontally, fit within max_w x max_h, placed at given top."""
    if not Path(path).exists():
        txt(slide, 1, top, SW - 2, 1, f"[missing figure: {path}]", 14, color=GREY); return
    w, h = Image.open(path).size
    ar = w / h
    iw, ih = max_w, max_w / ar
    if ih > max_h:
        ih, iw = max_h, max_h * ar
    left = (SW - iw) / 2
    slide.shapes.add_picture(str(path), Inches(left), Inches(top), width=Inches(iw), height=Inches(ih))


def content(title, *, fig=None, takeaway=None, notes="", kicker=None, title_color=NAVY):
    s = prs.slides.add_slide(BLANK)
    bar(s, 0, 0, SW, 0.18, ACCENT)
    y = 0.45
    if kicker:
        txt(s, 0.6, y, SW - 1.2, 0.4, kicker.upper(), 14, bold=True, color=ACCENT); y += 0.45
    txt(s, 0.6, y, SW - 1.2, 1.1, title, 26, bold=True, color=title_color)
    if fig:
        picture_fit(s, fig, SW - 1.6, SH - (y + 1.4) - 0.9, top=y + 1.25)
    if takeaway:
        bar(s, 0, SH - 0.85, SW, 0.85, RGBColor(0xF2, 0xF5, 0xF7))
        txt(s, 0.6, SH - 0.82, SW - 1.2, 0.8, takeaway, 16, bold=True, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def section(title, subtitle=""):
    s = prs.slides.add_slide(BLANK)
    bar(s, 0, 0, SW, SH, ACCENT)
    txt(s, 1, 2.7, SW - 2, 1.5, title, 40, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        txt(s, 1, 4.1, SW - 2, 1.0, subtitle, 20, color=RGBColor(0xD8, 0xE8, 0xEE))
    return s


F = "results/dec4"
TTL = "analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png"

# ============================ TITLE ============================
s = prs.slides.add_slide(BLANK)
bar(s, 0, 0, SW, SH, NAVY)
bar(s, 0, 5.0, SW, 0.08, ACCENT)
txt(s, 1, 2.0, SW - 2, 1.6, "Can we talk to the brain through the skin?", 38, bold=True, color=WHITE)
txt(s, 1, 3.6, SW - 2, 1.0, "What happens in the brain when we buzz the body at different rhythms", 20, color=RGBColor(0xBF, 0xD0, 0xDA))
txt(s, 1, 5.3, SW - 2, 0.8, "Pardis Miri  ·  Buzsáki Lab  ·  haptic-stimulation electrophysiology", 16, color=RGBColor(0x9A, 0xA8, 0xB5))
s.notes_slide.notes_text_frame.text = (
    "Welcome. Today: a simple-sounding question with a surprisingly subtle answer. If you buzz someone's "
    "skin, does it actually change what their brain is doing — and can the brain 'tune in' to the rhythm of the buzz? "
    "No neuroscience background needed; I'll build up every idea with an analogy. (~35 min, stop me with questions.)")

# ============================ BIG PICTURE ============================
content("The dream: wearables that gently 'nudge' the brain through touch",
        takeaway="To build that, we first have to answer a basic question: does a buzz on the body actually reach and change the brain?",
        notes=(
            "Big picture first. There's huge interest in wearables that touch your skin to shift a brain state — "
            "to help you sleep, focus, calm down, or aid therapy after injury. The skin is the easiest, safest door "
            "to the nervous system. But before any of that, we need the unglamorous groundwork: if I buzz the body, "
            "(1) does the brain even notice, (2) does it matter how FAST I buzz, and (3) can the brain lock onto the "
            "rhythm of the buzz? That third one — 'marching in step' with the stimulus — is the holy grail, because "
            "that's how you'd drive a brain rhythm on purpose. That's what this project chips away at."))

content("The experiment, in one picture",
        takeaway="Buzz the body in 3-second bursts at different speeds; listen to the brain at the same time; repeat 200×.",
        notes=(
            "Here's the whole setup in plain terms. We put a little vibrating motor — a 'tactor', like the buzz in "
            "your phone — on the body. We buzz it for 3 seconds, then rest 3 seconds, over and over. We try different "
            "buzz SPEEDS: 5, 10, 26, and 50 buzzes per second. And different strengths. While that happens, we listen "
            "to the brain with fine electrodes. Then we ask: what changed in the brain during the buzz versus the rest?"))

content("Three questions",
        takeaway="(1) Does the brain notice?   (2) Does the buzz SPEED matter?   (3) Does the brain march in step with the buzz?",
        notes=(
            "Keep these three questions in your head — the whole talk answers them. One: does the brain register the "
            "buzz at all? Two: does it care how fast we buzz — is 50/sec different from 26/sec? Three, the big one: "
            "does the brain 'entrain' — literally oscillate in lockstep with the buzz, like marching to a drumbeat? "
            "Spoiler: yes, yes-ish, and 'we couldn't fully test it' — and WHY we couldn't is one of the most useful "
            "things we learned."))

# ============================ PART 1: THE TOOLS ============================
section("Part 1 — How do you 'listen' to a brain?", "Two ideas you need, both with analogies")

content("We listened in two neighboring brain regions",
        takeaway="Hippocampus = the brain's inner GPS & memory.  Entorhinal cortex = its main input hub. Two listening posts.",
        notes=(
            "We recorded from two spots that talk to each other: the hippocampus — think of it as the brain's inner "
            "GPS and memory-maker — and right next to it the entorhinal cortex, which is the hippocampus's main "
            "inbox, where a lot of sensory information arrives. So: two listening posts in a circuit that handles "
            "where-you-are and what-just-happened. Don't worry about the names; just 'two connected regions.'"))

content("THE key idea: a brain recording has two very different signals",
        kicker="concept · analogy",
        takeaway="Stadium analogy → the CROWD MURMUR (the field potential) vs. INDIVIDUAL VOICES (single neurons firing).",
        notes=(
            "This is the single most important idea in the talk, so here's the analogy I want you to remember. "
            "Imagine a microphone hung over a packed stadium. You hear TWO things. First, the low ROAR of the whole "
            "crowd — rising and falling together. In the brain that's the 'field potential' (the LFP): the blended, "
            "slow electrical hum of thousands of cells. Second, if you listen closely, individual people SHOUTING — "
            "sharp, brief, distinct. In the brain those are 'spikes': single neurons firing, each a crisp ~1-millisecond "
            "blip. The crowd murmur is easy to hear but vague; the individual voices are harder to pick out but tell "
            "you exactly who said what. We'll use BOTH — and the difference between them is the whole plot."))

content("Why single neurons are the gold standard",
        kicker="concept",
        takeaway="A real neuron firing is unambiguous — it's much harder for noise or equipment to fake than the crowd hum.",
        notes=(
            "Why care about the hard-to-hear individual voices? Because they're trustworthy. The crowd murmur can be "
            "contaminated by all sorts of background noise — a passing truck, a buzzing speaker. But an individual, "
            "identified shout is a real event from a real person. Same in the brain: a sorted single-neuron spike is "
            "a genuine cell doing its thing, and — as we'll see — it's much harder for the equipment's own electrical "
            "noise to fake one. Hold that thought; it becomes the hero of the story."))

# ============================ PART 2: THE FINDINGS ============================
section("Part 2 — What the brain actually did")

content("Yes — the brain notices the buzz. But it reacts to the START and STOP",
        kicker="finding 1 · analogy",
        fig=f"{F}/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png",
        takeaway="Like a doorbell: the brain responds to the EVENT of the buzz turning on/off — not by humming along with it.",
        notes=(
            "First result. The crowd-murmur signal clearly changes when we buzz — so yes, the brain notices. But "
            "HOW it responds matters. It mostly reacts to the buzz turning ON and OFF — the transitions — not by "
            "settling into the buzz's rhythm. Analogy: a doorbell. Your attention spikes when it RINGS and when it "
            "STOPS, but you don't start vibrating at the doorbell's pitch. So far: the brain registers the event, "
            "but isn't obviously 'tuning in.' Which raises question 3..."))

content("'Marching in step' has a name: entrainment",
        kicker="concept · analogy",
        takeaway="Pushing a swing in rhythm → if the brain entrains, its own waves line up with the buzz's beat.",
        notes=(
            "The dream is 'entrainment': the brain's own electrical waves locking onto the rhythm of the buzz. "
            "Analogy: pushing a child's swing. If you push exactly in time with the swing, it goes higher and higher — "
            "your rhythm drives its rhythm. If the brain entrained to a 50-per-second buzz, we'd see brain activity "
            "ticking along at 50 per second. That would be powerful — it'd mean you can DIAL IN a brain rhythm from "
            "the skin. So: does the brain hum along at the buzz frequency? Let's look."))

content("The hippocampus does NOT hum along — at any buzz speed",
        kicker="finding 2",
        fig=f"{F}/05_Frequency_Spectral/spectral_slope_itpc_dec4.png",
        takeaway="No matter the buzz speed (5–50/sec), we see no matching brain rhythm above the normal background.",
        notes=(
            "Here's the test. If the brain hummed at the buzz speed, we'd see a sharp 'spike' of energy at that exact "
            "frequency, sticking up above the brain's normal background. We don't — at any speed. The line just "
            "follows the usual background. So in the hippocampus, no frequency-following: it notices the buzz but "
            "doesn't oscillate in step with it. And importantly, this replicated across two recording sessions. "
            "So far the swing isn't catching the push."))

content("Plot twist: the OTHER region shows a 50-per-second signal",
        kicker="finding 3",
        fig=f"{F}/05_Frequency_Spectral/driven_power_change_by_analysis_group.png",
        takeaway="In the entorhinal region, a 50 Hz signal appears in the crowd murmur — and it grows with buzz strength. Exciting!",
        notes=(
            "Now it gets interesting. In the second region — the entorhinal inbox — a signal at exactly 50 per second "
            "DOES show up in the crowd murmur, and it gets bigger as we buzz harder. At this point in the project we "
            "were excited: maybe THIS region entrains at 50! But here's where you have to be a careful scientist, "
            "because there's a trap. Let me teach you the trap."))

content("The trap: the machine has its OWN electrical hum",
        kicker="concept · analogy",
        takeaway="A microphone can pick up the speaker's buzz, not just the crowd. Electrical equipment leaks its own signal.",
        notes=(
            "Analogy: you're recording the crowd, but the stadium's PA speaker is humming at 50 Hz, and your "
            "microphone picks up THAT hum too. Now your recording shows a clean 50 Hz — but it's the speaker, not the "
            "crowd. Same risk here: the buzzing motor and its electronics can leak a 50-per-second electrical signal "
            "straight into our recording wires. That would look exactly like a '50 Hz brain signal' but be pure "
            "equipment artifact. So how do you tell the brain from the machine? We found a clean test."))

content("That 50 Hz is mostly the machine — the dead-electrode test proves it",
        kicker="finding 3b · the killer test",
        fig=f"{F}/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png",
        takeaway="Broken electrodes that CAN'T hear neurons still pick up the 50 Hz — ~6× more than the live ones. So it's pickup.",
        notes=(
            "Here's the trick. Some of our electrodes were broken/disconnected — they physically can't hear any "
            "neurons. They're dead microphones. If a dead microphone still records a loud 50 Hz, that 50 Hz CANNOT be "
            "the brain — it can only be the machine's hum leaking in. And that's exactly what we saw: the dead "
            "electrodes picked up about SIX TIMES MORE 50 Hz than the live, in-brain ones (left panel: the clean "
            "region is flat; right: it piles up on the broken channels in red). Verdict: the entorhinal '50 Hz brain "
            "wave' is largely equipment pickup. The crowd-murmur signal fooled us. Good thing we checked — and good "
            "thing we have a more trustworthy signal."))

content("The real result: individual neurons change their firing at 50 Hz",
        kicker="finding 4 · the headline",
        fig=f"{F}/11_Spikes/spike_onoff_cross_dataset.png",
        takeaway="Single neurons fire differently during the 50 Hz buzz — in BOTH regions. Equipment hum can't fake a neuron firing.",
        notes=(
            "Now the hero arrives: the individual voices. When we track single, identified neurons, they genuinely "
            "change how much they fire during the strong 50-per-second buzz — and this happens in BOTH regions. Why "
            "is this trustworthy when the crowd-murmur wasn't? Because the machine's electrical hum can make a "
            "recording wiggle, but it can't make a real, identified neuron decide to fire. This is the clean, "
            "honest result: 50 Hz, strong buzz, is the condition where the brain's actual cells respond — far more "
            "than at the slower speeds. So question 2 — does speed matter? — yes: 50 is special."))

content("How do we KNOW it's neurons and not the machine? Two filters",
        kicker="concept · analogy",
        fig=f"{F}/11_Spikes/unit87_acg_artifact_screen.png",
        takeaway="(1) Strip out the slow hum to find the sharp spikes.  (2) Check the neuron isn't 'ticking like a clock' at 50 Hz.",
        notes=(
            "Two safeguards, both intuitive. First: to find spikes we throw away the slow, low part of the signal and "
            "keep only the fast, sharp blips — like turning up the treble to hear finger-snaps over a rumble. The 50 Hz "
            "hum is a slow rumble, so it gets thrown away before we ever count a spike. Second safeguard: if the hum "
            "WERE sneaking in as fake spikes, the neuron would look like a metronome — ticking exactly every 1/50th of "
            "a second. We checked (this figure): the neuron's firing shows NO such 50 Hz ticking, and it looks the "
            "same during buzz and rest. So these are real neurons responding, not the machine. (This was the unit we "
            "scrutinized hardest; it passed.)"))

content("Same buzz, opposite reactions — the brain is PROCESSING, not echoing",
        kicker="finding 4b · analogy",
        fig=f"{F}/11_Spikes/spike_50hz_interpretation.png",
        takeaway="One region revs a subset of cells UP; the other quiets DOWN. A passive echo would look the same everywhere.",
        notes=(
            "And here's the satisfying part. The two regions react to the SAME buzz in OPPOSITE directions: in the "
            "hippocampus a subset of cells revs up; in the entorhinal region cells mostly quiet down. Analogy: two "
            "people hearing the same news — one gets excited, one goes quiet. That difference tells you they're "
            "actively PROCESSING the input, each in their own way — not just passively echoing the buzz. (Bonus: the "
            "quieting-down is itself strong evidence it's real, because equipment pickup can only ADD fake blips, it "
            "can't make a neuron go silent.)"))

content("Do the two regions 'work together' at 50 Hz? Not clearly",
        kicker="finding 5 · analogy",
        fig=f"{F}/11_Spikes/coordination_50hz_pooled.png",
        takeaway="Two orchestras can SOUND synced because of a hallway metronome (shared hum) — not because they're playing together.",
        notes=(
            "Last finding. Both regions respond — do they coordinate, like partners in a conversation? The crowd-murmur "
            "made them look in sync. But analogy: two orchestras in separate rooms can SEEM synchronized simply because "
            "both hear the same metronome ticking in the hallway — not because they're listening to each other. The "
            "trustworthy test is whether the actual MUSICIANS (the neurons) time themselves to the other room — and "
            "they don't, not more during the buzz. So the apparent 'sync' is the shared hum (that 50 Hz pickup again), "
            "not genuine teamwork. Honest answer: no clear coordination."))

# ============================ PART 3: THE LIMIT + FUTURE ============================
section("Part 3 — The one thing we couldn't test (and how we fix it)")

content("We could NOT test 'marching in step' — and it's not the brain's fault",
        kicker="the honest limit · analogy",
        takeaway="It's like judging whether a dancer is on-beat when you forgot to record the music. The reference was missing.",
        notes=(
            "Back to the holy-grail question — does the brain entrain, march in step? We genuinely could not test it, "
            "and the reason is important and honest. Analogy: to judge whether a dancer is on the beat, you need to "
            "have recorded the MUSIC. We recorded the dancer (the brain) beautifully — but we never properly recorded "
            "the music (the exact timing of the buzz). Without the beat, you can't score the dancing. So 'we didn't "
            "show entrainment' is NOT 'the brain failed to entrain' — it's 'we were missing the measurement.'"))

content("Why: the wire meant to record the buzz never captured it",
        kicker="the diagnosis",
        fig=TTL,
        takeaway="It updated ~4×/sec while the tactor buzzed 26×/sec — like checking a hummingbird's wings 4 times a second.",
        notes=(
            "I went back and proved this from the data. The signal that was supposed to mark each buzz cycle actually "
            "updated only about 4 times a second — but the tactor was buzzing 26 times a second. Analogy: trying to "
            "track a hummingbird's wingbeats by glancing 4 times a second — between your glances the wings have flapped "
            "6 times; you simply can't recover the motion. (Top: the actual recorded line, irregular and slow. Middle: "
            "what a real 26-per-second buzz looks like. Bottom: the recorded gaps are ~6× too long.) So the 'music "
            "track' was effectively blank. That single missing signal is the main limitation of the whole study."))

content("The fix is concrete — next round records the buzz properly",
        takeaway="A per-cycle marker from the firmware + a tiny force sensor that measures the ACTUAL vibration, on the same clock.",
        notes=(
            "The good news: this is a wiring problem, not a dead end, and we've already designed the fix. Next round "
            "we record the music three ways at once, all on the same clock as the brain: (1) a clean marker the buzzer's "
            "own software emits once per cycle; (2) a tiny force sensor squeezed between the tactor and the skin that "
            "measures the ACTUAL vibration delivered — proving the buzz really happened and giving us its exact beat; "
            "and (3) a copy of the drive signal as a backup. And we'll do a 2-minute test recording to CONFIRM it works "
            "before collecting real data — the check that would have caught this last time. Then entrainment becomes "
            "directly testable."))

# ============================ WRAP ============================
content("The big picture, in plain words",
        kicker="takeaways",
        takeaway="Buzzing the body DOES change the brain — most clearly as single-neuron activity at 50 Hz — but 'driving a brain rhythm' isn't shown yet.",
        notes=(
            "Let me land the plane with three plain-language takeaways. ONE: a buzz on the body really does change the "
            "brain — that's not trivial, and it's real. TWO: the most trustworthy effect is at the level of individual "
            "neurons, specifically at the fast 50-per-second buzz, and the two regions handle it differently — active "
            "processing, not a passive echo. THREE: the flashy 'brain wave at 50 Hz' turned out to be mostly the "
            "machine's hum, and whether the brain truly 'marches in step' (entrains) we couldn't test yet — because "
            "the stimulus timing wasn't recorded. We know exactly how to fix that."))

content("Why it matters",
        kicker="the road ahead",
        takeaway="If we can verify entrainment, we move toward wearables that gently and non-invasively steer brain states through touch.",
        notes=(
            "Why should a non-neuroscientist care? Because if the next round shows the brain CAN be entrained through "
            "the skin, that's a foundation for safe, non-invasive wearables that nudge brain states — for sleep, "
            "focus, calm, or rehabilitation — without surgery or drugs. This study did the honest groundwork: it "
            "found a real neural effect, it caught itself when a result was actually equipment noise, and it "
            "pinpointed the one measurement we must add to ask the biggest question properly. That's how careful "
            "science gets built."))

s = prs.slides.add_slide(BLANK)
bar(s, 0, 0, SW, SH, NAVY)
txt(s, 1, 3.0, SW - 2, 1.2, "Thank you — questions?", 40, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
txt(s, 1, 4.2, SW - 2, 0.8, "Happy to dig into any figure, the analogies, or the next-round design.", 18, color=RGBColor(0xBF, 0xD0, 0xDA))
s.notes_slide.notes_text_frame.text = (
    "Likely questions: 'Is 50 Hz special or just strongest?' (strongest clean single-unit effect of the speeds we "
    "tested). 'Could it be arousal — they just felt a strong buzz?' (possible; but it's frequency-specific, 50 beats "
    "26 at the same strength, which argues against pure arousal). 'Why not just trust the 50 Hz brain wave?' (dead "
    "electrodes picked it up → it's largely machine pickup).")

out = OUT / "haptic_brain_talk.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")

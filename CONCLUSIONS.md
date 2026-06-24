# Conclusions — Haptic Stimulation Electrophysiology (Dec 3 + Dec 4)

A single-page synthesis across both sessions. For the figure-by-figure version see
the [README key findings](README.md#abstract) and the per-topic writeups linked
below.

## Bottom line
Haptic stimulation affects the brain. Dec 3 showed a broadband, **transition-weighted**
dHPC response but **no clean entrainment**. Dec 4's clean readout is **single-unit
firing**: 50 Hz, high-amplitude stimulation produces the **strongest frequency-specific
rate effect**, with a **driven-up subset in dHPC** and **net suppression in LEC**. The
LEC 50 Hz **LFP** is pickup-contaminated, so **spikes are the trustworthy measure**.
The up-going units, including unit 87, pass the spike-artifact screens. We do **not**
yet show **entrainment** (no stimulus phase was recorded), and we do **not** show
**cross-region coordination**.

## The arc, in order
1. **There is a genuine response (Dec 3).** Haptic stimulation drives an
   amplitude-graded **broadband LFP** response, strongest at `amp180/250_freq26`.
   It is **transition-weighted** (onset/offset), statistically reliable on
   trial-level CIs at `amp250_freq26`. → broadband / transition-index figures.
2. **It is not frequency-following.** dHPC shows **no narrowband peak and no phase
   locking** at any tested frequency (5/10/26/50 Hz). This **replicates across Dec 3
   and Dec 4 on the same probe**. The brain is responding to the *stimulus events*,
   not oscillating at the drive frequency.
3. **A 50 Hz LFP appears in LEC — but it is contaminated.** Dec 4's LEC probe shows
   an amplitude-graded, *induced* (not phase-locked) 50 Hz LFP power increase. A
   **dedicated artifact check** ([DEC4_50HZ_ARTIFACT_CHECK.md](docs/DEC4_50HZ_ARTIFACT_CHECK.md))
   shows disconnected LEC electrodes pick up **~6× more** 50 Hz than tissue and the
   cross-region lag is **~0 ms** → a real **non-neural pickup component**. So the
   LEC 50 Hz *LFP* is not clean neural evidence.
4. **The clean neural result is single-unit (Dec 4).** Sorted, curated units change
   their **firing rate** during 50 Hz / high-amplitude ON vs OFF, in **both** regions
   (dHPC 19/180 unit-conditions, LEC 13/180; concentrated at 50 Hz: 15/19 and 8/13).
   The ~300 Hz spike high-pass removes the slow 50 Hz pickup before detection, and
   the ACG/ISI/waveform screens argue against pickup-manufactured spikes, so this is
   the cleanest evidence. It also explains the Dec 3 single-unit null: Dec 3 only
   tested 5/26 Hz, where there is no effect.
   *Note:* responders are a **modest fraction** (~7–11% of tests) and FDR allows a
   few false positives — so the trustworthy claim is the **concentration at 50 Hz**
   (15/19 and 8/13, far above the uniform spread chance would give), not that every
   flagged unit is real. →
   [DEC4_SPIKE_ONOFF_RESULT.md](docs/DEC4_SPIKE_ONOFF_RESULT.md).
   - *Why 50 Hz and not 26 Hz?* In the **LFP** (Dec 3) the biggest gross *transient*
     was at 26 Hz / high amplitude — but that is the **contaminated, frequency-non-
     specific** measure (onset/offset broadband), not clean entrainment. The **clean
     single-unit** measure points to **50 Hz**.
5. **The response is active & region-specific, not a passive echo** — the strongest
   biological argument. A passive relay/echo would look **similar across regions**;
   instead the two regions transform the 50 Hz input **in opposite directions**:
   **dHPC shows a driven-up subset** — a few strong up-units carry a positive mean
   (**+0.79 Hz** at amp250_freq50); across all 50 Hz amplitudes the dHPC population is
   **mixed**, so this is a *subset*, **not a globally excited dHPC** — while **LEC
   leans net-suppressed** (10 of 15 units down, mean −0.08 Hz). Same external stimulus,
   different regional transformation. The LEC suppression doubles as **artifact logic**:
   additive pickup *adds*, not removes, apparent spikes, so a net loss of spikes is not
   what pickup produces.
6. **But the regions do not demonstrably coordinate.** The cross-region
   **spike–field** test (do one region's neurons lock to the *other* region's
   rhythm? — harder for pickup to fake than the LFP) is weak and **does not rise**
   during stimulation. The LFP
   coherence rise is the foolable measure (inflated by the shared 50 Hz pickup from
   #3). → [DEC4_COORDINATION_50HZ.md](docs/DEC4_COORDINATION_50HZ.md).

## What is genuinely supported
- A real, amplitude-graded, **event-/transition-driven** haptic response (LFP).
- **No frequency-following** (no entrainment by power *or* phase), replicated.
- A genuine, frequency-specific (**50 Hz**), region-specific **single-unit rate**
  modulation at high amplitude — **driven-up subset in dHPC, net suppression in LEC**
  (same input, opposite transformations) — the headline neural finding.

## What is NOT supported / explicitly negative
- The brain does **not** oscillate at the drive frequency.
- The LEC **50 Hz LFP** is **not** clean neural signal (pickup-contaminated).
- The two regions do **not** demonstrably **work together** at 50 Hz.

## Limitations
- **Single animal**, single session per region pairing.
- **Our hardware was not equipped to test entrainment.** No stimulus-phase reference
  was recorded — free-running actuator, no analog stimulus copy, and the digital sync
  channel never captured the carrier (TTL diagnostic). So phase-following was
  **untestable, not negative** — a hardware limitation, not a neural result.
- **Stimulus fidelity at low frequencies.** Post hoc, the delivered vibration was
  **not a clean sine wave at 5 / 10 / 26 Hz** (the actuator did not produce clean
  sinusoids at low frequencies). So the apparent frequency-specificity (effect at
  50 Hz) is **partly confounded with stimulus quality** — 50 Hz was delivered more
  cleanly than the lower carriers.
- ON-vs-OFF is a within-trial contrast (OFF = post-stim, not neutral baseline). A
  strong-stimulus **arousal/state** component could ride along with the **whole** 50 Hz
  rate effect (amp250_freq50 is the most intense buzz), not just unit 87. The defense
  is **frequency-specificity** — 50 Hz produces much stronger spike modulation than
  26 Hz at matched amplitude, which argues against pure intensity-driven arousal — but
  **indirect sensory/state mechanisms remain possible**. The screens rule out
  pickup-manufactured spikes, **not** the direct-circuit-modulation-vs-indirect-cascade
  distinction.
- **Checked against true baseline & post-study.** The ON/OFF result was re-tested
  against the **pre-experiment baseline and post-study** windows (25–46 min each;
  [DEC_BASELINE_POSTSTUDY_STATES.md](docs/DEC_BASELINE_POSTSTUDY_STATES.md)). ON/OFF is
  a drift-immune *local* contrast, so it survives — and dHPC's up-drive is confirmed
  **above baseline** (+1.05 Hz at amp250_freq50). But the baseline reference exposes a
  **session-long downward firing drift**: mild in dHPC (−4 to −6 %), **substantial in
  LEC (−26 %)**. The LEC 50 Hz suppression is sustained into the OFF window (so ON−OFF
  under-reports it) but is partly entangled with that drift — a state-stability caveat
  for any non-local comparison, and another reason the **local** ON/OFF and the
  recorded-stimulus next round are the right measures.
- All 15 curated good **LEC** units sit in the 50 Hz **pickup zone** (peak channels
  173–214; none in the clean shallow region), so unit location and pickup location
  can't be spatially separated. The rate result still holds: ≈300 Hz high-pass
  removes 50 Hz pre-detection; the LEC population *leans down* during ON (10/15 units —
  additive pickup adds, not removes, apparent spikes); and two spike-artifact screens clear **0/8 up-going
  units** — no ON 50 Hz ACG comb, and no ON rise in ISI<2ms violations (unit 87 incl.;
  closing both the periodic-pickup and broadband-noise-floor loopholes). So the
  up-going units **pass the spike-artifact screens** (clean refractory, no comb,
  stable ON/OFF violation rate) — the remaining caveats are n=1, arousal/state, and
  **indirect sensory-network effects** (direct 50 Hz circuit modulation vs an indirect
  sensory/state cascade), **not** 50 Hz pickup manufacturing spikes. See
  [DEC4_50HZ_ARTIFACT_CHECK.md](docs/DEC4_50HZ_ARTIFACT_CHECK.md).
- **Anatomical targeting is known** (surgeon's coordinates: dHPC = H12_2 @
  AP 1.8 / ML 1.5 / depth 1–1.8 mm, Port A; LEC = H15 @ AP 3.8 / ML 3.8 / 5°, Port B).
  What's still **provisional** is the electrode **channel-map** — the Cambridge
  NeuroTech site map (`.prb`) for H12_2 / H15 + adapter wiring; the analysis uses a
  linear placeholder. This gates only **depth / laminar / subregion** claims; the
  region-level (dHPC vs LEC) findings are unaffected.

## What the next recording must add (external, can't be done on this data)
1. **Continuous analog copy of the delivered vibration** (thin PVDF force sensor in
   the tactor→skin path → Intan analog input on the shared 20 kHz clock). Enables a
   true **phase-entrainment** test *and* lets you **regress out the 50 Hz artifact**.
2. **Per-cycle + per-trial digital sync lines** for exact stimulus timing (no TTL
   this session; timing came from the controller log).
3. The electrode **channel-map** (Cambridge NeuroTech `.prb` for H12_2 / H15 +
   adapter wiring) — needed only for depth / laminar / subregion analyses.

→ Hardware spec: [HARDWARE_ENG_MESSAGE_NEXT_ROUND.md](docs/HARDWARE_ENG_MESSAGE_NEXT_ROUND.md),
[PVDF_CHARGE_AMP_SPEC.md](docs/PVDF_CHARGE_AMP_SPEC.md).

## Detailed writeups
- [DEC4_SPIKE_ONOFF_RESULT.md](docs/DEC4_SPIKE_ONOFF_RESULT.md) — single-unit headline
- [DEC4_50HZ_ARTIFACT_CHECK.md](docs/DEC4_50HZ_ARTIFACT_CHECK.md) — the LFP artifact test
- [DEC4_COORDINATION_50HZ.md](docs/DEC4_COORDINATION_50HZ.md) — do the regions coordinate?
- [DEC_BASELINE_POSTSTUDY_STATES.md](docs/DEC_BASELINE_POSTSTUDY_STATES.md) — ON/OFF vs true baseline & post-study (drift)
- [DEC_CELLTYPE_CLASSIFICATION.md](docs/DEC_CELLTYPE_CLASSIFICATION.md) — putative pyr/interneuron types; 50 Hz response by type
- [DEC_LFP_APERIODIC_STATES.md](docs/DEC_LFP_APERIODIC_STATES.md) — 1/f slope across baseline/ON/OFF/post; real bump vs broad shift
- [DEC_RIPPLE_STATES.md](docs/DEC_RIPPLE_STATES.md) — sharp-wave ripples across states; participation by cell type (exploratory)
- [DEC_LFP_BANDPOWER_STATES.md](docs/DEC_LFP_BANDPOWER_STATES.md) — broadband/theta/gamma + driven-band power across states
- [DEC4_SUPERVISOR_SUMMARY.md](docs/DEC4_SUPERVISOR_SUMMARY.md) /
  [DEC3_SUPERVISOR_SUMMARY.md](docs/DEC3_SUPERVISOR_SUMMARY.md)

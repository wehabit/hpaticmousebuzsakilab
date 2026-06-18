# Dec 3 — External Blockers

Items that cannot be closed by more analysis. Each needs information or action
from the lab, the surgeon, or the hardware engineer. Sourced from
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) and
[STIMULUS_SYNC_RECORDING_SPEC.md](STIMULUS_SYNC_RECORDING_SPEC.md). Items the
Dec 4 recording already resolved are noted so they are not re-asked.

## Resolved by Dec 4 (no longer blockers)
- Probe identity: Dec 3 = dHPC probe (Cambridge NeuroTech H12_2), Port A.
- Both LEC and dHPC probes exist on this mouse; Dec 3 recorded the dHPC alone.

## 1. Probe geometry & anatomy — needs lab records / surgeon / histology
- [ ] The lab's specific **channel-map PDF or `.prb`** for this exact H12_2
      probe (site order). *Owner: lab / probe records.*
- [ ] Which physical shank is **medial vs lateral / anterior vs posterior**.
      Current safe labels: ch `0–63` = Shank A, ch `64–127` = Shank B; the
      mapping to brain axes is unknown. *Owner: surgeon / surgery notes.*
- [ ] Whether the **XML group order matches physical contact depth order** or is
      only a spike-sorting grouping. *Owner: lab.*
- [ ] Which contacts are expected in **CA1 / DG / subiculum / cortex** at depth
      1–1.8 mm. *Owner: histology / surgeon.*
- [ ] **Histology / post-hoc track reconstruction / final coordinates** for this
      mouse/session. *Owner: histology.*

> Blocks: shank- and depth-resolved summaries, and any anatomical (subregion)
> interpretation of the LFP/spike effects.

## 2. Recording metadata — needs acquisition records
- [ ] Any channels known to be **disconnected, shorted, reference, ground, or
      intentionally unused**. *Owner: lab / acquisition notes.*
- [ ] The **reference scheme used during acquisition**. *Owner: lab.*
- [ ] The **final Neuroscope bad-channel list** after visual review, if saved.
      *Owner: lab.*

> Blocks: final confirmation of the bad-channel list and referencing decisions
> (currently treated as analysis choices, not ground truth).

## 3. Stimulation & behavior — needs stim controller truth / hardware engineer
- [ ] Is `cmd_config_1_Dec3rd.json` the **final source of truth** for the
      1200-trial stimulation order? *Owner: stim controller / experimenter.*
- [ ] Why does the digital input show **extra pre/post TTL bursts** and fewer
      clean main-window bursts than the expected 1200 trials? *Owner: hardware.*
- [ ] Which **digital input bit is the true stimulation trigger** (currently the
      active bit with transitions is bit `7`). *Owner: hardware.*
- [ ] Were the **3 s ON / 3 s OFF intervals exact**, or should final event
      timing be corrected from TTL edges? *Owner: hardware / stim controller.*
- [ ] Any **mechanical/acoustic artifact, motor saturation, or missed delivery**
      during high-amplitude conditions? *Owner: experimenter notes.*

## 4. Hardware action item for next session (not retro-fixable for Dec 3)
- [ ] The actuator runs a **free-running sine oscillator** (phase not reset per
      trial) and **no stimulus copy was recorded**, which makes true entrainment
      untestable from the LFP. Add a **stimulus sync + delivery recording** for
      future sessions — full spec in
      [STIMULUS_SYNC_RECORDING_SPEC.md](STIMULUS_SYNC_RECORDING_SPEC.md).
      *Owner: hardware engineer.*

> Blocks: any direct (rather than inferred) test of stimulation-frequency
> following. This is why Dec 3 results say "LFP response at a 26 Hz condition"
> rather than "26 Hz entrainment."

## Analysis-side item (NOT external — your call, infra ready)
- [ ] **Phy manual curation** of the 194 Kilosort clusters before final
      single-unit claims. Not blocked on anyone else; the Modal noVNC desktop is
      set up and ready — see [PHY_DEC3_SETUP.md](PHY_DEC3_SETUP.md).

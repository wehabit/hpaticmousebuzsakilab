# Dec 4 Supervisor Summary — Two-Probe Haptic Stimulation (dHPC + LEC)

> Dec 4 session, run with the **same verified pipeline as Dec 3** (the Dec 3
> analysis modules were re-used unchanged; only the channel grouping and condition
> list were swapped). **Now includes spike sorting + curation + single-unit ON/OFF**
> for both probes (see headline finding 4 and `docs/DEC4_SPIKE_ONOFF_RESULT.md`),
> in addition to the LFP analyses.

## What is different from Dec 3

Same mouse, same headstage settings, same probes — Dec 4 simply records a
**second probe** and **two extra drive frequencies**:

| | Dec 3 | Dec 4 |
|---|---|---|
| Probes | dHPC only (128 ch, Port A) | **dHPC (Port A, 0–127) + LEC (Port B, 128–255)** = 256 ch |
| Drive frequencies | 5, 26 Hz | **5, 10, 26, 50 Hz** |
| Amplitudes | 100, 180, 250 | 100, 180, 250 (same) |
| Conditions × repeats | 6 × 200 = 1200 trials | **12 × 200 = 2400 trials** |
| Stimulation block | 120 min | **240 min** (15 min pre + 240 + 15 post; ~5 h total) |
| Timing source | controller schedule + accelerometer TTL | controller schedule + **log START offset** (no `digitalin.dat` shared) |

Port A is the **identical dHPC probe and channel map as Dec 3**, so dHPC results
are directly comparable channel-for-channel between the two sessions.

## Data / timing provenance

- 256-ch `amplifier.dat` (185 GB), 20 kHz → decimated to a 1250 Hz `amplifier.lfp`
  (`analysis/extract_lfp.py`; 22,669,544 samples = 18,135.6 s confirmed).
- **No `digitalin.dat`/analog-in was shared** for Dec 4 (the TTL was enabled in the
  Intan config but only `amplifier`/`auxiliary`/`time` files exist). Trial timing is
  therefore taken entirely from the randomized controller schedule
  (`cmd_config_1_Dec4th_randomized_all.json`) plus the controller log's wall-clock
  START, aligned to the Intan recording-start timestamp:
  **offset = 13:45:29.78 (log START) − 13:14:03 (filename) = 1886.78 s.**
  This same method reproduces the Dec 3 offset exactly (640 s), so it is validated.
- Authoritative trial table: `analysis/outputs/dec4/dec4_condition_sequence.csv`
  (2400 trials; baseline 1886.8–2786.8 s; stim 2786.8–17183.8 s recording time).

## Channel QC (per-probe) — an important hardware finding

QC was run **per probe** because the LEC probe is ~2× noisier than dHPC (pooling
the two probes' robust-z masks the real bad channels). See
`analysis/bad_channels_dec4.json`.

- **dHPC (Port A): clean — the dHPC hardware was improved before Dec 4.** Dec 4's
  own QC flags only **channel 121**. The 9 channels that were bad on Dec 3
  ({5,6,7,32,33,34,43,66,67}) are **no longer flagged** by Dec 4 QC (their per-probe
  robust-z ≈ 1.6, well below threshold), consistent with the pre-Dec-4 hardware fix,
  so they are **not carried over / not excluded** on Dec 4.
- **LEC (Port B): 45 disconnected-dead channels**, dominated by a **contiguous dead
  block 224–255** (all high/extreme noise — most likely a connector/hardware issue on
  that half-shank) plus 128–141. A post-hoc QC sweep later excluded **1 more**
  (ch142 — broadband-hot but *live*, 50 Hz rise ≈0, hosts no good unit). So LEC
  partitions **82 good / 45 disconnected-dead / 1 hot-excluded**. LEC results below
  use only good channels.

Total Dec 4 excluded channels = 47 — dHPC 1 (ch121) + LEC 45 disconnected-dead +
LEC 1 hot-excluded (ch142). The older "46 dead" count lumped ch142 into "dead";
the precise framing keeps it separate (live, not disconnected).

## Headline findings

1. **dHPC does not follow any drive frequency — replicating Dec 3 on the same probe.**
   Driven-frequency power change is near zero/negative at 5, 10, 26 *and* 50 Hz, and
   inter-trial phase locking (ITPC) sits at the finite-trial chance floor. The 1/f
   decomposition shows no robust narrowband peak (only a small, non-amplitude-graded
   50 Hz residual). This both **replicates Dec 3's "no frequency-following in dHPC"**
   on the identical probe and **extends it to the two new frequencies**.

2. **LEC shows a real, amplitude-graded narrowband 50 Hz power increase — but it is
   *induced*, not phase-locked.**
   - Driven-power change at 50 Hz in LEC grows monotonically with amplitude:
     **+0.28 → +0.71 → +1.26 log2** (group-median ref; ≈ 1.2× → 2.4× power) and is
     **robust across all reference schemes** (raw 0.18/0.47/0.83; probe-median
     0.32/0.76/1.37). No comparable effect at 5/10/26 Hz, and none in dHPC.
   - The 1/f decomposition confirms this is a **genuine narrowband peak above the
     aperiodic background** at 50 Hz (residual above 1/f **+0.35 → +0.48 → +0.64**,
     amplitude-graded), not a broadband shift.
   - **But ITPC at 50 Hz stays at the chance floor** (≈0.05–0.08 vs floor 0.063; all
     below the Rayleigh p<0.05 threshold of 0.122). So the 50 Hz power is **not
     consistently phase-locked to stimulus onset across trials** → induced 50 Hz
     power, not onset-locked entrainment.

3. **Broadband response is onset/transient and amplitude-graded** (mostly dHPC):
   onset-window broadband increases scale with amplitude and are largest at amp250,
   with little sustained elevation — the same transition-dominated character as Dec 3.

4. **Single-unit ON/OFF firing is modulated at 50 Hz / high amplitude — in BOTH
   probes.** Both probes were spike-sorted, over-split-corrected, and curated
   (dHPC 15, LEC 15 good units; see `docs/DEC4_SPIKE_ONOFF_RESULT.md`). On the
   curated ON-vs-OFF test, Dec 3 (5/26 Hz only) showed **0/174** responsive
   unit-conditions, but Dec 4 shows **dHPC 19/180 and LEC 13/180**, concentrated
   at **50 Hz** (15/19 and 8/13) and high amplitude (peak dHPC `amp250_freq50`:
   9 units, mean ON−OFF +0.79 Hz). Direction is mixed (a modulated *subset*, not
   a uniform drive). So the Dec 3 single-unit null was **frequency-limited**, and
   the 50 Hz spike modulation is coherent with the LEC 50 Hz LFP effect.
   Figure: `analysis/outputs/cross_dataset_spike_compare/spike_onoff_cross_dataset.png`.

**One-figure version:** `results/dec4/10_Biological_Summary/combined_explainer.png`.
**Entrainment test:** `results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png`.

## How Dec 4 answers Dec 3 open questions (`docs/OPEN_QUESTIONS.md`)

- **Recording Metadata Q1–Q2 (were both probes present; which port = which probe?)**
  → **Answered.** Both probes exist; Port A = dHPC (H12_2), Port B = LEC (H15).
  Dec 3's 128-ch recording was the dHPC probe (Port A) alone.
- **The README's central caveat (was Dec 3's "no entrainment" neural or a
  stimulus-delivery limitation at 5/26 Hz?)** → **Partially answered.** With four
  frequencies and a second region we *do* find a frequency-specific narrowband
  response, but only at **50 Hz** and only in **LEC**, and it is induced power rather
  than phase-locked entrainment. dHPC remains non-following at 5/26 Hz on the same
  probe, so that null is reproduced rather than overturned.
- **Stimulation Q1/Q4 (timing source / 3 s ON-OFF exactness)** → the controller
  schedule is the source of truth; ON/OFF windows come from it (no TTL this session).
- **Analysis-choice Q4 (which metric)** → with 4 frequencies, the driven-frequency
  1/f-residual + ITPC test is the decisive entrainment metric and is now in the
  pipeline (`spectral_slope_itpc_dec4.py`).

## Caveats (read before over-interpreting the 50 Hz LEC effect)

- **Artifact vs neural is not yet settled.** A 50 Hz, amplitude-graded, region-
  specific power increase is consistent with induced neural gamma-band power, but
  also with a 50 Hz stimulation/vibration artifact coupling preferentially into the
  (noisier) LEC analog path. Arguments *for* neural: it is amplitude-graded with the
  *stimulus drive* (not constant like mains), LEC-specific (a global electrical
  artifact should hit both probes — dHPC's 50 Hz peak is much smaller and not
  amplitude-graded), and a true narrowband peak above 1/f. Arguments *for* artifact:
  LEC is the damaged/noisy probe; 50 Hz is the highest driven rate; no analog stimulus
  monitor was saved to verify the delivered waveform.
- **Deep diagnostic (analysis/outputs/dec4/deep_diag/).** A direct look at the raw
  spectra confirms the analysis is sound (50 Hz and the 60 Hz mains line are cleanly
  separate; the LEC 50 Hz rises 1.8× over baseline; no aliasing/mislabeling) but
  *refines* the reading: the LEC 50 Hz is a **sharp spectral line at exactly the drive
  frequency** (not a broad endogenous-gamma hump), stimulus-locked to the 0–3 s ON
  window, with modest 100/150 Hz harmonics. dHPC by contrast has strong, *constant*
  endogenous 50 Hz gamma that the stimulus does not modulate. A sharp line at exactly
  the drive frequency + harmonics is consistent with the LEC **following / picking up
  the 50 Hz stimulus** rather than generating an endogenous induced gamma — which
  raises (not lowers) the artifact concern.
- **The accelerometer cross-check is NOT possible for Dec 4.** `auxiliary.dat` is
  entirely 0xFF (the headstage accelerometer was not recorded), and there is no
  `digitalin.dat`/analog-in. So there is **no independent stimulus or movement monitor**
  this session; physical 50 Hz delivery / head vibration cannot be verified from the
  data. The decisive remaining neural-vs-artifact test is therefore **spike sorting**
  (do LEC single units phase-lock to 50 Hz?), which needs the Modal/GPU run.
- **"Not phase-locked" ≠ "not neural."** ITPC requires the stimulus phase to be reset
  at trial onset. If the actuator's 50 Hz phase is not onset-locked, even true
  entrainment would show chance ITPC. Low ITPC rules out *onset-locked* entrainment,
  not all entrainment.
- No TTL/accelerometer and no analog stimulus monitor for this session → delivery
  cannot be audited as it was for Dec 3.
- An **LFP-based movement proxy** (no accelerometer) was added: the driven-power
  results are robust to excluding the highest-movement trials (full-vs-excluded
  r = 0.90), so they are not driven by movement. Spikes are prepped but not yet
  sorted (Kilosort = Modal/GPU step).

## Remaining Dec 3 analyses now also run for Dec 4

All Dec 3 LFP analyses have been reproduced for Dec 4 (same verified modules):
event-aligned LFP, frequency/driven power, time-frequency, phase locking,
trial-level bootstrap, broadband-transition, OFF-control, reference sensitivity,
artifact-aware, 1/f + ITPC entrainment test, **adaptation over repeats**,
**per-channel broadband CI**, **sustained-vs-offset explainer** (per probe),
**artifact-margin robustness** (per probe), an **LFP movement proxy + robustness
check**, a **per-probe condition-interpretation table**
(`condition_interpretation/`), **Pynapple ON/OFF/baseline intervals**, and
**spike-sorting prep + a SpikeInterface recording/trace-sanity** check.

Dec 3 steps that are **not applicable** to Dec 4: the TTL audits, the session/TTL
timeline, and the onset-jitter ("cohen-corrected") analysis — all require the
accelerometer TTL, which was not shared this session. Full **Kilosort/Phy + spike
PETH / cluster-quality** remain the Modal/GPU step (provisional on Dec 3 too).

## Stimulus is FREE-RUNNING (firmware) — this confounds onset-ITPC entrainment tests

The actuator firmware (`wehabit/FAR2.0`, `Firmware/refactor-version/actuator.cpp`)
generates the vibration from a **single continuously free-running sine oscillator**.
A 50-point sine table is stepped by a hardware-timer ISR that is started once at
boot and never stopped:

```c
volatile uint8_t sine_index1 = 0;
void TIMER2_IRQHandler(){ if(++sine_index1 == 50) sine_index1 = 0; }   // free-runs all session
void actuator_init(){ ... NRF_TIMER2->TASKS_START = 1; }               // started once, never reset
```

Starting a trial's ON only sets the step-rate (frequency) and the amplitude — it
does NOT reset the sine phase:

```c
NRF_TIMER2->CC[0] = 20000/freq;   // frequency only (50 Hz -> 400 us/step -> 20 ms/cycle)
HwPWM0.writePin(PWMPin, sine[sine_index1] * (float)OutputLevel/255, 0);  // phase free-running; only amplitude is gated
```

So each trial's vibration begins at whatever phase the oscillator happens to be at
(a spinning fan behind an amplitude shutter), and with interleaved frequencies the
onset phase is effectively random trial-to-trial.

**Implication.** The low onset-ITPC at 50 Hz (and at all frequencies) is **expected
from the stimulator itself** and is **uninformative about biology** — even a perfect
neural follower, recorded with a flawless TTL, would show chance onset-ITPC because
the stimulus has no fixed onset phase. The earlier "induced, not entrained" wording
is therefore **retracted as overstated**: onset-ITPC is the wrong test for this
free-running stimulus. What still stands unaffected is the amplitude-graded
narrowband 50 Hz **power** increase in LEC (power does not depend on phase).

**How to actually test entrainment given this design** (not mutually exclusive):
1. **Record the stimulus** (the real fix): route a sync copy of the drive — a TTL at
   the sine zero-crossings, a buffered copy of the PWM/drive, or the actuator's own
   accelerometer — into a spare Intan ADC/digital input. Then test LFP/​spike phase
   locking to the *actual stimulus waveform* (free-running is then a non-issue, and
   you also verify delivery). This is the standard solution and was already the plan
   for the "next" recording.
2. **Spike–field locking** (works on the data we have): do LEC single units fire at a
   consistent phase of the *local* 50 Hz LFP? Independent of stimulus phase and trial
   timing entirely — the Kilosort step sets this up.
3. (Optional firmware change) reset `sine_index1 = 0` at each ON to make onset-ITPC
   valid — but a hard phase reset injects an onset transient ("click") every trial and
   entangles the evoked edge with the entrainment response, so recording a sync
   channel (option 1) is preferable to changing the stimulus.

## Reproduce / rerun

```bash
# 1. metadata + authoritative condition sequence (no TTL)
python analysis/intan_haptic_summary_dec4.py \
  --session-dir Haptic_Stim_session2_251204_131403 \
  --config "Haptic_Stim_session2_251204_131403/My log/cmd_config_1_Dec4th_randomized_all.json" \
  --log "Haptic_Stim_session2_251204_131403/My log/log" \
  --output-dir analysis/outputs/dec4
# 2. LFP extraction (256 ch)
python analysis/extract_lfp.py --dat .../amplifier.dat --output .../amplifier.lfp \
  --n-channels 256 --summary analysis/outputs/dec4/lfp_extraction_summary.json --overwrite
# 3. per-probe channel QC
python analysis/channel_qc.py --dat .../amplifier.dat --n-channels 256 --compute-common-corr \
  --output-dir analysis/outputs/dec4/channel_qc
PYTHONPATH=analysis python analysis/channel_qc_perprobe_dec4.py
# 4. core LFP analyses (re-uses verified Dec 3 modules via channel_groups_dec4)
PYTHONPATH=analysis python analysis/run_dec4_lfp_pipeline.py
# 5. entrainment test + results folder
PYTHONPATH=analysis python analysis/spectral_slope_itpc_dec4.py --lfp .../amplifier.lfp \
  --sequence analysis/outputs/dec4/dec4_condition_sequence.csv \
  --bad-channels-json analysis/bad_channels_dec4.json \
  --output-dir analysis/outputs/dec4/spectral_slope_itpc
PYTHONPATH=analysis python analysis/build_dec4_results.py
```

## Reproducibility / where the data lives (so analyses can be re-run later)

- **Local, sufficient to re-run everything except spike sorting:** raw `amplifier.dat`
  (185 GB), the `amplifier_lec.dat` LEC slice (93 GB), `amplifier.lfp` (11.6 GB),
  `dec4_condition_sequence.csv`, `bad_channels_dec4.json`, the
  `spike_sorting_prep/` channel maps, and all analysis scripts. → LFP analyses and a
  Kilosort *re-sort* need nothing from Modal.
- **Only on Modal (download after the sort):** the Kilosort output
  `/dec4/kilosort4_results_lec/` on the **persistent named volume** `dec4-kilosort-data`.
  Pull it with `PROBE=lec bash analysis/download_dec4_kilosort.sh` →
  `analysis/outputs/dec4/modal_kilosort4_results_lec/` (full folder incl. `temp_wh.dat`,
  for re-running spike PETH / phase-locking without re-sorting). The volume is not
  deleted automatically, so this can be done any time.
- **Redundant on Modal (safe to delete to save storage after download):** `lec_chunks/`
  and `amplifier_lec.dat` (both reproducible from the local raw slice).

## Suggested next steps

1. **Settle artifact vs neural for the LEC 50 Hz effect:** check the `auxiliary.dat`
   accelerometer for a 50 Hz vibration component; test whether the LFP 50 Hz phase
   tracks the accelerometer; compare good vs bad LEC channels; look for the effect in
   OFF windows.
2. **Spike sorting** on both probes (Kilosort) — the Dec 3 spike pipeline scripts apply.
3. Confirm Port A = dHPC / Port B = LEC anatomy from surgery notes/probe orientation.

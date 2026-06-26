# Dec 4 figures — pointer set for Gyuri

**Design (Dec 4).** A skin-mounted tactor delivered vibration in **3 s ON / 3 s OFF** blocks
across **4 carrier frequencies (5, 10, 26, 50 Hz) × 3 amplitudes (100 / 180 / 250)**,
~200 trials per condition. A quiet **baseline** was recorded before the first trial and a
quiet period **after** the last; both probes (dHPC + LEC) recorded continuously throughout.

**Read this first:**

- **The robust result is the single-unit firing change.**
- **Stimulus quality — important.** Only the **50 Hz** drive was a clean sine wave at the
  tactor. The **5, 10, and 26 Hz** drives were degraded — not true sine waves on the
  actuator — so we **do not take those conditions into account**. 50 Hz is the one
  well-delivered stimulus, and it is the one that drove the units.
- **The LFP 50 Hz is largely instrumental pickup** (controls below), so we lean on the
  single-unit readout, not the LFP.
- **No entrainment claim.** No stimulus-phase reference was recorded, so phase-locking /
  entrainment is untestable here — a measurement gap, not a null.
- **The next-generation hardware removes both limits:** it records the *delivered* waveform
  (a clean sine plus a transduced copy of the actual vibration) and a per-cycle phase
  reference on the acquisition clock — making frequency specificity *and* phase-locking /
  entrainment directly testable.
- **Probes / anatomy.** dHPC = Cambridge NeuroTech H12/L13 (2 shanks, recorded as 4 verified
  32-channel sections); LEC = H15 (2 shanks). CA1 layer is by ripple-band localization, not
  histology.

Figures in the first section are embedded — **click any image to open it at full
resolution**. The rest are grouped below as links.

---

## Show these — raster · PSTH · spectrogram

The clean, immediate evidence: sorted neurons changing their firing, the population, the
frequency specificity, and the LFP picture.

**1. Example modulated units (dHPC & LEC).** Spikes per trial + PSTH, against the
never-stimulated pre-study baseline.

[![raster_psth_examples_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/raster_psth_examples_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_psth_examples_dec4.png)

**2. Population PSTH** of the modulated units.

[![psth_population_modulated_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/psth_population_modulated_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/psth_population_modulated_dec4.png)

**3. Every curated unit + the Dec 3 null control**, on one shared scale.

[![raster_psth_all_good_units_combined](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/raster_psth_all_good_units_combined.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_psth_all_good_units_combined.png)

**4. Frequency specificity — PSTH.** The single-unit response concentrates at 50 Hz.
*Caveat: the 5/10/26 Hz drives were not clean sine waves (degraded delivered waveform), so
their weaker response is partly a stimulus-quality artifact — the solid claim is that 50 Hz,
the one well-delivered condition, drove the units. The next rig records the waveform to
settle this.*

[![psth_frequency_specific_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/psth_frequency_specific_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/psth_frequency_specific_dec4.png)

**5. Frequency specificity — raster** version of the same (same stimulus-quality caveat as #4).

[![raster_frequency_specific_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/raster_frequency_specific_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_frequency_specific_dec4.png)

**6. Trial-averaged LFP spectrogram.** LEC has a 50 Hz band that grows with amplitude;
dHPC has none. *A real measured line, but artifact-suspect — see the pickup controls below.*

[![trial_avg_spectrogram_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec4.png)

---

## …and a battery of other analyses

### The LFP 50 Hz is largely pickup (not entrainment)

**50hz_pickup_gradient_dhpc_vs_lec.png** — disconnected channels carry the 50 Hz ~6×.

[![50hz_pickup_gradient_dhpc_vs_lec](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png)

**fiftyhz_tissue_contamination_dec4.png** — it reaches ~1/3 of the *good* LEC tissue channels too; dHPC tissue is clean.

[![fiftyhz_tissue_contamination_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/12_ChannelQC_Traces/fiftyhz_tissue_contamination_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/12_ChannelQC_Traces/fiftyhz_tissue_contamination_dec4.png)

**spectral_slope_itpc_dec4.png** — narrowband 50 Hz above 1/f in LEC, but **ITPC at chance** = induced, not entrained.

[![spectral_slope_itpc_dec4](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png)

### The spikes are real (and summarized)

**unit87_acg_artifact_screen.png** — high-pass detection (>300 Hz) + ACG/ISI screens; load-bearing because all LEC units sit on contaminated channels.

[![unit87_acg_artifact_screen](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/unit87_acg_artifact_screen.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/unit87_acg_artifact_screen.png)

**spike_onoff_cross_dataset.png** — the ON/OFF summary: Dec 3 null vs Dec 4 50 Hz responders, both regions.

[![spike_onoff_cross_dataset](https://raw.githubusercontent.com/wehabit/hpaticmousebuzsakilab/main/results/dec4/11_Spikes/spike_onoff_cross_dataset.png)](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/spike_onoff_cross_dataset.png)

---

The rest (links open each figure at full resolution):

**It's genuine CA1.**
- [ripple_examples.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/ripple_examples.png) — real sharp-wave ripples.
- [ripple_localization_by_shank.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/ripple_localization_by_shank.png) — ripple-band power peaks at the data-driven detection channel, both sessions = CA1 pyramidal layer.

**Where on the probe, and what cell types.**
- [unit_by_shank_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/unit_by_shank_dec4.png) — responders span sections (not a one-shank quirk).
- [dec4_celltype.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/dec4_celltype.png) — putative pyramidal vs interneuron separation (LEC interneuron n = 2).

**Region-specific processing.**
- [spike_50hz_interpretation.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/spike_50hz_interpretation.png) — dHPC has a driven-up subset, LEC is net-suppressed → opposite transforms of the same input = active processing, not a passive relay.

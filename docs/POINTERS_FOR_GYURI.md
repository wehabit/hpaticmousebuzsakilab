# Dec 4 figures — pointer set for Gyuri

Organized by the three questions a rigorous reviewer asks, in order. The repository is
public, so each link opens the rendered figure on GitHub.

**Read this first:** the robust result is the **single-unit** firing change. The **LFP
50 Hz is largely instrumental pickup**, and we do **not** claim entrainment — no
stimulus-phase reference was recorded, so phase-following is untestable here (a
measurement gap, not a null). Probes: dHPC = Cambridge NeuroTech H12/L13 (2 shanks,
recorded as 4 verified 32-channel sections); LEC = H15 (2 shanks). CA1 layer is by
ripple-band localization, not histology.

---

## A. Is this really CA1?

1. [ripple_examples.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/ripple_examples.png)
   — real sharp-wave ripples.
2. [ripple_localization_by_shank.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/ripple_localization_by_shank.png)
   — ripple-band power peaks at one section/depth = the data-driven detection channel, in
   **both** sessions. The "CA1-like" figure.

## B. The robust result — single-unit, artifact-resistant

3. [spike_onoff_cross_dataset.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/spike_onoff_cross_dataset.png)
   — headline: single-unit ON/OFF firing, Dec 3 null vs Dec 4 50 Hz responders in both regions.
4. [raster_psth_examples_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_psth_examples_dec4.png)
   — example of modulated units in dHPC and LEC (spikes per trial, with the never-stimulated
   pre-study baseline).
5. [psth_population_modulated_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/psth_population_modulated_dec4.png)
   — population PSTH for the modulated units.
6. [raster_psth_all_good_units_combined.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_psth_all_good_units_combined.png)
   — every curated unit: Dec 3 null + Dec 4 together, on one shared scale.
7. [psth_frequency_specific_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/psth_frequency_specific_dec4.png)
   — the response is concentrated at 50 Hz vs the other carrier frequencies.
8. [raster_frequency_specific_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/raster_frequency_specific_dec4.png)
   — raster version of the frequency-specificity result.

## C. Did you catch your own artifact / are you overclaiming?

9. [50hz_pickup_gradient_dhpc_vs_lec.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png)
   — disconnected channels carry the 50 Hz LFP ~6× → the LFP effect is largely pickup.
10. [spectral_slope_itpc_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png)
   — a narrowband 50 Hz peak above 1/f in LEC, **but ITPC at chance** = induced, not
   entrained. This is his distinction (steady-state ≠ entrainment); showing it pre-empts the
   objection.

## D. Further dig — hold in reserve

11. [unit87_acg_artifact_screen.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/unit87_acg_artifact_screen.png)
   — the soft-spot unit passes the ACG/ISI screens (rate change is a real neuron). Relevant
   because **all LEC units sit on 50 Hz-contaminated channels**, so this is the spike-level defense.
12. [fiftyhz_tissue_contamination_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/12_ChannelQC_Traces/fiftyhz_tissue_contamination_dec4.png)
    + [unit_by_shank_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/unit_by_shank_dec4.png)
    — the spatial story: 50 Hz pickup reaches a third of the *good* LEC tissue channels too
    (not only the dead ones); dHPC responders span sections.
13. [trial_avg_spectrogram_dec4.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec4.png)
    — LEC has a 50 Hz band that grows with amplitude; dHPC has none (only broadband
    suppression). Show *after* the artifact figures, not before.
14. [dec4_celltype.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/dec4_celltype.png)
    — units separate cleanly into putative pyramidal vs interneuron by trough-to-peak width ×
    firing rate, with sensible mean waveforms (LEC interneuron n = 2).
15. [spike_50hz_interpretation.png](https://github.com/wehabit/hpaticmousebuzsakilab/blob/main/results/dec4/11_Spikes/spike_50hz_interpretation.png)
    — the bidirectional, region-specific result (dHPC has a driven-up subset, LEC is
    net-suppressed → opposite transforms of the same input = active processing, not a passive
    relay).

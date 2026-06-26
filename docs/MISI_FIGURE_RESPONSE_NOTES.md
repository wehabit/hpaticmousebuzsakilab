# Misi Figure Questions — Combined Explainer And Spectrogram

This note is the presentation-safe answer to two figure questions:

1. `combined_explainer.png`: why was the highest amplitude not always the most
   efficient?
2. `trial_avg_spectrogram_dec4.png`: can we show a trial-averaged spectrogram,
   and do we need to crop out 60 Hz?

## Short Answer

The amplitude answer is **session- and measure-specific**.

For **Dec 3**, the combined explainer shows a nonlinear LFP result:
`amp180_freq26` gives the clearest broadband/recovery response, while
`amp250_freq26` is more offset-heavy and adapts downward. So Dec 3 is **not** a
clean "higher amplitude = stronger response" story. The honest interpretation is
that the Dec 3 response depends on timing window and recovery dynamics, and we
cannot separate neural nonlinearity from actuator/skin-delivery nonlinearity
because the delivered vibration waveform was not recorded.

For **Dec 4 at 50 Hz**, the dose-response is clearer: LEC 50 Hz LFP power grows
with amplitude, and the dHPC single-unit drive is strongest at amp250. The main
exception is LEC single-unit suppression, where amp180 looks more negative than
amp250; that is small-n and drift-confounded, so do not lean on it as a robust
inverted-U result.

## Dec 4 50 Hz Dose-Response Check

| measure | amp100 | amp180 | amp250 | interpretation |
|---|---:|---:|---:|---|
| LEC 50 Hz LFP driven power | +0.28 | +0.71 | +1.26 log2 | monotonic measured LFP increase |
| LEC 50 Hz residual above 1/f | +0.35 | +0.48 | +0.64 | monotonic narrowband bump |
| LEC 50 Hz ITPC | 0.052 | 0.069 | 0.080 | all near chance; not entrainment |
| dHPC single-unit ON−OFF | −0.12 | −0.00 | +0.79 Hz | amp250 is strongest |
| LEC single-unit ON−OFF | +0.02 | −0.20 | −0.05 Hz | non-monotonic; small-n/drift caveat |

Important caveat: the LEC 50 Hz **LFP** increase is a real measured spectral
line, but artifact-suspect. It should not be presented as clean neural
entrainment. The cleaner Dec 4 neural readout is the curated single-unit
firing-rate effect.

## Spike Figure Set: Dec 4 Effect vs Dec 3 Null

Use these as the matched figure set when answering "show a raster or PSTH for the
modulated neurons." The Dec 4 figures show the 50 Hz/high-amplitude effect; the
Dec 3 figures show the same style of readout for the 5/26 Hz null-control session.

| purpose | Dec 4 effect | Dec 3 null control | what it shows |
|---|---|---|---|
| Example raster + PSTH | [`raster_psth_examples_dec4.png`](../results/dec4/11_Spikes/raster_psth_examples_dec4.png) | [`raster_psth_dec3_null.png`](../results/dec3/11_Spikes/raster_psth_dec3_null.png) | A few individual units, with trial-by-trial spike rasters above the averaged PSTH. |
| All curated units (combined 3-row heatmap) | [`raster_psth_all_good_units_combined.png`](../results/dec4/11_Spikes/raster_psth_all_good_units_combined.png) — top 2 rows = Dec 4 dHPC + LEC @ 50 Hz | bottom row = Dec 3 dHPC @ 26 Hz, **same figure** | One shared color/bar-scale heatmap of every curated good unit across both sessions: Dec 4 dHPC 9/15 responsive (clear 50 Hz ON column), Dec 4 LEC 3/15 (principal-cell suppression), Dec 3 dHPC 0/29 at `amp250_freq26` (0/174 across all conditions) — a flat null with no ON-driven column. Per-session versions: [`raster_psth_all_good_units_dec4.png`](../results/dec4/11_Spikes/raster_psth_all_good_units_dec4.png) · [`raster_psth_all_good_units_dec3.png`](../results/dec3/11_Spikes/raster_psth_all_good_units_dec3.png). Full statistics in [`DEC3_CURATED_SPIKE_RESULT.md`](DEC3_CURATED_SPIKE_RESULT.md). |
| Population PSTH | [`psth_population_modulated_dec4.png`](../results/dec4/11_Spikes/psth_population_modulated_dec4.png) | [`psth_dec3_null_control.png`](../results/dec3/11_Spikes/psth_dec3_null_control.png) | Average time-course across the modulated/strongest-condition units: Dec 4 changes during ON, Dec 3 stays flat. |
| Frequency-specificity | [`psth_frequency_specific_dec4.png`](../results/dec4/11_Spikes/psth_frequency_specific_dec4.png) and [`raster_frequency_specific_dec4.png`](../results/dec4/11_Spikes/raster_frequency_specific_dec4.png) | Same Dec 3 null-control PSTH/raster above; Dec 3 only had `5`/`26` Hz. | Dec 4 modulation is concentrated at `50` Hz; lower-frequency conditions do not show the same effect. |
| 50 Hz cycle-following check | [`acg_50hz_following_dec4.png`](../results/dec4/11_Spikes/acg_50hz_following_dec4.png) | Not applicable; Dec 3 did not include 50 Hz. | Tests whether 50 Hz-responsive units fire in a 20 ms comb. Current result supports firing-rate modulation, not proven spike frequency-following. |

## Raw-ish LFP Example Answer

If the question is "can you show a more raw LFP example?", do **not** use the
spectrogram or driven-power bar plot as the first answer. Those are useful
summaries, but they are not raw-looking LFP.

Use
[raw_lfp_time_domain_examples_dec4.png](../results/dec4/04_EventAligned_LFP/raw_lfp_time_domain_examples_dec4.png).
It shows representative Dec 4 dHPC and LEC time-domain LFP traces before the
spectral summaries: single-trial `amp250_freq50` examples on top, and
trial-averaged high-amplitude LFP traces across `5`/`10`/`26`/`50` Hz underneath.
These traces are baseline-subtracted and scaled to microvolts. They are still LFP
examples, not proof of entrainment, and the LEC 50 Hz LFP remains artifact-suspect.

Email-safe wording:

> You are right that the old channel heatmap is not an intuitive figure. I would
> not lead with it. I added a time-domain LFP example panel showing actual
> baseline-subtracted LFP traces around vibration onset, plus trial-averaged LFP
> traces across the high-amplitude conditions. Then I would use the spectrogram
> as the spectral summary, not as the raw example.

## Spectrogram Answer

Use [trial_avg_spectrogram_dec4.png](../results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec4.png).
It is a **1–100 Hz** trial-averaged spectrogram around ON onset. For the Dec 3
comparison, use
[trial_avg_spectrogram_dec3.png](../results/dec3/05_Frequency_Spectral/trial_avg_spectrogram_dec3.png),
which uses the same color scale and time/frequency window for the Dec 3 dHPC
`5` and `26` Hz conditions.
For the direct shared-frequency comparison across sessions/regions, use
[trial_avg_spectrogram_dec3_dec4_freq5_26.png](../results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec3_dec4_freq5_26.png):
Dec 3 dHPC, Dec 4 dHPC, and Dec 4 LEC at `5` and `26` Hz on one shared scale.

The 60 Hz line is minimal in this figure, so there is no need to crop to 1–40 Hz.
Sanity check from the same spectrogram method:

| panel | 60 Hz / neighboring bins | 60 Hz ON-vs-baseline |
|---|---:|---:|
| LEC amp100 freq50 | 1.045× | +0.16 dB |
| LEC amp180 freq50 | 0.985× | +0.03 dB |
| LEC amp250 freq50 | 1.004× | +0.07 dB |
| dHPC amp250 freq50 | 0.993× | −0.49 dB |

What the spectrogram shows:

- LEC has a 50 Hz band that grows from amp100 to amp250.
- dHPC does not show a comparable induced 50 Hz band.
- The matched Dec 3 dHPC spectrogram does not show a clean sustained
  commanded-frequency band at `26` Hz; it looks more broadband/state-like than
  frequency-following.
- The shared `5`/`26` Hz Dec 3-vs-Dec 4 comparison similarly does not reveal a
  clean, sustained commanded-frequency band like the Dec 4 LEC `50` Hz panel.
- The figure supports "measured 50 Hz LFP power grows with amplitude in LEC,"
  not "proven entrainment."

## Email-Safe Wording

> The amplitude story depends on which result we are discussing. In Dec 3,
> `amp180_freq26` produced the clearest broadband/recovery LFP response, while
> `amp250_freq26` was more offset-heavy and adapted downward, so I would not call
> Dec 3 a monotonic dose-response. That may reflect neural nonlinearity, recovery
> dynamics, or delivered-stimulus nonlinearity; without the recorded vibration
> waveform we cannot separate those.
>
> In Dec 4 at 50 Hz, the dose-response is clearer: LEC 50 Hz LFP power increases
> with amplitude, and dHPC single-unit drive is strongest at amp250. The one
> non-monotonic piece is LEC single-unit suppression, where amp180 looks larger
> than amp250, but that is small-n and drift-confounded. The spectrogram is
> 1–100 Hz, and the 60 Hz line is minimal, so I would keep the 1–100 Hz version.
> I would present the LEC 50 Hz LFP as a real measured, artifact-suspect spectral
> line, and the single-unit result as the cleaner neural readout.

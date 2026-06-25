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

## Spectrogram Answer

Use [trial_avg_spectrogram_dec4.png](../results/dec4/05_Frequency_Spectral/trial_avg_spectrogram_dec4.png).
It is a **1–100 Hz** trial-averaged spectrogram around ON onset.

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

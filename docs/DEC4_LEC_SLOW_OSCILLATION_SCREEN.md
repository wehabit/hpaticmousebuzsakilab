# Dec 4 — LEC Slow-Oscillation / UP-DOWN-Compatible Screen

This is a **figure + table** physiology check added after Vöröslakos's metadata reply.
His practical criterion was: dHPC ripples support CA1/dHPC placement; cortical
UP/DOWN states and slow oscillations support cortex/LEC placement.

## What was tested

- Session: Dec 4, two-probe recording.
- Regions: dHPC channels `0-127`; LEC channels `128-255`.
- Bad channels excluded using `analysis/bad_channels_dec4.json`.
- Windows: quiet non-stimulation periods only:
  - baseline: `1886.78-2786.78 s`
  - post-study: `17183.78-18135.64 s`
- Method: median LFP across good channels, Welch spectra, and 0.5-4 Hz
  slow-deflection counts. Script:
  [lec_slow_oscillation_screen_dec4.py](../analysis/lec_slow_oscillation_screen_dec4.py).
- Figure:
  [lec_slow_oscillation_screen_dec4.png](../results/dec4/12_ChannelQC_Traces/lec_slow_oscillation_screen_dec4.png).

## Result

| region | state | slow peak | slow/delta-to-theta ratio | negative slow-deflection rate |
|---|---:|---:|---:|---:|
| dHPC | baseline | 1.44 Hz | 1.15 | 0.89/s |
| dHPC | post | 2.44 Hz | 1.38 | 0.90/s |
| LEC | baseline | 2.38 Hz | 24.63 | 0.34/s |
| LEC | post | 2.25 Hz | 24.31 | 0.45/s |

Plain English: the LEC quiet-window LFP is strongly slow/delta-dominant relative
to theta, and this is stable in both baseline and post-study. The dHPC comparator
does not have that cortex-like slow/delta dominance because theta remains strong.

This is the **soft** LEC/cortex support test. It asks whether LEC quiet-state LFP
has cortex-like slow/delta dominance compared with dHPC. The stricter test asks
whether we can see stereotyped UP/DOWN-state alternation in awake baseline/post
data; that stricter image is
[lec_updown_states_dec4.png](../results/dec4/12_ChannelQC_Traces/lec_updown_states_dec4.png)
and should be described as negative/limited.

## Interpretation

This **supports the LEC/cortex functional placement criterion** from Vöröslakos:
LEC shows cortical slow-oscillation / UP-DOWN-compatible physiology, while dHPC
is independently supported by ripple physiology.

Keep the wording honest: this is **not** formal sleep scoring, not a laminar
UP/DOWN-state analysis, and not histological reconstruction. It closes the
region-level sanity check; it does **not** justify fine depth, laminar,
medial/lateral, or subregion claims.

## Outputs

- `analysis/outputs/dec4/lec_slow_oscillation_screen/slow_oscillation_summary.csv`
- `analysis/outputs/dec4/lec_slow_oscillation_screen/slow_oscillation_spectra.csv`
- `analysis/outputs/dec4/lec_slow_oscillation_screen/slow_deflection_events.csv`
- `analysis/outputs/dec4/lec_slow_oscillation_screen/lec_slow_oscillation_screen_dec4.png`
- `analysis/outputs/dec4/lec_slow_oscillation_screen/run_summary.json`

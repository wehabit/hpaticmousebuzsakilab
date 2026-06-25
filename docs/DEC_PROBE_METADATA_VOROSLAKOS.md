# Probe / Channel Metadata From Vöröslakos Reply

This note records the collaborator metadata update that supersedes the older
"provisional channel-map" caveat in the front-page documents.

## Confirmed

| item | current metadata |
|---|---|
| dHPC probe | Cambridge NeuroTech `H12_2` |
| LEC probe | Cambridge NeuroTech `H15` |
| Dec 4 channel ranges | dHPC = Intan `0-127` (`1-128` in 1-indexed lab notation); LEC = Intan `128-255` (`129-256`) |
| Dec 4 XML grouping | `amplifier.xml` `channelGroups` order is the verified order; each group is a shank/group |
| LEC coordinate | AP `3.8 mm`, ML `3.8 mm`, depth as needed, angle `10 degrees` |
| dHPC coordinate | AP `1.8 mm`, ML `1.5 mm`, depth `1-1.8 mm` |
| reference / ground | stainless steel over cerebellum; ground and reference tied together |
| probe maps | Cambridge NeuroTech ASSY-350 maps for `H15` and `H12/L13`; H15 PDF: https://www.cambridgeneurotech.com/assets/files/ASSY-350-H15-map.pdf |

The current Dec 3 analysis uses the corrected 128-channel dHPC/Port A recording.
If an alternate Dec 3 256-channel file exists outside this repository, it is not
the file analyzed in the current Dec 3 result set.

## Functional Placement Criteria

- dHPC / CA1: ripple physiology supports CA1/dHPC placement by Vöröslakos's
  criterion. See [DEC_RIPPLE_STATES.md](DEC_RIPPLE_STATES.md).
- LEC / cortex: slow-oscillation / UP-DOWN-compatible quiet-state physiology
  supports cortex/LEC placement by Vöröslakos's criterion. See
  [DEC4_LEC_SLOW_OSCILLATION_SCREEN.md](DEC4_LEC_SLOW_OSCILLATION_SCREEN.md).

## Still Conservative

- Bad channels should still receive final manual Neuroscope review.
- Fine site-order, depth, laminar, medial/lateral, CA1-vs-DG/subiculum, and
  per-contact anatomy claims still need implant orientation and/or histology.
- The metadata improves region-level interpretation; it does not fix the missing
  analog stimulus waveform needed for true entrainment tests.

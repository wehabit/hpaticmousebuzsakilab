# Study Notes

This file preserves the experimental notes that used to live in the root
README. The root README is now a clean project entry point; these notes remain
here for context and future reference.

## Study Images

Images from the experiment:

- https://photos.app.goo.gl/NzK9YqrbCPufYTYV8

## December 4: One Mouse, Two Shanks Implanted

Data shared by Mishi:

- https://drive.google.com/drive/u/3/folders/11S4fJvwI5_ZltETXopUXOIprmO7udT9G

Implant locations:

- Hippocampus (dHPC)
- Lateral Entorhinal Cortex (LEC), a gateway to hippocampus

Coordinates:

- LEC: AP `3.8 mm`, ML `3.8 mm`, depth as needed, angle `5 degrees`;
  H15 probe from Cambridge NeuroTech.
- dHPC: AP `1.8`, ML `1.5`, depth `1 to 1.8 mm`; H12_2 probe from Cambridge
  NeuroTech.
- HPC schematic:
  https://labs.gaidi.ca/mouse-brain-atlas/?ml=1.5&ap=-1.8&dv=3.2

Stimulation parameters:

- Amplitudes: `100`, `180`, `250`
- Frequencies: `5`, `10`, `26`, `50`
- Repeats: `200`

Timing:

- Pre-stimulation period: `15 minutes`
- Post-stimulation period: `>15 minutes`

Original note:

- Mishi was going to send `amplifier.dat`.
- Other files were noted here:
  https://drive.google.com/drive/u/2/folders/1KCHj2yOEkNIjX9bO9ZMiSj2WCGB7mrga

## December 3: Same Mouse, One Shank Implanted

Implant location:

- Hippocampus

Stimulation parameters:

- Amplitudes: `100`, `180`, `250`
- Frequencies: `5`, `26`
- Repeats: `200`

Timing:

- Pre-stimulation period: `15 minutes`
- Post-stimulation period: `>15 minutes`

Good/bad channel notes from original README:

- Since the LEC channel was not there, delete the following channels from the
  XML file:
  - `225 to 207`
  - `161 to 143`
- For anatomical redundancy, try to delete those too.
- For dHPC:
  - shank 1: `96 to 127`
  - shank 2: `64 to 95`
  - shank 3: `32 to 63`
  - shank 4: `0 to 31`

Correction note:

- The original note listed shank 1 as `96 to 113`, but Dec 3 has 128 valid
  amplifier channels and the corrected XML has four 32-channel groups.
- The Cambridge NeuroTech ASSY-350 H12/L13 map indicates these are most likely
  two physical shanks split into upper/lower halves, not four independent
  physical shanks:
  - Shank A upper half: `0 to 31`
  - Shank A lower half: `32 to 63`
  - Shank B upper half: `64 to 95`
  - Shank B lower half: `96 to 127`
- Exact anatomical attribution of Shank A vs Shank B depends on implant
  orientation, so it should be confirmed from surgery notes/photos or the probe
  orientation marker.

## Current Dec 3 Analysis Notes

The cleaned Dec 3 analysis lives here:

- `docs/DEC3_SUPERVISOR_SUMMARY.md`
- `docs/DEC3_RESULTS_SUMMARY.md`
- `docs/DEC3_MAJOR_IMAGES.md`
- `analysis/outputs/dec3/RESULTS_DASHBOARD.html`

The current confirmed bad channels for the Dec 3 analysis pass are:

```text
5, 6, 7, 32, 33, 34, 43, 66, 67
```

The current anatomy stance is conservative: use channel groups/provisional
physical shanks, but do not make CA1/DG/medial/lateral claims yet.

# dHPC ripple localization by shank section / depth (Dec 3 + Dec 4)

**Question:** where on the probe is ripple-band power strongest? Does the data-driven
ripple channel sit on a focal dHPC ripple-band zone?

**Answer: yes — a focal peak appears in section 1 at ~140–160 µm, and the data-driven
detection channel sits exactly on it.** Both sessions, same probe. This is a strong
internal check that the ripple channel was not arbitrary and supports **CA1-like dHPC
ripple physiology**. It does **not** prove an exact laminar identity without histology or
CSD.

Figure: [`ripple_localization_by_shank.png`](../results/dec4/11_Spikes/ripple_localization_by_shank.png) ·
table: `analysis/outputs/cross_dataset_spike_compare/ripples/ripple_localization_by_channel.csv`

## Method

For every dHPC channel (0–127) we measure ripple-band (100–250 Hz) RMS over a quiet
~3-min pre-stimulation baseline slice, then place each channel at its (section, depth):
section = 1 + ch//32, depth = (ch%32)·20 µm (four verified 32-channel XML sections,
20 µm spacing — verified against the probe metadata / `amplifier.xml` channelGroups).
The Cambridge H12/L13 map indicates these four sections are likely two physical shanks
split into upper/lower halves, so do **not** present this as four independent physical
dHPC shanks. This is the same ripple-band metric used
to pick the data-driven detection channel, now evaluated across the whole probe so the
spatial peak is visible. Bad channels are marked and excluded from the peak.

## Result

| session | detection channel | ripple-band peak channel | peak section | peak depth | peak = detection? |
|---|---|---|---|---|---|
| Dec 3 dHPC | ch 8 | ch 8 | 1 | 160 µm | **yes** |
| Dec 4 dHPC | ch 7 | ch 7 | 1 | 140 µm | **yes** |

The ripple-band power is not spread evenly: it concentrates in a narrow depth band on
**section 1**, and the independently chosen detection channel lands on that exact peak in
both sessions. A focal ripple-band maximum at one section/depth is consistent with a CA1
ripple zone; finding it twice on the same probe is strong, self-consistent evidence that
the detected ripples are genuine dHPC/CA1-like events.

## Why this matters

- Upgrades the ripple result from "real ripples on a chosen channel" to "the chosen
  channel is the probe's focal ripple-band maximum," supporting the dHPC/CA1-like reading
  more cleanly.
- The peak/detection agreement is an internal cross-check: the detection channel wasn't
  arbitrary — it is the ripple-band maximum of the probe.

## Caveats

- Depth/section are from the verified probe geometry; the **layer identity is still
  anatomical-by-inference**, not histology. Fine laminar claims (str. radiatum vs
  pyramidale boundaries) still need histology / CSD.
- The metric is baseline ripple-band RMS; a sharp-wave-triggered depth profile (averaging
  power at detected ripple times across channels) would sharpen the layer estimate further
  and is the natural next refinement.

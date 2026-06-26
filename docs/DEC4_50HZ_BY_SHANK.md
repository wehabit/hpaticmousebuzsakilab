# Dec 4 — 50 Hz LFP pickup by verified shank section / XML group

**Question:** does the Dec 4 50 Hz LFP bump track dead / disconnected / pickup-heavy
contact groups, or does it look like a clean tissue-local LFP signal? (Especially LEC.)

**Answer: it tracks pickup-heavy LEC groups, with dead channels strongest.** dHPC groups
(≈0 % dead) sit near 0; the LEC groups are 20–50 % dead and carry the 50 Hz. Tissue-good
LEC channels are also elevated, so this is not "only dead channels" — the careful reading
is that the LEC 50 Hz LFP is **pickup-contaminated**, not a clean tissue-local neural LFP.
This resolves the earlier dHPC-vs-LEC pickup gradient down to the individual verified
group/section, and keeps the headline reading: **single-unit firing is the cleaner neural
readout.**

Figure: [`fiftyhz_by_shank_dec4.png`](../results/dec4/12_ChannelQC_Traces/fiftyhz_by_shank_dec4.png) ·
table: `analysis/outputs/cross_dataset_spike_compare/lfp_50hz_by_shank/fiftyhz_by_shank_channels_dec4.csv`

## Measure

Per channel, the 50 Hz **ON−OFF band-limited envelope amplitude** (the pickup metric
already computed by the `artifact_check_50hz` screen, key `diff`). A channel is "dead" if auto-excluded
(extreme/high noise), flagged `is_bad`, or not `connected`.

Shank-count clarification: Dec 4 has **six verified XML channel groups**, not six
independent physical shanks. The Cambridge H12/L13 map indicates dHPC is best
treated as two physical shanks split into four 32-channel sections; the H15 LEC
probe contributes two 64-channel physical shanks. This figure uses the six
verified groups/sections because they are the finest reliable map units:
dHPC groups 1–4 (channels 0–127, 32/group), LEC groups 5–6 (channels 128–255,
64/group). We deliberately use ON−OFF *absolute* 50 Hz power, not the log2 ON/pre ratio —
the ratio normalizes by the noisy baseline and makes dead channels look artificially
quiet.

## Result by verified group / section

| group / section | region | % dead | 50 Hz ON−OFF envelope, tissue-good | 50 Hz ON−OFF envelope, dead |
|---|---|---:|---:|---:|
| 1 | dHPC | 0 % | −1.22 | — |
| 2 | dHPC | 0 % | −1.89 | — |
| 3 | dHPC | 0 % | −1.02 | — |
| 4 | dHPC | 3 % | +0.22 | +1.89 |
| 5 | LEC | 20 % | +3.19 | +4.90 |
| 6 | LEC | **50 %** | **+7.64** | **+37.94** |

The four dHPC sections have essentially no dead channels and little/no positive 50 Hz ON−OFF.
The LEC 50 Hz is concentrated on **group 6** (channels 192–255), which is half dead and
whose dead channels — which cannot record a neuron and act as antennas — carry ~38, while
even its tissue-good channels are elevated (~7.6). LEC group 5 is intermediate (20 % dead,
~3–5). The amount of 50 Hz a group carries tracks how dead/pickup-heavy it is.

## Why this matters

- A clean neural 50 Hz oscillation should not be strongest on disconnected channels; an
  instrumental pickup does exactly this. So the LEC 50 Hz **LFP** is much easier to explain
  as pickup-contaminated than as clean tissue-only neural signal.
- It localizes the problem: LEC group 6 is the worst, group 5 milder, dHPC clean — useful
  for siting/grounding on the next probe.
- It does **not** erase the single-unit result: spike detection is high-pass (>~300 Hz),
  and the dHPC curated units' 50 Hz rate modulation is not confined to one dHPC section
  (see [`DEC4_UNIT_BY_SHANK.md`](DEC4_UNIT_BY_SHANK.md)). The LEC units sit on tissue-good
  LEC contacts within a probe that has elevated 50 Hz pickup, so the LEC spike result should
  keep the existing artifact-control caveat.

## Caveats

- "% dead" pools auto-exclude + `is_bad` + not-connected; the exact threshold shifts the
  count slightly but not the dHPC-clean / LEC-group-6-worst ordering.
- This is a channel-health vs pickup description, not a claim about LEC laminar anatomy.
- Values are envelope-amplitude differences from the 45–55 Hz filtered signal, not dB.

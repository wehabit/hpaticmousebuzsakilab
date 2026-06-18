# Dec 3 Cluster Quality

Automated pre-curation summary for the Dec 3 Kilosort4 output.

Use `phy_review_priority.csv` as the checklist for manual Phy review. The
categories are conservative helpers, not final neuroscience claims.

- `high_confidence_ks_good`: KS-good, low contamination, enough spikes, low
  short-ISI fraction.
- `mua_candidate_review`: not KS-good, but clean enough to inspect manually.
- `manual_review`: ambiguous and should be inspected in Phy.
- `likely_noise_or_multiunit`: likely to exclude unless Phy shows otherwise.

## Over-split / merge detection

`merge_candidates.csv` and `merge_candidates_summary.json` come from
`analysis/cluster_merge_candidates_dec3.py`, which the per-cluster table above
cannot produce: it scans cluster *pairs* for the 0-lag cross-correlogram
duplication that marks one neuron over-split into several templates.

- `strong_merge` (duplication frac >= 0.5): one over-split group on Dec 3,
  templates `{90, 91, 92, 97, 104}` = a single high-rate neuron. Collapsing it
  takes 194 -> ~190 candidate units.
- None of the 19 high-confidence units are over-split duplicates of each other,
  so the count of distinct high-confidence units is unchanged by merging.
- `possible_merge` (0.2-0.5): weaker partial overlap, eyeball in Phy.

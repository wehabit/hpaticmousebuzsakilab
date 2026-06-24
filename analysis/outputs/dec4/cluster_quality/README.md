# Dec 4 LEC Cluster Quality

Automated pre-curation summary for the Dec 4 LEC Kilosort4 output.

Use `phy_review_priority.csv` as a review checklist. The categories are
conservative helpers, not final neuroscience claims. Final Dec 4 spike claims
come from the curated/merged outputs and
[`DEC4_SPIKE_ONOFF_RESULT.md`](../../../../docs/DEC4_SPIKE_ONOFF_RESULT.md).

- `high_confidence_ks_good`: KS-good, low contamination, enough spikes, low
  short-ISI fraction.
- `mua_candidate_review`: not KS-good, but clean enough to inspect manually.
- `manual_review`: ambiguous in the automated pass; only usable after review.
- `likely_noise_or_multiunit`: likely to exclude unless review shows otherwise.

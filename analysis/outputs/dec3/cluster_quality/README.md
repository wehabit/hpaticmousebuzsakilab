# Dec 3 Cluster Quality

Automated pre-curation summary for the Dec 3 Kilosort4 output.

Use `phy_review_priority.csv` as the checklist for manual Phy review. The
categories are conservative helpers, not final neuroscience claims.

- `high_confidence_ks_good`: KS-good, low contamination, enough spikes, low
  short-ISI fraction.
- `mua_candidate_review`: not KS-good, but clean enough to inspect manually.
- `manual_review`: ambiguous and should be inspected in Phy.
- `likely_noise_or_multiunit`: likely to exclude unless Phy shows otherwise.

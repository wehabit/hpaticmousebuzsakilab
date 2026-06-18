# Dec 3 High-Confidence Spike ON/OFF

This report compares three spike unit sets:

- all Kilosort clusters
- Kilosort `good` clusters
- automated high-confidence KS-good clusters from the cluster-quality report

The high-confidence subset is a cleaner exploratory analysis before manual Phy
curation. It should reduce obvious noise/multiunit contamination, but it is not
a substitute for human curation.

The CSV/PNG outputs are present, but this checkout does not currently contain
the large Kilosort `.npy` arrays needed to regenerate the spike PETH analyses
from scratch. Restore those arrays from the Modal volume or lab data store
before rerunning spike exports or PETH scripts locally.

# Dec 3 Modal Kilosort4 Output

Full-session Kilosort4 run completed on Modal.

- Run URL: `https://modal.com/apps/pardis-stanford/main/ap-98jIARtjd6sXnqLgEOCynL`
- GPU: `NVIDIA A10`
- Raw input: Dec 3 `amplifier.dat`, 128 channels, 20 kHz
- Runner elapsed time: `3165.96 s`
- Kilosort runtime: `3068.10 s`
- Total units: `194`
- Good refractory-period units: `28`
- Runner spike count: `7,370,558`
- Kilosort final summary spike count: `7,311,421`
- Mean absolute drift: `0.8 um`

Important files currently present in this checkout:

- `params.py`: Phy parameter file
- `cluster_group.tsv`: Kilosort/Phy group labels
- `cluster_KSLabel.tsv`: Kilosort labels
- `cluster_ContamPct.tsv`: contamination estimates
- `diagnostics.png`: Kilosort diagnostic figure
- `drift_amount.png`: estimated drift over time
- `drift_scatter.png`: drift scatter plot
- `spike_positions.png`: spike-position plot
- `modal_kilosort_run_summary.json`: runner summary
- `kilosort4.log`: full Kilosort log

Large Kilosort arrays needed for full local reruns are not present in this
checkout:

- `spike_times.npy`
- `spike_clusters.npy`
- `templates.npy`
- related waveform/template arrays

Restore those files from the Modal volume or lab data store before rerunning
Phy, Pynapple spike export, or spike PETH analyses from scratch.

Caveat:

This is the first full-session sort using the provisional two-shank H12_2 map
and the current confirmed bad-channel list. Use it for Phy inspection and
exploratory trial-aligned analysis. Do not make final anatomical or unit-depth
claims until the exact probe geometry/channel order is confirmed.

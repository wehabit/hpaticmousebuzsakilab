# Kilosort and Pynapple Plan for Dec 3

This note records the current spike-sorting environment decision and where
Pynapple fits in the Dec 3 analysis.

## Kilosort4 Environment Decision

Official Kilosort4 documentation says Kilosort4 is a Python spike sorter built
for GPU template matching, with Linux/Windows as the supported platforms for
running the code. The docs say macOS is only partially tested and not guaranteed
for full support. Hardware recommendations also say CPU runs are possible only
for testing, and NVIDIA GPUs are the supported/recommended path for real
sorting.

Sources checked:

- https://kilosort.readthedocs.io/en/latest/README.html
- https://kilosort.readthedocs.io/en/latest/hardware.html
- https://kilosort.readthedocs.io/en/latest/tutorials/make_probe.html
- https://kilosort.readthedocs.io/en/latest/tutorials/load_data.html

Current local machine status:

- macOS x86_64
- base environment: Python 3.12 in Anaconda
- clean Kilosort environment created: `kilosort4-dec3`
- `kilosort` imports successfully in `kilosort4-dec3`
- `torch.cuda.is_available()` is `False`
- PyTorch MPS is visible, but Kilosort4 documentation recommends/supports
  NVIDIA CUDA for real sorting

Verified package versions in `kilosort4-dec3`:

| Package | Version |
| --- | --- |
| `kilosort` | `4.1.7` |
| `spikeinterface` | `0.104.3` |
| `probeinterface` | `0.3.2` |
| `phylib` | `2.7.0` |
| `pynapple` | `0.11.3` |
| `torch` | `2.2.2` |
| `numpy` | `1.26.4` |
| `numba` | `0.65.1` |
| `llvmlite` | `0.47.0` |

Practical conclusion:

1. Use this Mac for preparation, metadata checks, probe-file checks, and small
   smoke tests.
2. Run final Kilosort4 sorting on a Linux/Windows machine with an NVIDIA GPU
   and enough local SSD space for the 51 GB `amplifier.dat` plus outputs.
3. Keep Phy in a separate environment, as Kilosort recommends, to avoid GUI and
   package conflicts.

## Clean Environment Files

Environment/setup files are in:

- `analysis/envs/kilosort4_dec3_gpu.yml`
- `analysis/envs/setup_kilosort4_dec3_gpu.sh`
- `analysis/modal_kilosort_dec3.py`
- `analysis/stage_dec3_for_modal.sh`

Local activation:

```bash
conda activate kilosort4-dec3
```

Local GUI/sanity check:

```bash
python -m kilosort
```

Important: this Mac env is for setup checks, not final sorting, because CUDA is
not available locally.

## Modal GPU Option

Modal is available locally under the `pardis-stanford` profile, and the CLI
version checked locally is `1.4.3`.

Use this workflow if we want to spend Modal credits instead of moving the data
to a lab GPU workstation:

```bash
./analysis/stage_dec3_for_modal.sh
modal run analysis/modal_kilosort_dec3.py --action check
modal run analysis/modal_kilosort_dec3.py --action run
modal volume get dec3-kilosort-data /dec3/kilosort4_results analysis/outputs/dec3/modal_kilosort4_results
```

Notes:

- The upload step sends the 51 GB `amplifier.dat` to a Modal Volume named
  `dec3-kilosort-data`.
- The `check` step builds/verifies the GPU image and confirms CUDA plus file
  visibility.
- The `run` step launches the full Kilosort4 job on an `A10G` GPU.
- This supports sorting/inspection; fine unit-depth claims still need
  site-order/orientation confirmation.

The shell script follows the official Kilosort4 install sequence:

1. create a fresh conda env with Python 3.11
2. install `kilosort[gui]`
3. install CUDA PyTorch for an NVIDIA GPU workstation
4. verify Python, Kilosort, Torch, and CUDA visibility

The full 51 GB Dec 3 sort has now been run once on Modal with the working
geometry/channel order. Use this run for inspection and curated spike/LFP
alignment, but keep exact site order/orientation as a required input before final
unit-depth or anatomical claims.

## Dec 3 Kilosort Inputs Already Prepared

Existing prep folder:

- `analysis/outputs/dec3/spike_sorting_prep/`

Important files:

- `kilosort_channel_map.mat`: working Kilosort channel map
- `channel_metadata.csv`: good/bad channel status
- `good_channels.txt`: 119 connected channels
- `bad_channels.txt`: confirmed excluded channels for this pass
- `trial_windows.csv`: ON/OFF windows for 1200 trials
- `stim_artifact_intervals.csv`: onset/offset intervals to inspect
- `phy_params.py`: minimal Phy params pointing to the raw binary

Caveat:

The current Kilosort map is enough for sorting/curation, but not enough for
final anatomical or unit-depth claims.

## Pynapple Decision

Pynapple is useful for the analysis layer after we have clean time objects:

- `nap.IntervalSet` for baseline, 3 s ON epochs, and 3 s OFF control epochs
- interval metadata for condition, amplitude, frequency, and trial number
- `nap.TsdFrame` for LFP-derived features if we want to keep time support
  attached to arrays
- `nap.TsGroup` for spike trains after Kilosort/Phy curation
- `TsGroup.restrict(...)` and `TsGroup.count(...)` for trial-wise firing-rate
  comparisons

Sources checked:

- https://pynapple.org/user_guide/01_introduction_to_pynapple.html
- https://pynapple.org/generated/pynapple.IntervalSet.html
- https://pynapple.org/generated/pynapple.TsGroup.restrict.html
- https://pynapple.org/generated/pynapple.TsGroup.count.html

The immediate Pynapple bridge is:

- `analysis/export_pynapple_dec3.py`

It exports reusable Dec 3 baseline, ON, OFF, and condition-specific interval
objects from `trial_windows.csv`.

Current exported interval status:

- output folder: `analysis/outputs/dec3/pynapple_intervals/`
- baseline: 1 interval, total `1540 s`
- ON intervals: 1200 intervals, total `3600 s`
- OFF-control intervals: 1200 intervals, total `3600 s`

## Completed Modal Kilosort4 Run

Full-session Kilosort4 completed on Modal:

- Run URL:
  `https://modal.com/apps/pardis-stanford/main/ap-98jIARtjd6sXnqLgEOCynL`
- Local output:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`
- Total units: `194`
- Good refractory-period units: `28`
- Runner summary spikes: `7,370,558`
- Kilosort final summary spikes: `7,311,421`
- Runner elapsed time: `3165.96 s`
- GPU: `NVIDIA A10`

Important files for the next analysis step:

- `spike_times.npy`
- `spike_clusters.npy`
- `cluster_group.tsv`
- `cluster_KSLabel.tsv`
- `cluster_ContamPct.tsv`
- `params.py`
- `diagnostics.png`
- `drift_amount.png`
- `drift_scatter.png`
- `spike_positions.png`

## Completed First Spike PETH / ON-OFF Pass

Script:

- `analysis/export_kilosort_pynapple_dec3.py`
- `analysis/spike_peth_on_off_dec3.py`

Output:

- `analysis/outputs/dec3/pynapple_spikes/`
- `analysis/outputs/dec3/spike_peth_on_off/index.html`

Result:

- Kilosort spikes are now exported as Pynapple `TsGroup` objects:
  - `kilosort_all_units_tsgroup.npz`
  - `kilosort_ks_good_units_tsgroup.npz`
- No KS-good unit/condition ON-vs-OFF comparison survives BH correction at
  `q < 0.05`.
- KS-good condition-average ON-minus-OFF deltas are small or negative except
  for a very small `amp100_freq26` positive mean.
- The largest positive `amp180_freq26` effects are in MUA-labeled clusters.

Consequence:

- The immediate next step is Phy inspection/curation, not final spike claims.
- After curation, rerun `analysis/spike_peth_on_off_dec3.py` or a curated-unit
  variant on accepted units.

## Next Analysis Step After Environment Setup

The next scientific step is not to claim final units yet. It is:

1. inspect the Modal Kilosort4 output in Phy
2. confirm fine H12_2 site order/orientation before unit-depth interpretation
3. inspect the exported Pynapple `TsGroup` objects
4. after Phy curation, repeat the same analysis on curated units
5. relate spike responses back to the LFP findings:
   - `amp180_freq26`: strong broadband/recovery LFP
   - `amp100_freq26`: best current 26 Hz power candidate, meaning largest
     positive 26 Hz-band power change among 26 Hz conditions, not a final
     entrainment claim
   - `amp250_freq26`: offset-heavy/adapting response

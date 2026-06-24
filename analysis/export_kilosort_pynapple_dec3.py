#!/usr/bin/env python
"""Export Dec 3 Kilosort spike trains as Pynapple TsGroup objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pynapple as nap


DEFAULT_KILOSORT_DIR = Path(
    "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
)
DEFAULT_TRIAL_WINDOWS = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/pynapple_spikes")
DEFAULT_FS = 20_000.0


def read_cluster_metadata(kilosort_dir: Path, n_clusters: int) -> pd.DataFrame:
    metadata = pd.DataFrame({"cluster_id": np.arange(n_clusters, dtype=int)})
    for filename in [
        "cluster_group.tsv",
        "cluster_KSLabel.tsv",
        "cluster_ContamPct.tsv",
        "cluster_Amplitude.tsv",
    ]:
        path = kilosort_dir / filename
        if path.exists():
            table = pd.read_csv(path, sep="\t")
            metadata = metadata.merge(table, on="cluster_id", how="left", suffixes=("", "_dup"))

    if "KSLabel" not in metadata.columns and "KSLabel_dup" in metadata.columns:
        metadata["KSLabel"] = metadata["KSLabel_dup"]
    metadata = metadata.drop(columns=[c for c in metadata.columns if c.endswith("_dup")])
    metadata["KSLabel"] = metadata.get("KSLabel", "unknown")
    metadata["is_ks_good"] = metadata["KSLabel"].eq("good")
    return metadata


def build_tsgroup(
    spike_times_s: np.ndarray,
    spike_clusters: np.ndarray,
    cluster_ids: np.ndarray,
    metadata: pd.DataFrame,
    recording_end_s: float,
) -> nap.TsGroup:
    time_support = nap.IntervalSet(start=0.0, end=recording_end_s, time_units="s")

    order = np.argsort(spike_clusters, kind="mergesort")
    sorted_clusters = spike_clusters[order]
    sorted_times = spike_times_s[order]

    data = {}
    for cluster_id in cluster_ids:
        lo = np.searchsorted(sorted_clusters, cluster_id, side="left")
        hi = np.searchsorted(sorted_clusters, cluster_id, side="right")
        data[int(cluster_id)] = nap.Ts(
            t=sorted_times[lo:hi],
            time_units="s",
            time_support=time_support,
        )

    group_metadata = metadata[metadata["cluster_id"].isin(cluster_ids)].copy()
    group_metadata = group_metadata.set_index("cluster_id", drop=False)
    return nap.TsGroup(
        data,
        time_support=time_support,
        time_units="s",
        metadata=group_metadata,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kilosort-dir", type=Path, default=DEFAULT_KILOSORT_DIR)
    parser.add_argument("--trial-windows", type=Path, default=DEFAULT_TRIAL_WINDOWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fs", type=float, default=DEFAULT_FS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    spike_times_samples = np.load(args.kilosort_dir / "spike_times.npy")
    spike_clusters = np.load(args.kilosort_dir / "spike_clusters.npy").astype(np.int64, copy=False)
    spike_times_s = spike_times_samples.astype(np.float64) / args.fs
    n_clusters = int(spike_clusters.max()) + 1

    trial_windows = pd.read_csv(args.trial_windows)
    recording_end_s = float(max(spike_times_s.max(), trial_windows["off_end_s"].max()))
    metadata = read_cluster_metadata(args.kilosort_dir, n_clusters)
    metadata.to_csv(args.output_dir / "cluster_metadata.csv", index=False)

    all_cluster_ids = metadata["cluster_id"].to_numpy(dtype=int)
    good_cluster_ids = metadata.loc[metadata["is_ks_good"], "cluster_id"].to_numpy(dtype=int)

    all_group = build_tsgroup(
        spike_times_s,
        spike_clusters,
        all_cluster_ids,
        metadata,
        recording_end_s,
    )
    all_group.save(str(args.output_dir / "kilosort_all_units_tsgroup.npz"))

    good_group = build_tsgroup(
        spike_times_s,
        spike_clusters,
        good_cluster_ids,
        metadata,
        recording_end_s,
    )
    good_group.save(str(args.output_dir / "kilosort_ks_good_units_tsgroup.npz"))

    summary = {
        "kilosort_dir": str(args.kilosort_dir),
        "trial_windows": str(args.trial_windows),
        "output_dir": str(args.output_dir),
        "fs_hz": args.fs,
        "recording_end_s": recording_end_s,
        "n_spikes": int(len(spike_times_s)),
        "n_clusters": int(n_clusters),
        "n_ks_good_clusters": int(len(good_cluster_ids)),
        "pynapple_version": nap.__version__,
        "outputs": {
            "all_units": "kilosort_all_units_tsgroup.npz",
            "ks_good_units": "kilosort_ks_good_units_tsgroup.npz",
            "metadata": "cluster_metadata.csv",
        },
        "caveat": (
            "Pynapple exports are convenience spike-time objects. The KS-good "
            "TsGroup follows Kilosort KSLabel, while final presentation claims "
            "should use the curated/merged ON/OFF analyses. Probe geometry remains "
            "provisional for depth/layer claims."
        ),
    }
    (args.output_dir / "pynapple_spike_export_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    readme = f"""# Dec 3 Pynapple Spike Export

Kilosort spike trains exported as Pynapple `TsGroup` objects. These files are
convenience objects for interval-count and PETH-style analyses; the final
presentation spike claim comes from the curated/merged ON/OFF analysis, not from
the KS-good export alone.

## Files

- `kilosort_all_units_tsgroup.npz`: all `{n_clusters}` Kilosort clusters.
- `kilosort_ks_good_units_tsgroup.npz`: `{len(good_cluster_ids)}` historical KS-good clusters.
- `cluster_metadata.csv`: Kilosort labels, optional curated `group`, contamination, amplitude, and good flag.
- `pynapple_spike_export_summary.json`: export summary.

## Example

```python
import pynapple as nap

spikes = nap.load_file("kilosort_ks_good_units_tsgroup.npz")
on = nap.load_file("../pynapple_intervals/all_on_intervals.npz")
counts = spikes.count(3.0, ep=on)
```

Caveat: the KS-good `TsGroup` follows Kilosort `KSLabel`. The final Dec 3
presentation result uses the curated/merged spike analyses: 29 curated good units
and 0/174 responsive unit-conditions. Probe geometry/channel order remains
provisional for depth/layer claims.
"""
    (args.output_dir / "README.md").write_text(readme)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Apply detected strong-merge groups to a curated copy of a Kilosort output.

Non-destructive: reads the original Kilosort directory + the merge_candidates.csv
produced by cluster_merge_candidates_dec3.py, and writes a CURATED copy to a new
directory. The originals are never modified.

For each strong-merge connected component (one over-split neuron), every member
template's spikes are reassigned to the group's target id (the member with the
most spikes), and cluster_group.tsv is rewritten accordingly.

  python analysis/apply_cluster_merges.py \
      --kilosort-dir analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results \
      --merge-csv    analysis/outputs/dec3/cluster_quality/merge_candidates.csv \
      --out-dir      analysis/outputs/dec3/curated_merged
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


def connected_components(edges: list[tuple[int, int]]) -> list[list[int]]:
    parent: dict[int, int] = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    groups: dict[int, list[int]] = {}
    for node in list(parent):
        groups.setdefault(find(node), []).append(node)
    return [sorted(v) for v in groups.values() if len(v) > 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kilosort-dir", type=Path, required=True)
    ap.add_argument("--merge-csv", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    ks, out = args.kilosort_dir, args.out_dir
    spike_clusters = np.load(ks / "spike_clusters.npy").astype(np.int64)
    counts = np.bincount(spike_clusters)

    merges = pd.read_csv(args.merge_csv)
    strong = merges[merges["flag"] == "strong_merge"]
    edges = [(int(r.cluster_a), int(r.cluster_b)) for _, r in strong.iterrows()]
    groups = connected_components(edges)

    # Target = highest-spike-count member of each group.
    remap: dict[int, int] = {}
    log_rows = []
    for g in groups:
        target = max(g, key=lambda c: counts[c] if c < len(counts) else 0)
        for c in g:
            if c != target:
                remap[c] = target
        log_rows.append({
            "merged_group": ",".join(map(str, g)),
            "target_cluster": target,
            "n_templates_merged": len(g),
            "total_spikes_after": int(sum(counts[c] for c in g if c < len(counts))),
        })

    new_clusters = spike_clusters.copy()
    for src, dst in remap.items():
        new_clusters[spike_clusters == src] = dst

    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "spike_clusters.npy", new_clusters)

    # Rewrite cluster_group.tsv: drop merged-away ids, keep targets.
    grp_path = ks / "cluster_group.tsv"
    if grp_path.exists():
        grp = pd.read_csv(grp_path, sep="\t")
        grp = grp[~grp["cluster_id"].isin(remap.keys())]
        grp.to_csv(out / "cluster_group.tsv", sep="\t", index=False)

    # Copy through the remaining (unchanged) Kilosort files by reference note,
    # rather than duplicating ~GBs: symlink the directory's other files.
    for f in ks.iterdir():
        if f.name in {"spike_clusters.npy", "cluster_group.tsv"}:
            continue
        link = out / f.name
        if not link.exists():
            try:
                link.symlink_to(f.resolve())
            except OSError:
                shutil.copy2(f, link)

    pd.DataFrame(log_rows).to_csv(out / "merge_log.csv", index=False)
    summary = {
        "source_kilosort_dir": str(ks),
        "curated_dir": str(out),
        "n_merge_groups_applied": len(groups),
        "n_templates_removed": len(remap),
        "n_clusters_before": int(spike_clusters.max()) + 1,
        "n_distinct_clusters_after": int(len(np.unique(new_clusters))),
        "groups": [r["merged_group"] for r in log_rows],
        "note": "Non-destructive curated copy; other Kilosort files symlinked. "
                "Originals untouched. Re-run analyses against this dir to use merges.",
    }
    (out / "merge_apply_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

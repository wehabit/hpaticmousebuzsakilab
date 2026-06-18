#!/usr/bin/env python
"""Detect over-split / merge-candidate cluster pairs in the Dec 3 Kilosort output.

The existing cluster_quality_dec3.py grades each cluster in isolation. It cannot
see that two clusters are really one neuron that Kilosort over-split (e.g. by
amplitude or across drift). This script adds that missing layer.

Method
------
For candidate pairs (the top-K most template-similar clusters, the same ranking
Phy's SimilarityView uses) it computes the 0-lag cross-correlogram coincidence:

    n_coincident = # spike pairs (a in A, b in B) with |t_a - t_b| <= window
    expected     = n_a * (n_b / T) * 2*window         (independent Poisson)
    ratio        = n_coincident / expected

A ratio >> 1 means A and B fire at the *same instant* far more than chance.
When two clusters are each internally clean (no self ISI violations) yet share a
0-lag coincidence peak, the same physical spike is being detected twice -- the
textbook over-split signature -> they should be merged.

Outputs a ranked CSV of candidate pairs plus a JSON summary. It proposes nothing
destructive: it only flags pairs for a final human glance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_KILOSORT_DIR = Path(
    "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
)
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/cluster_quality")
DEFAULT_FS = 20_000.0


def coincidence_count(ta: np.ndarray, tb: np.ndarray, window_s: float) -> int:
    """# of (a,b) spike pairs within +/- window_s. Both arrays must be sorted."""
    lo = np.searchsorted(tb, ta - window_s, side="left")
    hi = np.searchsorted(tb, ta + window_s, side="right")
    return int(np.sum(hi - lo))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kilosort-dir", type=Path, default=DEFAULT_KILOSORT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fs", type=float, default=DEFAULT_FS)
    parser.add_argument("--window-ms", type=float, default=1.0,
                        help="coincidence half-window for the 0-lag check")
    parser.add_argument("--top-k", type=int, default=8,
                        help="candidate pairs per cluster from template similarity")
    parser.add_argument("--ratio-threshold", type=float, default=3.0,
                        help="coincidence ratio above which a pair is flagged to merge")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ks = args.kilosort_dir
    spike_times = np.load(ks / "spike_times.npy").astype(np.float64) / args.fs
    spike_clusters = np.load(ks / "spike_clusters.npy").astype(np.int64)
    sim = np.load(ks / "similar_templates.npy")  # (n_templates, n_templates)
    n_clusters = int(spike_clusters.max()) + 1
    T = float(spike_times.max() - spike_times.min())
    window_s = args.window_ms / 1000.0

    # Per-cluster sorted spike-time arrays.
    order = np.argsort(spike_clusters, kind="stable")
    sc = spike_clusters[order]
    st = spike_times[order]
    starts = np.r_[0, np.flatnonzero(np.diff(sc)) + 1]
    ends = np.r_[starts[1:], len(sc)]
    times_by_cluster: dict[int, np.ndarray] = {}
    for s, e in zip(starts, ends):
        cid = int(sc[s])
        times_by_cluster[cid] = np.sort(st[s:e])
    counts = {cid: len(t) for cid, t in times_by_cluster.items()}

    # Candidate pairs = top-K most template-similar per cluster (dedup, i<j).
    pairs: set[tuple[int, int]] = set()
    n_sim = sim.shape[0]
    for i in range(n_sim):
        if counts.get(i, 0) == 0:
            continue
        order_sim = np.argsort(sim[i])[::-1]
        taken = 0
        for j in order_sim:
            j = int(j)
            if j == i or counts.get(j, 0) == 0:
                continue
            pairs.add((min(i, j), max(i, j)))
            taken += 1
            if taken >= args.top_k:
                break

    rows = []
    for a, b in sorted(pairs):
        ta, tb = times_by_cluster[a], times_by_cluster[b]
        na, nb = len(ta), len(tb)
        small = na if na <= nb else nb
        n_coin = coincidence_count(ta if na <= nb else tb,
                                   tb if na <= nb else ta, window_s)
        expected = na * (nb / T) * 2.0 * window_s
        ratio = n_coin / expected if expected > 0 else np.nan
        rows.append({
            "cluster_a": a, "cluster_b": b,
            "n_spikes_a": na, "n_spikes_b": nb,
            "template_similarity": float(sim[a, b]),
            "n_coincident_1lag": n_coin,
            "expected_by_chance": round(expected, 2),
            "coincidence_ratio": round(ratio, 2) if np.isfinite(ratio) else np.nan,
            "coincident_frac_of_smaller": round(n_coin / small, 4) if small else np.nan,
        })

    df = pd.DataFrame(rows).sort_values("coincident_frac_of_smaller", ascending=False)
    # Decide on the *duplication fraction* (what share of the smaller cluster is
    # the same spikes as the bigger one), not the chance-ratio, which over-fires
    # for low-rate clusters. A genuine over-split duplicates most of the smaller
    # cluster; 7% overlap is two mostly-separate neurons.
    frac = df["coincident_frac_of_smaller"]
    sim_ok = df["template_similarity"] >= 0.30
    df["flag"] = "separate"
    df.loc[(frac >= 0.20) & sim_ok, "flag"] = "possible_merge"
    df.loc[(frac >= 0.50) & sim_ok, "flag"] = "strong_merge"
    out_csv = args.output_dir / "merge_candidates.csv"
    df.to_csv(out_csv, index=False)

    # Connected components over strong_merge edges => groups of templates that
    # are really one neuron. Union-find.
    parent: dict[int, int] = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        parent[find(x)] = find(y)
    strong = df[df["flag"] == "strong_merge"]
    for _, r in strong.iterrows():
        union(int(r["cluster_a"]), int(r["cluster_b"]))
    groups: dict[int, list[int]] = {}
    for node in list(parent):
        groups.setdefault(find(node), []).append(node)
    merge_groups = sorted(
        [sorted(v) for v in groups.values() if len(v) > 1], key=len, reverse=True
    )
    clusters_collapsed = sum(len(g) - 1 for g in merge_groups)  # net units removed

    # Reconcile with the per-cluster quality table (the "19 high-confidence").
    n_high_conf = n_high_conf_after = None
    hc_set: set[int] = set()
    qual_path = args.output_dir / "cluster_quality_summary.csv"
    if qual_path.exists():
        qual = pd.read_csv(qual_path)
        hc_set = set(
            qual.loc[qual["review_category"] == "high_confidence_ks_good",
                     "cluster_id"].astype(int)
        )
        n_high_conf = len(hc_set)
        # How many high-confidence clusters collapse together via strong merges?
        hc_collapsed = sum(
            len([c for c in g if c in hc_set]) - 1
            for g in merge_groups
            if len([c for c in g if c in hc_set]) > 1
        )
        n_high_conf_after = n_high_conf - hc_collapsed

    summary = {
        "kilosort_dir": str(ks),
        "n_clusters": n_clusters,
        "recording_duration_s": round(T, 1),
        "coincidence_window_ms": args.window_ms,
        "n_candidate_pairs_tested": int(len(df)),
        "n_strong_merge_pairs": int(len(strong)),
        "n_possible_merge_pairs": int((df["flag"] == "possible_merge").sum()),
        "merge_groups": merge_groups,
        "n_merge_groups": len(merge_groups),
        "clusters_removed_by_merging": int(clusters_collapsed),
        "n_clusters_after_merging": int(n_clusters - clusters_collapsed),
        "n_high_confidence_before": n_high_conf,
        "n_high_confidence_after_merging": n_high_conf_after,
        "method": "0-lag cross-correlogram duplication fraction; candidate pairs "
                  "from Kilosort template similarity (top-K).",
    }
    (args.output_dir / "merge_candidates_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))
    print("\nStrong-merge pairs (duplication frac >= 0.5):")
    cols = ["cluster_a", "cluster_b", "template_similarity", "n_spikes_a",
            "n_spikes_b", "coincidence_ratio", "coincident_frac_of_smaller", "flag"]
    print(strong[cols].to_string(index=False))


if __name__ == "__main__":
    main()

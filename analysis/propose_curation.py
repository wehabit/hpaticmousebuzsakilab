#!/usr/bin/env python
"""Turn automated metrics + merge detection into a proposed Phy curation.

This is the furthest automation can honestly push Phy curation: it assigns every
cluster a good/mua/noise label from the quality triage, folds in the detected
strong merges, and emits a short "review shortlist" of the ambiguous clusters a
human should actually open in Phy. It does NOT replace the human GUI sign-off --
it just means you confirm/override labels instead of starting from a blank slate.

Writes into the curated (post-merge) directory so it is directly Phy-openable:
  - cluster_group.tsv          proposed good/mua/noise per surviving cluster
  - proposed_cluster_group.tsv identical copy (audit trail)
  - review_shortlist.csv       the clusters to eyeball (ambiguous + merge targets)
  - curation_proposal_summary.json

  python analysis/propose_curation.py \
      --quality-csv analysis/outputs/dec3/cluster_quality/cluster_quality_summary.csv \
      --merge-csv   analysis/outputs/dec3/cluster_quality/merge_candidates.csv \
      --curated-dir analysis/outputs/dec3/curated_merged
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# review_category (from cluster_quality_dec3.py) -> proposed Phy group label.
CATEGORY_TO_GROUP = {
    "high_confidence_ks_good": "good",
    "mua_candidate_review": "mua",
    "manual_review": "mua",                 # conservative default; also shortlisted
    "likely_noise_or_multiunit": "noise",
}
# Which categories a human should actually eyeball in Phy.
SHORTLIST_CATEGORIES = {"manual_review", "mua_candidate_review"}


def connected_components(edges):
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    groups = {}
    for n in list(parent):
        groups.setdefault(find(n), []).append(n)
    return [sorted(v) for v in groups.values() if len(v) > 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality-csv", type=Path, required=True)
    ap.add_argument("--merge-csv", type=Path, required=True)
    ap.add_argument("--curated-dir", type=Path, required=True)
    args = ap.parse_args()

    qual = pd.read_csv(args.quality_csv)
    qual["cluster_id"] = qual["cluster_id"].astype(int)

    # Merge groups -> target = highest-spike-count member; others are dropped.
    merges = pd.read_csv(args.merge_csv)
    strong = merges[merges["flag"] == "strong_merge"]
    edges = [(int(r.cluster_a), int(r.cluster_b)) for _, r in strong.iterrows()]
    groups = connected_components(edges)
    spike_count = dict(zip(qual["cluster_id"], qual.get("spike_count", pd.Series(0, index=qual.index))))
    merged_away, target_of = set(), {}
    for g in groups:
        target = max(g, key=lambda c: spike_count.get(c, 0))
        for c in g:
            if c != target:
                merged_away.add(c)
        target_of[target] = g

    # Proposed label per surviving cluster.
    rows, shortlist = [], []
    for _, r in qual.iterrows():
        cid = int(r["cluster_id"])
        if cid in merged_away:
            continue
        cat = r.get("review_category", "manual_review")
        group = CATEGORY_TO_GROUP.get(cat, "mua")
        rows.append({"cluster_id": cid, "group": group})
        reason = None
        if cid in target_of:
            reason = f"merge target of {target_of[cid]} -- confirm the merge"
        elif cat in SHORTLIST_CATEGORIES:
            reason = f"{cat} -- ambiguous, confirm good/mua/noise"
        if reason:
            shortlist.append({
                "cluster_id": cid, "proposed_group": group,
                "review_category": cat,
                "spike_count": int(r.get("spike_count", 0)),
                "firing_rate_hz": round(float(r.get("firing_rate_hz", np.nan)), 3),
                "ContamPct": r.get("ContamPct", np.nan),
                "isi_violation_fraction": round(float(r.get("isi_violation_fraction", np.nan)), 4),
                "best_raw_channel": r.get("best_raw_channel", np.nan),
                "reason": reason,
            })

    out = args.curated_dir
    out.mkdir(parents=True, exist_ok=True)
    grp = pd.DataFrame(rows).sort_values("cluster_id")
    grp.to_csv(out / "cluster_group.tsv", sep="\t", index=False)
    grp.to_csv(out / "proposed_cluster_group.tsv", sep="\t", index=False)
    short = pd.DataFrame(shortlist).sort_values(["proposed_group", "cluster_id"])
    short.to_csv(out / "review_shortlist.csv", index=False)

    counts = grp["group"].value_counts().to_dict()
    summary = {
        "curated_dir": str(out),
        "n_clusters_before_merge": int(len(qual)),
        "n_templates_merged_away": len(merged_away),
        "n_surviving_clusters": int(len(grp)),
        "proposed_labels": {k: int(counts.get(k, 0)) for k in ["good", "mua", "noise"]},
        "n_on_review_shortlist": int(len(short)),
        "merge_groups_applied": [target_of[t] for t in target_of],
        "note": "Proposed automated curation. Human Phy sign-off still required; "
                "start by reviewing review_shortlist.csv in the GUI.",
    }
    (out / "curation_proposal_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if len(short):
        print(f"\nReview shortlist ({len(short)} clusters to eyeball):")
        print(short[["cluster_id", "proposed_group", "review_category",
                     "firing_rate_hz", "best_raw_channel", "reason"]].to_string(index=False))


if __name__ == "__main__":
    main()

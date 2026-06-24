#!/usr/bin/env python
"""Full CellExplorer-style autocorrelogram-TYPE classification (Dec 3 + Dec 4).

Completes the one feature the cell-type analysis explicitly had NOT done: a real
ACG-type classification. We fit each curated good unit's autocorrelogram with the
CellExplorer triple-exponential model (Petersen, Hernandez & Buzsaki 2021):

    ACG(t) = max( c*(exp(-(t-t0)/tau_decay) - d*exp(-(t-t0)/tau_rise))
                  + h*exp(-(t-t0)^2/tau_burst^2) + asymptote , 0 )

extract tau_rise / tau_decay / tau_burst / refractory, and apply the CellExplorer
3-way scheme combining waveform width with the ACG rise time:

    trough-to-peak <= 0.425 ms                      -> Narrow Interneuron
    trough-to-peak  > 0.425 ms AND tau_rise <= 6 ms -> Wide Interneuron
    trough-to-peak  > 0.425 ms AND tau_rise  > 6 ms -> Pyramidal Cell

We then compare this ACG-informed 3-way typing to the earlier width x rate 2-way
GMM ([spike_celltype_classify_dec.py]) — does the ACG rise time refine it (split out
wide interneurons)? Outputs ->
analysis/outputs/cross_dataset_spike_compare/acg_type/ and (builders)
results/dec*/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20_000.0
TTP_CUT, TAU_RISE_CUT = 0.425, 6.0          # CellExplorer defaults (ms)
NARROW, WIDE, PYR = "Narrow Interneuron", "Wide Interneuron", "Pyramidal Cell"
UNREL = "ACG-unreliable (low count)"
ACG_MIN_COUNTS = 200            # min total ACG pairs in 0-50 ms for a trustworthy tau_rise
COL = {NARROW: "#e76f51", WIDE: "#f4a261", PYR: "#2a6f97", UNREL: "#cccccc"}

DATASETS = [
    ("dec3_dHPC", "analysis/outputs/dec3/curated_merged"),
    ("dec4_dHPC", "analysis/outputs/dec4/curated_merged_dhpc"),
    ("dec4_LEC", "analysis/outputs/dec4/curated_merged_lec"),
]
FEATURES = Path("analysis/outputs/cross_dataset_spike_compare/celltype/celltype_features_by_unit.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/acg_type")


def acg_oneside(st_s, win_ms=50.0, bin_ms=0.5):
    st = np.sort(np.asarray(st_s, float)); win = win_ms / 1000.0
    right = np.searchsorted(st, st + win, side="right")
    lags = [st[i + 1:right[i]] - st[i] for i in range(len(st)) if right[i] > i + 1]
    lags = np.concatenate(lags) if lags else np.array([])
    edges = np.arange(0, win_ms + bin_ms, bin_ms)
    h, _ = np.histogram(lags * 1000, bins=edges)
    return (edges[:-1] + edges[1:]) / 2, h.astype(float)


def acg_model(t, c, tau_decay, d, tau_rise, h, tau_burst, t0, asym):
    return np.maximum(c * (np.exp(-(t - t0) / tau_decay) - d * np.exp(-(t - t0) / tau_rise))
                      + h * np.exp(-(t - t0) ** 2 / tau_burst ** 2) + asym, 0)


def fit_acg(centers, counts):
    y = counts / (counts.max() + 1e-9)
    p0 = [1.0, 20.0, 1.5, 1.0, 0.5, 5.0, 1.5, 0.3]
    lo = [0, 1, 0, 0.2, 0, 0.5, 0.3, 0]
    hi = [10, 500, 20, 50, 20, 50, 8, 5]
    try:
        popt, _ = curve_fit(acg_model, centers, y, p0=p0, bounds=(lo, hi), maxfev=20000)
        return dict(tau_decay=popt[1], tau_rise=popt[3], tau_burst=popt[5], refrac=popt[6],
                    fit=acg_model(centers, *popt) * (counts.max() + 1e-9), ok=True)
    except Exception:
        return dict(tau_decay=np.nan, tau_rise=np.nan, tau_burst=np.nan, refrac=np.nan,
                    fit=np.full_like(centers, np.nan), ok=False)


def classify(ttp, tau_rise):
    if not np.isfinite(ttp):
        return None
    if ttp <= TTP_CUT:
        return NARROW
    if not np.isfinite(tau_rise):
        return PYR                                # default broad -> pyramidal if no ACG fit
    return WIDE if tau_rise <= TAU_RISE_CUT else PYR


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    feat = pd.read_csv(FEATURES).set_index(["dataset", "cluster_id"])
    rows, acg_store = [], {}
    for name, p in DATASETS:
        d = Path(p)
        st = np.load(d / "spike_times.npy").astype(np.int64)
        sc = np.load(d / "spike_clusters.npy").astype(np.int64)
        good = pd.read_csv(d / "cluster_group.tsv", sep="\t")
        gids = good.loc[good.group == "good", "cluster_id"].to_numpy(int)
        for cid in gids:
            ts = np.sort(st[sc == cid] / FS)
            centers, counts = acg_oneside(ts)
            fr = fit_acg(centers, counts)
            ttp = float(feat.loc[(name, cid), "trough_to_peak_ms"]) if (name, cid) in feat.index else np.nan
            prev = feat.loc[(name, cid), "cell_type"] if (name, cid) in feat.index else None
            acg_total = float(counts.sum())
            reliable = acg_total >= ACG_MIN_COUNTS and fr["ok"]
            ct = classify(ttp, fr["tau_rise"]) if reliable else UNREL
            acg_store[(name, cid)] = (centers, counts, fr["fit"])
            rows.append(dict(dataset=name, cluster_id=int(cid), trough_to_peak_ms=round(ttp, 3),
                             tau_rise_ms=round(fr["tau_rise"], 3), tau_decay_ms=round(fr["tau_decay"], 2),
                             tau_burst_ms=round(fr["tau_burst"], 3), refrac_ms=round(fr["refrac"], 3),
                             acg_total_counts=int(acg_total), acg_reliable=reliable,
                             acg_fit_ok=fr["ok"], celltype_acg3=ct, celltype_width_rate2=prev))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "acg_type_by_unit.csv", index=False)

    rel = df[df.acg_reliable]
    summary = dict(n_units=len(df), n_acg_fit_ok=int(df.acg_fit_ok.sum()),
                   acg_min_counts=ACG_MIN_COUNTS, n_reliable=int(len(rel)),
                   n_unreliable_lowcount=int((~df.acg_reliable).sum()),
                   counts_3way_reliable_only=rel.celltype_acg3.value_counts().to_dict(),
                   ttp_cut_ms=TTP_CUT, tau_rise_cut_ms=TAU_RISE_CUT)
    # agreement among reliable units: do prior interneuron-like units land in the interneuron classes?
    r = rel.copy()
    r["prev_int"] = r.celltype_width_rate2 == "interneuron-like"
    r["acg_int"] = r.celltype_acg3.isin([NARROW, WIDE])
    summary["agreement_int_vs_acgInt_reliable"] = float((r.prev_int == r.acg_int).mean()) if len(r) else None
    (OUT / "acg_type_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    _fig_plane(df, OUT)
    _fig_acg_fits(df, acg_store, OUT)
    print("=== CellExplorer-style ACG-type classification ===")
    print(json.dumps(summary, indent=2))
    print("\n3-way counts by dataset:")
    print(df.groupby(["dataset", "celltype_acg3"]).size().to_string())


def _fig_plane(df, out):
    fig, ax = plt.subplots(figsize=(8, 6))
    g = df[df.tau_rise_ms.notna()]
    for ct in [PYR, WIDE, NARROW, UNREL]:
        s = g[g.celltype_acg3 == ct]
        ax.scatter(s.trough_to_peak_ms, s.tau_rise_ms, c=COL[ct], s=55,
                   alpha=0.45 if ct == UNREL else 0.9, edgecolor="white", linewidth=0.6,
                   label=f"{ct} (n={len(s)})")
    ax.axvline(TTP_CUT, color="#777", ls=":", lw=1.2)
    ax.axhline(TAU_RISE_CUT, color="#777", ls=":", lw=1.2)
    ax.text(TTP_CUT + 0.01, ax.get_ylim()[1] * 0.95, f"{TTP_CUT} ms", fontsize=8, color="#555")
    ax.text(0.02, TAU_RISE_CUT + 0.3, f"tau_rise {TAU_RISE_CUT} ms", fontsize=8, color="#555")
    ax.set_xlabel("trough-to-peak (ms)"); ax.set_ylabel("ACG tau_rise (ms)")
    ax.set_title("CellExplorer 3-way cell types: waveform width x ACG rise time")
    ax.legend(fontsize=9)
    fig.tight_layout(); fig.savefig(out / "acg_type_classification_plane.png", dpi=170); plt.close(fig)


def _fig_acg_fits(df, store, out):
    """Representative ACG + triple-exponential fit for each 3-way type."""
    picks = []
    for ct in [NARROW, WIDE, PYR]:
        g = df[(df.celltype_acg3 == ct) & df.acg_fit_ok]
        if len(g):
            r = g.iloc[len(g) // 2]
            picks.append((ct, r.dataset, int(r.cluster_id), r.tau_rise_ms))
    if not picks:
        return
    fig, axes = plt.subplots(1, len(picks), figsize=(5 * len(picks), 4))
    axes = np.atleast_1d(axes)
    for ax, (ct, ds, cid, tr) in zip(axes, picks):
        centers, counts, fit = store[(ds, cid)]
        ax.bar(centers, counts, width=0.5, color=COL[ct], alpha=0.6)
        ax.plot(centers, fit, color="#222", lw=2)
        ax.set_title(f"{ct}\n{ds} u{cid} · tau_rise={tr:.1f} ms"); ax.set_xlabel("lag (ms)"); ax.set_ylabel("count")
    fig.suptitle("Triple-exponential ACG fit (CellExplorer model) by cell type", fontsize=12)
    fig.tight_layout(); fig.savefig(out / "acg_type_fits.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()

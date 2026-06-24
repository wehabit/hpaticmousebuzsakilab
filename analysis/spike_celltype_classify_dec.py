#!/usr/bin/env python
"""CellExplorer-style putative cell-type classification (Dec 3 + Dec 4).

For every curated 'good' unit we compute, from the Kilosort templates + spike
trains (no channel-map / anatomy needed — these are waveform-shape + spike-timing
features):

  WAVEFORM (peak channel)   trough-to-peak width (ms), half-width (ms),
                            peak/trough asymmetry
  RATE                      mean firing rate (Hz)
  ACG / ISI                 burst index, refractory-violation %, CV2 of ISI

Putative type (pyramidal-like vs interneuron-like) is assigned by a 2-component
Gaussian mixture on [trough-to-peak, log10 firing rate] over the POOLED units,
with a literature trough-to-peak cut shown for reference. Narrow-waveform /
high-rate -> interneuron-like; broad / lower-rate -> pyramidal-like.

Payoff: cross-reference type with the 50 Hz single-unit response
(amp250_freq50 ON - baseline, from the baseline/post-study analysis) to ask which
cell types carry the dHPC up-drive and the LEC suppression.

NOT anatomy: this is waveform/spiking typing only. Ripple participation is
deferred (it needs ripple detection, which is gated by the provisional channel-map).

Outputs -> analysis/outputs/cross_dataset_spike_compare/celltype/ and (via the
results builders) results/dec*/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.mixture import GaussianMixture

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20_000.0
TTP_LIT_CUT_MS = 0.5          # literature-style narrow/broad trough-to-peak cut (reference only)
PYR, INT = "pyramidal-like", "interneuron-like"
C_PYR, C_INT = "#2a6f97", "#e76f51"
RNG = np.random.default_rng(0)

DATASETS = [
    ("dec3_dHPC", "analysis/outputs/dec3/curated_merged"),
    ("dec4_dHPC", "analysis/outputs/dec4/curated_merged_dhpc"),
    ("dec4_LEC", "analysis/outputs/dec4/curated_merged_lec"),
]
BASELINE_LONG = Path("analysis/outputs/cross_dataset_spike_compare/baseline_poststudy/state_comparisons_long.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/celltype")


# ---------------- feature extraction ----------------
def waveform_features(template: np.ndarray) -> dict:
    """template: (n_samples, n_channels) -> peak-channel waveform shape features."""
    ptp = np.ptp(template, axis=0)
    ch = int(ptp.argmax())
    w = template[:, ch].astype(float)
    w = w - w[:5].mean()                       # baseline to pre-spike
    trough = int(w.argmin())
    depth = -w[trough]
    if depth <= 0:                             # degenerate
        return dict(peak_channel=ch, trough_to_peak_ms=np.nan, half_width_ms=np.nan,
                    peak_trough_ratio=np.nan, waveform=w / (np.abs(w).max() + 1e-9))
    after = w[trough:]
    peak_idx = trough + int(after.argmax())
    ttp = (peak_idx - trough) / FS * 1000.0
    # half-width: width of the trough at half depth
    half = -depth / 2
    left = trough
    while left > 0 and w[left] < half:
        left -= 1
    right = trough
    while right < len(w) - 1 and w[right] < half:
        right += 1
    half_width = (right - left) / FS * 1000.0
    peak_amp = w[peak_idx]
    return dict(peak_channel=ch, trough_to_peak_ms=ttp, half_width_ms=half_width,
                peak_trough_ratio=float(peak_amp / depth),
                waveform=w / (depth + 1e-9))   # normalized to trough depth


def acg(st_s: np.ndarray, win_ms=50.0, bin_ms=0.5) -> tuple[np.ndarray, np.ndarray]:
    """Symmetric autocorrelogram (counts) over +/- win_ms."""
    st = np.sort(np.asarray(st_s, float))
    win = win_ms / 1000.0
    right = np.searchsorted(st, st + win, side="right")
    lags = [st[i + 1:right[i]] - st[i] for i in range(len(st)) if right[i] > i + 1]
    lags = np.concatenate(lags) if lags else np.array([])
    alll = np.concatenate([lags, -lags]) * 1000.0
    edges = np.arange(-win_ms, win_ms + bin_ms * 0.5, bin_ms)
    h, _ = np.histogram(alll, bins=edges)
    return h, edges


def spike_features(st_s: np.ndarray, duration_s: float) -> dict:
    isi = np.diff(np.sort(st_s))
    fr = len(st_s) / duration_s
    refr = 100.0 * np.mean(isi < 0.002) if len(isi) else np.nan
    burst = 100.0 * np.mean(isi < 0.008) if len(isi) else np.nan   # % short-ISI (bursty)
    cv2 = float(np.mean(2 * np.abs(np.diff(isi)) / (isi[:-1] + isi[1:] + 1e-12))) if len(isi) > 2 else np.nan
    return dict(firing_rate_hz=fr, refractory_pct=refr, burst_pct=burst, cv2=cv2)


def boot_ci(values, b=10_000, alpha=0.05):
    v = np.asarray(values, float); v = v[np.isfinite(v)]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    if len(v) == 1:
        return (float(v[0]),) * 3
    idx = RNG.integers(0, len(v), size=(b, len(v)))
    m = v[idx].mean(1)
    return (float(v.mean()), float(np.percentile(m, 100 * alpha / 2)),
            float(np.percentile(m, 100 * (1 - alpha / 2))))


# ---------------- main ----------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    waveforms = {}                              # (dataset, cid) -> normalized waveform
    acgs = {}                                    # (dataset, cid) -> (h, edges)

    for name, p in DATASETS:
        d = Path(p)
        templ = np.load(d / "templates.npy")
        st = np.load(d / "spike_times.npy").astype(np.int64)
        sc = np.load(d / "spike_clusters.npy").astype(np.int64)
        good = pd.read_csv(d / "cluster_group.tsv", sep="\t")
        gids = good.loc[good.group == "good", "cluster_id"].to_numpy(int)
        duration = st.max() / FS
        for cid in gids:
            wf = waveform_features(templ[cid])
            sts = st[sc == cid] / FS
            sf = spike_features(sts, duration)
            h, edges = acg(sts)
            waveforms[(name, cid)] = wf.pop("waveform")
            acgs[(name, cid)] = (h, edges)
            rows.append({"dataset": name, "cluster_id": int(cid), **wf, **sf})

    feat = pd.DataFrame(rows)

    # ---- classification: 2-component GMM on [trough-to-peak, log10 rate], pooled ----
    X = np.column_stack([feat["trough_to_peak_ms"].to_numpy(),
                         np.log10(feat["firing_rate_hz"].to_numpy())])
    Xz = (X - X.mean(0)) / X.std(0)
    gmm = GaussianMixture(n_components=2, random_state=0, n_init=10).fit(Xz)
    comp = gmm.predict(Xz)
    # component with the smaller mean trough-to-peak = interneuron-like
    ttp_by_comp = [feat["trough_to_peak_ms"].to_numpy()[comp == k].mean() for k in (0, 1)]
    int_comp = int(np.argmin(ttp_by_comp))
    feat["cell_type"] = np.where(comp == int_comp, INT, PYR)
    feat["type_posterior"] = gmm.predict_proba(Xz)[np.arange(len(feat)),
                                                   np.where(comp == int_comp, int_comp, 1 - int_comp)]
    feat["narrow_by_litcut"] = feat["trough_to_peak_ms"] < TTP_LIT_CUT_MS

    # ---- cross-reference: 50 Hz response (amp250_freq50 ON - baseline) ----
    if BASELINE_LONG.exists():
        ld = pd.read_csv(BASELINE_LONG)
        on50 = ld[(ld.comparison == "ON_vs_baseline") & (ld.condition == "amp250_freq50")][
            ["dataset", "cluster_id", "delta_hz"]].rename(columns={"delta_hz": "on50_minus_base_hz"})
        feat = feat.merge(on50, on=["dataset", "cluster_id"], how="left")

    feat.to_csv(OUT / "celltype_features_by_unit.csv", index=False)

    # ---- summary ----
    summary = {"lit_cut_ttp_ms": TTP_LIT_CUT_MS, "n_units_total": int(len(feat)), "by_dataset": {}}
    for name, _ in DATASETS:
        g = feat[feat.dataset == name]
        summary["by_dataset"][name] = {
            "n": int(len(g)),
            "n_pyramidal_like": int((g.cell_type == PYR).sum()),
            "n_interneuron_like": int((g.cell_type == INT).sum()),
            "median_ttp_ms_pyr": round(float(g.loc[g.cell_type == PYR, "trough_to_peak_ms"].median()), 3),
            "median_ttp_ms_int": round(float(g.loc[g.cell_type == INT, "trough_to_peak_ms"].median()), 3),
            "median_rate_pyr": round(float(g.loc[g.cell_type == PYR, "firing_rate_hz"].median()), 2),
            "median_rate_int": round(float(g.loc[g.cell_type == INT, "firing_rate_hz"].median()), 2),
        }
    (OUT / "celltype_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    # ---- figures ----
    _fig_pooled(feat, OUT)
    _fig_session("dec3_celltype.png", ["dec3_dHPC"], feat, waveforms, OUT,
                 "Dec 3 dHPC — putative cell types (waveform + rate)")
    _fig_session("dec4_celltype.png", ["dec4_dHPC", "dec4_LEC"], feat, waveforms, OUT,
                 "Dec 4 — putative cell types (waveform + rate)")
    _fig_acg_examples(feat, acgs, waveforms, OUT)
    if "on50_minus_base_hz" in feat.columns:
        _fig_50hz_by_type(feat, OUT)

    print("=== Putative cell-type classification ===")
    print(json.dumps(summary, indent=2))
    print("\nPer-dataset type counts:")
    print(feat.groupby(["dataset", "cell_type"]).size().to_string())


# ---------------- plots ----------------
def _scatter(ax, g):
    for t, c in ((PYR, C_PYR), (INT, C_INT)):
        s = g[g.cell_type == t]
        ax.scatter(s.trough_to_peak_ms, s.firing_rate_hz, c=c, s=42, alpha=0.85, label=t,
                   edgecolor="white", linewidth=0.5)
    ax.axvline(TTP_LIT_CUT_MS, color="#777", ls=":", lw=1)
    ax.set_yscale("log"); ax.set_xlabel("trough-to-peak (ms)"); ax.set_ylabel("firing rate (Hz)")


def _fig_pooled(feat, out):
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    markers = {"dec3_dHPC": "o", "dec4_dHPC": "s", "dec4_LEC": "^"}
    for ds, mk in markers.items():
        for t, c in ((PYR, C_PYR), (INT, C_INT)):
            s = feat[(feat.dataset == ds) & (feat.cell_type == t)]
            ax[0].scatter(s.trough_to_peak_ms, s.firing_rate_hz, c=c, marker=mk, s=46,
                          alpha=0.85, edgecolor="white", linewidth=0.5,
                          label=f"{ds} · {t.split('-')[0]}")
    ax[0].axvline(TTP_LIT_CUT_MS, color="#777", ls=":", lw=1, label=f"lit cut {TTP_LIT_CUT_MS} ms")
    ax[0].set_yscale("log"); ax[0].set_xlabel("trough-to-peak (ms)"); ax[0].set_ylabel("firing rate (Hz)")
    ax[0].set_title("Pooled feature space (marker = dataset, colour = type)")
    ax[0].legend(fontsize=7, ncol=2)
    # trough-to-peak histogram
    ax[1].hist(feat.loc[feat.cell_type == PYR, "trough_to_peak_ms"], bins=np.arange(0, 1.7, 0.1),
               color=C_PYR, alpha=0.8, label=PYR)
    ax[1].hist(feat.loc[feat.cell_type == INT, "trough_to_peak_ms"], bins=np.arange(0, 1.7, 0.1),
               color=C_INT, alpha=0.8, label=INT)
    ax[1].axvline(TTP_LIT_CUT_MS, color="#777", ls=":", lw=1)
    ax[1].set_xlabel("trough-to-peak (ms)"); ax[1].set_ylabel("units"); ax[1].legend()
    ax[1].set_title("Waveform-width distribution (GMM-labelled)")
    fig.suptitle(f"Putative cell types — {len(feat)} curated units (GMM on width × log-rate)", fontsize=13)
    fig.tight_layout(); fig.savefig(out / "celltype_classification.png", dpi=170); plt.close(fig)


def _fig_session(fname, datasets, feat, waveforms, out, suptitle):
    fig, axes = plt.subplots(2, len(datasets), figsize=(6.2 * len(datasets), 8.4), squeeze=False)
    tt = np.arange(61) / FS * 1000.0
    for j, ds in enumerate(datasets):
        g = feat[feat.dataset == ds]
        _scatter(axes[0][j], g)
        np_, ni = int((g.cell_type == PYR).sum()), int((g.cell_type == INT).sum())
        axes[0][j].set_title(f"{ds}  (pyr {np_} · int {ni})"); axes[0][j].legend(fontsize=8)
        # mean waveforms by type
        for t, c in ((PYR, C_PYR), (INT, C_INT)):
            ws = [waveforms[(ds, cid)] for cid in g.loc[g.cell_type == t, "cluster_id"]]
            if not ws:
                continue
            W = np.vstack(ws)
            m = W.mean(0)
            axes[1][j].plot(tt, m, color=c, lw=2.2, label=f"{t} (n={len(ws)})")
            axes[1][j].fill_between(tt, m - W.std(0), m + W.std(0), color=c, alpha=0.18)
        axes[1][j].set_xlabel("time (ms)"); axes[1][j].set_ylabel("norm. amplitude")
        axes[1][j].set_title(f"{ds}: mean waveform by type"); axes[1][j].legend(fontsize=8)
    fig.suptitle(suptitle, fontsize=13)
    fig.tight_layout(); fig.savefig(out / fname, dpi=170); plt.close(fig)


def _fig_acg_examples(feat, acgs, waveforms, out):
    """One representative pyr and int unit: waveform + ACG."""
    picks = []
    for t in (PYR, INT):
        g = feat[feat.cell_type == t]
        if len(g):
            # most typical: closest to the type's median trough-to-peak
            med = g.trough_to_peak_ms.median()
            r = g.iloc[(g.trough_to_peak_ms - med).abs().argmin()]
            picks.append((t, r.dataset, int(r.cluster_id)))
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    tt = np.arange(61) / FS * 1000.0
    for i, (t, ds, cid) in enumerate(picks):
        c = C_PYR if t == PYR else C_INT
        axes[i][0].plot(tt, waveforms[(ds, cid)], color=c, lw=2.2)
        axes[i][0].set_title(f"{t}: {ds} unit {cid} — waveform"); axes[i][0].set_xlabel("ms")
        h, edges = acgs[(ds, cid)]
        ctr = (edges[:-1] + edges[1:]) / 2
        axes[i][1].bar(ctr, h, width=np.diff(edges)[0], color=c, alpha=0.85)
        axes[i][1].set_title(f"{t}: {ds} unit {cid} — autocorrelogram"); axes[i][1].set_xlabel("lag (ms)")
    fig.suptitle("Representative units: narrow/fast interneuron-like vs broad pyramidal-like", fontsize=12)
    fig.tight_layout(); fig.savefig(out / "celltype_acg_examples.png", dpi=170); plt.close(fig)


def _fig_50hz_by_type(feat, out):
    dsets = [d for d in ["dec4_dHPC", "dec4_LEC"] if (feat.dataset == d).any()]
    fig, axes = plt.subplots(1, len(dsets), figsize=(6.2 * len(dsets), 4.8), sharey=True, squeeze=False)
    for ax, ds in zip(axes[0], dsets):
        g = feat[(feat.dataset == ds) & feat.on50_minus_base_hz.notna()]
        for i, (t, c) in enumerate(((PYR, C_PYR), (INT, C_INT))):
            vals = g.loc[g.cell_type == t, "on50_minus_base_hz"].to_numpy()
            if len(vals) == 0:
                continue
            m, lo, hi = boot_ci(vals)
            ax.bar(i, m, 0.6, yerr=[[m - lo], [hi - m]], capsize=4, color=c,
                   error_kw=dict(ecolor="#222", lw=1.4), label=f"{t} (n={len(vals)})")
            ax.scatter(np.full(len(vals), i) + RNG.uniform(-0.12, 0.12, len(vals)), vals,
                       color="#444", s=16, zorder=3)
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks([0, 1]); ax.set_xticklabels([PYR, INT], fontsize=9)
        ax.set_title(f"{ds}"); ax.legend(fontsize=8)
    axes[0][0].set_ylabel("amp250_freq50  ON − baseline (Hz)")
    fig.suptitle("50 Hz single-unit response by putative cell type (95% bootstrap CI)", fontsize=12)
    fig.tight_layout(); fig.savefig(out / "dec4_celltype_vs_50hz.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()

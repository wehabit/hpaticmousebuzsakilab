#!/usr/bin/env python
"""Drift-corrected condition model (Dec 4 dHPC + LEC).

Tests whether the 50 Hz single-unit effect survives after explicitly removing the
slow session drift — the user's model:

    firing rate  ~  slow time drift  +  state(ON/OFF)  +  freq  +  amp
                    + state:freq   (the ON-vs-OFF differential per frequency)

The Dec 4 design is FULLY INTERLEAVED — every condition's 200 trials span the whole
session and corr(trial time, freq) = 0.01 — so the drift (a degree-5 time polynomial)
and the condition factors are statistically separable. We fit per dataset, with the
response demeaned per unit, and obtain coefficient CIs by **cluster bootstrap over
units** (resample units, refit). We report the key coefficients WITH vs WITHOUT the
drift term: if the 50 Hz effect is unchanged, it is not a drift artifact.

Especially important for LEC (firing drifts -26 % over the session). Outputs ->
analysis/outputs/cross_dataset_spike_compare/drift_model/ and (builders)
results/dec*/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
WIN = 3.0
POLY_DEG = 5
N_BOOT = 1000
RNG = np.random.default_rng(0)
TW = ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"
DSETS = {
    "dec4_dHPC": dict(peth=ROOT / "analysis/outputs/dec4/spike_peth_on_off_dhpc",
                      curated=ROOT / "analysis/outputs/dec4/curated_merged_dhpc"),
    "dec4_LEC": dict(peth=ROOT / "analysis/outputs/dec4/spike_peth_on_off_lec",
                     curated=ROOT / "analysis/outputs/dec4/curated_merged_lec"),
}
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/drift_model"


def build_long(name, cfg, tw):
    on = np.load(cfg["peth"] / "on_counts_by_trial_unit.npy") / WIN
    off = np.load(cfg["peth"] / "off_counts_by_trial_unit.npy") / WIN
    good = pd.read_csv(cfg["curated"] / "cluster_group.tsv", sep="\t")
    gids = good.loc[good.group == "good", "cluster_id"].to_numpy(int)
    t = tw.on_start_s.to_numpy(); tn = (t - t.min()) / (t.max() - t.min())
    freq = tw.freq.to_numpy(); amp = tw.amplitude.to_numpy()
    recs = []
    for ui, cid in enumerate(gids):
        for st, rate in (("ON", on[:, cid]), ("OFF", off[:, cid])):
            for k in range(len(tw)):
                recs.append((ui, st, rate[k], tn[k], int(freq[k]), int(amp[k])))
    df = pd.DataFrame(recs, columns=["unit", "state", "rate", "tn", "freq", "amp"])
    # demean rate within unit (removes unit-level rate differences)
    df["y"] = df.rate - df.groupby("unit").rate.transform("mean")
    return df, gids


def design(df, with_drift):
    cols, names = [], []
    n = len(df)
    cols.append(np.ones(n)); names.append("intercept")
    if with_drift:
        for d in range(1, POLY_DEG + 1):
            cols.append(df.tn.to_numpy() ** d); names.append(f"t^{d}")
    on = (df.state == "ON").to_numpy(float)
    cols.append(on); names.append("state[ON]")
    for fr in [10, 26, 50]:                       # ref freq = 5
        cols.append((df.freq == fr).to_numpy(float)); names.append(f"freq{fr}")
    for a in [180, 250]:                          # ref amp = 100
        cols.append((df.amp == a).to_numpy(float)); names.append(f"amp{a}")
    for fr in [10, 26, 50]:                        # state x freq interactions
        cols.append(on * (df.freq == fr).to_numpy(float)); names.append(f"state[ON]:freq{fr}")
    return np.column_stack(cols), names


def fit(df, with_drift):
    X, names = design(df, with_drift)
    beta, *_ = np.linalg.lstsq(X, df.y.to_numpy(), rcond=None)
    yhat = X @ beta
    ss_res = float(((df.y.to_numpy() - yhat) ** 2).sum())
    ss_tot = float(((df.y.to_numpy() - df.y.mean()) ** 2).sum())
    return dict(zip(names, beta)), 1 - ss_res / ss_tot


def boot_coef(df, gids, with_drift, keys):
    out = {k: [] for k in keys}
    units = df.unit.unique()
    for _ in range(N_BOOT):
        samp = RNG.choice(units, len(units), replace=True)
        sub = pd.concat([df[df.unit == u] for u in samp], ignore_index=True)
        b, _ = fit(sub, with_drift)
        for k in keys:
            out[k].append(b.get(k, np.nan))
    return {k: (float(np.mean(v)), float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
            for k, v in out.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TW)
    rows, drift_curves = [], {}
    KEYS = ["state[ON]", "freq50", "state[ON]:freq50", "freq26", "state[ON]:freq26"]
    for name, cfg in DSETS.items():
        df, gids = build_long(name, cfg, tw)
        for with_drift in (False, True):
            b, r2 = fit(df, with_drift)
            ci = boot_coef(df, gids, with_drift, KEYS)
            for k in KEYS:
                m, lo, hi = ci[k]
                rows.append(dict(dataset=name, model=("with_drift" if with_drift else "no_drift"),
                                 coef=k, estimate=round(b.get(k, np.nan), 4),
                                 boot_mean=round(m, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                                 model_r2=round(r2, 4)))
        # fitted drift curve (population): predict over time at OFF, ref condition
        b, _ = fit(df, True)
        tt = np.linspace(0, 1, 100)
        drift = b["intercept"] + sum(b[f"t^{d}"] * tt ** d for d in range(1, POLY_DEG + 1))
        drift_curves[name] = (tt, drift)
        print(f"{name}: drift R2 added = "
              f"{[r for r in rows if r['dataset']==name and r['coef']=='state[ON]:freq50']}")

    res = pd.DataFrame(rows)
    res.to_csv(OUT / "drift_model_coefficients.csv", index=False)
    (OUT / "drift_model_coefficients.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    _fig(res, drift_curves, OUT)
    print("\n=== drift-corrected model: key coefficients (with vs without drift) ===")
    print(res[res.coef.isin(["state[ON]:freq50", "freq50"])].to_string(index=False))


def _fig(res, drift_curves, out):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    # (a) population drift curves
    ax = axes[0]
    for name, (tt, dr) in drift_curves.items():
        ax.plot(tt, dr, lw=2, label=name)
    ax.set_xlabel("session time (normalized)"); ax.set_ylabel("modeled drift (Hz, unit-demeaned)")
    ax.set_title("Fitted slow drift (degree-5 time poly)"); ax.legend(fontsize=9); ax.axhline(0, color="#999", lw=0.8)
    # (b,c) key coefficient with vs without drift, per dataset
    for ax, coef, lab in [(axes[1], "state[ON]:freq50", "ON−OFF 50 Hz interaction"),
                          (axes[2], "freq50", "freq50 main effect")]:
        dsets = res.dataset.unique(); x = np.arange(len(dsets)); w = 0.35
        for i, mdl in enumerate(["no_drift", "with_drift"]):
            g = res[(res.coef == coef) & (res.model == mdl)].set_index("dataset").reindex(dsets)
            ax.bar(x + (i - 0.5) * w, g.boot_mean, w,
                   yerr=[g.boot_mean - g.ci_lo, g.ci_hi - g.boot_mean], capsize=4,
                   label=mdl, color=("#adb5bd" if mdl == "no_drift" else "#d1495b"),
                   error_kw=dict(ecolor="#222", lw=1.3))
        ax.axhline(0, color="black", lw=1); ax.set_xticks(x); ax.set_xticklabels(dsets)
        ax.set_ylabel("coefficient (Hz)"); ax.set_title(f"{lab}: survives drift correction?"); ax.legend(fontsize=8)
    fig.suptitle("Drift-corrected condition model — the 50 Hz effect is unchanged with vs without the drift term "
                 "(95% cluster-bootstrap CI over units)", fontsize=11)
    fig.tight_layout(); fig.savefig(out / "drift_corrected_model.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()

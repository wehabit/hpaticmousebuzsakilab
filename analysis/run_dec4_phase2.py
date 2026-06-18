#!/usr/bin/env python3
"""Dec 4 phase-2: the remaining Dec 3 LFP analyses that are monkeypatch-able.

Runs (re-using the verified Dec 3 modules, only constants swapped):
  - adaptation_analysis        (early/middle/late + slope over repeats)
  - broadband_perchannel_ci    (per-channel bootstrap CI, both probes)
  - explain_sustained_vs_offset (per probe: dHPC@26Hz, LEC@50Hz)
  - margin_exclusion_test      (artifact-margin robustness, per probe)

Per-probe single-condition illustrations use the NCH/BAD trick: set BAD to also
cover the *other* probe so `good = [c for c in range(NCH) if c not in BAD]`
reduces to the responsive probe's good channels.

Run:  PYTHONPATH=analysis python analysis/run_dec4_phase2.py
"""
from __future__ import annotations

import importlib
import json
import sys
import time
import traceback
from pathlib import Path

import channel_groups_dec4 as cg

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
LFP = ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp"
SEQ = ROOT / "analysis/outputs/dec4/dec4_condition_sequence.csv"
BADJSON = ROOT / "analysis/bad_channels_dec4.json"
OUT = ROOT / "analysis/outputs/dec4"

bad = sorted(json.loads(BADJSON.read_text())["candidate_bad_channels"])
DHPC = set(range(0, 128))
LEC = set(range(128, 256))
COND_ORDER = list(cg.CONDITION_ORDER)
results = []


def run(name, module_name, argv, patches):
    print(f"\n{'='*68}\n[dec4-p2] {name}\n{'='*68}", flush=True)
    t0 = time.time()
    rec = {"step": name}
    try:
        mod = importlib.import_module(module_name)
        saved = {k: getattr(mod, k) for k in patches if hasattr(mod, k)}
        for k, v in patches.items():
            setattr(mod, k, v)
        sys.argv = [module_name + ".py"] + argv
        mod.main()
        for k, v in saved.items():
            setattr(mod, k, v)
        rec["status"] = "ok"
    except Exception as exc:  # noqa: BLE001
        rec["status"] = "error"
        rec["detail"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    rec["seconds"] = round(time.time() - t0, 1)
    print(f"[dec4-p2] {name}: {rec['status']} ({rec['seconds']}s)", flush=True)
    results.append(rec)


def main():
    # 1. Adaptation over the course of the block (reads off-control per-trial metrics).
    run("adaptation_analysis", "adaptation_analysis_dec3",
        ["--trial-metrics", str(OUT / "off_control_broadband/off_control_trial_metrics.csv"),
         "--output-dir", str(OUT / "adaptation_analysis"), "--rolling-window", "15", "--n-bootstrap", "2000"],
        {"CONDITION_ORDER": COND_ORDER})

    # 2. Per-channel broadband bootstrap CI across all 256 channels (both probes).
    run("broadband_perchannel_ci", "broadband_perchannel_ci_dec3",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--bad-channels-json", str(BADJSON),
         "--bad-channel-field", "candidate_bad_channels",
         "--output", str(OUT / "biological_summary/broadband_perchannel_ci.png"),
         "--fs", "1250", "--n-boot", "2000"],
        {"NCH": 256})

    # 3. Sustained-vs-offset explainer, per probe (dHPC at 26 Hz, LEC at 50 Hz).
    run("explain_sustained_vs_offset_dHPC", "explain_sustained_vs_offset_dec3",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--condition", "amp180_freq26",
         "--output-dir", str(OUT / "biological_summary/dHPC_amp180_freq26"), "--fs", "1250", "--max-trials", "200"],
        {"NCH": 256, "BAD": set(bad) | LEC})
    run("explain_sustained_vs_offset_LEC", "explain_sustained_vs_offset_dec3",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--condition", "amp250_freq50",
         "--output-dir", str(OUT / "biological_summary/LEC_amp250_freq50"), "--fs", "1250", "--max-trials", "200"],
        {"NCH": 256, "BAD": set(bad) | DHPC})

    # 4. Artifact-margin robustness, per probe.
    run("margin_exclusion_test_dHPC", "margin_exclusion_test_dec3",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--condition", "amp180_freq26",
         "--output-dir", str(OUT / "methods/dHPC_amp180_freq26"), "--fs", "1250", "--max-trials", "200"],
        {"NCH": 256, "BAD": set(bad) | LEC})
    run("margin_exclusion_test_LEC", "margin_exclusion_test_dec3",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--condition", "amp250_freq50",
         "--output-dir", str(OUT / "methods/LEC_amp250_freq50"), "--fs", "1250", "--max-trials", "200"],
        {"NCH": 256, "BAD": set(bad) | DHPC})

    (OUT / "dec4_phase2_run_log.json").write_text(json.dumps(results, indent=2) + "\n")
    print("\n=== Dec 4 phase-2 summary ===")
    for r in results:
        print(f"  {r['step']:34s} {r['status']:6s} {r.get('seconds')}s {r.get('detail','')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run the verified Dec 3 LFP analyses on the Dec 4 session (256 ch, 2 probes).

Approach: import each verified Dec 3 analysis module and monkeypatch ONLY its
channel-group / condition-order constants to the Dec 4 values before calling its
main(). The analysis *logic* is therefore identical to the audited Dec 3
pipeline; only the grouping (256 ch -> dHPC Port A + LEC Port B) and the 12
conditions (freqs 5/10/26/50) change.

Bad-channel handling:
  - Scripts that accept --bad-channels-json (trial stats, off-control, broadband
    transition, time-frequency, phase-locking, reference sensitivity) get the
    Dec 4 per-probe bad list and FULL group membership; they exclude internally.
  - frequency_lfp.py / artifact_aware_lfp.py have no bad-channel option, so they
    receive group dicts with bad channels already removed (CLEAN groups), which
    keeps their group means / median references clean.
  - event_aligned_lfp.py is an all-channel overview (bad channels left visible).

Run from the repo root:  PYTHONPATH=analysis python analysis/run_dec4_lfp_pipeline.py
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
SESSION = ROOT / "Haptic_Stim_session2_251204_131403"
LFP = SESSION / "amplifier.lfp"
SEQ = ROOT / "analysis/outputs/dec4/dec4_condition_sequence.csv"
BADJSON = ROOT / "analysis/bad_channels_dec4.json"
OUT = ROOT / "analysis/outputs/dec4"
FS = "1250"
NCH = "256"

bad = set(json.loads(BADJSON.read_text())["candidate_bad_channels"])
good_channels = [c for c in range(256) if c not in bad]


def clean(groups: dict) -> dict:
    return {name: [c for c in chs if c not in bad] for name, chs in groups.items()}


GROUPS_FULL = {k: list(v) for k, v in cg.ANALYSIS_GROUPS.items()}
GROUPS_CLEAN = clean(cg.ANALYSIS_GROUPS)
PROBES_FULL = {k: list(v) for k, v in cg.PHYSICAL_SHANKS.items()}
PROBES_CLEAN = clean(cg.PHYSICAL_SHANKS)
# FULL shanks must cover every channel 0-255 (artifact_aware maps each channel to a
# shank with next(); a channel missing from all shanks raises StopIteration).
SHANKS_FULL = {k: list(range(r.start, r.stop)) for k, r in cg.SHANKS.items()}
COND_ORDER = list(cg.CONDITION_ORDER)


def run(name: str, module_name: str, argv: list[str], patches: dict) -> dict:
    print(f"\n{'='*70}\n[dec4] {name}  ({module_name})\n{'='*70}", flush=True)
    t0 = time.time()
    rec = {"step": name, "module": module_name}
    try:
        mod = importlib.import_module(module_name)
        saved = {}
        for key, val in patches.items():
            if hasattr(mod, key):
                saved[key] = getattr(mod, key)
            setattr(mod, key, val)
        sys.argv = [module_name + ".py"] + argv
        mod.main()
        for key, val in saved.items():
            setattr(mod, key, val)
        rec["status"] = "ok"
    except SystemExit as exc:  # argparse / sys.exit
        rec["status"] = "exit"
        rec["detail"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        rec["status"] = "error"
        rec["detail"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    rec["seconds"] = round(time.time() - t0, 1)
    print(f"[dec4] {name}: {rec['status']} in {rec['seconds']}s", flush=True)
    return rec


def base(out_sub: str, *, bad_json: bool) -> list[str]:
    argv = ["--lfp", str(LFP), "--sequence", str(SEQ),
            "--output-dir", str(OUT / out_sub),
            "--n-channels", NCH, "--sample-rate-hz", FS]
    if bad_json:
        argv += ["--bad-channels-json", str(BADJSON), "--bad-channel-field", "candidate_bad_channels"]
    return argv


def main() -> None:
    if not LFP.exists():
        raise SystemExit(f"LFP not found: {LFP}")
    only = set(sys.argv[1:])  # optional: run only these step names
    results = []

    def step(name, *a):
        if only and name not in only:
            return
        results.append(run(name, *a))

    # 1. Event-aligned broadband overview (all channels; both probes visible).
    step(
        "event_aligned_lfp", "event_aligned_lfp",
        base("event_aligned_lfp", bad_json=False) + ["--max-trials-per-condition", "120"],
        {})

    # 2. Frequency-specific driven power. frequency_lfp maps EVERY channel to a
    # group (next()-style) and has no bad-channel option, so it needs FULL group
    # membership; group means therefore include bad channels (exploratory only, as
    # in Dec 3). Authoritative bad-excluded driven power comes from
    # reference_sensitivity / trial_level / the Dec 4 entrainment figure.
    step(
        "frequency_lfp", "frequency_lfp",
        base("frequency_lfp", bad_json=False) + ["--max-trials-per-condition", "200"],
        {"ANALYSIS_GROUPS": GROUPS_FULL, "PHYSICAL_SHANKS": PROBES_FULL})

    # 3. Time-frequency grid (bad excluded via json; FULL group membership).
    step(
        "time_frequency_lfp", "time_frequency_lfp",
        base("time_frequency_lfp", bad_json=True) + ["--max-trials-per-condition", "150", "--max-freq-hz", "80"],
        {"ANALYSIS_GROUPS": GROUPS_FULL})

    # 4. Phase locking / ITPC at the driven frequency (the entrainment test).
    step(
        "phase_locking_lfp", "phase_locking_lfp",
        base("phase_locking_lfp", bad_json=True),
        {"ANALYSIS_GROUPS": GROUPS_FULL, "PHYSICAL_SHANKS": PROBES_FULL})

    # 5. Trial-level bootstrap broadband stats (writes per-trial metrics for adaptation).
    step(
        "trial_level_stats", "trial_level_stats_dec3",
        base("trial_level_stats", bad_json=True),
        {"ANALYSIS_GROUPS": GROUPS_FULL, "CONDITION_ORDER": COND_ORDER})

    # 6. Broadband transition (onset/sustained/offset/recovery) stats.
    step(
        "broadband_transition", "broadband_transition_stats_dec3",
        base("broadband_transition", bad_json=True),
        {"ANALYSIS_GROUPS": GROUPS_FULL, "CONDITION_ORDER": COND_ORDER})

    # 7. OFF-window control broadband.
    step(
        "off_control_broadband", "off_control_broadband_dec3",
        base("off_control_broadband", bad_json=True),
        {"ANALYSIS_GROUPS": GROUPS_FULL, "CONDITION_ORDER": COND_ORDER})

    # 8. Reference-scheme sensitivity (raw / probe-median / group-median).
    step(
        "reference_sensitivity", "reference_sensitivity_lfp",
        base("reference_sensitivity", bad_json=True),
        {"ANALYSIS_GROUPS": GROUPS_FULL, "PHYSICAL_SHANKS": PROBES_FULL})

    # 9. Artifact-aware sustained response by group (CLEAN groups).
    step(
        "artifact_aware_lfp", "artifact_aware_lfp",
        ["--lfp", str(LFP), "--sequence", str(SEQ), "--output-dir", str(OUT / "artifact_aware_lfp"),
         "--n-channels", NCH, "--sample-rate-hz", FS, "--max-trials-per-condition", "100"],
        {"SHANKS": SHANKS_FULL})

    (OUT / "dec4_pipeline_run_log.json").write_text(json.dumps(results, indent=2) + "\n")
    print("\n=== Dec 4 pipeline summary ===")
    for r in results:
        print(f"  {r['step']:24s} {r['status']:6s} {r.get('seconds','?')}s  {r.get('detail','')}")


if __name__ == "__main__":
    main()

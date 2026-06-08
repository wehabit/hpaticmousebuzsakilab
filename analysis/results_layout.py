#!/usr/bin/env python3
"""Canonical Results/ folder layout for the Dec 3 haptic analysis.

One curated, human-browsable tree of figures, grouped by analysis type (the same
categories used in the review). Raw pipeline outputs still live under
analysis/outputs/dec3/<step>/ (downstream code reads them there); Results/ is the
deliverable view. New analysis scripts write straight here via results_dir().
"""
from __future__ import annotations
from pathlib import Path

RESULTS_ROOT = Path("Results")

CATEGORIES = {
    "timeline":   "01_Session_Timeline",
    "ttl":        "02_TTL_Alignment",
    "movement":   "03_Movement_DataCleaning",
    "event_lfp":  "04_EventAligned_LFP",
    "frequency":  "05_Frequency_Spectral",
    "phase":      "06_Phase_Locking",
    "broadband":  "07_Broadband_OFFcontrol_TrialStats",
    "adaptation": "08_Adaptation",
    "reference":  "09_Reference_Sensitivity",
    "biological": "10_Biological_Summary",
    "spikes":     "11_Spikes",
    "channelqc":  "12_ChannelQC_Traces",
    "teaching":   "13_Teaching_and_Methods",
}


def results_dir(category: str, subfolder: str | None = None) -> Path:
    """Return (and create) Results/<NN_Category>[/subfolder]."""
    if category not in CATEGORIES:
        raise KeyError(f"unknown results category {category!r}; valid: {sorted(CATEGORIES)}")
    d = RESULTS_ROOT / CATEGORIES[category]
    if subfolder:
        d = d / subfolder
    d.mkdir(parents=True, exist_ok=True)
    return d

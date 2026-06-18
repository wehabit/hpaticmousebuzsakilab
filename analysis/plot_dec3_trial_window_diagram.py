#!/usr/bin/env python3
"""Draw the Dec 3 trial-window definitions used by the broadband analyses."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


COLORS = {
    "pre": "#8A8F98",
    "stim": "#D4E6F7",
    "off": "#DDEDD3",
    "onset": "#D65F5F",
    "sustained": "#4C78A8",
    "offset": "#F2A340",
    "recovery": "#59A14F",
    "off_control": "#2E8B57",
    "margin": "#F6D7A7",
}


def add_block(ax, start: float, end: float, y: float, height: float, color: str, label: str, alpha: float = 0.92) -> None:
    ax.add_patch(
        Rectangle(
            (start, y),
            end - start,
            height,
            facecolor=color,
            edgecolor="white",
            linewidth=1.2,
            alpha=alpha,
        )
    )
    if label:
        ax.text(
            (start + end) / 2,
            y + height / 2,
            label,
            ha="center",
            va="center",
            fontsize=10,
            color="#1f2933",
            weight="bold",
        )


def add_interval_label(ax, start: float, end: float, y: float, text: str) -> None:
    ax.annotate(
        "",
        xy=(start, y),
        xytext=(end, y),
        arrowprops={"arrowstyle": "<->", "color": "#2f3b45", "linewidth": 1.1},
    )
    ax.text((start + end) / 2, y + 0.05, text, ha="center", va="bottom", fontsize=8.5, color="#2f3b45")


def make_figure(output: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.5, 6.4))

    ax.set_xlim(-1.85, 6.2)
    ax.set_ylim(0.0, 4.35)
    ax.set_yticks([])
    ax.set_title("Dec 3 Trial Window Definitions", fontsize=16, weight="bold", pad=14)

    for x in [-1, 0, 0.1, 2.9, 3, 3.1, 4, 5.9, 6]:
        ax.axvline(x, color="#8a949e" if x in [0, 3, 6] else "#ccd2d8", linewidth=1.2 if x in [0, 3, 6] else 0.8, zorder=0)
    ax.text(
        2.5,
        4.08,
        "Time is relative to commanded trial onset: ON starts at 0 s, OFF starts at 3 s, next trial starts at 6 s.",
        ha="center",
        va="center",
        fontsize=10.5,
        color="#37424c",
    )

    # Row 1: physical trial structure.
    ax.text(-1.78, 3.66, "Trial structure", ha="left", va="center", fontsize=11, weight="bold")
    add_block(ax, -1.0, 0.0, 3.43, 0.46, COLORS["pre"], "pre baseline\n-1-0 s")
    add_block(ax, 0.0, 3.0, 3.43, 0.46, COLORS["stim"], "stimulus ON\n0-3 s")
    add_block(ax, 3.0, 6.0, 3.43, 0.46, COLORS["off"], "within-trial OFF\n3-6 s")

    # Row 2: transition/broadband windows.
    ax.text(-1.78, 2.66, "Transition analysis", ha="left", va="center", fontsize=11, weight="bold")
    add_block(ax, -1.0, 0.0, 2.43, 0.46, COLORS["pre"], "pre\n-1-0 s")
    add_block(ax, 0.0, 0.1, 2.43, 0.46, COLORS["onset"], "", alpha=0.95)
    add_block(ax, 0.1, 2.9, 2.43, 0.46, COLORS["sustained"], "sustained ON\n0.1-2.9 s")
    add_block(ax, 2.9, 3.1, 2.43, 0.46, COLORS["offset"], "offset", alpha=0.95)
    add_block(ax, 3.1, 4.0, 2.43, 0.46, COLORS["recovery"], "recovery\n3.1-4.0 s")
    add_block(ax, 4.0, 6.0, 2.43, 0.46, "#EEF2F5", "not used here", alpha=0.65)
    ax.text(0.05, 2.96, "onset", ha="center", va="bottom", fontsize=8.5, color="#802f2f", weight="bold")

    # Row 3: full ON/OFF control windows.
    ax.text(-1.78, 1.66, "OFF-control analysis", ha="left", va="center", fontsize=11, weight="bold")
    add_block(ax, -1.0, 0.0, 1.43, 0.46, COLORS["pre"], "pre\n-1-0 s")
    add_block(ax, 0.0, 0.1, 1.43, 0.46, COLORS["margin"], "")
    add_block(ax, 0.1, 2.9, 1.43, 0.46, COLORS["sustained"], "ON window\n0.1-2.9 s")
    add_block(ax, 2.9, 3.1, 1.43, 0.46, COLORS["margin"], "skip")
    add_block(ax, 3.1, 5.9, 1.43, 0.46, COLORS["off_control"], "OFF-control window\n3.1-5.9 s")
    add_block(ax, 5.9, 6.0, 1.43, 0.46, COLORS["margin"], "")
    ax.text(0.05, 1.96, "skip", ha="center", va="bottom", fontsize=8.5, color="#806131", weight="bold")
    ax.text(5.95, 1.96, "skip", ha="center", va="bottom", fontsize=8.5, color="#806131", weight="bold")

    # Row 4: interpretation notes.
    ax.text(-1.78, 0.82, "Interpretation", ha="left", va="center", fontsize=11, weight="bold")
    ax.text(
        -1.0,
        0.78,
        "Each analysis window is compared to the 1 s pre baseline. The 100 ms margins around ON and OFF\n"
        "separate transition/artifact periods from sustained ON/OFF activity.",
        ha="left",
        va="center",
        fontsize=10,
        color="#27313a",
    )

    add_interval_label(ax, 0.0, 0.1, 3.12, "100 ms")
    add_interval_label(ax, 0.1, 2.9, 3.12, "2.8 s")
    add_interval_label(ax, 2.9, 3.1, 3.12, "200 ms")
    add_interval_label(ax, 3.1, 4.0, 3.12, "0.9 s")
    add_interval_label(ax, 3.1, 5.9, 2.12, "2.8 s")

    ax.spines[["left", "right", "top", "bottom"]].set_visible(False)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/outputs/dec3/methods/trial_window_diagram.png"),
    )
    args = parser.parse_args()
    make_figure(args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Re-run figure generators emitting editable-text SVG next to every PNG.

svg.fonttype='none' keeps text as <text> elements (editable in Illustrator / Inkscape /
Canva), and a savefig monkeypatch writes 'x.svg' whenever a script saves 'x.png'.
Run from the repo root: python export_svgs.py analysis/<script>.py [...]
"""
import sys
import runpy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"      # editable text in SVG
from matplotlib.figure import Figure

sys.path.insert(0, "analysis")
_orig = Figure.savefig


def savefig_svg_too(self, fname, *a, **k):
    _orig(self, fname, *a, **k)                    # the normal PNG
    p = Path(str(fname))
    if p.suffix.lower() == ".png":
        k2 = {kk: vv for kk, vv in k.items() if kk not in ("dpi", "pil_kwargs")}
        try:
            _orig(self, str(p.with_suffix(".svg")), format="svg", **k2)
            print("  +svg", p.with_suffix(".svg"))
        except Exception as e:                     # noqa: BLE001
            print("  svg-skip", p.name, e)


Figure.savefig = savefig_svg_too

for script in sys.argv[1:]:
    print("=== running", script)
    try:
        runpy.run_path(script, run_name="__main__")
    except Exception as e:                          # noqa: BLE001
        print("  FAILED", script, repr(e))

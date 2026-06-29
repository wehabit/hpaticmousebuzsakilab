#!/usr/bin/env python
"""Inject editable-text SVGs into the deck .pptx (PNG kept as fallback).

PowerPoint stores an SVG picture as an <asvg:svgBlip> extension on the normal <a:blip>,
next to a raster fallback. python-pptx can't add SVG, so we post-process the OOXML:
match each embedded picture to a figure by CONTENT HASH (robust to the builder renaming
files on copy) and, where an SVG with the same sibling PNG exists, attach the svgBlip.

Re-runnable: reads the clean PNG-only master (haptic_brain_talk.clean.pptx) and writes the
vector deck to haptic_brain_talk.pptx. SVGs are discovered under presentation/concept_figs
and analysis/outputs (each .svg keyed by the md5 of its sibling .png).
"""
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, "analysis")
import build_presentation_dec as B  # noqa: E402

OUT_PPTX = Path("presentation/haptic_brain_talk.pptx")
CLEAN = Path("presentation/haptic_brain_talk.clean.pptx")     # PNG-only master
WORK = Path("/private/tmp/claude-501/-Users-paris-Documents-Buzsakli-Lab-Github/5a9d16fd-6fe3-4a7b-91df-730fbdcfdf22/scratchpad/pptx_work")

CT = "http://schemas.openxmlformats.org/package/2006/content-types"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ASVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
IMG_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def deck_figure_stems():
    stems = {}
    for s in B.SLIDES:
        if s.get("fig"):
            stems[Path(s["fig"]).stem] = Path(s["fig"])
        for p, _ in (s.get("figs") or []):
            stems[Path(p).stem] = Path(p)
    return stems


def main():
    if not CLEAN.exists():
        raise SystemExit(f"clean master missing: {CLEAN} (cp the PNG-only .pptx there first)")

    # content-based: every SVG keyed by the md5 of its sibling PNG
    md5map = {}
    for svg in list(Path("presentation/concept_figs").glob("*.svg")) + list(Path("analysis/outputs").rglob("*.svg")):
        png = svg.with_suffix(".png")
        if png.exists():
            md5map[md5(png.read_bytes())] = svg.read_bytes()

    have, missing = [], []
    for stem, png in deck_figure_stems().items():
        (have if (png.exists() and md5(png.read_bytes()) in md5map) else missing).append(stem)
    print(f"SVG available for {len(have)}/{len(have) + len(missing)} deck figures.")
    for m in sorted(missing):
        print("  png-only:", m)

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(CLEAN) as z:
        z.extractall(WORK)

    ctf = WORK / "[Content_Types].xml"
    ct = etree.parse(str(ctf))
    if not any(d.get("Extension") == "svg" for d in ct.getroot().findall(f"{{{CT}}}Default")):
        d = etree.SubElement(ct.getroot(), f"{{{CT}}}Default")
        d.set("Extension", "svg"); d.set("ContentType", "image/svg+xml")
        ct.write(str(ctf), xml_declaration=True, encoding="UTF-8", standalone=True)

    slides = WORK / "ppt" / "slides"
    media = WORK / "ppt" / "media"
    counter = 0
    for sx in sorted(slides.glob("slide*.xml")):
        relsf = slides / "_rels" / (sx.name + ".rels")
        rels = etree.parse(str(relsf)); rroot = rels.getroot()
        id2tgt = {r.get("Id"): r.get("Target") for r in rroot.findall(f"{{{PR}}}Relationship")}
        st = etree.parse(str(sx)); sroot = st.getroot()
        changed = False
        for blip in sroot.iter(f"{{{A}}}blip"):
            tgt = id2tgt.get(blip.get(f"{{{R}}}embed"))
            if not tgt:
                continue
            mf = (slides / tgt).resolve()
            if not mf.exists() or mf.suffix.lower() != ".png":
                continue
            svg_bytes = md5map.get(md5(mf.read_bytes()))
            if not svg_bytes:
                continue
            counter += 1
            (media / f"svgfig{counter}.svg").write_bytes(svg_bytes)
            new_id = f"rIdSvg{counter}"
            nr = etree.SubElement(rroot, f"{{{PR}}}Relationship")
            nr.set("Id", new_id); nr.set("Type", IMG_REL); nr.set("Target", f"../media/svgfig{counter}.svg")
            extLst = blip.find(f"{{{A}}}extLst")
            if extLst is None:
                extLst = etree.SubElement(blip, f"{{{A}}}extLst")
            ext = etree.SubElement(extLst, f"{{{A}}}ext"); ext.set("uri", SVG_EXT_URI)
            sb = etree.SubElement(ext, f"{{{ASVG}}}svgBlip"); sb.set(f"{{{R}}}embed", new_id)
            changed = True
        if changed:
            st.write(str(sx), xml_declaration=True, encoding="UTF-8", standalone=True)
            rels.write(str(relsf), xml_declaration=True, encoding="UTF-8", standalone=True)

    with zipfile.ZipFile(OUT_PPTX, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(WORK.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(WORK).as_posix())
    print(f"injected {counter} SVG pictures -> {OUT_PPTX}")


if __name__ == "__main__":
    main()

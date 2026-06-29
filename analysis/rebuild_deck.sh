#!/usr/bin/env bash
# Rebuild the Dec haptics deck so the PDF always comes from the NATIVE .pptx.
#
# Why this exists: build_presentation_dec.py's own build_pdf() renders the concept
# slides from low-res matplotlib images. The good PDF is the one LibreOffice makes
# from the native .pptx (vector concept shapes + injected SVG data figures). Running
# the plain builder alone would clobber that good PDF, so use THIS instead.
#
# Steps:
#   1. build_presentation_dec.py   -> haptic_brain_talk.pptx  (native shapes, PNG data figs)
#                                     + haptic_brain_talk.pdf  (matplotlib; discarded in step 4)
#   2. snapshot that PNG-only deck -> haptic_brain_talk.clean.pptx   (master for the injector)
#   3. inject_svg_into_pptx.py     -> haptic_brain_talk.pptx  (SVG data figures attached)
#   4. soffice --convert-to pdf    -> haptic_brain_talk.pdf   (the sharp, native PDF)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

PY="$REPO/.venv-dec3/bin/python"
PRES="$REPO/presentation"
PPTX="$PRES/haptic_brain_talk.pptx"
CLEAN="$PRES/haptic_brain_talk.clean.pptx"
PDF="$PRES/haptic_brain_talk.pdf"

# Use the REAL binary, not the brew wrapper at /opt/homebrew/bin/soffice — the wrapper
# drops -env:UserInstallation, which we need to run headless alongside an open GUI and
# to avoid default-profile lock collisions.
SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
[ -x "$SOFFICE" ] || SOFFICE="$(command -v soffice || true)"
[ -x "$SOFFICE" ] || { echo "ERROR: soffice not found (brew install --cask libreoffice)"; exit 1; }

echo "==> 1/4  build native .pptx (+ throwaway matplotlib .pdf)"
"$PY" analysis/build_presentation_dec.py

echo "==> 2/4  snapshot PNG-only master -> $(basename "$CLEAN")"
cp "$PPTX" "$CLEAN"

echo "==> 3/4  inject editable-text SVG data figures"
"$PY" analysis/inject_svg_into_pptx.py

echo "==> 4/4  render PDF from the PNG master (LibreOffice headless)"
# IMPORTANT: render the CLEAN (PNG) master, NOT the SVG-injected .pptx — LibreOffice's PDF
# export HANGS rendering many injected SVGs. The PNG master looks identical in the PDF and
# converts in seconds. The injected .pptx keeps its editable-text SVGs for PowerPoint.
# Kill any stale LibreOffice first: zombies from prior runs corrupt/lock the profile and make
# the next convert HANG forever with no output (cost us many wedged builds).
pkill -9 -f "LibreOffice.app/Contents/MacOS/soffice" 2>/dev/null || true
sleep 1
# FRESH per-run profile ($$): a profile that was ever killed mid-run gets a stuck lock that
# hangs every subsequent convert. A clean profile each time is the reliable cure.
LO_PROFILE="${TMPDIR:-/tmp}/hd_lo_prof_$$"
rm -rf "$LO_PROFILE"
# Convert into a temp dir, then mv over the target — so a PDF open in Preview/LibreOffice
# can't block the write (the IO-abort 'Code:27').
TMP_OUT="$(mktemp -d)"
# Compress images on export: JPEG quality 90, downsample raster to 200 DPI. Native vector
# shapes stay vector. Without this LibreOffice re-embeds data-figure PNGs LOSSLESSLY -> ~500 MB.
FILT='pdf:impress_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"false"},"Quality":{"type":"long","value":"90"},"ReduceImageResolution":{"type":"boolean","value":"true"},"MaxImageResolution":{"type":"long","value":"200"}}'
# Synchronous warm-up: create+register the profile and PDF export filter, then exit. Doing this
# BEFORE the convert (and waiting for it to fully exit) makes the first convert honor the filter.
echo "    initializing a clean LibreOffice profile..."
"$SOFFICE" --headless -env:UserInstallation="file://$LO_PROFILE" --terminate_after_init >/dev/null 2>&1 || true
made="$TMP_OUT/haptic_brain_talk.clean.pdf"   # soffice names output after the input ($CLEAN)
convert_pdf () {
    "$SOFFICE" --headless --convert-to "$FILT" --outdir "$TMP_OUT" \
        -env:UserInstallation="file://$LO_PROFILE" "$CLEAN" >/dev/null 2>&1 &
    local spid=$!
    # Hard timeout (~120 s): a hang can never wedge the build again.
    local i
    for i in $(seq 1 40); do kill -0 "$spid" 2>/dev/null || break; sleep 3; done
    if kill -0 "$spid" 2>/dev/null; then kill -9 "$spid" 2>/dev/null; echo "    WARNING: soffice convert timed out"; fi
}
convert_pdf
# Insurance: if a pass came out huge (filter ignored), render once more.
if [ -s "$made" ] && [ "$(/usr/bin/stat -f '%z' "$made")" -gt 104857600 ]; then
    echo "    (re-rendering to apply image compression)"; rm -f "$made"; convert_pdf
fi
if [ ! -s "$made" ]; then
    echo "ERROR: LibreOffice produced no PDF; the matplotlib PDF from step 1 remains on disk."
    rm -rf "$TMP_OUT" "$LO_PROFILE"; exit 1
fi
mv "$made" "$PDF"
rm -rf "$TMP_OUT" "$LO_PROFILE"

echo "----"
for f in "$PPTX" "$PDF"; do
    sz=$(/usr/bin/stat -f '%z' "$f")
    printf "%-28s %6.1f MB\n" "$(basename "$f")" "$(echo "scale=1; $sz/1048576" | bc)"
done
echo "done — PDF is from the native pptx (sharp, matches the deck)."

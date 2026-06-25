# Dec 3 Phy Setup Notes

## Goal

Open the Dec 3 Kilosort4 output in Phy for manual curation before making
biological claims from sorted spikes.

## Environment

Conda environment:

```bash
conda create -y -n phy-dec3 python=3.11 pip
conda run -n phy-dec3 python -m pip install --upgrade git+https://github.com/cortex-lab/phy.git
```

Important note: the PyPI `phy==1.0.9` package did install, but it did not
include the `template-gui` command. The GitHub install fixed that and installed
`phy==2.0b6`.

Verified command surface:

```bash
conda run -n phy-dec3 phy --version
```

Result:

```text
phy, version 2.0b6
```

## Files

Kilosort output:

```text
analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/
```

Raw data used by Phy:

```text
Haptic_Stim_session1_251203_143031/amplifier.dat
```

`params.py` was corrected to point to the workspace-local raw data path:

```python
dat_path = ['Haptic_Stim_session1_251203_143031/amplifier.dat']
```

Launch helper:

```text
analysis/launch_phy_dec3.sh
```

## Dataset Validation

This non-GUI Phy command works:

```bash
cd "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
conda run --no-capture-output -n phy-dec3 phy template-describe params.py
```

Result:

```text
Data files              Haptic_Stim_session1_251203_143031/amplifier.dat
Duration                10644.4s
Sample rate             20.0 kHz
Data type               int16
# of channels           119
# of channels (raw)     128
# of templates          194
# of spikes             7,311,421
```

Interpretation: the Kilosort output and local raw data path are valid from
Phy's point of view.

## Current GUI Blocker

The Phy GUI starts loading, but the OpenGL views fail on this macOS/Qt setup
with shader errors like:

```text
Could not create view TemplateFeatureView.
Error in Vertex shader ... version '120' is not supported
#version required and missing
'varying' : syntax error
```

Trying `QT_OPENGL=software` did not fix it.

Interpretation: this is a local graphics/OpenGL compatibility issue, not a
problem with the Dec 3 data or Kilosort files. Phy uses an older OpenGL shader
path for several views, and the current macOS/Qt OpenGL context is rejecting
that shader profile.

## Working Commands To Retry

Foreground launch, best for seeing errors:

```bash
cd "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
conda run --no-capture-output -n phy-dec3 phy template-gui --clear-state params.py
```

Detached launch:

```bash
cd "/Users/paris/Documents/Buzsakli Lab Github"
bash analysis/launch_phy_dec3.sh
```

## Practical Next Step

Because the data validates but the GUI rendering fails locally, the cleanest
next path is one of:

- run Phy on a Linux machine or remote desktop with a compatible OpenGL context;
- try a different local Phy/Qt/OpenGL stack;
- continue with automated spike QC and treat Phy curation as pending.

This local GUI note is historical. The current Dec 3 spike result now uses the
curated/merged output set; use [DEC3_CURATED_SPIKE_RESULT.md](DEC3_CURATED_SPIKE_RESULT.md)
for presentation claims.

## Legacy Local Environment Attempt

A second, more conservative environment was created:

```bash
conda create -y -n phy-dec3-legacy python=3.10 pip
```

Installed stack:

- Python `3.10.18`
- Qt `5.15.11`
- PyOpenGL `3.1.6`
- Phy `2.0b6`

Important launch detail:

- `conda run -n phy-dec3-legacy phy ...` can hang on this Mac.
- Calling the executable directly works better:

```bash
/opt/anaconda3/envs/phy-dec3-legacy/bin/phy --version
```

Result:

```text
phy, version 2.0b6
```

The Dec 3 dataset also validates in the legacy environment:

```bash
cd "/Users/paris/Documents/Buzsakli Lab Github/analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
/opt/anaconda3/envs/phy-dec3-legacy/bin/phy template-describe params.py
```

The best local GUI attempt is:

```bash
bash "/Users/paris/Documents/Buzsakli Lab Github/analysis/launch_phy_dec3_foreground.sh"
```

Observed result:

- The legacy GUI launch gets farther than the first environment.
- macOS reported a visible `python` GUI process during the foreground test.
- The log still reports:

```text
Could not create view TemplateFeatureView.
```

Interpretation:

- The conservative environment did not fully solve the local graphics issue.
- It may be partially usable for visual inspection if the main cluster, trace,
  waveform, correlogram, or amplitude views appear.
- It is not yet a clean, fully trusted Phy curation setup because at least the
  feature view fails.

Launcher files:

- `analysis/launch_phy_dec3_foreground.sh`: confirmed best foreground command.
- `analysis/launch_phy_dec3.command`: macOS double-click/Terminal attempt.
- `analysis/launch_phy_dec3.sh`: Terminal-opening helper, but AppleScript
  automation may be blocked by macOS privacy permissions in this session.

## Modal noVNC Attempt

Because local macOS OpenGL remained unreliable, a Modal noVNC launcher was
added:

```text
analysis/modal_phy_dec3.py
```

Purpose:

- reuse the existing Modal Volume `dec3-kilosort-data`;
- avoid re-uploading the 51 GB raw `amplifier.dat`;
- start a Linux desktop with `Xvfb`, `x11vnc`, `fluxbox`, and `noVNC`;
- launch Phy inside that remote desktop;
- expose the desktop through a temporary Modal tunnel.

Command (launch detached so a disconnected client cannot kill the desktop
mid-curation):

```bash
modal run --detach analysis/modal_phy_dec3.py
```

Retrieve the browser URL after a detached launch (it is also written to the
volume, not just streamed to stdout):

```bash
modal volume get dec3-kilosort-data dec3/kilosort4_results/NOVNC_URL.txt -
```

Stop the desktop when done curating:

```bash
modal app stop <app-id> --yes
```

What the script does on Modal:

- mounts the Modal volume at `/data`;
- expects raw data at `/data/dec3/amplifier.dat`;
- expects Kilosort output at `/data/dec3/kilosort4_results`;
- writes `/data/dec3/kilosort4_results/params_modal.py` with the Modal-side
  raw-data path;
- starts noVNC on port `6080`;
- prints a temporary browser URL.

Current run status:

- Modal image build succeeded.
- noVNC endpoint responded with `HTTP 200`.
- Modal app `dec3-phy-novnc` started as an ephemeral app.
- Latest run URL:
  `https://modal.com/apps/pardis-stanford/main/ap-O0vVndFQm109iop2498p3B`
- Latest noVNC URL:
  `https://ta-01kt7qere5egsvkkgaqavqrw1g-6080-g3z4bza5hovjt0iym527zpvvd.w.modal.host/vnc.html?autoconnect=true&resize=scale`
- Phy validates the Dec 3 Kilosort output on Modal:
  - duration: `10644.4 s`
  - sample rate: `20.0 kHz`
  - raw channels: `128`
  - active channels: `119`
  - templates: `194`
  - spikes: `7,311,421`
- Earlier Modal GUI failures were fixed by adding missing Qt/X11 libraries and
  QtWebEngine sandbox flags:
  - `libnss3` for `libsmime3.so`
  - `libasound2` for `libasound.so.2`
  - extra `libxcb-*`/X11 packages for the Qt `xcb` platform plugin
  - `QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox`
  - `QTWEBENGINE_DISABLE_SANDBOX=1`
- The latest Phy log gets past dataset validation and Qt startup without the
  previous crash. Browser-side visual confirmation is still needed.

Update (2026-06-17): the launcher was hardened and re-run successfully. The
tunnel-URL print was buffered and never reached the logs under `--detach`, so
the URL is now flushed and also persisted to
`/data/dec3/kilosort4_results/NOVNC_URL.txt`. On the latest detached run the
Phy GUI log reached `model: extracting waveforms on the fly` with **no
`Could not create view` / GLSL `version '120'` shader error** -- the failure
mode that blocked the local Mac GUI and earlier Modal attempts. The Mesa
software-GL overrides (`LIBGL_ALWAYS_SOFTWARE=1`, `MESA_GL_VERSION_OVERRIDE=3.3`,
`MESA_GLSL_VERSION_OVERRIDE=330`) appear to resolve it. Final step is user
browser confirmation + the curation pass itself.

Important caveats:

- The noVNC URL is temporary and remains alive only while the Modal run is
  active.
- The URL is public-but-random; treat it like a temporary private lab link.
- This setup still needs user-side visual confirmation that Phy renders
  correctly inside the remote desktop.

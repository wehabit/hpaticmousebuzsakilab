"""Run Dec 4 Phy (per probe) in a browser-accessible Modal noVNC desktop.

Reuses the existing `dec4-kilosort-data` Modal Volume. Generalized from
modal_phy_dec3.py to take a probe (lec or dhpc).

Launch (detached so a disconnected client cannot kill the desktop mid-curation):

  modal run --detach analysis/modal_phy_dec4.py --probe dhpc
  modal run --detach analysis/modal_phy_dec4.py --probe lec

Retrieve the browser URL after a detached launch (also written to the volume):

  modal volume get dec4-kilosort-data dec4/kilosort4_results_dhpc/NOVNC_URL.txt -

Stop the desktop when done curating:

  modal app stop <app-id> --yes
"""
from __future__ import annotations

import modal

APP_NAME = "dec4-phy-novnc"
VOLUME_NAME = "dec4-kilosort-data"
VOLUME_MOUNT = "/data"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=False)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "git", "procps", "xvfb", "x11vnc", "fluxbox", "xterm", "novnc",
        "websockify", "libglib2.0-0", "libgl1", "libgl1-mesa-dri", "libegl1",
        "libasound2", "libdbus-1-3", "libfontconfig1", "libnss3", "libx11-xcb1",
        "libxkbcommon-x11-0", "libxcb-cursor0", "libxcb-icccm4", "libxcb-image0",
        "libxcb-keysyms1", "libxcb-randr0", "libxcb-render-util0", "libxcb-shape0",
        "libxcb-shm0", "libxcb-sync1", "libxcb-xfixes0", "libxcb-xinerama0",
        "libxcb1", "libxcomposite1", "libxdamage1", "libxrandr2", "libxrender1",
        "libxext6", "libxtst6", "libsm6",
    )
    .pip_install(
        "numpy<2", "scipy<1.12", "matplotlib<3.9", "h5py", "joblib", "click",
        "requests", "traitlets", "tqdm", "phylib", "qtpy", "PyOpenGL==3.1.6",
        "PyQt5==5.15.10", "PyQtWebEngine==5.15.6", "scikit-learn", "colorcet",
        "qtconsole",
    )
    .pip_install("git+https://github.com/cortex-lab/phy.git")
)


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=8 * 60 * 60,
              cpu=4.0, memory=32768)
def start_phy_novnc(probe: str = "dhpc") -> None:
    import os
    import shutil
    import subprocess
    import time
    from pathlib import Path

    session = "/data/dec4"
    raw = f"{session}/amplifier_{probe}.dat"
    results = f"{session}/kilosort4_results_{probe}"
    params_path = f"{results}/params_modal.py"
    launch_log = f"{results}/phy_modal_launch.log"

    if not Path(raw).exists():
        raise FileNotFoundError(f"Missing raw binary in volume: {raw}")
    if not Path(results).exists():
        raise FileNotFoundError(f"Missing Kilosort results in volume: {results}")

    Path(params_path).write_text("\n".join([
        "n_channels_dat = 128", "offset = 0", "sample_rate = 20000",
        "dtype = 'int16'", "hp_filtered = False", f"dat_path = ['{raw}']", "",
    ]))

    env = os.environ.copy()
    env.update({
        "DISPLAY": ":99", "QT_X11_NO_MITSHM": "1", "LIBGL_ALWAYS_SOFTWARE": "1",
        "MESA_GL_VERSION_OVERRIDE": "3.3", "MESA_GLSL_VERSION_OVERRIDE": "330",
        "QTWEBENGINE_CHROMIUM_FLAGS": "--no-sandbox", "QTWEBENGINE_DISABLE_SANDBOX": "1",
    })

    subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1600x1000x24", "-ac",
                      "+extension", "GLX"], env=env)
    time.sleep(2)
    subprocess.Popen(["fluxbox"], env=env)
    subprocess.Popen(["x11vnc", "-display", ":99", "-forever", "-shared", "-nopw",
                      "-listen", "0.0.0.0", "-rfbport", "5900"], env=env)
    websockify = shutil.which("websockify") or "/usr/bin/websockify"

    with modal.forward(6080) as tunnel:
        vnc_url = f"{tunnel.url}/vnc.html?autoconnect=true&resize=scale"
        Path(f"{results}/NOVNC_URL.txt").write_text(vnc_url + "\n")
        volume.commit()
        print("", flush=True)
        print(f"Dec 4 {probe} Phy desktop URL:", flush=True)
        print(vnc_url, flush=True)
        print("URL also saved to:", f"{results}/NOVNC_URL.txt", flush=True)
        print("", flush=True)

        subprocess.Popen([websockify, "--web", "/usr/share/novnc", "6080",
                          "localhost:5900"], env=env)
        time.sleep(3)
        launch_command = (
            f"cd {results}; echo 'Kilosort dir:' {results}; "
            f"phy template-describe {params_path} 2>&1 | tee {launch_log}; "
            f"echo ''; echo 'Starting Phy GUI...'; "
            f"phy template-gui --clear-state {params_path} 2>&1 | tee -a {launch_log}; "
            "echo ''; echo 'Phy exited.'; bash"
        )
        subprocess.Popen(["xterm", "-geometry", "160x42", "-e", launch_command], env=env)
        while True:
            time.sleep(60)


@app.local_entrypoint()
def main(probe: str = "dhpc") -> None:
    start_phy_novnc.remote(probe)

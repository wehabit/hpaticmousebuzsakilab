"""Run Dec 3 Phy in a browser-accessible Modal noVNC desktop.

This reuses the existing `dec3-kilosort-data` Modal Volume. It does not upload
the 51 GB raw file again.
"""

from __future__ import annotations

import modal


APP_NAME = "dec3-phy-novnc"
VOLUME_NAME = "dec3-kilosort-data"
VOLUME_MOUNT = "/data"

SESSION_DIR = "/data/dec3"
RAW_BINARY = f"{SESSION_DIR}/amplifier.dat"
RESULTS_DIR = f"{SESSION_DIR}/kilosort4_results"
PARAMS_PATH = f"{RESULTS_DIR}/params_modal.py"
LAUNCH_LOG = f"{RESULTS_DIR}/phy_modal_launch.log"
START_HERE = f"{RESULTS_DIR}/START_HERE_MODAL_PHY.txt"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=False)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "git",
        "procps",
        "xvfb",
        "x11vnc",
        "fluxbox",
        "xterm",
        "novnc",
        "websockify",
        "libglib2.0-0",
        "libgl1",
        "libgl1-mesa-dri",
        "libegl1",
        "libasound2",
        "libdbus-1-3",
        "libfontconfig1",
        "libnss3",
        "libx11-xcb1",
        "libxkbcommon-x11-0",
        "libxcb-cursor0",
        "libxcb-icccm4",
        "libxcb-image0",
        "libxcb-keysyms1",
        "libxcb-randr0",
        "libxcb-render-util0",
        "libxcb-shape0",
        "libxcb-shm0",
        "libxcb-sync1",
        "libxcb-xfixes0",
        "libxcb-xinerama0",
        "libxcb1",
        "libxcomposite1",
        "libxdamage1",
        "libxrandr2",
        "libxrender1",
        "libxext6",
        "libxtst6",
        "libsm6",
    )
    .pip_install(
        "numpy<2",
        "scipy<1.12",
        "matplotlib<3.9",
        "h5py",
        "joblib",
        "click",
        "requests",
        "traitlets",
        "tqdm",
        "phylib",
        "qtpy",
        "PyOpenGL==3.1.6",
        "PyQt5==5.15.10",
        "PyQtWebEngine==5.15.6",
        "scikit-learn",
        "colorcet",
        "qtconsole",
    )
    .pip_install("git+https://github.com/cortex-lab/phy.git")
)


@app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    timeout=8 * 60 * 60,
    cpu=4.0,
    memory=32768,
)
def start_phy_novnc() -> None:
    import os
    import shutil
    import subprocess
    import time
    from pathlib import Path

    raw_path = Path(RAW_BINARY)
    results_dir = Path(RESULTS_DIR)
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw binary in Modal volume: {raw_path}")
    if not results_dir.exists():
        raise FileNotFoundError(f"Missing Kilosort results in Modal volume: {results_dir}")

    params_text = "\n".join(
        [
            "n_channels_dat = 128",
            "offset = 0",
            "sample_rate = 20000",
            "dtype = 'int16'",
            "hp_filtered = False",
            f"dat_path = ['{RAW_BINARY}']",
            "",
        ]
    )
    Path(PARAMS_PATH).write_text(params_text)
    Path(START_HERE).write_text(
        "\n".join(
            [
                "Dec 3 Modal Phy launcher",
                "",
                "Kilosort directory:",
                RESULTS_DIR,
                "",
                "Phy params:",
                PARAMS_PATH,
                "",
                "Launch log:",
                LAUNCH_LOG,
                "",
                "Manual command if the GUI did not open automatically:",
                f"cd {RESULTS_DIR}",
                f"phy template-describe {PARAMS_PATH}",
                f"phy template-gui --clear-state {PARAMS_PATH}",
                "",
            ]
        )
    )

    env = os.environ.copy()
    env.update(
        {
            "DISPLAY": ":99",
            "QT_X11_NO_MITSHM": "1",
            "LIBGL_ALWAYS_SOFTWARE": "1",
            "MESA_GL_VERSION_OVERRIDE": "3.3",
            "MESA_GLSL_VERSION_OVERRIDE": "330",
            "QTWEBENGINE_CHROMIUM_FLAGS": "--no-sandbox",
            "QTWEBENGINE_DISABLE_SANDBOX": "1",
        }
    )

    subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1600x1000x24", "-ac", "+extension", "GLX"],
        env=env,
    )
    time.sleep(2)
    subprocess.Popen(["fluxbox"], env=env)
    subprocess.Popen(
        ["x11vnc", "-display", ":99", "-forever", "-shared", "-nopw", "-listen", "0.0.0.0", "-rfbport", "5900"],
        env=env,
    )

    novnc_index = "/usr/share/novnc/vnc.html"
    if not Path(novnc_index).exists():
        novnc_index = "/usr/share/novnc/index.html"

    websockify = shutil.which("websockify") or "/usr/bin/websockify"
    with modal.forward(6080) as tunnel:
        print("")
        print("Open this URL in your browser for the Modal Phy desktop:")
        print(f"{tunnel.url}/vnc.html?autoconnect=true&resize=scale")
        print("")
        print("Inside the desktop, Phy should be launching automatically.")
        print("Kilosort results:", RESULTS_DIR)
        print("Params:", PARAMS_PATH)
        print("Launch log:", LAUNCH_LOG)
        print("")

        subprocess.Popen(
            [
                websockify,
                "--web",
                "/usr/share/novnc",
                "6080",
                "localhost:5900",
            ],
            env=env,
        )
        time.sleep(3)
        launch_command = (
            f"cd {RESULTS_DIR}; "
            f"echo 'Kilosort directory:' {RESULTS_DIR}; "
            f"echo 'Params:' {PARAMS_PATH}; "
            f"echo 'Running template-describe first...'; "
            f"phy template-describe {PARAMS_PATH} 2>&1 | tee {LAUNCH_LOG}; "
            f"echo ''; echo 'Starting Phy GUI...'; "
            f"phy template-gui --clear-state {PARAMS_PATH} 2>&1 | tee -a {LAUNCH_LOG}; "
            "echo ''; echo 'Phy exited. See log above.'; "
            "bash"
        )
        subprocess.Popen(["xterm", "-geometry", "160x42", "-e", launch_command], env=env)

        while True:
            time.sleep(60)


@app.local_entrypoint()
def main() -> None:
    start_phy_novnc.remote()

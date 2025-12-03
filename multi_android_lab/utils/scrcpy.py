"""Helpers to launch scrcpy for device mirroring."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from .logger import get_logger

SCRCPY_ENV_VAR = "MULTI_ANDROID_LAB_SCRCPY"
logger = get_logger("scrcpy")

_dpi_awareness_set = False


def _resolve_scrcpy_binary() -> Optional[str]:
    env_path = os.environ.get(SCRCPY_ENV_VAR)
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            logger.info("Using scrcpy from %s (via %s)", candidate, SCRCPY_ENV_VAR)
            return str(candidate)
        logger.warning("%s is set to %s but file not found", SCRCPY_ENV_VAR, candidate)

    which_value = shutil.which("scrcpy")
    if which_value:
        logger.info("Using scrcpy from PATH: %s", which_value)
        return which_value

    logger.warning("scrcpy binary was not found; screen mirroring disabled.")
    return None


SCRCPY_BINARY = _resolve_scrcpy_binary()


def launch_scrcpy(
    device_id: str,
    window_title: Optional[str] = None,
    borderless: bool = False,
    extra_args: Optional[List[str]] = None,
) -> Optional[subprocess.Popen]:
    """Launch scrcpy for the provided device ID."""
    if not SCRCPY_BINARY:
        logger.error("Cannot start scrcpy because the binary is missing.")
        return None

    args = [
        SCRCPY_BINARY,
        "-s",
        device_id,
    ]
    if window_title:
        args += ["--window-title", window_title]
    if borderless:
        args.append("--window-borderless")
    if extra_args:
        args += extra_args

    logger.info("Launching scrcpy: %s", " ".join(args))
    try:
        return subprocess.Popen(args)
    except OSError as exc:  # e.g., permission denied
        logger.error("Failed to start scrcpy: %s", exc)
        return None


def find_window_handle(window_title: str) -> Optional[int]:
    """Locate the window handle for the scrcpy instance with the given title."""
    if not window_title:
        return None

    if sys.platform.startswith("win"):
        import ctypes
        from ctypes import wintypes

        global _dpi_awareness_set
        if not _dpi_awareness_set:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:  # pragma: no cover - best-effort only
                pass
            _dpi_awareness_set = True

        FindWindow = ctypes.windll.user32.FindWindowW
        FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        FindWindow.restype = wintypes.HWND
        hwnd = FindWindow(None, window_title)
        return int(hwnd) if hwnd else None

    # Other platforms not implemented yet.
    return None

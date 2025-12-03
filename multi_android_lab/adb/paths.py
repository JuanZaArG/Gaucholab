"""Helpers to locate the adb binary."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..utils import get_logger

ADB_ENV_VAR = "MULTI_ANDROID_LAB_ADB"
logger = get_logger("adb.path")


def _resolve_adb_binary() -> str:
    env_value = os.environ.get(ADB_ENV_VAR)
    if env_value:
        adb_path = Path(env_value).expanduser()
        if adb_path.exists():
            logger.info("Using ADB from %s (via %s)", adb_path, ADB_ENV_VAR)
            return str(adb_path)
        logger.warning("Env var %s set to %s but file not found", ADB_ENV_VAR, adb_path)

    which_result = shutil.which("adb")
    if which_result:
        logger.info("Using ADB from PATH: %s", which_result)
        return which_result

    logger.warning("Falling back to plain 'adb' command; ensure it is in PATH.")
    return "adb"


ADB_BINARY = _resolve_adb_binary()

"""Logging helpers for MultiAndroidLab."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

LOG_DIR = Path.home() / ".multi_android_lab" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_loggers: Dict[str, logging.Logger] = {}


def _build_handlers() -> list[logging.Handler]:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=5)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    return [file_handler, console_handler]


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger that writes to the shared log directory."""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        for handler in _build_handlers():
            logger.addHandler(handler)

    _loggers[name] = logger
    return logger

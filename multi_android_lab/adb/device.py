"""Representation of a single Android device controlled via ADB."""

from __future__ import annotations

import re
import shlex
import subprocess
from typing import List, Optional, Tuple

from ..utils import LOG_DIR, get_logger
from .paths import ADB_BINARY


class Device:
    """Abstraction for an Android device connected through ADB."""

    def __init__(self, device_id: str, status: str = "device") -> None:
        self.id = device_id
        self.status = status
        self._model: Optional[str] = None
        self._battery: Optional[int] = None
        self._resolution: Optional[Tuple[int, int]] = None
        self.logger = get_logger(f"device.{device_id}")
        self.device_log_file = LOG_DIR / f"{self._sanitize_filename(device_id)}.log"
        self.device_log_file.touch(exist_ok=True)

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]", "_", name)

    def update_status(self, status: str) -> None:
        self.status = status


    def get_model(self, force_refresh: bool = False) -> str:
        if self._model is None or force_refresh:
            self._model = self._run_shell_and_capture("getprop ro.product.model").strip()
        return self._model or "Unknown"

    def get_battery(self, force_refresh: bool = False) -> str:
        if self._battery is None or force_refresh:
            output = self._run_shell_and_capture("dumpsys battery")
            match = re.search(r"level:\s*(\d+)", output)
            self._battery = int(match.group(1)) if match else None
        return f"{self._battery or 0}%"

    def get_resolution(self, force_refresh: bool = False) -> Tuple[int, int]:
        if self._resolution is None or force_refresh:
            output = self._run_shell_and_capture("wm size")
            match = re.search(r"Physical size:\s*(\d+)x(\d+)", output)
            if match:
                self._resolution = (int(match.group(1)), int(match.group(2)))
            else:
                self._resolution = (1080, 1920)
        return self._resolution

    def get_latency(self) -> str:
        output = self._run_shell_and_capture('ping -c 4 true', timeout=5)
        match = re.search(r"= [^/]+/([^/]+)/", output)
        return f"{match.group(1)} ms" if match else "n/a"


    def run_shell(self, command: str, timeout: Optional[int] = None) -> str:
        if not command:
            return ""
        output = self._run_shell_and_capture(command, timeout=timeout)
        self._write_device_log(f"$ {command}\n{output.strip()}\n")
        return output

    def open_app(self, package: str, activity: str) -> None:
        self.run_shell(f"am start -n {package}/{activity}")

    def close_app(self, package: str) -> None:
        self.run_shell(f"am force-stop {package}")

    def open_settings(self) -> None:
        self.run_shell("am start -a android.settings.SETTINGS")

    def back(self) -> None:
        self.run_shell("input keyevent 4")

    def home(self) -> None:
        self.run_shell("input keyevent 3")

    def swipe_down(self) -> None:
        self.swipe(0.5, 0.2, 0.5, 0.8, 300)

    def swipe_up(self) -> None:
        self.swipe(0.5, 0.8, 0.5, 0.2, 300)

    def tap(self, normalized_x: float, normalized_y: float) -> None:
        x, y = self._normalized_to_pixels(normalized_x, normalized_y)
        self.run_shell(f"input tap {x} {y}")

    def swipe(
        self,
        norm_x1: float,
        norm_y1: float,
        norm_x2: float,
        norm_y2: float,
        duration_ms: int = 300,
    ) -> None:
        x1, y1 = self._normalized_to_pixels(norm_x1, norm_y1)
        x2, y2 = self._normalized_to_pixels(norm_x2, norm_y2)
        self.run_shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")


    def get_logs(self, tail: int = 50) -> str:
        lines = self.device_log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[-tail:])

    def _write_device_log(self, message: str) -> None:
        with self.device_log_file.open("a", encoding="utf-8") as fh:
            fh.write(message)


    def _normalized_to_pixels(self, nx: float, ny: float) -> Tuple[int, int]:
        width, height = self.get_resolution()
        nx = min(max(nx, 0.0), 1.0)
        ny = min(max(ny, 0.0), 1.0)
        return int(nx * width), int(ny * height)

    def _run_shell_and_capture(self, command: str, timeout: Optional[int] = None) -> str:
        shell_args = self._normalize_command(command)
        if not shell_args:
            return ""
        adb_args = [ADB_BINARY, "-s", self.id, "shell", *shell_args]
        self.logger.debug("Running shell command: %s", command)
        try:
            proc = subprocess.run(
                adb_args,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            self.logger.warning("Command timeout: %s", command)
            return "Command timed out"

        output = proc.stdout.strip()
        if proc.returncode != 0:
            self.logger.error("Command failed (%s): %s", proc.returncode, output)
        return output

    @staticmethod
    def _normalize_command(command: str) -> List[str]:
        if not command:
            return []
        return shlex.split(command)

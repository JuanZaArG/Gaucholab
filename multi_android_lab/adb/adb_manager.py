"""ADB manager to discover and control connected devices."""

from __future__ import annotations

import subprocess
from typing import Dict, Iterable, List

from ..utils import get_logger
from .device import Device
from .paths import ADB_BINARY


class ADBManager:
    """Keeps track of devices connected via ADB."""

    def __init__(self) -> None:
        self.devices: Dict[str, Device] = {}
        self.logger = get_logger("adb.manager")


    def refresh_devices(self) -> List[Device]:
        """Refresh the device cache by running `adb devices -l`."""
        command = [ADB_BINARY, "devices", "-l"]
        self.logger.debug("Executing: %s", " ".join(command))
        try:
            proc = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5,
            )
        except FileNotFoundError:
            self.logger.error("ADB executable not found in PATH.")
            return []

        raw_output = proc.stdout.strip()
        self.logger.debug("adb devices output:\n%s", raw_output or "<sin salida>")
        output = raw_output.splitlines()
        seen_ids = set()
        for line in output[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            device_id = parts[0]
            status = parts[1] if len(parts) > 1 else "unknown"
            seen_ids.add(device_id)
            device = self.devices.get(device_id)
            if not device:
                self.logger.info("Device discovered: %s (%s)", device_id, status)
                device = Device(device_id, status=status)
                self.devices[device_id] = device
            else:
                device.update_status(status)


        for stale in set(self.devices.keys()) - seen_ids:
            self.logger.info("Device disconnected: %s", stale)
            self.devices.pop(stale, None)

        if not seen_ids:
            self.logger.info("No devices detected por adb.")
        return list(self.devices.values())


    def get_connected_devices(self) -> List[Device]:
        """Return the cached devices (call refresh_devices first)."""
        return list(self.devices.values())

    def execute_on_all(self, method: str, *args, **kwargs) -> None:
        """Call a Device method on every connected device."""
        for device in self.get_connected_devices():
            func = getattr(device, method, None)
            if callable(func):
                func(*args, **kwargs)

    def broadcast_shell(self, command: str) -> None:
        """Run an arbitrary shell command on all devices."""
        for device in self.get_connected_devices():
            device.run_shell(command)

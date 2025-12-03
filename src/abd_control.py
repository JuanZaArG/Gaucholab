import subprocess
import sys
from typing import List, Tuple, Optional
from pathlib import Path
import logging


ADB_PATH = Path(r"C:\scrcpy-win64-v3.3.3\adb.exe")

logger = logging.getLogger(__name__)

def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    """Ejecuta un comando del sistema y devuelve el resultado."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if result.stderr.strip():
            logger.debug(f"STDERR for {cmd}: {result.stderr.strip()}")
        return result
    except FileNotFoundError:
        logger.error("No se encontró adb.exe. Verificá ADB_PATH.")
        print("ERROR: No se encontró adb.exe. Verificá ADB_PATH en adb_control.py")
        sys.exit(1)


def list_devices() -> List[Tuple[str, str]]:
    """
    Devuelve una lista de (device_id, estado) usando 'adb devices'.
    """
    result = run_cmd([str(ADB_PATH), "devices"])
    lines = result.stdout.strip().splitlines()
    devices: List[Tuple[str, str]] = []

    for line in lines[1:]:  
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            device_id, state = parts[0], parts[1]
            devices.append((device_id, state))
    return devices


def get_device_model(device_id: str) -> Optional[str]:
    """Obtiene el modelo del dispositivo."""
    result = run_cmd([str(ADB_PATH), "-s", device_id, "shell", "getprop", "ro.product.model"])
    model = result.stdout.strip()
    return model or None


def adb_shell(device_id: str, command: str) -> str:
    """Ejecuta un comando 'adb shell' en un dispositivo específico."""
    result = run_cmd([str(ADB_PATH), "-s", device_id, "shell", command])
    stdout = result.stdout.strip()
    if result.stderr.strip():
        logger.warning(f"[{device_id}] STDERR: {result.stderr.strip()}")
    logger.debug(f"[{device_id}] SHELL '{command}' → {stdout}")
    return stdout


def adb_simple(device_id: str, args: List[str]) -> subprocess.CompletedProcess:
    """
    Ejecuta un comando adb genérico contra un dispositivo específico.
    Ej: args = ["reboot"] → adb -s device_id reboot
    """
    cmd = [str(ADB_PATH), "-s", device_id] + args
    logger.info(f"Ejecutando adb simple en {device_id}: {' '.join(args)}")
    return run_cmd(cmd)


def print_device_list() -> None:
    """Imprime en consola la lista de dispositivos con modelo."""
    devices = list_devices()
    if not devices:
        print("No se detectó ningún dispositivo ADB.")
        return

    print("Dispositivos conectados:")
    for dev_id, state in devices:
        model = get_device_model(dev_id) or "Modelo desconocido"
        print(f" - {dev_id} [{state}] → {model}")


def shell_all(command: str) -> None:
    """Ejecuta un 'adb shell <command>' en TODOS los dispositivos."""
    devices = list_devices()
    if not devices:
        print("No hay dispositivos para ejecutar el comando.")
        return

    print(f"\nEjecutando en todos: adb shell {command}\n")
    for dev_id, state in devices:
        model = get_device_model(dev_id) or "Modelo desconocido"
        print(f"=== {dev_id} ({model}) ===")
        out = adb_shell(dev_id, command)
        print(out or "(sin salida)")


def reboot_all() -> None:
    """Reinicia todos los dispositivos conectados."""
    devices = list_devices()
    if not devices:
        print("No hay dispositivos para reiniciar.")
        return

    print("Reiniciando TODOS los dispositivos...")
    for dev_id, state in devices:
        model = get_device_model(dev_id) or "Modelo desconocido"
        print(f"- {dev_id} ({model}) reiniciando...")
        adb_simple(dev_id, ["reboot"])

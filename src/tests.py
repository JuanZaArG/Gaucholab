import time
import logging
from typing import Dict, Any, List, Tuple

from abd_control import list_devices, adb_shell, get_device_model

logger = logging.getLogger(__name__)

def get_basic_stats(device_id: str) -> Dict[str, Any]:
    """
    Devuelve stats básicos del dispositivo:
    - modelo
    - nivel de batería
    - temperatura batería (si disponible)
    - uptime (segundos desde el arranque)
    """
    model = get_device_model(device_id) or "Modelo desconocido"

    # nivel batería
    battery_raw = adb_shell(device_id, "dumpsys battery")
    level = None
    temp = None
    for line in battery_raw.splitlines():
        line = line.strip()
        if line.startswith("level:"):
            try:
                level = int(line.split(":")[1].strip())
            except ValueError:
                pass
        if line.startswith("temperature:"):
            try:
                # muchos devs lo dan en 1/10 de grado
                temp_val = int(line.split(":")[1].strip())
                temp = temp_val / 10.0
            except ValueError:
                pass

    # uptime
    uptime_raw = adb_shell(device_id, "cat /proc/uptime")
    uptime_secs = None
    try:
        uptime_secs = float(uptime_raw.split()[0])
    except Exception:
        pass

    stats = {
        "device_id": device_id,
        "model": model,
        "battery_level": level,
        "battery_temp": temp,
        "uptime_secs": uptime_secs,
    }
    logger.info(f"Stats básicas {device_id}: {stats}")
    return stats


def test_response_time(device_id: str, iterations: int = 5) -> float:
    """
    Mide tiempo promedio de respuesta para un comando simple 'echo ping'.
    Devuelve tiempo medio en milisegundos.
    """
    times: List[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        adb_shell(device_id, "echo ping > /dev/null")
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)  # ms

    avg_ms = sum(times) / len(times)
    logger.info(f"Latencia promedio {device_id}: {avg_ms:.2f} ms")
    return avg_ms


def run_basic_diagnostics() -> List[Dict[str, Any]]:
    """
    Corre un set de diagnósticos simples en todos los dispositivos:
    - Stats básicas
    - Latencia de comando

    Devuelve una lista de dicts con resultados (para log, CSV, etc.)
    """
    devices = list_devices()
    if not devices:
        print("No hay dispositivos para diagnosticar.")
        return []

    results: List[Dict[str, Any]] = []
    print("\n=== Diagnóstico básico de todos los dispositivos ===\n")
    for dev_id, state in devices:
        print(f"-> {dev_id} (state={state})")
        stats = get_basic_stats(dev_id)
        latency = test_response_time(dev_id)
        stats["latency_ms"] = latency
        results.append(stats)

        # Mostrar en pantalla
        print(
            f"   Modelo: {stats['model']}\n"
            f"   Batería: {stats['battery_level']}%\n"
            f"   Temp batería: {stats['battery_temp']}°C\n"
            f"   Uptime: {stats['uptime_secs']} s\n"
            f"   Latencia promedio: {latency:.2f} ms\n"
        )

    return results

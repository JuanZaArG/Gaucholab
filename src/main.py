import logging
from pathlib import Path

from abd_control import print_device_list, shell_all, reboot_all
from tests import run_basic_diagnostics


# Configuración de logs
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "multi_adb.log"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main_menu():
    while True:
        print("\n=== LAB MULTI-ANDROID (ADB) ===")
        print("1) Listar dispositivos")
        print("2) Ejecutar comando shell en TODOS")
        print("3) Reiniciar TODOS los dispositivos")
        print("4) Diagnóstico básico (batería, uptime, latencia)")
        print("0) Salir")
        choice = input("Elegí una opción: ").strip()

        if choice == "1":
            print_device_list()
        elif choice == "2":
            cmd = input("Comando a ejecutar (sin 'adb shell'): ").strip()
            if cmd:
                shell_all(cmd)
        elif choice == "3":
            confirm = input("¿Seguro que querés reiniciar TODOS? (si/no): ").strip().lower()
            if confirm == "si":
                reboot_all()
        elif choice == "4":
            results = run_basic_diagnostics()
            print("Resultados guardados en logs (multi_adb.log).")
        elif choice == "0":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    logger.info("Iniciando LAB MULTI-ANDROID")
    main_menu()

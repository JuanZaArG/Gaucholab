
<div align="center">
  <img src="multi_android_lab/assets/gaucho_full.jpg" alt="Gaucho One" width="360" />
  <br/>
  <sub style="color:#d1d1d1;font-size:16px;">
    MultiAndroidLab · Gaucho One — <br>Laboratorio profesional para flotas Android.<br>
    Professional Android Lab for USB Device Orchestration.
  </sub>
</div>

---

#  Language / Idioma

| Español | English |
|--------|---------|
| 👉 [Ir a Características clave](#características-clave) | 👉 [Go to Key Features](#key-features) |

---

# 🇪🇸 Versión en Español

##  Características clave

- **Control simultáneo** de cualquier cantidad de dispositivos Android conectados vía USB (ADB).
- **Panel global** con acciones preconfiguradas (abrir/cerrar apps, BACK, HOME, gestos) e inyección de comandos Shell.
- **Vistas individuales** con métricas en tiempo real (modelo, batería, resolución, latencia) y consola dedicada.
- **Integración scrcpy**: abre la pantalla del dispositivo desde la propia app (ventana nativa de scrcpy).
- **Pantalla inicial** con branding Gaucho One.
- **Tematización MD3** alineada a la identidad visual de Gaucho One.

---

##  Requisitos

- Windows 10/11 (64 bits) o Linux con Python 3.10+
- [PySide6](https://doc.qt.io/qtforpython/) y dependencias listadas en `requirements.txt`
- [Android Platform Tools (ADB)](https://developer.android.com/studio/releases/platform-tools)
- [scrcpy](https://github.com/Genymobile/scrcpy) (opcional pero recomendado)

Variables de entorno si tus binarios no están en el PATH:

```

MULTI_ANDROID_LAB_ADB=C:\ruta\adb.exe
MULTI_ANDROID_LAB_SCRCPY=C:\ruta\scrcpy.exe

````

---

##  Instalación rápida (Windows)

```powershell
git clone https://github.com/<tu_usuario>/multi_android_lab.git
cd multi_android_lab
run_multi_android_lab.bat
````

El script:

1. Crea/activa `.venv`
2. Instala dependencias
3. Ejecuta `python -m multi_android_lab.main`

### Crear un `.exe`

```powershell
build_multi_android_lab_exe.bat
```

El ejecutable final quedará en:

```
dist/MultiAndroidLab.exe
```

---

## Uso

1. Ejecuta el programa (`run_multi_android_lab.bat`, `.exe` o `python -m multi_android_lab.main`).
2. En la pantalla de inicio presiona **INICIAR**.
3. Conecta tus dispositivos con **Depuración USB** activada.
4. Desde el panel global:

   * Configura `Paquete` y `Actividad`.
   * Usa las acciones rápidas:

     * ▶ Abrir app en todos
     * ■ Cerrar app en todos
     * ↩ BACK
     * 🏠 HOME
     * ↓ Swipe Down
     * `>` Ejecutar Shell en todos
5. Abre la vista individual para:

   * Métricas (modelo, batería, resolución, latencia)
   * Consola ADB dedicada
   * Gestos normalizados (tap, swipe)
   * Ejecutar scrcpy para esa unidad

Logs almacenados en:

```
~/.multi_android_lab/logs/
```

---

## Arquitectura del proyecto

```
multi_android_lab/
│
├── adb/
│   ├── adb_manager.py
│   └── device.py
│
├── ui/
│   ├── main_window.py
│   ├── device_window.py
│   ├── start_screen.py
│   └── styles.qss
│
├── utils/
│   ├── logger.py
│   └── scrcpy_helper.py
│
├── assets/
│   ├── g1.png
│   └── gaucho_full.jpg
│
└── main.py
```

---

## Añadir acciones nuevas

1. Crear un nuevo método en `Device` dentro de `device.py`.
2. Mapearlo en `ADBManager` si necesita ejecución masiva.
3. Asociarlo a un botón en la UI (`main_window.py` o `device_window.py`).
4. Ejecutarlo mediante `run_in_executor` para no bloquear la interfaz.

---

## Contribuir

1. Crear una rama descriptiva:
   `feature/g1-metrics`
2. Instalar dependencias:
   `pip install -r requirements.txt`
3. Compilar antes del PR:
   `python3 -m compileall multi_android_lab`
4. Documentar cambios relevantes en este README.

---

## Licencia

Proyecto interno de **Gaucho One**.
Requiere autorización para redistribución o uso comercial.

---

---

# 🇺🇸 English Version

## Key Features

* **Simultaneous control** of any number of Android devices via USB (ADB).
* **Global control panel** with predefined actions (open/close apps, BACK, HOME, gestures) and broadcast Shell injection.
* **Individual device views** with realtime metrics (model, battery, resolution, latency) and a dedicated ADB console.
* **scrcpy integration**: open device screens using native scrcpy windows.
* **Start screen** with Gaucho One branding.
* **Material Design 3** theming aligned with Gaucho One identity.

---

## Requirements

* Windows 10/11 (64-bit) or Linux with Python 3.10+
* [PySide6](https://doc.qt.io/qtforpython/)
* [Android Platform Tools (ADB)](https://developer.android.com/studio/releases/platform-tools)
* [scrcpy](https://github.com/Genymobile/scrcpy) (recommended)

Environment variables if binaries are not in PATH:

```
MULTI_ANDROID_LAB_ADB=C:\path\adb.exe  
MULTI_ANDROID_LAB_SCRCPY=C:\path\scrcpy.exe
```

---

## Quick Installation (Windows)

```powershell
git clone https://github.com/<your_user>/multi_android_lab.git
cd multi_android_lab
run_multi_android_lab.bat
```

The script will:

1. Create/activate `.venv`
2. Install dependencies
3. Run `python -m multi_android_lab.main`

### Build a Windows `.exe`

```powershell
build_multi_android_lab_exe.bat
```

Output:

```
dist/MultiAndroidLab.exe
```

---

## Usage

1. Run the program.
2. Press **START** on the welcome screen.
3. Connect devices with **USB Debugging** enabled.
4. Use the global panel:

   * Set `Package` and `Activity`.
   * Use quick actions:

     * ▶ Open app on all devices
     * ■ Close app on all devices
     * ↩ BACK
     * 🏠 HOME
     * ↓ Swipe Down
     * `>` Broadcast Shell
5. Open individual views for:

   * Metrics (model, battery, resolution, latency)
   * Per-device ADB console
   * Normalized gestures
   * Launching scrcpy

Logs stored at:

```
~/.multi_android_lab/logs/
```

---

## Project Architecture

```
multi_android_lab/
│
├── adb/
│   ├── adb_manager.py
│   └── device.py
│
├── ui/
│   ├── main_window.py
│   ├── device_window.py
│   ├── start_screen.py
│   └── styles.qss
│
├── utils/
│   ├── logger.py
│   └── scrcpy_helper.py
│
├── assets/
│   ├── g1.png
│   └── gaucho_full.jpg
│
└── main.py
```

---

## Adding New Actions

1. Implement a new method in `Device` inside `device.py`.
2. Map it inside `ADBManager` for broadcast execution.
3. Bind it to a button or action in the UI.
4. Execute it through async helpers to keep the UI responsive.

---

## Contributing

1. Create a descriptive branch.
2. Install dependencies.
3. Run: `python3 -m compileall multi_android_lab`
4. Document changes in this README.

---

## License

Internal project of **Gaucho One**.
Authorization required before redistribution or commercial use.






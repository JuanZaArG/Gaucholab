"""Per-device window with advanced controls."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..adb import Device
from ..utils import launch_scrcpy, run_in_executor, style_icon_button


class DeviceWindow(QMainWindow):
    """Detailed controls for an individual device."""

    def __init__(self, device: Device) -> None:
        super().__init__()
        self.device = device
        self.setWindowTitle(f"Dispositivo {device.id}")
        self.resize(680, 720)
        self.assets_dir = Path(__file__).resolve().parent.parent / "assets"
        icon_path = self.assets_dir / "g1.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.info_future = None

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(3000)
        self.refresh_timer.timeout.connect(self._request_info_refresh)

        self._setup_ui()
        self.scrcpy_process = None

        self.refresh_timer.start()
        self._request_info_refresh()
        self._start_scrcpy()


    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.info_labels = {
            "id": QLabel(self.device.id),
            "model": QLabel(""),
            "battery": QLabel(""),
            "resolution": QLabel(""),
            "latency": QLabel(""),
        }

        main_layout.addWidget(self._build_scrcpy_panel())

        info_grid = QGridLayout()
        info_grid.addWidget(QLabel("ID"), 0, 0)
        info_grid.addWidget(self.info_labels["id"], 0, 1)
        info_grid.addWidget(QLabel("Modelo"), 0, 2)
        info_grid.addWidget(self.info_labels["model"], 0, 3)
        info_grid.addWidget(QLabel("Batería"), 1, 0)
        info_grid.addWidget(self.info_labels["battery"], 1, 1)
        info_grid.addWidget(QLabel("Resolución"), 1, 2)
        info_grid.addWidget(self.info_labels["resolution"], 1, 3)
        info_grid.addWidget(QLabel("Latencia"), 2, 0)
        info_grid.addWidget(self.info_labels["latency"], 2, 1)
        main_layout.addLayout(info_grid)

        main_layout.addWidget(self._build_action_panel())

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Comando ADB shell para este dispositivo")
        self.command_button = QPushButton()
        style_icon_button(self.command_button, "terminal", size=30)
        self.command_button.setToolTip("Ejecutar comando ADB")
        self.command_button.clicked.connect(self._run_custom_command)

        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(self.command_input, stretch=1)
        cmd_layout.addWidget(self.command_button)
        main_layout.addLayout(cmd_layout)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Últimos logs...")
        main_layout.addWidget(self.log_view, stretch=1)

    def _build_action_panel(self) -> QWidget:
        group = QGroupBox("Acciones")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        form_layout = QHBoxLayout()
        self.device_package_input = QLineEdit("com.example.app")
        self.device_activity_input = QLineEdit(".MainActivity")
        form_layout.addWidget(QLabel("Paquete"))
        form_layout.addWidget(self.device_package_input, stretch=1)
        form_layout.addWidget(QLabel("Actividad"))
        form_layout.addWidget(self.device_activity_input, stretch=1)
        layout.addLayout(form_layout)

        icons_layout = QHBoxLayout()
        icons_layout.setSpacing(12)

        def make_action_button(icon_name: str, tooltip: str, handler) -> QToolButton:
            btn = QToolButton()
            style_icon_button(btn, icon_name, size=30)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(handler)
            return btn

        icons_layout.addWidget(make_action_button("play", "Abrir App", self._open_app))
        icons_layout.addWidget(make_action_button("stop", "Cerrar App", self._close_app))
        icons_layout.addWidget(
            make_action_button("settings", "Abrir Ajustes", lambda: self._run_device_method("open_settings"))
        )
        icons_layout.addWidget(make_action_button("back", "BACK", lambda: self._run_device_method("back")))
        icons_layout.addWidget(make_action_button("home", "HOME", lambda: self._run_device_method("home")))
        icons_layout.addWidget(
            make_action_button("arrow-down", "SWIPE DOWN", lambda: self._run_device_method("swipe_down"))
        )
        icons_layout.addWidget(
            make_action_button("arrow-up", "SWIPE UP", lambda: self._run_device_method("swipe_up"))
        )
        layout.addLayout(icons_layout)

        tap_group = QGroupBox("Tap normalizado")
        tap_layout = QHBoxLayout(tap_group)
        self.tap_x_input = QDoubleSpinBox()
        self.tap_y_input = QDoubleSpinBox()
        for spin in (self.tap_x_input, self.tap_y_input):
            spin.setDecimals(2)
            spin.setRange(0.0, 1.0)
        tap_button = QPushButton()
        style_icon_button(tap_button, "target", size=28)
        tap_button.setToolTip("Tap en las coordenadas normalizadas")
        tap_button.clicked.connect(self._tap_device)
        tap_layout.addWidget(QLabel("X"))
        tap_layout.addWidget(self.tap_x_input)
        tap_layout.addWidget(QLabel("Y"))
        tap_layout.addWidget(self.tap_y_input)
        tap_layout.addWidget(tap_button)

        layout.addWidget(tap_group)

        return group

    def _build_scrcpy_panel(self) -> QWidget:
        group = QGroupBox("Pantalla (scrcpy)")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        self.scrcpy_status_label = QLabel("Abre scrcpy para este dispositivo en una ventana separada.")
        self.scrcpy_status_label.setWordWrap(True)
        layout.addWidget(self.scrcpy_status_label)

        self.scrcpy_button = QPushButton()
        style_icon_button(self.scrcpy_button, "monitor", size=30)
        self.scrcpy_button.setToolTip("Abrir scrcpy")
        self.scrcpy_button.setCursor(Qt.PointingHandCursor)
        self.scrcpy_button.clicked.connect(self._start_scrcpy)
        layout.addWidget(self.scrcpy_button, alignment=Qt.AlignLeft)

        return group


    def _request_info_refresh(self) -> None:
        if self.info_future and not self.info_future.done():
            return
        self.info_future = run_in_executor(self._gather_device_info, ui_callback=self._apply_info_result)

    def _gather_device_info(self) -> Dict[str, str]:
        model = self.device.get_model(force_refresh=True)
        battery = self.device.get_battery(force_refresh=True)
        width, height = self.device.get_resolution(force_refresh=True)
        latency = self.device.get_latency()
        logs = self.device.get_logs()
        return {
            "model": model,
            "battery": battery,
            "resolution": f"{width}x{height}",
            "latency": latency,
            "logs": logs,
        }

    def _apply_info_result(self, data: Dict[str, str] | Exception) -> None:
        self.info_future = None
        if isinstance(data, Exception):
            QMessageBox.warning(self, "Error", f"No se pudo actualizar la info:\n{data}")
            return
        self.info_labels["model"].setText(data.get("model", "n/a"))
        self.info_labels["battery"].setText(data.get("battery", "n/a"))
        self.info_labels["resolution"].setText(data.get("resolution", "n/a"))
        self.info_labels["latency"].setText(data.get("latency", "n/a"))
        logs = data.get("logs", "")
        self.log_view.setPlainText(logs)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())


    def _open_app(self) -> None:
        package = self.device_package_input.text().strip()
        activity = self.device_activity_input.text().strip() or ".MainActivity"
        if not package:
            QMessageBox.warning(self, "Error", "Define un paquete antes de abrir la app.")
            return
        self._run_device_method("open_app", package, activity)

    def _close_app(self) -> None:
        package = self.device_package_input.text().strip()
        if not package:
            QMessageBox.warning(self, "Error", "Define un paquete antes de cerrar la app.")
            return
        self._run_device_method("close_app", package)

    def _tap_device(self) -> None:
        x = self.tap_x_input.value()
        y = self.tap_y_input.value()
        self._run_device_method("tap", x, y)

    def _run_device_method(self, method_name: str, *args) -> None:
        run_in_executor(getattr(self.device, method_name), *args)

    def _run_custom_command(self) -> None:
        command = self.command_input.text().strip()
        if not command:
            return
        run_in_executor(self.device.run_shell, command)


    def _start_scrcpy(self) -> None:
        self._stop_scrcpy()
        self.scrcpy_status_label.setText("Abriendo scrcpy...")
        proc = launch_scrcpy(self.device.id)
        if proc:
            self.scrcpy_process = proc
            self.scrcpy_status_label.setText("scrcpy ejecutándose en ventana externa.")
        else:
            self.scrcpy_status_label.setText(
                "No se pudo iniciar scrcpy. Verifica la instalación o la variable MULTI_ANDROID_LAB_SCRCPY."
            )

    def _stop_scrcpy(self) -> None:
        if self.scrcpy_process and self.scrcpy_process.poll() is None:
            self.scrcpy_process.terminate()
            try:
                self.scrcpy_process.wait(timeout=2)
            except Exception:
                self.scrcpy_process.kill()
        self.scrcpy_process = None
        self.scrcpy_status_label.setText("scrcpy detenido.")


    def closeEvent(self, event) -> None:
        self.refresh_timer.stop()
        self._stop_scrcpy()
        super().closeEvent(event)

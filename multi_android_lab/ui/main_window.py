"""Main application window."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..adb import ADBManager
from ..utils import get_logger, run_in_executor, style_icon_button
from .device_window import DeviceWindow
from .widgets import DeviceListItem


class MainWindow(QMainWindow):
    """Top-level MultiAndroidLab window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MultiAndroidLab")
        self.resize(1280, 800)
        self.showMaximized()
        self.assets_dir = Path(__file__).resolve().parent.parent / "assets"

        self.adb_manager = ADBManager()
        self.device_windows: Dict[str, DeviceWindow] = {}
        self.device_items: Dict[str, DeviceListItem] = {}
        self.logger = get_logger("ui.main_window")
        self._last_snapshot_ids: set[str] = set()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(2000)
        self.refresh_timer.timeout.connect(self.trigger_refresh)

        self.refresh_future = None

        self._setup_ui()
        self.refresh_timer.start()
        self.trigger_refresh()

    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(self._build_brand_header())

        self.device_list = QListWidget()
        self.device_list.setSpacing(8)
        self.device_list.setAlternatingRowColors(False)
        self.device_list.setFrameShape(QFrame.NoFrame)
        layout.addWidget(QLabel("Dispositivos conectados"))
        layout.addWidget(self.device_list, stretch=1)

        layout.addWidget(self._build_controls())

    def _build_brand_header(self) -> QWidget:
        container = QFrame()
        container.setObjectName("BrandHeader")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        full_logo_label = QLabel()
        full_logo_label.setObjectName("BrandLogoFull")
        full_logo = self.assets_dir / "gaucho_full.jpg"
        pixmap_full = QPixmap(str(full_logo)) if full_logo.exists() else QPixmap()
        if not pixmap_full.isNull():
            full_logo_label.setPixmap(pixmap_full.scaledToHeight(110, Qt.SmoothTransformation))
        else:
            full_logo_label.setText("Gaucho One")
        layout.addWidget(full_logo_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)
        text_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("MultiAndroidLab · Gaucho One")
        title.setObjectName("BrandTitle")

        subtitle_es = QLabel("Laboratorio profesional para flotas Android con ADN Gaucho One.")
        subtitle_es.setObjectName("BrandSubtitle")
        subtitle_es.setAlignment(Qt.AlignCenter)

        subtitle_en = QLabel("Professional Android lab to orchestrate USB fleets with Gaucho One DNA.")
        subtitle_en.setObjectName("BrandSubtitle")
        subtitle_en.setAlignment(Qt.AlignCenter)

        text_layout.addWidget(title, alignment=Qt.AlignCenter)
        text_layout.addWidget(subtitle_es)
        text_layout.addWidget(subtitle_en)
        text_layout.addStretch(1)
        layout.addWidget(text_container, stretch=1)

        return container

    def _build_controls(self) -> QWidget:
        container = QGroupBox("Panel Global")
        controls_layout = QVBoxLayout(container)
        controls_layout.setSpacing(8)

        pkg_layout = QHBoxLayout()
        self.package_input = QLineEdit("com.example.app")
        self.activity_input = QLineEdit(".MainActivity")
        pkg_layout.addWidget(QLabel("Paquete"))
        pkg_layout.addWidget(self.package_input)
        pkg_layout.addWidget(QLabel("Actividad"))
        pkg_layout.addWidget(self.activity_input)
        controls_layout.addLayout(pkg_layout)

        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton()
        style_icon_button(self.refresh_button, "refresh", size=30)
        self.refresh_button.setToolTip("Refrescar dispositivos")
        buttons_layout.addWidget(self.refresh_button)

        self.open_all_btn = QPushButton()
        style_icon_button(self.open_all_btn, "play", size=30)
        self.open_all_btn.setToolTip("Abrir app en todos")

        self.close_all_btn = QPushButton()
        style_icon_button(self.close_all_btn, "stop", size=30)
        self.close_all_btn.setToolTip("Cerrar app en todos")

        self.back_all_btn = QPushButton()
        style_icon_button(self.back_all_btn, "back", size=30)
        self.back_all_btn.setToolTip("Enviar BACK a todos")

        self.home_all_btn = QPushButton()
        style_icon_button(self.home_all_btn, "home", size=30)
        self.home_all_btn.setToolTip("Enviar HOME a todos")

        self.swipe_down_btn = QPushButton()
        style_icon_button(self.swipe_down_btn, "arrow-down", size=30)
        self.swipe_down_btn.setToolTip("Swipe down en todos")

        for btn in [
            self.open_all_btn,
            self.close_all_btn,
            self.back_all_btn,
            self.home_all_btn,
            self.swipe_down_btn,
        ]:
            buttons_layout.addWidget(btn)

        controls_layout.addLayout(buttons_layout)

        command_layout = QHBoxLayout()
        self.custom_command_input = QLineEdit()
        self.custom_command_input.setPlaceholderText("Comando ADB shell para todos los dispositivos")
        self.custom_command_btn = QPushButton()
        style_icon_button(self.custom_command_btn, "terminal", size=30)
        self.custom_command_btn.setToolTip("Ejecutar comando ADB en todos")
        command_layout.addWidget(self.custom_command_input, stretch=1)
        command_layout.addWidget(self.custom_command_btn)
        controls_layout.addLayout(command_layout)

        self.status_label = QLabel("Listo")
        controls_layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.trigger_refresh)
        self.open_all_btn.clicked.connect(self._open_app_all)
        self.close_all_btn.clicked.connect(self._close_app_all)
        self.back_all_btn.clicked.connect(lambda: self._run_on_all("back"))
        self.home_all_btn.clicked.connect(lambda: self._run_on_all("home"))
        self.swipe_down_btn.clicked.connect(lambda: self._run_on_all("swipe_down"))
        self.custom_command_btn.clicked.connect(self._run_custom_command)

        return container

    # ------------------------------------------------------------------
    def trigger_refresh(self) -> None:
        if self.refresh_future and not self.refresh_future.done():
            return
        self.status_label.setText("Actualizando dispositivos...")
        self.refresh_future = run_in_executor(
            self._collect_device_snapshots,
            ui_callback=self._apply_refresh_result,
        )

    def _collect_device_snapshots(self) -> List[dict]:
        self.logger.debug("Collecting device snapshots...")
        devices = self.adb_manager.refresh_devices()
        snapshots: List[dict] = []
        for device in devices:
            snapshots.append(
                {
                    "id": device.id,
                    "model": device.get_model(force_refresh=True),
                    "battery": device.get_battery(force_refresh=True),
                    "status": device.status,
                }
            )
        return snapshots

    def _apply_refresh_result(self, snapshots: List[dict] | Exception) -> None:
        self.logger.debug(
            "Refresh result received: %s",
            "error" if isinstance(snapshots, Exception) else f"{len(snapshots)} devices",
        )
        self.status_label.setText("Listo")
        self.refresh_future = None
        if isinstance(snapshots, Exception):
            QMessageBox.warning(self, "Error", f"No se pudieron obtener dispositivos:\n{snapshots}")
            return
        snapshots = snapshots or []
        current_ids = {snap["id"] for snap in snapshots}
        if current_ids != self._last_snapshot_ids:
            self.logger.info("Dispositivos actualizados: %s", ", ".join(sorted(current_ids)) or "ninguno")
            self._last_snapshot_ids = current_ids
        self._populate_device_list(snapshots)

    def _populate_device_list(self, snapshots: List[dict]) -> None:
        self.logger.debug("Populating list with %s devices", len(snapshots))
        self.device_list.clear()
        self.device_items.clear()
        for data in snapshots:
            device = self.adb_manager.devices.get(data["id"])
            if not device:
                continue
            item = QListWidgetItem()
            widget = DeviceListItem(device)
            widget.update_info(data)
            widget.open_requested.connect(self.open_device_window)
            item.setSizeHint(widget.sizeHint())
            self.device_list.addItem(item)
            self.device_list.setItemWidget(item, widget)
            self.device_items[device.id] = widget

    # ------------------------------------------------------------------
    def _open_app_all(self) -> None:
        package = self.package_input.text().strip()
        activity = self.activity_input.text().strip() or ".MainActivity"
        if not package:
            QMessageBox.warning(self, "Error", "Define un paquete antes de abrir la app.")
            return
        self._run_on_all("open_app", package, activity)

    def _close_app_all(self) -> None:
        package = self.package_input.text().strip()
        if not package:
            QMessageBox.warning(self, "Error", "Define un paquete antes de cerrar la app.")
            return
        self._run_on_all("close_app", package)

    def _run_custom_command(self) -> None:
        command = self.custom_command_input.text().strip()
        if not command:
            return
        run_in_executor(self.adb_manager.broadcast_shell, command)

    def _run_on_all(self, method_name: str, *args) -> None:
        run_in_executor(self.adb_manager.execute_on_all, method_name, *args)

    # ------------------------------------------------------------------
    def open_device_window(self, device_id: str) -> None:
        device = self.adb_manager.devices.get(device_id)
        if not device:
            QMessageBox.warning(self, "Error", "El dispositivo ya no está conectado.")
            return
        window = self.device_windows.get(device_id)
        if window is None:
            window = DeviceWindow(device)
            self.device_windows[device_id] = window
        window.show()
        window.raise_()
        window.activateWindow()

    # ------------------------------------------------------------------
    def closeEvent(self, event: QCloseEvent) -> None:
        self.refresh_timer.stop()
        for window in self.device_windows.values():
            window.close()
        super().closeEvent(event)

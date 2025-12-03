"""Widget representing a device entry."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from ...adb import Device
from ...utils import style_icon_button


class DeviceListItem(QFrame):
    """Compact card widget showing device information."""

    open_requested = Signal(str)

    def __init__(self, device: Device, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.device = device
        self.setObjectName("DeviceListItem")
        self.setFrameShape(QFrame.StyledPanel)
        self.setProperty("status", device.status)

        self.id_label = QLabel()
        self.model_label = QLabel()
        self.battery_label = QLabel()
        self.status_label = QLabel()
        self.open_button = QPushButton()
        self.open_button.setCursor(Qt.PointingHandCursor)
        style_icon_button(self.open_button, "external", size=30)
        self.open_button.setToolTip("Abrir detalles del dispositivo")
        self.open_button.clicked.connect(self._emit_open)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("ID"), 0, 0)
        layout.addWidget(self.id_label, 0, 1)
        layout.addWidget(QLabel("Modelo"), 0, 2)
        layout.addWidget(self.model_label, 0, 3)
        layout.addWidget(QLabel("Batería"), 1, 0)
        layout.addWidget(self.battery_label, 1, 1)
        layout.addWidget(QLabel("Estado"), 1, 2)
        layout.addWidget(self.status_label, 1, 3)
        layout.addWidget(self.open_button, 0, 4, 2, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        self.update_info(
            {
                "id": device.id,
                "model": "Cargando...",
                "battery": "n/a",
                "status": device.status,
            }
        )

    def update_info(self, data: dict) -> None:
        self.setProperty("status", data.get("status", self.device.status))
        self.id_label.setText(data.get("id", self.device.id))
        self.model_label.setText(data.get("model", "n/a"))
        self.battery_label.setText(data.get("battery", "n/a"))
        self.status_label.setText(data.get("status", self.device.status))
        self.style().polish(self)

    def _emit_open(self) -> None:
        self.open_requested.emit(self.device.id)

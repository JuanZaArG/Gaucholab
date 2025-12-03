"""Intro/start screen displayed before the main window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StartScreen(QDialog):
    """Simple welcome dialog with logo, legend and start button."""

    def __init__(self, assets_dir: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gaucho One · Inicio")
        self.setModal(True)
        self.resize(640, 520)
        self.setObjectName("StartScreen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setObjectName("StartLogo")
        full_logo = assets_dir / "gaucho_full.jpg"
        pixmap = QPixmap(str(full_logo)) if full_logo.exists() else QPixmap()
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(360, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("Gaucho One")
        layout.addWidget(logo_label)

        legend_label = QLabel("“El Gauchito V1”")
        legend_label.setAlignment(Qt.AlignCenter)
        legend_label.setObjectName("StartLegend")
        layout.addWidget(legend_label)

        start_button = QPushButton("INICIAR")
        start_button.setCursor(Qt.PointingHandCursor)
        start_button.setObjectName("StartButton")
        start_button.clicked.connect(self.accept)
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

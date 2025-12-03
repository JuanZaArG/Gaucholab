"""Entry point for MultiAndroidLab."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog

from .ui import MainWindow
from .ui.start_screen import StartScreen


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def load_stylesheet() -> str:
    qss_path = Path(__file__).resolve().parent / "ui" / "styles.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MultiAndroidLab • Gaucho One")

    icon_path = ASSETS_DIR / "g1.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    start_screen = StartScreen(ASSETS_DIR)
    if start_screen.exec() != QDialog.DialogCode.Accepted:
        return 0

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

"""Lucide-like monochrome icon helper."""

from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, Qt, QObject, QEvent, QSize
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QAbstractButton

SVG_TEMPLATES = {
    "refresh": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <polyline points="23 4 23 10 17 10"/>
        <path d="M20.49 15A9 9 0 1 1 23 10"/>
    </svg>
    """,
    "play": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>
    """,
    "stop": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <rect width="14" height="14" x="5" y="5" rx="2"/>
    </svg>
    """,
    "back": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"/>
        <line x1="9" y1="12" x2="21" y2="12"/>
    </svg>
    """,
    "home": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-6 9 6v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
    """,
    "arrow-down": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <polyline points="19 12 12 19 5 12"/>
    </svg>
    """,
    "arrow-up": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="19" x2="12" y2="5"/>
        <polyline points="5 12 12 5 19 12"/>
    </svg>
    """,
    "external": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 13v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
    """,
    "terminal": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <polyline points="4 17 10 11 4 5"/>
        <line x1="12" y1="19" x2="20" y2="19"/>
    </svg>
    """,
    "settings": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <line x1="4" y1="21" x2="4" y2="14"/>
        <line x1="4" y1="10" x2="4" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12" y2="3"/>
        <line x1="20" y1="21" x2="20" y2="16"/>
        <line x1="20" y1="12" x2="20" y2="3"/>
        <line x1="1" y1="14" x2="7" y2="14"/>
        <line x1="9" y1="8" x2="15" y2="8"/>
        <line x1="17" y1="16" x2="23" y2="16"/>
    </svg>
    """,
    "monitor": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <rect width="18" height="14" x="3" y="4" rx="2"/>
        <line x1="8" y1="20" x2="16" y2="20"/>
        <line x1="12" y1="20" x2="12" y2="16"/>
    </svg>
    """,
    "target": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="4"/>
        <line x1="12" y1="2" x2="12" y2="5"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
        <line x1="2" y1="12" x2="5" y2="12"/>
        <line x1="19" y1="12" x2="22" y2="12"/>
    </svg>
    """,
    "run": """
    <svg viewBox="0 0 24 24" fill="none" stroke="CURRENT_COLOR" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 4 15 12 5 20 5 4"/>
        <line x1="19" y1="5" x2="19" y2="19"/>
    </svg>
    """,
}


def _build_svg(name: str, color: str) -> str:
    template = SVG_TEMPLATES.get(name)
    if not template:
        raise KeyError(f"Icon '{name}' is not defined")
    return template.replace("CURRENT_COLOR", color)


@lru_cache(maxsize=256)
def get_icon(name: str, size: int = 28, color: str = "#373737") -> QIcon:
    """Return a QIcon rendered from the Lucide-style template."""
    svg_data = _build_svg(name, color).encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg_data))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

@lru_cache(maxsize=256)
def get_hover_icon(name: str, size: int = 28, color: str = "#4a4a4a") -> QIcon:
    svg_data = _build_svg(name, color).encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg_data))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class _IconHoverFilter(QObject):
    def __init__(self, button: QAbstractButton, normal: QIcon, hover: QIcon) -> None:
        super().__init__(button)
        self.button = button
        self.normal = normal
        self.hover = hover

    def eventFilter(self, obj, event):
        if obj is self.button:
            if event.type() == QEvent.Enter:
                self.button.setIcon(self.hover)
            elif event.type() == QEvent.Leave:
                self.button.setIcon(self.normal)
        return False


def style_icon_button(
    button: QAbstractButton,
    icon_name: str,
    *,
    size: int = 30,
    base_color: str = "#373737",
    hover_color: str = "#4a4a4a",
) -> None:
    """Apply a Lucide icon with hover support to any button."""
    normal_icon = get_icon(icon_name, size=size, color=base_color)
    hover_icon = get_hover_icon(icon_name, size=size, color=hover_color)
    button.setIcon(normal_icon)
    button.setIconSize(QSize(size + 4, size + 4))
    filter_obj = _IconHoverFilter(button, normal_icon, hover_icon)
    button._icon_hover_filter = filter_obj  # type: ignore[attr-defined]
    button.installEventFilter(filter_obj)

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root (parent of this file's directory) is on sys.path
# so that `src.*` imports work whether this file is run directly or as a module.
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PyQt6.QtWidgets import QApplication  # noqa: E402

from src.ui.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Dark studio palette — matches the 3D viewport dark background
    from PyQt6.QtGui import QPalette, QColor
    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window,          QColor( 38,  40,  50))  # dark sidebar
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(210, 212, 220))  # light text
    pal.setColor(QPalette.ColorRole.Base,            QColor( 28,  30,  38))  # input fields
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor( 34,  36,  46))
    pal.setColor(QPalette.ColorRole.ToolTipBase,     QColor( 50,  52,  65))
    pal.setColor(QPalette.ColorRole.ToolTipText,     QColor(210, 212, 220))
    pal.setColor(QPalette.ColorRole.Text,            QColor(210, 212, 220))
    pal.setColor(QPalette.ColorRole.Button,          QColor( 55,  58,  72))  # buttons
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(210, 212, 220))
    pal.setColor(QPalette.ColorRole.BrightText,      QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.Link,            QColor( 80, 140, 240))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor( 65, 120, 220))  # blue accent
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.Mid,             QColor( 45,  47,  58))
    pal.setColor(QPalette.ColorRole.Dark,            QColor( 25,  26,  34))
    pal.setColor(QPalette.ColorRole.Shadow,          QColor( 15,  15,  20))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

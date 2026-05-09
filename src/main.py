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
    # Light gray palette for the whole window
    from PyQt6.QtGui import QPalette, QColor
    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(226, 226, 232))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor( 30,  30,  40))
    pal.setColor(QPalette.ColorRole.Base,            QColor(240, 240, 244))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(220, 220, 226))
    pal.setColor(QPalette.ColorRole.Button,          QColor(210, 210, 218))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor( 30,  30,  40))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor( 70, 120, 220))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

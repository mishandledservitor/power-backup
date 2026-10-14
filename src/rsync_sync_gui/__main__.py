"""App entry point: `python -m rsync_sync_gui` and the packaged .app launch target (FR-001)."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from rsync_sync_gui.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 600)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

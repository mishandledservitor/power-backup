"""Live rsync output + final success/error summary + cancel (FR-004, FR-012, FR-013)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from rsync_sync_gui.services.rsync_runner import parse_overall_progress


class ProgressView(QWidget):
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.output = QPlainTextEdit(readOnly=True)
        self.status_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate until the first progress line arrives
        self.progress_bar.setTextVisible(True)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.output)
        layout.addWidget(self.cancel_button)

    def start(self) -> None:
        self.output.clear()
        self.status_label.setText("Syncing…")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat("Starting…")
        self.cancel_button.setEnabled(True)

    def append_line(self, line: str) -> None:
        self.output.appendPlainText(line)
        progress = parse_overall_progress(line)
        if progress is not None:
            done, total = progress
            self.progress_bar.setRange(0, max(total, 1))
            self.progress_bar.setValue(done)
            self.progress_bar.setFormat(f"{done} / {total} files (%p%)")

    def finish_success(self, files_transferred: int, bytes_transferred: int) -> None:
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.progress_bar.setFormat("Done")
        self.status_label.setText(
            f"Success — {files_transferred} file(s), {bytes_transferred} bytes transferred."
        )

    def finish_error(self, message: str) -> None:
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Failed")
        self.status_label.setText("Failed.")
        self.output.appendPlainText(message)

    def finish_canceled(self) -> None:
        self.cancel_button.setEnabled(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Canceled")
        self.status_label.setText("Canceled.")

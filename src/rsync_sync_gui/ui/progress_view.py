"""Live rsync output + final success/error summary + cancel (FR-004, FR-012, FR-013)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class ProgressView(QWidget):
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.output = QPlainTextEdit(readOnly=True)
        self.status_label = QLabel("")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.output)
        layout.addWidget(self.cancel_button)

    def start(self) -> None:
        self.output.clear()
        self.status_label.setText("Syncing…")
        self.cancel_button.setEnabled(True)

    def append_line(self, line: str) -> None:
        self.output.appendPlainText(line)

    def finish_success(self, files_transferred: int, bytes_transferred: int) -> None:
        self.cancel_button.setEnabled(False)
        self.status_label.setText(
            f"Success — {files_transferred} file(s), {bytes_transferred} bytes transferred."
        )

    def finish_error(self, message: str) -> None:
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Failed.")
        self.output.appendPlainText(message)

    def finish_canceled(self) -> None:
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Canceled.")

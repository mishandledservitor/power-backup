"""Dry-run preview + explicit Confirm/Cancel before any destructive sync (FR-006)."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QListWidget, QVBoxLayout

from rsync_sync_gui.models.sync_run import PreviewChange

_LABELS = {"add": "Add", "update": "Update", "delete": "Delete"}


class PreviewDialog(QDialog):
    def __init__(self, changes: list[PreviewChange], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm destructive sync")

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Mirror mode is enabled. The following changes will be applied, "
                "including deletions at the destination. Review before confirming."
            )
        )

        self.list_widget = QListWidget()
        for change in sorted(changes, key=lambda c: c.change_type):
            self.list_widget.addItem(f"[{_LABELS.get(change.change_type, change.change_type)}] {change.path}")
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Confirm")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def confirm(changes: list[PreviewChange], parent=None) -> bool:
        dialog = PreviewDialog(changes, parent)
        return dialog.exec() == QDialog.Accepted

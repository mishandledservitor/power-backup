"""Main window: folder pickers, saved jobs, mirror toggle, and the sync flow."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from rsync_sync_gui.models.job import Job, JobValidationError
from rsync_sync_gui.models.sync_run import SyncStatus
from rsync_sync_gui.services import path_validation
from rsync_sync_gui.services.errors import readable_error
from rsync_sync_gui.services.job_store import JobStore
from rsync_sync_gui.services.rsync_runner import parse_preview_changes, parse_summary
from rsync_sync_gui.ui.preview_dialog import PreviewDialog
from rsync_sync_gui.ui.progress_view import ProgressView
from rsync_sync_gui.ui.sync_worker import SyncWorker


class MainWindow(QMainWindow):
    def __init__(self, job_store: JobStore | None = None):
        super().__init__()
        self.setWindowTitle("Rsync Sync GUI")
        self.job_store = job_store or JobStore()
        self._worker: SyncWorker | None = None
        self._sync_status = SyncStatus.PENDING
        self._active_run_is_mirror = False

        self.source_label = QLabel("No source selected")
        self.destination_label = QLabel("No destination selected")
        pick_source = QPushButton("Choose Source…")
        pick_source.clicked.connect(self._pick_source)
        pick_destination = QPushButton("Choose Destination…")
        pick_destination.clicked.connect(self._pick_destination)

        self.mirror_checkbox = QCheckBox("Mirror mode (deletes files at destination not in source)")

        self.sync_button = QPushButton("Sync")
        self.sync_button.setEnabled(False)
        self.sync_button.clicked.connect(self._on_sync_clicked)

        self.progress_view = ProgressView()
        self.progress_view.cancel_requested.connect(self._on_cancel_clicked)

        self.job_list = QListWidget()
        self.job_list.itemSelectionChanged.connect(self._on_job_selected)
        save_job_button = QPushButton("Save as Job")
        save_job_button.clicked.connect(self._on_save_job_clicked)
        delete_job_button = QPushButton("Delete Job")
        delete_job_button.clicked.connect(self._on_delete_job_clicked)
        run_job_button = QPushButton("Run Selected Job")
        run_job_button.clicked.connect(self._on_sync_clicked)

        picker_row = QHBoxLayout()
        picker_row.addWidget(pick_source)
        picker_row.addWidget(pick_destination)

        job_buttons_row = QHBoxLayout()
        job_buttons_row.addWidget(save_job_button)
        job_buttons_row.addWidget(delete_job_button)
        job_buttons_row.addWidget(run_job_button)

        layout = QVBoxLayout()
        layout.addLayout(picker_row)
        layout.addWidget(self.source_label)
        layout.addWidget(self.destination_label)
        layout.addWidget(self.mirror_checkbox)
        layout.addWidget(self.sync_button)
        layout.addWidget(QLabel("Saved Jobs"))
        layout.addWidget(self.job_list)
        layout.addLayout(job_buttons_row)
        layout.addWidget(self.progress_view)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.source: str | None = None
        self.destination: str | None = None
        self._refresh_job_list()

    # -- Folder selection -------------------------------------------------

    def _pick_source(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose Source Folder")
        if path:
            self.source = path
            self.source_label.setText(path)
            self._update_sync_enabled()

    def _pick_destination(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose Destination Folder")
        if path:
            self.destination = path
            self.destination_label.setText(path)
            self._update_sync_enabled()

    def _update_sync_enabled(self) -> None:
        if not self.source or not self.destination:
            self.sync_button.setEnabled(False)
            return
        reason = path_validation.is_nested_or_equal(self.source, self.destination)
        self.sync_button.setEnabled(reason is None)
        if reason:
            QMessageBox.warning(self, "Invalid selection", reason)

    # -- Job list -----------------------------------------------------------

    def _refresh_job_list(self) -> None:
        self.job_list.clear()
        for job in self.job_store.load():
            available = path_validation.is_available(job.source) and path_validation.is_available(
                job.destination
            )
            label = job.name if available else f"{job.name} (unavailable)"
            item = QListWidgetItem(label)
            item.setData(1, job.id)
            if not available:
                item.setToolTip("Source or destination folder is not currently available.")
            self.job_list.addItem(item)

    def _on_job_selected(self) -> None:
        items = self.job_list.selectedItems()
        if not items:
            return
        job_id = items[0].data(1)
        job = next((j for j in self.job_store.load() if j.id == job_id), None)
        if job is None:
            return
        self.source = job.source
        self.destination = job.destination
        self.source_label.setText(job.source)
        self.destination_label.setText(job.destination)
        self.mirror_checkbox.setChecked(job.mirror_enabled)
        self._update_sync_enabled()

    def _on_save_job_clicked(self) -> None:
        if not self.source or not self.destination:
            QMessageBox.warning(self, "Cannot save job", "Choose a source and destination first.")
            return
        name, ok = _prompt_for_name(self)
        if not ok or not name:
            return
        job = Job(
            name=name,
            source=self.source,
            destination=self.destination,
            mirror_enabled=self.mirror_checkbox.isChecked(),
        )
        try:
            self.job_store.add(job)
        except JobValidationError as exc:
            QMessageBox.warning(self, "Cannot save job", str(exc))
            return
        self._refresh_job_list()

    def _on_delete_job_clicked(self) -> None:
        items = self.job_list.selectedItems()
        if not items:
            return
        job_id = items[0].data(1)
        self.job_store.delete(job_id)
        self._refresh_job_list()

    # -- Sync flow ------------------------------------------------------------

    def _on_sync_clicked(self) -> None:
        if not self.source or not self.destination:
            return
        reason = path_validation.is_nested_or_equal(self.source, self.destination)
        if reason:
            QMessageBox.warning(self, "Invalid selection", reason)
            return
        if not path_validation.is_available(self.source) or not path_validation.is_available(
            self.destination
        ):
            QMessageBox.warning(
                self, "Folder unavailable", "Source or destination folder is not currently available."
            )
            return

        mirror = self.mirror_checkbox.isChecked()
        self._active_run_is_mirror = mirror
        self._sync_status = SyncStatus.PENDING
        if mirror:
            self._start_preview()
        else:
            self._sync_status = SyncStatus.RUNNING
            self._start_worker(dry_run=False)

    def _start_preview(self) -> None:
        self._sync_status = SyncStatus.PREVIEWING
        self._start_worker(dry_run=True)

    def _start_worker(self, dry_run: bool) -> None:
        self.progress_view.start()
        self._worker = SyncWorker(self.source, self.destination, self._active_run_is_mirror, dry_run=dry_run)
        self._worker.line_output.connect(self.progress_view.append_line)
        if dry_run:
            self._worker.finished_run.connect(self._on_preview_finished)
        else:
            self._worker.finished_run.connect(self._on_real_run_finished)
        self._worker.start()

    def _on_preview_finished(self, exit_code: int, output_lines: list[str]) -> None:
        if exit_code != 0:
            self._sync_status = SyncStatus.FAILED
            self.progress_view.finish_error(readable_error(exit_code, output_lines))
            return

        changes = parse_preview_changes(output_lines)
        self._sync_status = SyncStatus.AWAITING_CONFIRMATION
        confirmed = PreviewDialog.confirm(changes, parent=self)
        if not confirmed:
            self._sync_status = SyncStatus.CANCELED
            self.progress_view.finish_canceled()
            return
        self._sync_status = SyncStatus.RUNNING
        self._start_worker(dry_run=False)

    def _on_real_run_finished(self, exit_code: int, output_lines: list[str]) -> None:
        if self._worker and self._worker.process.canceled:
            self._sync_status = SyncStatus.CANCELED
            self.progress_view.finish_canceled()
            return
        if exit_code != 0:
            self._sync_status = SyncStatus.FAILED
            self.progress_view.finish_error(readable_error(exit_code, output_lines))
            return
        self._sync_status = SyncStatus.SUCCEEDED
        summary = parse_summary(output_lines) or (0, 0)
        self.progress_view.finish_success(*summary)

    def _on_cancel_clicked(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Sync in progress",
                "A sync is currently running. Quitting will cancel it. Quit anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            self._worker.cancel()
            self._worker.wait()
        event.accept()


def _prompt_for_name(parent) -> tuple[str, bool]:
    from PySide6.QtWidgets import QInputDialog

    return QInputDialog.getText(parent, "Save Job", "Job name:")

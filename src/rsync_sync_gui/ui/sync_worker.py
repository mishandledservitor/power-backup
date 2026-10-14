"""Runs an RsyncProcess off the Qt main thread, emitting signals for the UI."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from rsync_sync_gui.services.rsync_runner import RsyncProcess


class SyncWorker(QThread):
    line_output = Signal(str)
    finished_run = Signal(int, list)  # exit_code, output_lines

    def __init__(self, source: str, destination: str, mirror_enabled: bool, dry_run: bool = False):
        super().__init__()
        self.process = RsyncProcess(source, destination, mirror_enabled, dry_run=dry_run)

    def run(self) -> None:
        for line in self.process.stream():
            self.line_output.emit(line)
        self.finished_run.emit(self.process.exit_code, self.process.output_lines)

    def cancel(self) -> None:
        self.process.cancel()

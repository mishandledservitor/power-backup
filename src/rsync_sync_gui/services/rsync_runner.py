"""Builds rsync argv lists and runs them as a subprocess, streaming output.

Never builds a shell string - always an argv list, per the constitution's Technology
Constraints (no shelling through unsanitized user input).
"""

from __future__ import annotations

import re
import subprocess

from rsync_sync_gui.models.sync_run import PreviewChange

_STATS_RE = re.compile(r"Number of files transferred:\s*([\d,]+)")
_BYTES_RE = re.compile(r"Total transferred file size:\s*([\d,]+)")

# itemize-changes lines look like: ">f+++++++++ path/to/file" or "*deleting   path/to/file"
_ITEMIZE_DELETE_RE = re.compile(r"^\*deleting\s+(.+)$")
_ITEMIZE_CHANGE_RE = re.compile(r"^([<>c.*][fdLDS]\S{9})\s+(.+)$")


def build_argv(source: str, destination: str, mirror_enabled: bool, dry_run: bool = False) -> list[str]:
    """Build an rsync argv list. Never returns a shell string."""
    argv = ["rsync", "-a", "--itemize-changes", "--stats"]
    if mirror_enabled:
        argv.append("--delete")
    if dry_run:
        argv.append("--dry-run")
    # Trailing slash on source means "copy contents of", matching user expectation
    # of syncing folder-to-folder rather than nesting source inside destination.
    src = source if source.endswith("/") else source + "/"
    argv.append(src)
    argv.append(destination)
    return argv


class RsyncProcess:
    """Wraps a running rsync subprocess: streamed output plus a way to cancel it (FR-013)."""

    def __init__(self, source: str, destination: str, mirror_enabled: bool, dry_run: bool = False):
        self.argv = build_argv(source, destination, mirror_enabled, dry_run=dry_run)
        self._process = subprocess.Popen(
            self.argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self.output_lines: list[str] = []
        self.canceled = False

    def stream(self):
        assert self._process.stdout is not None
        for line in self._process.stdout:
            line = line.rstrip("\n")
            self.output_lines.append(line)
            yield line
        self._process.stdout.close()
        self.exit_code = self._process.wait()

    def cancel(self) -> None:
        """Terminate the in-progress rsync subprocess (FR-013)."""
        self.canceled = True
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()


def parse_preview_changes(output_lines: list[str]) -> list[PreviewChange]:
    """Parse `--itemize-changes` dry-run output into PreviewChange entries."""
    changes: list[PreviewChange] = []
    for line in output_lines:
        delete_match = _ITEMIZE_DELETE_RE.match(line)
        if delete_match:
            changes.append(PreviewChange(path=delete_match.group(1).strip(), change_type="delete"))
            continue
        change_match = _ITEMIZE_CHANGE_RE.match(line)
        if change_match:
            flags, path = change_match.groups()
            change_type = "add" if flags.startswith(">f+") else "update"
            changes.append(PreviewChange(path=path.strip(), change_type=change_type))
    return changes


def parse_summary(output_lines: list[str]) -> tuple[int, int] | None:
    """Parse rsync's final stats block (from --stats) into (files_transferred, bytes_transferred)."""
    files = bytes_ = None
    for line in output_lines:
        m = _STATS_RE.search(line)
        if m:
            files = int(m.group(1).replace(",", ""))
        m = _BYTES_RE.search(line)
        if m:
            bytes_ = int(m.group(1).replace(",", ""))
    if files is None or bytes_ is None:
        return None
    return files, bytes_

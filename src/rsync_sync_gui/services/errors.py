"""Turns rsync/subprocess failures into readable messages for the UI (FR-012)."""

from __future__ import annotations

import logging

logger = logging.getLogger("rsync_sync_gui")
logging.basicConfig(level=logging.INFO)


def readable_error(exit_code: int, output_lines: list[str]) -> str:
    """Build a human-readable error message from rsync's exit code and output."""
    logger.error("rsync exited with code %s", exit_code)
    tail = [line for line in output_lines[-5:] if line.strip()]
    if tail:
        return f"Sync failed (exit code {exit_code}):\n" + "\n".join(tail)
    return f"Sync failed (exit code {exit_code}). No further output was captured."

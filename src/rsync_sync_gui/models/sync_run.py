"""SyncRun entity: a single execution of a sync, with its state machine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SyncStatus(Enum):
    PENDING = "pending"
    PREVIEWING = "previewing"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class InvalidTransitionError(ValueError):
    """Raised when a SyncRun status transition would violate the state machine."""


# Allowed transitions. previewing/awaiting_confirmation can only be skipped when mirror is off.
_TRANSITIONS: dict[SyncStatus, set[SyncStatus]] = {
    SyncStatus.PENDING: {SyncStatus.PREVIEWING, SyncStatus.RUNNING},
    SyncStatus.PREVIEWING: {SyncStatus.AWAITING_CONFIRMATION, SyncStatus.FAILED},
    SyncStatus.AWAITING_CONFIRMATION: {SyncStatus.RUNNING, SyncStatus.CANCELED},
    SyncStatus.RUNNING: {SyncStatus.SUCCEEDED, SyncStatus.FAILED, SyncStatus.CANCELED},
    SyncStatus.SUCCEEDED: set(),
    SyncStatus.FAILED: set(),
    SyncStatus.CANCELED: set(),
}


@dataclass
class PreviewChange:
    path: str
    change_type: str  # "add" | "update" | "delete"


@dataclass
class SyncSummary:
    files_transferred: int
    bytes_transferred: int


@dataclass
class SyncRun:
    source: str
    destination: str
    mirror_enabled: bool
    status: SyncStatus = SyncStatus.PENDING
    preview_changes: list[PreviewChange] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)
    exit_code: int | None = None
    error_message: str | None = None
    summary: SyncSummary | None = None

    def transition_to(self, new_status: SyncStatus) -> None:
        allowed = _TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from {self.status.value} to {new_status.value}."
            )
        if self.mirror_enabled and self.status is SyncStatus.PENDING and new_status is SyncStatus.RUNNING:
            raise InvalidTransitionError(
                "Mirror-enabled runs must go through previewing/awaiting_confirmation before running."
            )
        self.status = new_status

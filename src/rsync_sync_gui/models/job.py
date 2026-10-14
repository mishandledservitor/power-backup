"""Job entity: a saved, named sync configuration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from rsync_sync_gui.services.path_validation import is_nested_or_equal


class JobValidationError(ValueError):
    """Raised when a Job's fields violate a validation rule."""


@dataclass
class Job:
    name: str
    source: str
    destination: str
    mirror_enabled: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = ""
    updated_at: str = ""

    def validate(self, existing_names: list[str] = ()) -> None:
        if not self.name or not self.name.strip():
            raise JobValidationError("Job name must not be empty.")
        if not self.source or not self.source.strip():
            raise JobValidationError("Source path must not be empty.")
        if not self.destination or not self.destination.strip():
            raise JobValidationError("Destination path must not be empty.")
        if not self.source.startswith("/") or not self.destination.startswith("/"):
            raise JobValidationError("Source and destination must be absolute paths.")

        lowered = self.name.strip().lower()
        if any(n.strip().lower() == lowered for n in existing_names):
            raise JobValidationError(f'A job named "{self.name}" already exists.')

        reason = is_nested_or_equal(self.source, self.destination)
        if reason:
            raise JobValidationError(reason)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "destination": self.destination,
            "mirror_enabled": self.mirror_enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Job:
        return cls(
            id=data["id"],
            name=data["name"],
            source=data["source"],
            destination=data["destination"],
            mirror_enabled=data.get("mirror_enabled", False),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

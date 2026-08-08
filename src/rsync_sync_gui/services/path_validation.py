"""Path validation: mounted/available check and nested-or-equal check (FR-010, FR-011)."""

from __future__ import annotations

from pathlib import Path


def is_available(path: str) -> bool:
    """Return True if `path` currently exists and is reachable on disk."""
    try:
        return Path(path).is_dir()
    except OSError:
        return False


def is_nested_or_equal(source: str, destination: str) -> str | None:
    """Return a human-readable reason if source/destination are equal or nested, else None."""
    try:
        src = Path(source).resolve()
        dst = Path(destination).resolve()
    except OSError:
        # Can't resolve (e.g. path doesn't exist yet) - fall back to raw string comparison.
        src = Path(source)
        dst = Path(destination)

    if src == dst:
        return "Source and destination must not be the same folder."
    if dst == src or dst.is_relative_to(src):
        return "Destination must not be inside the source folder."
    if src.is_relative_to(dst):
        return "Source must not be inside the destination folder."
    return None

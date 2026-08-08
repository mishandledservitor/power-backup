# Quickstart: Rsync Folder Sync GUI

Validates the feature end-to-end once implemented. See [data-model.md](./data-model.md) for the
Job/Sync Run fields referenced below, and [plan.md](./plan.md) for the source layout.

## Prerequisites

- macOS with `rsync` available on `PATH` (`rsync --version` succeeds).
- Python 3.11+ with project dependencies installed (PySide6, and dev dependency `pytest`).
- Two scratch folders for manual testing, e.g. `~/tmp/sync-src` and `~/tmp/sync-dst`, each on a
  different mounted volume if you want to exercise the "different hard drives" scenario for real
  (a second folder on the same drive is fine for functional testing).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the app (development, unpackaged)

```bash
python -m rsync_sync_gui
```

## Validation scenarios

### 1. One-off sync (User Story 1)

1. Put a few files in `~/tmp/sync-src`.
2. Launch the app, pick `~/tmp/sync-src` as source and `~/tmp/sync-dst` as destination.
3. Click Sync (mirror mode left off).
4. **Expect**: live output while it runs; on completion, a success summary; `~/tmp/sync-dst` now
   contains the source's files.

### 2. Saved job persists (User Story 2)

1. From the same source/destination, save as a job named "Test Job".
2. Quit and relaunch the app.
3. **Expect**: "Test Job" appears in the job list; running it again succeeds without re-picking
   folders.
4. Rename the job, then delete it. **Expect**: both changes survive another relaunch.

### 3. Unavailable job folder (User Story 2, edge case)

1. Save a job pointing at a folder on a removable volume.
2. Unmount that volume.
3. Reopen the app / select that job.
4. **Expect**: the job is visibly flagged as unavailable; the app does not attempt to run rsync
   against it.

### 4. Destructive mirror sync requires preview + confirm (User Story 3)

1. Add an extra file to `~/tmp/sync-dst` that does not exist in `~/tmp/sync-src`.
2. Enable mirror mode on the job/pair and start the sync.
3. **Expect**: a dry-run preview appears listing that extra file as a deletion, before anything
   runs for real.
4. Click Cancel. **Expect**: the extra file still exists in `~/tmp/sync-dst`.
5. Repeat the sync, this time confirming. **Expect**: the extra file is now removed, and the
   preview accurately predicted this.

### 5. Blocked nested/identical paths (edge case, FR-011)

1. Try to set destination equal to source, then destination as a subfolder of source.
2. **Expect**: both are rejected before any rsync invocation, with a clear message.

### 6. Error surfaced readably (edge case, FR-012)

1. Point the destination at a path you don't have write permission to (or unplug the destination
   drive mid-sync, if testing manually with a real removable drive).
2. **Expect**: the app shows a readable error message and does not report success.

## Automated checks

```bash
pytest tests/unit          # rsync_runner argv building, job_store persistence, path_validation
pytest tests/integration   # end-to-end sync against temp folders, no GUI required
```

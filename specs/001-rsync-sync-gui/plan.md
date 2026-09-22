# Implementation Plan: Rsync Folder Sync GUI

**Branch**: `001-rsync-sync-gui` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-rsync-sync-gui/spec.md`

## Summary

A double-clickable macOS desktop app (PySide6/Qt GUI over the system `rsync` binary) that lets a user pick source/destination folders, run a sync with live progress, save recurring folder pairs as named jobs, and — for any destructive/mirror sync — always shows an `rsync --dry-run` preview requiring explicit confirmation before anything is deleted.

## Technical Context

**Language/Version**: Python 3.11+ (matched to the packaging tool's supported range)

**Primary Dependencies**: PySide6 (Qt6 bindings) for the GUI; system `rsync` binary invoked via `subprocess` (argument list, not shell string); py2app or PyInstaller for `.app` packaging

**Storage**: Local JSON file under the user's app-support directory (e.g.
`~/Library/Application Support/RsyncSyncGui/jobs.json`) for saved jobs — no database needed

**Testing**: pytest for unit tests (argument-building, path-validation logic); manual/quickstart validation for GUI flows (Qt GUI test automation is out of scope for v1 given the small surface)

**Target Platform**: macOS (current and previous major OS version), local filesystem paths only

**Project Type**: Desktop application (single project)

**Performance Goals**: UI remains responsive (no frozen window) while a sync runs; progress updates at least once per second during an active transfer

**Constraints**: No terminal interaction required for normal use; destructive operations must always be preview-then-confirm (constitution Principle II); sync must run off the Qt main thread so the UI doesn't block

**Scale/Scope**: Single user, single machine; expected job count in the tens, not hundreds; folder trees of ordinary personal/backup size (rsync itself handles the scale, not the app)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Thin Wrapper Over rsync | Plan only invokes `rsync` as a subprocess for all transfer/diff logic; app never re-implements copy/delete/diff itself | PASS |
| II. Safety by Default (NON-NEGOTIABLE) | Destructive flags (`--delete` etc.) only added when mirror mode is explicitly enabled per job; dry-run preview + explicit confirm required before any such run (FR-005, FR-006, US3) | PASS |
| III. Native macOS Experience | PySide6 GUI, packaged as `.app` via py2app/PyInstaller, no terminal required (FR-001) | PASS |
| IV. Observable Operations | Live rsync stdout/stderr streamed to the UI; exact command shown; errors surfaced readably (FR-004, FR-012) | PASS |
| V. Simplicity (YAGNI) | No scheduling, cloud sync, or plugin system in this feature; scope matches spec's Assumptions | PASS |

No violations — Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-rsync-sync-gui/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` directory: this feature exposes no external API, CLI, or network interface — its only "contract" is the rsync command-line invocation itself, which is documented in `data-model.md` and `quickstart.md` instead.

### Source Code (repository root)

```text
src/
├── rsync_sync_gui/
│   ├── __main__.py           # App entry point (launches the Qt application)
│   ├── models/
│   │   ├── job.py            # Job entity: source, destination, options
│   │   └── sync_run.py       # SyncRun entity: status, progress, preview
│   ├── services/
│   │   ├── rsync_runner.py   # Builds argv, runs rsync subprocess, streams output
│   │   ├── job_store.py      # Load/save jobs.json in app-support dir
│   │   └── path_validation.py# Mounted-drive check, nested-path check
│   └── ui/
│       ├── main_window.py    # Job list, source/destination pickers, Sync button
│       ├── progress_view.py  # Live output + progress display
│       └── preview_dialog.py # Dry-run preview + confirm/cancel
│
tests/
├── unit/
│   ├── test_rsync_runner.py
│   ├── test_job_store.py
│   └── test_path_validation.py
└── integration/
    └── test_sync_flow.py     # End-to-end sync against temp folders (no real GUI needed)

packaging/
└── setup.py                  # py2app (or equivalent PyInstaller spec) build config
```

**Structure Decision**: Single desktop-app project (Option 1 pattern) under `src/rsync_sync_gui/`, split into `models/` (data), `services/` (rsync invocation, persistence, validation — all independently unit-testable without Qt), and `ui/` (PySide6 widgets). This keeps the rsync/ subprocess logic testable in isolation from the GUI, per Principle I and the constitution's Development Workflow expectations.

## Complexity Tracking

*No violations — table omitted.*

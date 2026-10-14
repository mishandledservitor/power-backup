<!--
Sync Impact Report
Version change: (none) → 1.0.0
Modified principles: n/a (initial ratification)
Added sections: Core Principles (I-V), Technology Constraints, Development Workflow, Governance
Removed sections: none
Follow-up TODOs: none
-->

# RsyncSyncGui Constitution

## Core Principles

### I. Thin Wrapper Over rsync
The app MUST NOT reimplement file-sync, diffing, or transfer logic. All actual synchronization work is delegated to the system `rsync` binary, invoked as a subprocess. The GUI's job is limited
to: composing rsync command-line arguments from user choices, running the command, and presenting its output/progress/errors. Rationale: rsync is battle-tested for exactly this problem; reimplementing any part of it introduces correctness and data-loss risk for no benefit.

### II. Safety by Default (NON-NEGOTIABLE)
Any rsync flag that can delete or overwrite data at the destination (e.g. `--delete`, `--delete-excluded`, `-I`/`--ignore-times` combined with overwrite, or any dry-run being skipped) MUST be opt-in, never default. Before running a sync job that includes a destructive flag, the app MUST show the user a dry-run summary (via `rsync --dry-run`) of what will change or be removed, and require explicit confirmation before the real run executes. Rationale: this tool moves data between physical hard drives the user cares about; an accidental irreversible delete is the single worst failure mode.

### III. Native macOS Experience
The app MUST be packaged as a double-clickable `.app` bundle (via py2app or PyInstaller) and MUST NOT require the user to open a terminal for normal use. The GUI MUST use PySide6 (Qt for Python) widgets and follow standard macOS interaction conventions (menu bar, standard dialogs, drag-and-drop folder selection). Rationale: the explicit goal is a double-click launchable GUI, not a script.

### IV. Observable Operations
Every rsync invocation MUST be visible to the user in the moment: the exact command being run, and its live stdout/stderr output, must be shown in the UI (not just a spinner). Errors from rsync (non-zero exit codes) MUST surface as a readable message, not be silently swallowed. Rationale: sync jobs move real data across drives; users need to trust and verify what happened.

### V. Simplicity (YAGNI)
Favor the smallest feature set that lets the user define a source folder, a destination folder, and rsync options, save that as a named "job", and run it. Do not add scheduling, cloud sync, multi-machine coordination, or plugin systems unless a real need is documented in a spec first.
Rationale: this is a personal utility for syncing folders across drives, not a backup platform.

## Technology Constraints

- Language: Python 3 (target the version bundled with the chosen packaging tool).
- GUI toolkit: PySide6 (Qt).
- Packaging: py2app or PyInstaller producing a signed-or-unsigned double-clickable `.app`.
- External dependency: system `rsync` (invoked via `subprocess`, never shelled through a string that concatenates unsanitized user input — build argument lists, not shell strings).
- Target platform: macOS only. No requirement to support Linux/Windows.

## Development Workflow

- All feature work MUST flow through Spec Kit (`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`), per this repo's root `CLAUDE.md` standing rules.
- All work happens on a worktree/branch, never directly on `main`.
- Each round of work ends in a commit of what changed, including Spec Kit artifacts.

## Governance

This constitution supersedes ad-hoc practices for this project. Amendments require editing this file via `/speckit-constitution`, bumping the version per semantic versioning (MAJOR: incompatible principle removal/redefinition; MINOR: new principle or materially expanded guidance; PATCH: wording/clarification only), and updating `Last Amended`. Any plan or task that conflicts with a principle here — especially Principle II (Safety by Default) — must be revised, not the principle.

**Version**: 1.0.0 | **Ratified**: 2026-08-08 | **Last Amended**: 2026-08-08

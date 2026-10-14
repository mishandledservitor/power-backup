# Feature Specification: Rsync Folder Sync GUI

**Feature Branch**: `001-rsync-sync-gui`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "A GUI, launchable by double-clicking an app icon, that helps use rsync to synchronize various folders across different hard drives."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a one-off folder sync (Priority: P1)

A user picks a source folder and a destination folder (each possibly on a different attached hard drive), reviews what will happen, and runs a sync that copies new/changed files from source to destination.

**Why this priority**: This is the core value of the app — without it there is no product. Every other capability builds on being able to pick two folders and sync them.

**Independent Test**: Can be fully tested by selecting a source folder and a destination folder on two different drives, running the sync, and confirming the destination now contains the source's files. Delivers value on its own even with no saved jobs.

**Acceptance Scenarios**:

1. **Given** the app is open with no folders selected, **When** the user picks a source and a destination folder, **Then** the app shows both paths and enables a "Sync" action.
2. **Given** valid source and destination folders are selected, **When** the user starts the sync, **Then** the app shows live progress/output and, on completion, a clear success summary (files copied, bytes transferred).
3. **Given** a sync is running, **When** rsync exits with an error (e.g. destination drive disconnected mid-transfer), **Then** the app shows a readable error message and does not report false success.

---

### User Story 2 - Save and re-run a sync job (Priority: P2)

A user who regularly syncs the same pair of folders (e.g. "Photos" drive → "Backup" drive) saves that source/destination/options combination as a named job, so they don't have to re-pick folders every time.

**Why this priority**: Turns the app from a one-off utility into something usable for recurring backup routines — the main reason someone would want a persistent double-click app instead of a one-liner terminal command.

**Independent Test**: Can be tested by creating a job, closing and reopening the app, and confirming the saved job still appears and runs correctly against the same folders.

**Acceptance Scenarios**:

1. **Given** a source and destination are selected, **When** the user saves the job with a name, **Then** the job appears in a persistent list the next time the app is opened.
2. **Given** a saved job whose source or destination folder no longer exists (e.g. drive not currently connected), **When** the user opens the app or selects that job, **Then** the app clearly indicates the folder is unavailable rather than failing silently or crashing.
3. **Given** a saved job, **When** the user deletes or renames it, **Then** the change persists across app restarts.

---

### User Story 3 - Preview and confirm before a destructive sync (Priority: P1)

A user wants the destination to exactly mirror the source, including removing files at the destination that no longer exist at the source. Before anything is deleted, the user sees exactly what would change and must explicitly confirm.

**Why this priority**: This is the app's core safety guarantee (constitution Principle II). It is P1 because shipping "mirror mode" without this preview/confirm step would violate the project's non-negotiable safety principle and risks real, unrecoverable data loss on the user's drives.

**Independent Test**: Can be tested by enabling mirror/delete mode on a job where the destination has extra files, confirming a dry-run preview lists exactly those files as "to be removed", and verifying nothing is deleted until the user explicitly confirms.

**Acceptance Scenarios**:

1. **Given** mirror mode is enabled for a job, **When** the user starts the sync, **Then** the app first runs a dry-run and displays every file/folder that would be added, changed, or removed, before touching the destination.
2. **Given** a dry-run preview is shown, **When** the user cancels, **Then** no files at the destination are modified or removed.
3. **Given** a dry-run preview is shown, **When** the user explicitly confirms, **Then** the real sync runs with the previewed destructive changes applied.
4. **Given** mirror mode is disabled (the default for a new job), **When** the user runs a sync, **Then** no destination files are ever removed, regardless of source contents.

---

### Edge Cases

- What happens when the source or destination folder is on a drive that is not currently mounted/ connected? App must detect this before attempting to run rsync and tell the user, not attempt the sync and produce a confusing rsync error.
- What happens when the source and destination resolve to the same folder, or the destination is a subfolder of the source (or vice versa)? App must detect and block this before running rsync.
- What happens if the user closes the app while a sync is in progress? The running rsync process must be handled gracefully (e.g. app warns the sync is in progress and either blocks quitting or confirms cancellation) rather than leaving an orphaned or half-finished transfer with no indication to the user.
- What happens if the destination folder does not have enough free space? rsync's own error must be surfaced to the user in readable form; the app does not need to pre-check free space itself.
- What happens when a selected folder requires permissions the app does not have (e.g. macOS privacy-protected folders)? App must surface the permission error clearly and guide the user to grant access, rather than failing with a raw/opaque error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST launch as a double-clickable application with no terminal interaction required for normal use.
- **FR-002**: Users MUST be able to select a source folder and a destination folder using a standard folder picker (or drag-and-drop).
- **FR-003**: Users MUST be able to run a one-off sync between the selected source and destination without first saving a job.
- **FR-004**: The system MUST show the user, in real time, what the current sync operation is doing (files being transferred, progress, and any errors) — not just a generic "working" state.
- **FR-005**: The system MUST NOT remove any file at the destination, and MUST NOT overwrite a destination file whose content differs from the source, unless the user has explicitly enabled mirror mode for that job. Mirror mode's only additional effects, beyond a normal sync, are: (a) deleting destination files/folders that do not exist at the source, and (b) overwriting destination files that differ from the source. Mirror mode introduces no other destructive behavior. This requirement governs deletion and mirror-triggered overwrites only — it does not cover data loss from an interrupted transfer (see FR-012a).
- **FR-006**: When mirror mode is enabled, every single run — with no exception, and no "remember my choice" shortcut — MUST first execute a dry-run and display its full preview of additions, changes, and removals, and MUST require a fresh explicit user confirmation each time before performing the real sync. If the dry-run itself fails (e.g. rsync errors before any real change is attempted), the system MUST treat this as a sync failure per FR-012 and MUST NOT proceed to the real run.
- **FR-007**: Users MUST be able to save a source/destination/options combination as a named, reusable job.
- **FR-008**: Saved jobs MUST persist across app restarts.
- **FR-009**: Users MUST be able to view, rename, and delete previously saved jobs.
- **FR-010**: The system MUST detect and clearly report when a job's source or destination folder is currently unavailable (e.g. drive not connected) rather than attempting the sync.
- **FR-011**: The system MUST detect and block sync configurations where the destination is the same as, or nested inside, the source (or vice versa).
- **FR-012**: The system MUST surface any error reported by the underlying sync operation (non-zero exit, permission denied, out of space, connection lost) to the user in readable form.
- **FR-012a**: A transfer interrupted mid-file (e.g. by disk-full or a disconnected drive) MAY leave a partially-written file at the destination; this risk exists independent of mirror mode and is not a "destructive" operation under FR-005. The system is not required to detect or roll back partial writes beyond surfacing the failure per FR-012.
- **FR-013**: The system MUST allow the user to cancel a sync that is in progress.

### Key Entities

- **Job**: A saved, named sync configuration consisting of a source folder path, a destination folder path, and a set of sync options (at minimum: whether destructive/mirror mode is enabled). Persists across app launches.
- **Sync Run**: A single execution of a sync (from a saved job or an ad-hoc one-off pair), producing progress output, a final status (success/error/canceled), and — when destructive mode is enabled — a preview of pending changes requiring confirmation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from opening the app to a completed sync of two folders in under
  2 minutes on first use, without consulting documentation.
- **SC-002**: A user can re-run a previously saved job in two interactions or fewer (e.g. select job, click Run).
- **SC-003**: Zero unconfirmed destructive deletions occur across all usage — every removal at a destination is preceded by a preview the user explicitly approved.
- **SC-004**: When a sync fails for any reason, the user can identify what went wrong from the app's own output alone, without needing to inspect logs outside the app.

## Assumptions

- Single-user, single-machine desktop tool — no multi-user accounts, no network/remote sync server component; source and destination are both accessible as local filesystem paths (local disks or locally-mounted external/removable drives).
- No scheduling/automation in this version — every sync is user-initiated (covers a saved job as well as an ad-hoc pair); recurring/scheduled runs are out of scope unless specified in a future feature.
- "Different hard drives" means locally attached/mounted volumes (internal or external), not network shares or cloud storage; network/cloud destinations are out of scope for this version.
- Rsync options exposed to the user in v1 are limited to what's needed for the stories above (source, destination, mirror/delete toggle); advanced rsync flag tuning is out of scope unless a future story requires it.
- The `rsync` binary is assumed to already be present on the user's macOS system (as it ships with macOS or via common package managers); the app does not bundle or install it.

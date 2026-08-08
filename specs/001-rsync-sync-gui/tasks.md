---

description: "Task list for feature implementation"
---

# Tasks: Rsync Folder Sync GUI

**Input**: Design documents from `/specs/001-rsync-sync-gui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included — plan.md's Project Structure explicitly defines `tests/unit/` and
`tests/integration/`, and constitution Principle I (thin wrapper) is best enforced by unit-testing
the rsync argv-building/validation logic in isolation from the GUI.

**Organization**: Tasks are grouped by user story per spec.md priorities. US1 and US3 are both
P1; US1 (one-off sync) is sequenced first because US3 (destructive preview/confirm) extends the
same rsync runner with a dry-run step and cannot be built before it exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project, per plan.md: `src/rsync_sync_gui/`, `tests/`, `packaging/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per plan.md: `src/rsync_sync_gui/{models,services,ui}/`,
      `tests/{unit,integration}/`, `packaging/`, each with `__init__.py` where it's a Python package
- [X] T002 Create `pyproject.toml` declaring the package, Python 3.11+ requirement, and
      dependencies (`PySide6`) plus dev dependencies (`pytest`)
- [X] T003 [P] Configure linting/formatting (e.g. `ruff`) via `pyproject.toml` or `.ruff.toml`
- [X] T004 [P] Create `packaging/setup.py` with a py2app configuration stub for building the
      `.app` bundle (per research.md's packaging decision), to be completed once the app entry
      point exists

**Checkpoint**: `pip install -e ".[dev]"` succeeds; `pytest` runs (with zero tests) cleanly

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure every user story depends on — path validation, the rsync
subprocess runner, and the entities from data-model.md

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create `Job` model (per data-model.md) in `src/rsync_sync_gui/models/job.py`:
      `id`, `name`, `source`, `destination`, `mirror_enabled`, `created_at`, `updated_at`, plus a
      `validate()` method enforcing non-empty absolute paths, unique-name rules, and — reusing
      T007's `is_nested_or_equal()` check — rejecting a source/destination pair that are equal or
      nested (FR-011), so this rule holds for every `Job` regardless of whether it was built from
      the UI or loaded from `job_store.py` (depends on T007)
- [X] T006 [P] Create `SyncRun` model (per data-model.md) in
      `src/rsync_sync_gui/models/sync_run.py`: fields `source`, `destination`, `mirror_enabled`,
      `status` (enum: pending/previewing/awaiting_confirmation/running/succeeded/failed/canceled),
      `preview_changes`, `output_lines`, `exit_code`, `error_message`, `summary`, plus the
      transition guard described in data-model.md's state machine (no skipping
      previewing/awaiting_confirmation when `mirror_enabled` is true)
- [X] T007 [P] Implement path validation in `src/rsync_sync_gui/services/path_validation.py`:
      `is_available(path)` (exists/mounted check), `is_nested_or_equal(source, destination)`
      (FR-011), returning clear reasons for failure, not booleans alone
- [X] T008 Implement the rsync subprocess runner in
      `src/rsync_sync_gui/services/rsync_runner.py`: builds an argv list (never a shell string)
      from a `Job`/ad-hoc source+destination+`mirror_enabled`, runs it via `subprocess.Popen`
      with piped stdout/stderr, and yields output lines as they arrive (depends on T005, T006)
- [X] T009 Configure error handling/logging infrastructure in
      `src/rsync_sync_gui/services/__init__.py` (or a small `logging_config.py`): route rsync
      failures and unexpected exceptions to a readable message (FR-012), never a raw traceback in
      the UI

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Run a one-off folder sync (Priority: P1) 🎯 MVP

**Goal**: User picks a source and destination folder and runs a non-destructive sync, with live
progress and a clear success/error result.

**Independent Test**: Select a source and destination folder on two different drives, run the
sync, and confirm the destination now contains the source's files (quickstart.md scenario 1).

### Tests for User Story 1

- [X] T010 [P] [US1] Unit test for argv building (non-mirror mode) in
      `tests/unit/test_rsync_runner.py`: asserts no delete-capable flags are ever included when
      `mirror_enabled` is `False`
- [X] T011 [P] [US1] Unit test for path validation in `tests/unit/test_path_validation.py`:
      unavailable-drive detection and nested/identical-path detection
- [X] T012 [P] [US1] Integration test for an end-to-end non-destructive sync in
      `tests/integration/test_sync_flow.py`, using temp folders (no GUI required)

### Implementation for User Story 1

- [X] T013 [US1] Implement `main_window.py` in `src/rsync_sync_gui/ui/main_window.py`: source/
      destination folder pickers (native dialog + drag-and-drop), a "Sync" action enabled once
      both are valid (uses T007's validation to block equal/nested paths before enabling Sync)
- [X] T014 [US1] Implement `progress_view.py` in `src/rsync_sync_gui/ui/progress_view.py`:
      displays streamed rsync output live and a final success/error summary using `SyncRun`'s
      `output_lines`/`summary`/`error_message` (FR-004, FR-012)
- [X] T015 [US1] Run the rsync runner (T008) off the Qt main thread (`QThread`/`QRunnable`) from
      `main_window.py`, wiring its streamed output into `progress_view.py` so the UI never blocks
      during a sync
- [X] T016 [US1] Implement `src/rsync_sync_gui/__main__.py` as the app entry point: constructs the
      `QApplication`, shows `main_window.py`, and is the target both `python -m rsync_sync_gui`
      and the packaged `.app` launch (FR-001)
- [X] T017 [US1] Handle app-quit during an in-progress sync in `main_window.py`/`__main__.py`:
      warn the user and require confirmation before terminating a running rsync process (edge
      case from spec.md)
- [X] T018 [US1] Add a "Cancel" action to `progress_view.py` that is enabled only while a sync is
      running: terminates the in-progress rsync subprocess (via T008's runner) and transitions
      `SyncRun.status` to `canceled` (FR-013) — distinct from and in addition to T017's app-quit
      handling (depends on T008, T014, T015)

**Checkpoint**: User Story 1 fully functional — a user can pick two folders and run a real,
non-destructive sync with live feedback.

---

## Phase 4: User Story 3 - Preview and confirm before a destructive sync (Priority: P1)

**Goal**: When mirror mode is enabled, the user always sees an accurate dry-run preview of
additions/changes/removals and must explicitly confirm before anything destructive happens.

**Independent Test**: Enable mirror mode on a pair where the destination has extra files, confirm
the dry-run preview lists exactly those files as removals, and verify nothing is deleted until
explicitly confirmed (quickstart.md scenario 4).

### Tests for User Story 3

- [X] T019 [P] [US3] Unit test for argv building (mirror mode) in `tests/unit/test_rsync_runner.py`:
      asserts delete-capable flags (e.g. `--delete`) are included only when `mirror_enabled` is
      `True`, and that a dry-run invocation always adds `--dry-run`
- [X] T020 [P] [US3] Unit test for dry-run output parsing in `tests/unit/test_rsync_runner.py`:
      parses sample `rsync --dry-run --itemize-changes` output into `SyncRun.preview_changes`
      entries (`path`, `change_type` of add/update/delete)
- [X] T021 [P] [US3] Integration test for the full preview → cancel → no-changes path and
      preview → confirm → changes-applied path in `tests/integration/test_sync_flow.py`, using
      temp folders

### Implementation for User Story 3

- [X] T022 [US3] Extend `rsync_runner.py` (`src/rsync_sync_gui/services/rsync_runner.py`) with a
      `run_dry_run()` step that always precedes a real run when `mirror_enabled` is `True`,
      parsing output into `preview_changes` (depends on T008, T020)
- [X] T023 [US3] Implement `preview_dialog.py` in `src/rsync_sync_gui/ui/preview_dialog.py`:
      displays `preview_changes` grouped by add/update/delete, with explicit Confirm and Cancel
      actions; Cancel guarantees no destination changes (FR-006)
- [X] T024 [US3] Add a mirror-mode toggle to `main_window.py`, defaulting to off (FR-005); wire
      Sync so that when mirror mode is on it drives `SyncRun` through
      `pending → previewing → awaiting_confirmation → running`, invoking `preview_dialog.py`
      before any real rsync run (depends on T013, T022, T023)
- [X] T025 [US3] Ensure the real (non-dry-run) sync started from `preview_dialog.py`'s Confirm
      action reuses `progress_view.py` (T014) for live output, so the destructive run gets the
      same observability as a normal sync

**Checkpoint**: User Stories 1 and 3 both work — the app's core safety guarantee (constitution
Principle II) is enforced for every destructive sync.

---

## Phase 5: User Story 2 - Save and re-run a sync job (Priority: P2)

**Goal**: User saves a source/destination/options combination as a named job that persists across
app restarts and can be re-run, renamed, or deleted.

**Independent Test**: Create a job, close and reopen the app, and confirm the saved job still
appears and runs correctly against the same folders (quickstart.md scenario 2).

### Tests for User Story 2

- [X] T026 [P] [US2] Unit test for job persistence in `tests/unit/test_job_store.py`: save, load,
      rename, delete a job; unique-name validation (FR-009); round-trips through a real temp file
- [X] T027 [P] [US2] Integration test for the unavailable-job-folder flow in
      `tests/integration/test_sync_flow.py`: a saved job whose folder no longer exists is flagged,
      not silently run (quickstart.md scenario 3)

### Implementation for User Story 2

- [X] T028 [US2] Implement `job_store.py` in `src/rsync_sync_gui/services/job_store.py`: load/save
      a list of `Job` entities to/from a single JSON file under
      `~/Library/Application Support/RsyncSyncGui/jobs.json` (per research.md), creating the
      directory/file on first run
- [X] T029 [US2] Add a job list panel to `main_window.py`: shows saved jobs, a "Save as job" action
      from the current source/destination/mirror selection, and Rename/Delete actions (FR-007,
      FR-009), persisting through `job_store.py` (T028)
- [X] T030 [US2] On app start and on job-list refresh, run T007's availability check against each
      saved job's source/destination and visibly flag unavailable jobs in the job list (FR-010),
      without attempting to run them
- [X] T031 [US2] Wire "Run" on a saved job to reuse the existing sync flow (T013/T015 for
      non-mirror jobs, T024/T025 for mirror-enabled jobs) so a saved job behaves identically to an
      ad-hoc pair with the same options

**Checkpoint**: All three user stories independently functional — one-off sync, safe destructive
sync, and saved/reusable jobs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that span multiple user stories

- [X] T032 [P] Add a `README.md` (or extend the root one) documenting how to run the app in dev
      mode and how to build the `.app` bundle, based on quickstart.md
- [X] T033 Complete `packaging/setup.py` (started in T004) into a working py2app build producing a
      double-clickable `.app`, falling back to a PyInstaller spec per research.md if py2app proves
      incompatible with PySide6 during the build
- [X] T034 [P] Add unit test coverage for the app-quit-during-sync edge case (T017) in
      `tests/unit/test_rsync_runner.py` (process termination on cancel)
- [X] T035 Run the full quickstart.md validation checklist manually against the packaged `.app`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational only
- **User Story 3 (Phase 4)**: Depends on Foundational, and specifically on User Story 1's
  `rsync_runner.py`/`progress_view.py` (T008, T014) being in place — not independent of US1 at the
  code level, though it is independently *testable* once built
- **User Story 2 (Phase 5)**: Depends on Foundational only for its own logic (job persistence,
  availability check); its "Run" action (T031) reuses US1/US3 sync flows once they exist
- **Polish (Phase 6)**: Depends on all three user stories being complete

### Parallel Opportunities

- T003 and T004 (Setup) can run in parallel
- T006 and T007 (Foundational models/validation) can run in parallel; T005 depends on T007 (reuses
  its nested/equal check); T008 depends on T005/T006
- Within US1: T010, T011, T012 (tests) can run in parallel; T013/T014 can be worked in parallel
  before T015 wires them together
- Within US3: T019, T020, T021 (tests) can run in parallel
- Within US2: T026, T027 (tests) can run in parallel
- T032 and T034 (Polish) can run in parallel

---

## Parallel Example: User Story 1

```bash
Task: "Unit test for argv building (non-mirror mode) in tests/unit/test_rsync_runner.py"
Task: "Unit test for path validation in tests/unit/test_path_validation.py"
Task: "Integration test for end-to-end non-destructive sync in tests/integration/test_sync_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md scenario 1 against the real app
5. Demo if ready — note that mirror mode is not yet safe to expose until Phase 4 lands

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → validate → MVP (non-destructive sync only)
3. User Story 3 → validate → mirror mode becomes safe to expose (constitution Principle II)
4. User Story 2 → validate → saved/reusable jobs
5. Polish → package as a `.app` and run full quickstart.md validation

---

## Notes

- Do not expose mirror mode in the UI until Phase 4 (US3) is complete — shipping US1 alone with a
  mirror toggle but no preview/confirm would violate constitution Principle II.
- [P] tasks touch different files with no unmet dependencies.
- Commit after each task or logical group, per this repo's standing rule to commit every round.

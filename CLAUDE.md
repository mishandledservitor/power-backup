# power-backup

## What this repo is

A double-clickable macOS app, Rsync Sync GUI, that syncs one folder into another (typically across drives) by running the system `rsync`. It offers folder pickers, live rsync output with an overall progress bar, cancel, saved named jobs, and an opt-in mirror mode that always shows a dry-run preview and asks for confirmation before anything is deleted. The repository is called power-backup; the app it builds is Rsync Sync GUI. Requirements and design live in `.specify/memory/constitution.md` and `specs/001-rsync-sync-gui/`.

## Conventions

- **Thin wrapper over rsync.** The app composes rsync arguments, runs rsync and shows its output. It never reimplements copying, diffing or deleting (constitution I).
- **Safety by default.** Any flag that can delete or overwrite at the destination is opt-in, and a destructive run is always preceded by a `--dry-run` preview and an explicit confirmation (constitution II, non-negotiable).
- **Argument lists, never shell strings.** rsync is started with `subprocess.Popen` and an argv list built in `build_argv()`; user paths never pass through a shell.
- **Tests run on temporary folders.** Unit and integration tests use pytest's `tmp_path` and the real system `rsync`. No test may read or write the user's real jobs file or any real folder outside its temporary directory.
- **Formatting is ruff's.** Lines are up to 100 characters; `ruff check` and `ruff format --check` must pass, as in CI.

## Standing rules

Binding on any agent working in this repo. These are process rules, not project conventions. **This file is the only source of truth for them.** Delete one only deliberately, never because it looks like unused scaffolding.

1. **No agent memory.** Never rely on assistant-side memory, per-project memory files, or recall from a previous session. Everything durable lives in the repo: this file, `CHANGELOG.md`, `docs/decisions.md`, `.specify/memory/constitution.md` and `specs/`. If something is worth remembering, write it here in the same turn you learn it. If a memory and the repo disagree, the repo wins.
2. **Spec Kit governs all development.** Every feature flows through `/speckit-specify`, then `/speckit-clarify` as needed, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze` or `/speckit-checklist` as needed, and `/speckit-implement`. No production code is written outside a spec'd, planned, tasked feature. The constitution outranks this file on anything about the code itself; these standing rules govern process and agent behaviour.
3. **All development happens on a worktree.** Never write code, tests, specs or plans on a checkout of the main branch. Create a worktree with its own branch and work there. Only repository management belongs outside a worktree: opening and merging pull requests, reviewing, tagging, releases, branch cleanup and reading. If you notice you are about to edit a file on main, stop and make a worktree first.
4. **Commit every round.** Each round (one user request plus its completion) ends with a git commit of whatever that round changed, without waiting to be asked. This includes Spec Kit artefacts (`spec.md`, `plan.md`, `tasks.md`). Stage specific paths, never `git add -A`; review what is staged first; make new commits only (no `--amend` unless asked); never force-push. A pure question-and-answer round that changes no files has nothing to commit.
5. **Refresh `Current status` before each commit.** Update the "Current status" section below, including its `Last updated:` date, to match reality as part of the same commit, so the summary never drifts from the repo.
6. **Context and delegation.** Keep long sessions clean: hand work that would produce large exploratory output (broad searches, file dumps, log reads) or that can run on its own to a subagent, and keep only its conclusion in the main conversation. When a phase is self-contained (its own branch, its own test run), run it in its own worktree. Skip that when the phase is a few lines, or when phases touch the same files and would conflict on merge.
7. **Don't narrate no-ops.** A check that came back empty doesn't need a line of output. Report what you did and what the user has to decide. In particular, with no `.specify/extensions.yml` every `/speckit-*` hook check is a guaranteed no-op, so skip it silently.
8. **True TDD: red, green, refactor.** No production code without a failing test first. For every unit of work, write a test that fails for the right reason (red), write the minimum code to make it pass (green), then clean up with the tests still green (refactor). This happens inside `/speckit-implement`: each task's test is written and shown failing before that task's implementation is written.
9. **Spec Kit and TDD apply whatever door the work came in by,** whether that is a chat message, an issue, or the user typing at a session directly. Act on what is genuinely urgent, then spec and test the build rather than implementing straight from a message. The only exception is a small, reversible change that ships no behaviour, such as a typo, a comment or a note. If a user can see the behaviour change, it is spec'd and tested.
10. **Never hard-wrap text meant for a human to read.** No fixed-column line breaks in UI copy, generated reports, chat messages, docs prose or commit-message bodies: one paragraph is one line, and the device does the wrapping. This does not touch code: source lines, `<pre>` blocks, ASCII tables and fixed-width terminal output stay as they are.
11. **Never touch a `.env` file without asking the user.** Do not untrack, delete, move or rewrite one. Report what you found, say what reads the file, and ask. Reading one to classify a key is allowed, changing one is not, and no value ever appears in a report, a commit message or a prompt. Before removing any file to satisfy a guard, ask what reads it. This app reads no `.env` today; the rule stands for when one appears.

## Commands

Python 3.11 or later, macOS 12 or later, and the system `rsync` at `/usr/bin/rsync`.

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"                 # app plus pytest and ruff
.venv/bin/python -m rsync_sync_gui                # run the app from source
.venv/bin/pytest tests/unit tests/integration     # all tests (integration runs the real rsync)
.venv/bin/ruff check src tests                    # lint
.venv/bin/ruff format src tests                   # format (CI runs --check)
.venv/bin/pip install py2app && (cd packaging && ../.venv/bin/python setup.py py2app)   # build packaging/dist/Rsync Sync GUI.app
.venv/bin/pip install pillow && .venv/bin/python packaging/generate_icon.py            # regenerate packaging/AppIcon.icns
```

## Structure

- `src/rsync_sync_gui/__main__.py` is the entry point for `python -m rsync_sync_gui` and for the `.app`.
- `src/rsync_sync_gui/models/` holds `Job` (a saved sync with validation) and `SyncRun` (the run state machine and preview entries).
- `src/rsync_sync_gui/services/` holds `rsync_runner.py` (argv building, the subprocess wrapper, parsers for itemised changes, progress and stats), `job_store.py` (the JSON jobs file), `path_validation.py` (availability and nested-path checks) and `errors.py` (readable failure messages).
- `src/rsync_sync_gui/ui/` holds the PySide6 main window, the mirror preview dialog, the progress view and the `QThread` worker.
- `packaging/` holds the py2app `setup.py`, the icon and its generator.
- `tests/unit/` and `tests/integration/` hold the pytest suites.
- `specs/001-rsync-sync-gui/` holds the feature's spec, plan, research, data model, quickstart, tasks and checklists.
- `docs/decisions.md` records decisions about how the repository is run.

## CI/CD

- `.github/workflows/ci.yml` (`CI`) runs on every pull request and every push to main, on `macos-latest` with Python 3.11 and `QT_QPA_PLATFORM=offscreen`: install, `ruff check`, `ruff format --check`, pytest. It uses no secrets.

## Current status

Last updated: 2026-10-14
- Release 1.0.0, the first public release. What it does for a user: `CHANGELOG.md`. Constitution v1.0.0; repository decisions in `docs/decisions.md`.
- Built: feature 001 (one-off sync, saved jobs, mirror mode with dry-run preview and confirmation, cancel, overall progress bar, macOS volume-metadata excludes, app icon). All 34 tasks in `specs/001-rsync-sync-gui/tasks.md` are complete, 38 tests pass, and the py2app build produces a working `.app`.
- Open: renaming a job exists in `JobStore` but has no control in the window; drag-and-drop folder selection is not built; the window shows rsync's output but not the exact command line (constitution IV); 13 lower-priority items in `specs/001-rsync-sync-gui/checklists/safety.md` are accepted gaps; a full manual pass of `specs/001-rsync-sync-gui/quickstart.md` has not been run.
- If this section contradicts what you see in the repo, trust the repo and flag the mismatch.
- `.claude/skills/` holds only the Spec Kit `speckit-*` skills (see `THIRD_PARTY_NOTICES.md`); personal skills are gitignored. `.claude/settings.local.json` is gitignored too.
- Licence: MIT (`LICENSE`).

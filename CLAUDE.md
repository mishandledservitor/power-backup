# <Project Name>

<!-- Replace <Project Name> and write one line under "What this repo is" once the purpose is real.
     Anything marked TBD stays TBD until there's something true to write — don't fill space. -->

## What this repo is

TBD — no defined purpose yet. Treat as a blank scaffold: don't assume a stack, build system,
or layout, and ask before creating directories that imply a direction (`src/`, `packages/`, `docs/`…).

## Conventions

TBD — hard rules land here as real friction reveals them (style, non-negotiables, things never to do).
Don't pre-invent a rule list; an unenforced rule is worse than none.

## Standing rules

Binding on any agent working in this repo, from day one — these are process rules, not project
conventions, so unlike the section above they ship filled in. **This file is the only source of
truth for them.** They survive into every repo made from this template; delete one only
deliberately, never because it looks like unused scaffolding.

1. **No agent memory.** Never rely on assistant-side memory, per-project memory files, or recall
   from a previous session. Everything durable lives in the repo: this file, `CHANGELOG.md`, and
   (once Spec Kit is initialized) `.specify/memory/constitution.md` and `specs/`. If something is
   worth remembering, write it here in the same turn you learn it. If a memory and the repo
   disagree, the repo wins.
2. **Spec Kit governs all development.** Every feature flows through
   `/speckit-specify` → (`/speckit-clarify` as needed) → `/speckit-plan` → `/speckit-tasks` →
   (`/speckit-analyze` / `/speckit-checklist` as needed) → `/speckit-implement`. No production code
   is written outside a spec'd, planned, tasked feature. If Spec Kit isn't initialized yet, that is
   the first development step — it is not optional:

   ```bash
   specify init --here --integration claude
   ```

   Then ratify a constitution with `/speckit-constitution` before the first feature. The
   constitution outranks this file on anything about the code itself; these standing rules govern
   process and agent behaviour.
3. **All development happens on a worktree.** Never write code, tests, specs, or plans on a
   checkout of the main branch. Create a worktree with its own branch and work there. Only *repo
   management* belongs outside a worktree: opening and merging PRs, reviewing, tagging, releases,
   branch cleanup, and reading. If you notice you are about to edit a file on main, stop and make a
   worktree first.
4. **Commit every round.** Each round — one user request plus its completion — ends with a git
   commit of whatever that round changed, without waiting to be asked. This includes work that
   isn't a natural "please commit" moment, such as Spec Kit artifacts (`spec.md`, `plan.md`,
   `tasks.md`). Stage specific paths, never `-A`; review what's staged first; new commits only (no
   `--amend` unless asked); no force-push. A pure Q&A round that changes no files has nothing to
   commit.
5. **Refresh `Current status` before each commit.** Update the "Current status" section below —
   including its `Last updated:` date — to match reality as part of the same commit, so the summary
   can never drift from the repo. Check it every round rather than assuming it still holds.
6. **Context & delegation.** Use the `context-preservation` skill to keep long sessions clean, and
   dispatch a **worktree** subagent per phase whenever a phase is self-contained enough to run
   independently (its own branch, its own test run). Typical split: one worktree per Spec Kit phase,
   or per independent task group in `tasks.md`. Judgement call — skip it when the phase is a few
   lines, or when phases touch the same files and would conflict on merge.
7. **Don't narrate no-ops.** A check that came back empty doesn't need a line of output. Report
   what you did and what the user has to decide, not the scaffolding you looked at on the way.
   The recurring offender is Spec Kit's extension-hook check: with no `.specify/extensions.yml`
   — the default — every `/speckit-*` command's hook check is a guaranteed no-op, and the skills
   already say to skip it silently. Do that; don't announce "no hooks configured". If that file
   is ever added, the hooks become real and this rule stops covering them.

## Current status

Last updated: 2026-08-08
Spec Kit initialized; constitution ratified (macOS rsync folder-sync GUI, Python + PySide6,
`.app` packaging, safety-by-default). Baseline spec written for feature `001-rsync-sync-gui`
(`specs/001-rsync-sync-gui/spec.md`), quality checklist passed. Implementation plan, research,
data model, and quickstart written (`specs/001-rsync-sync-gui/`). Implemented (`src/rsync_sync_gui/`): folder-picker sync, mirror-mode dry-run preview + confirm,
cancel, JSON-backed saved jobs, and an overall progress bar. 37 tests pass
(`pytest tests/unit tests/integration`). Run with `.venv/bin/python -m rsync_sync_gui`, or build
the `.app` with `cd packaging && ../.venv/bin/python setup.py py2app` (verified working). All 34
tasks in `specs/001-rsync-sync-gui/tasks.md` complete. App has a custom icon
(`packaging/AppIcon.icns`, generated by `packaging/generate_icon.py`). Remaining: the 13
lower-priority items still open in `specs/001-rsync-sync-gui/checklists/safety.md` (accepted v1
gaps); a full manual quickstart.md pass hasn't been run.

- Full history: `CHANGELOG.md`.
- If this section contradicts what you see in the repo, trust the repo and flag the mismatch.
- `.claude/settings.local.json` is gitignored by default — commit it only to deliberately share config across machines.
- Add a `VERSION` file only once there's a package manifest, submodule set, or release process to pin it to.
- No `LICENSE` yet — this repo is **private by default**. Add one only once the purpose (and whether it goes public) is established.

<!-- ─── Add the sections below only when each is REAL. Use these exact names (they recur across the
         other repos). An empty version of any of these is ceremony that rots — leave it out until true. ───

## Structure         annotated tree — `path` — role — one line, once there's a layout worth mapping
## Commands          build / run / test, once such a system exists
## Data model / API   schema or route list, once there is one
## Branch strategy    once there's a release process or more than one contributor
## CI/CD              list each workflow by name + trigger, once workflows exist
## Deep reference     Need | File routing table, once there are enough docs to route to
## Important notes    recurring gotchas — a lessons-learned LOG (add an entry once a mistake has
                      actually recurred, not a place to pre-guess failure modes)

     .claude/agents/ and .claude/skills/ are opt-in — add one only for real delegation or a reusable
     procedure worth packaging; never ship a placeholder. See .claude/README.md.
     Short-term / session notes aren't scaffolded — make a dated scratch file or notes/ ad hoc;
     .scratch/ is already gitignored, so adopting the habit costs nothing. -->

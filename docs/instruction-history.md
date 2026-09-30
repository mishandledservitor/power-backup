# Instruction history

Record, not law. Text moved verbatim out of `CLAUDE.md` so the always-loaded file holds only rules; agents do not need to read this file. Each entry is dated by the day it was moved.

## 2026-09-30 — pre-sync local copy of the standing rules

Moved from `CLAUDE.md` lines 16–33. It duplicated the synced block at the bottom of `CLAUDE.md` (rules 1–7), which is the one kept; the synced block also carries rules 8–12, which this copy lacked.

## Standing rules

Binding on any agent working in this repo, from day one — these are process rules, not project conventions, so unlike the section above they ship filled in. **This file is the only source of truth for them.** They survive into every repo made from this template; delete one only deliberately, never because it looks like unused scaffolding.

1. **No agent memory.** Never rely on assistant-side memory, per-project memory files, or recall from a previous session. Everything durable lives in the repo: this file, `CHANGELOG.md`, and (once Spec Kit is initialized) `.specify/memory/constitution.md` and `specs/`. If something is worth remembering, write it here in the same turn you learn it. If a memory and the repo disagree, the repo wins.
2. **Spec Kit governs all development.** Every feature flows through `/speckit-specify` → (`/speckit-clarify` as needed) → `/speckit-plan` → `/speckit-tasks` → (`/speckit-analyze` / `/speckit-checklist` as needed) → `/speckit-implement`. No production code is written outside a spec'd, planned, tasked feature. If Spec Kit isn't initialized yet, that is the first development step — it is not optional:

   ```bash
   specify init --here --integration claude
   ```

   Then ratify a constitution with `/speckit-constitution` before the first feature. The constitution outranks this file on anything about the code itself; these standing rules govern process and agent behaviour.
3. **All development happens on a worktree.** Never write code, tests, specs, or plans on a checkout of the main branch. Create a worktree with its own branch and work there. Only *repo management* belongs outside a worktree: opening and merging PRs, reviewing, tagging, releases, branch cleanup, and reading. If you notice you are about to edit a file on main, stop and make a worktree first.
4. **Commit every round.** Each round — one user request plus its completion — ends with a git commit of whatever that round changed, without waiting to be asked. This includes work that isn't a natural "please commit" moment, such as Spec Kit artifacts (`spec.md`, `plan.md`, `tasks.md`). Stage specific paths, never `-A`; review what's staged first; new commits only (no `--amend` unless asked); no force-push. A pure Q&A round that changes no files has nothing to commit.
5. **Refresh `Current status` before each commit.** Update the "Current status" section below — including its `Last updated:` date — to match reality as part of the same commit, so the summary can never drift from the repo. Check it every round rather than assuming it still holds.
6. **Context & delegation.** Use the `context-preservation` skill to keep long sessions clean, and dispatch a **worktree** subagent per phase whenever a phase is self-contained enough to run independently (its own branch, its own test run). Typical split: one worktree per Spec Kit phase, or per independent task group in `tasks.md`. Judgement call — skip it when the phase is a few lines, or when phases touch the same files and would conflict on merge.
7. **Don't narrate no-ops.** A check that came back empty doesn't need a line of output. Report what you did and what the user has to decide, not the scaffolding you looked at on the way. The recurring offender is Spec Kit's extension-hook check: with no `.specify/extensions.yml` — the default — every `/speckit-*` command's hook check is a guaranteed no-op, and the skills already say to skip it silently. Do that; don't announce "no hooks configured". If that file is ever added, the hooks become real and this rule stops covering them.

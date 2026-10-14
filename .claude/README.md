# .claude/

Claude Code configuration for this repository.

- **`skills/speckit-*`** are the Spec Kit commands (`/speckit-specify`, `/speckit-plan` and the rest) that every feature goes through. They come from GitHub Spec Kit; see `THIRD_PARTY_NOTICES.md`. Any other skill you add under `skills/` is personal and stays out of git.
- **`settings.local.json`** is your machine-local permission list. It is gitignored; commit it only to share configuration across machines on purpose.
- **`worktrees/`** is managed by Claude Code and gitignored.

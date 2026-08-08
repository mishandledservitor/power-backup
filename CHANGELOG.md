# Changelog

Notable changes to this repo. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- Generated tasks.md for 001-rsync-sync-gui: 34 tasks across setup, foundational, three user-story
  phases, and polish. MVP = User Story 1 (one-off sync); mirror mode not exposed until User Story
  3 (preview/confirm) lands.
- Wrote implementation plan for 001-rsync-sync-gui: PySide6 desktop app, subprocess-driven rsync
  runner, JSON job persistence, dry-run-based preview. See plan.md/research.md/data-model.md/
  quickstart.md.
- Wrote baseline spec for feature 001-rsync-sync-gui: one-off sync, saved/reusable jobs, and
  mandatory dry-run preview + confirmation before any destructive/mirror sync.
- Initialized Spec Kit (`specify init --here --integration claude`).
- Ratified project constitution v1.0.0: macOS rsync folder-sync GUI, Python + PySide6, packaged
  as a double-clickable `.app`, safety-by-default around destructive rsync flags.
- Repo created from the default template.

<!-- If this repo turns out to be a short-lived experiment, delete this file rather than leave it
     unfilled — an absent changelog is more honest than a stale one. -->

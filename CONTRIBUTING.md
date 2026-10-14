# Contributing to power-backup

Bug reports, fixes and new features are all welcome.

## Before you start

- **For a security problem,** such as a way to make the app delete files without showing the preview, do not open a public issue. Report it privately from the repository's **Security** tab with **Report a vulnerability**.
- **For a bug,** open an issue that says what you did, what you expected and what happened instead. Include your macOS version and the output of `rsync --version`. Leave out the names of your own folders and files if they are private.
- **For a new feature or a change in behaviour,** open an issue first and describe the problem it solves. Agreeing on the idea before you write code saves you from building something that won't be merged.
- **For a typo or a small fix,** go straight to a pull request.

## Setting up

You need macOS 12 or later and Python 3.11 or later. The `rsync` that ships with macOS is all the tests need.

```sh
git clone https://github.com/<your-account>/power-backup.git
cd power-backup
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m rsync_sync_gui
```

The last command opens the app from your working copy, so you can try a change without building the `.app`. The README explains how to build the bundle.

## How changes are made here

**Every change to what a user sees starts with a spec.** The project uses [Spec Kit](https://github.com/github/spec-kit). A feature has its own folder under `specs/` with a `spec.md` (what it does and why), a `plan.md` (how it is built) and a `tasks.md` (the steps). If your change adds or alters behaviour, add or update the spec in the same pull request. A fix that makes the code match an existing spec doesn't need a new one. The rules that outrank everything else are in `.specify/memory/constitution.md`.

**Safety comes first.** Anything that can delete or overwrite files at the destination stays opt-in, and a destructive sync is always preceded by a dry-run preview and an explicit confirmation. A change that weakens this won't be merged.

**The app stays a thin wrapper over rsync.** It builds rsync's arguments, runs it and shows the result. Copying, comparing and deleting are left to rsync. rsync is started with a list of arguments, never through a shell.

**Tests come first.** Write a test that fails because the behaviour is missing, then write the code that makes it pass, then tidy up with the tests still passing. A pull request that changes behaviour without a test for it will be asked for one. Tests work in pytest's temporary folders and must never touch your real jobs file or real folders.

## Before you open a pull request

Run the same checks as CI:

```sh
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/pytest tests/unit tests/integration
```

Then open the pull request against `main`:

- Keep it to one change, and say in the description what it does and why. Link the issue it closes.
- If it changes what a user sees, add a line under `## [Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md), written for the people who use the app.
- CI must pass. On your first pull request, CI starts once a maintainer approves the run.
- Expect review comments; a maintainer merges the pull request once it is ready.

## Using coding agents

[`CLAUDE.md`](CLAUDE.md) holds the working rules for AI coding agents, and the Spec Kit commands are in `.claude/skills/`. Contributions written with an agent are welcome on the same terms as any other: the spec, the tests and the checks above all apply, and you are responsible for what you submit.

## Licence

power-backup is released under the MIT licence. By opening a pull request, you agree that your contribution is released under the same licence.

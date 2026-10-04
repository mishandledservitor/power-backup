# Rsync Sync GUI

A double-clickable macOS app for syncing folders across drives, backed by `rsync`. The repo is called power-backup; the app it builds is Rsync Sync GUI.

Agent-facing detail — conventions, current status, gotchas — lives in [`CLAUDE.md`](CLAUDE.md).
Feature spec, plan, and tasks live in [`specs/001-rsync-sync-gui/`](specs/001-rsync-sync-gui/).

## Run in development

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m rsync_sync_gui
```

## Run tests

```bash
.venv/bin/pytest tests/unit tests/integration
```

## Build the double-clickable `.app`

```bash
.venv/bin/pip install py2app
cd packaging
../.venv/bin/python setup.py py2app
# .app bundle appears in packaging/dist/
```

If py2app proves incompatible with PySide6 on your machine, PyInstaller is an acceptable
fallback (see `research.md` in the feature spec directory):

```bash
.venv/bin/pip install pyinstaller
.venv/bin/pyinstaller --windowed --name "Rsync Sync GUI" src/rsync_sync_gui/__main__.py
```

See [`specs/001-rsync-sync-gui/quickstart.md`](specs/001-rsync-sync-gui/quickstart.md) for the
full manual validation scenarios.

## Licence

MIT. See [`LICENSE`](LICENSE).

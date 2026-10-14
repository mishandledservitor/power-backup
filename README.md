# power-backup

power-backup builds Rsync Sync GUI, a double-clickable macOS app that copies the contents of one folder into another, for example from your internal disk to an external drive. You pick the two folders, press **Sync**, and the app runs the `rsync` that comes with macOS while showing its output and an overall progress bar. You can save a pair of folders as a named job and run it again later. Mirror mode also deletes files at the destination that are no longer in the source; before it deletes anything, it lists every change it is about to make and waits for you to confirm.

The app works entirely on your Mac. It needs no account or API key, and it never connects to the network.

## What you need

| What | Why |
|---|---|
| macOS 12 Monterey or later | The app is built for macOS only, and the bundle declares macOS 12 as its minimum. |
| The system `rsync` at `/usr/bin/rsync` | Every sync is done by rsync. It ships with macOS, so there's nothing to install. |
| Python 3.11 or later | You build the app yourself, because it is not distributed as a download. Python is needed only for building, not for using the finished app. |
| Git | You use it to clone the repository. |

## Quick start

1. Clone the repository and install the app with its build tools in a virtual environment:

   ```sh
   git clone https://github.com/mishandledservitor/power-backup.git
   cd power-backup
   python3 -m venv .venv
   .venv/bin/pip install -e ".[dev]" py2app
   ```

2. Build the app bundle. The command has to run from the `packaging` folder:

   ```sh
   cd packaging
   ../.venv/bin/python setup.py py2app
   ```

3. Drag `packaging/dist/Rsync Sync GUI.app` into your Applications folder and open it.
4. Click **Choose Source…** and pick the folder you want to copy, then click **Choose Destination…** and pick where the copy should go. The app refuses a destination that is the same as the source, inside it, or contains it.
5. Click **Sync**. The output of rsync scrolls past as it runs, the progress bar counts files, and the status line shows how many files and bytes were transferred when it finishes. Click **Cancel** to stop a sync that is running.
6. To reuse the pair, click **Save as Job** and give it a name. Next time, select the job in **Saved Jobs** and click **Run Selected Job**.

To try the app without building the bundle, run `.venv/bin/python -m rsync_sync_gui` after step 1.

To update, run `git pull` in the repository, repeat `.venv/bin/pip install -e ".[dev]" py2app`, rebuild with step 2, and replace the app in your Applications folder.

## Using it

**What gets copied.** The app copies the contents of the source folder into the destination folder, so syncing `Photos` to `Backup` puts the files directly in `Backup` instead of in `Backup/Photos`. It uses rsync's archive mode (`-a`), which copies subfolders, symbolic links, permissions and modification times. It skips files whose size and modification time already match, and it replaces a destination file that differs with the source's version, even when the destination's copy is newer. Without mirror mode, nothing at the destination is deleted.

**Mirror mode.** Tick **Mirror mode (deletes files at destination not in source)** to make the destination an exact copy of the source. The app first does a dry run and shows a list of every file it would add, update or delete. Nothing changes until you click **Confirm**; **Cancel** leaves the destination as it was. Files deleted by mirror mode are removed for good, not moved to the Bin.

**Saved jobs.** A job remembers the source, the destination and whether mirror mode is on. If either folder is missing when the app starts, for example because the drive is not connected, the job is shown with "(unavailable)" and the app will not run it. **Delete Job** removes the selected job immediately.

**Whole drives.** When you sync the top of an external drive, the app always skips the hidden folders macOS keeps there (such as `.Spotlight-V100`, `.Trashes` and `.fseventsd`), because a normal user account cannot read them and they are never worth copying.

**Errors.** If rsync fails, the status line says "Failed." and the output area ends with rsync's exit code and its last few lines.

## Your data

- Saved jobs are stored in `~/Library/Application Support/RsyncSyncGui/jobs.json`. The file holds each job's name, its two folder paths and its mirror setting. Delete the file to remove every saved job.
- The app reads and writes only the folders you choose and that one file.

## Known limitations

- A saved job cannot be renamed in the window. To change its name, save the folders as a new job and delete the old one.
- Folders are chosen with the pickers only; dragging a folder onto the window does nothing.
- Extended attributes, access control lists and Finder tags are not copied, because rsync runs with `-a` only.
- The progress bar reads the progress format of the rsync that ships with macOS. When you run the app from a terminal in which a newer rsync (for example from Homebrew) comes first on your `PATH`, the bar keeps moving without counting files, although the sync itself works.
- There is no scheduling: a sync runs only when you click it.
- The app is not code-signed. A bundle you build yourself opens normally on your own Mac, but if you copy it to another Mac, macOS may block it until you allow it in **System Settings > Privacy & Security**.
- The interface is in English.

## Development

```sh
.venv/bin/pytest tests/unit tests/integration   # unit and integration tests
.venv/bin/ruff check src tests                  # lint
.venv/bin/ruff format --check src tests         # formatting
```

The integration tests run the real `rsync` against temporary folders, so they need macOS but no setup. If py2app does not work with PySide6 on your machine, PyInstaller can build the app instead:

```sh
.venv/bin/pip install pyinstaller
.venv/bin/pyinstaller --windowed --name "Rsync Sync GUI" src/rsync_sync_gui/__main__.py
```

The project is built with [Spec Kit](https://github.com/github/spec-kit): the feature's spec, plan, tasks and manual test scenarios are in `specs/001-rsync-sync-gui/`, and the rules the code follows are in `.specify/memory/constitution.md`. [`CLAUDE.md`](CLAUDE.md) holds the conventions and working rules for coding agents. To propose a change, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence

power-backup is released under the MIT licence; see [`LICENSE`](LICENSE). Third-party files and dependencies are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

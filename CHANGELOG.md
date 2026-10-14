# Changelog

What changes in Rsync Sync GUI from one release to the next, for people who use it. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-14

This is the first public release. Rsync Sync GUI is a double-clickable macOS app that copies one folder into another with the `rsync` that ships with macOS. You build it yourself from this repository with py2app.

### Added

- You can choose a source and a destination folder with the standard macOS folder picker and sync them with one click. The app refuses a destination that is the same as the source, inside it, or contains it.
- rsync's output appears in the window while a sync runs, together with a progress bar that counts files and a summary of the files and bytes transferred.
- A running sync can be cancelled, and quitting during a sync asks first.
- You can save a source, a destination and the mirror setting as a named job and run it again later. Jobs are kept in `~/Library/Application Support/RsyncSyncGui/jobs.json`.
- A job whose source or destination is missing, for example on a drive that is not connected, is marked "(unavailable)" and will not run.
- Mirror mode deletes files at the destination that are no longer in the source. It is off by default, and before every mirror sync the app lists each file it would add, update or delete and waits for **Confirm**.
- The hidden system folders at the top of a macOS volume, such as `.Spotlight-V100`, `.Trashes` and `.fseventsd`, are always skipped, so syncing a whole drive does not fill the output with "Operation not permitted" warnings.
- When rsync fails, the app shows its exit code and the last lines of its output.
- The app has its own icon.

### Known limitations

- A saved job cannot be renamed in the window, and folders cannot be dragged onto it.
- Extended attributes, access control lists and Finder tags are not copied.
- The progress bar does not count files when a newer rsync than the one in macOS comes first on your `PATH`.
- The app is not code-signed, and there is no scheduling.

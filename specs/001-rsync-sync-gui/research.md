# Research: Rsync Folder Sync GUI

No `NEEDS CLARIFICATION` markers remained in the plan's Technical Context — the constitution
already pinned language, GUI toolkit, and packaging approach. Remaining decisions below cover
*how* to implement within that stack.

## Decision: Run rsync as a subprocess with streamed output, off the Qt main thread

**Rationale**: `subprocess.Popen` with `stdout=PIPE, stderr=STDOUT, text=True` and line-buffered
reads lets the app show live progress (constitution Principle IV). Running it on a `QThread` (or
`QRunnable` via a thread pool) keeps the UI responsive (Technical Context constraint). Passing
`rsync` an explicit `--info=progress2` (or per-file `-v`) flag gives parseable-enough progress
lines without needing a separate progress protocol.

**Alternatives considered**:
- `os.system`/shell string: rejected — string-built shell commands risk injection/quoting bugs
  with arbitrary folder names; constitution's Technology Constraints explicitly bar this.
- Polling process completion without streaming: rejected — fails Principle IV (must show live
  progress, not just a spinner).

## Decision: Dry-run preview via a separate `rsync --dry-run` invocation, parsed line-by-line

**Rationale**: rsync's own `--dry-run` (combined with `-v` or `--itemize-changes`) enumerates
exactly what would change/be removed without touching the filesystem. Running this as a distinct
step before any destructive real run gives an accurate, rsync-verified preview (not a hand-rolled
diff), satisfying FR-006 directly from rsync's own behavior rather than reimplementing diff logic
(Principle I).

**Alternatives considered**:
- App computes its own file-level diff to predict changes: rejected — duplicates rsync's own
  comparison logic (mtime/size/checksum rules) and could disagree with what the real run does,
  which is exactly the risk Principle I exists to avoid.

## Decision: Jobs persisted as a single JSON file in the user's Application Support directory

**Rationale**: Job count is small (tens, per spec Scale/Scope) and the shape is simple
(list of {name, source, destination, options}), so a single JSON file read/written via the
standard library is sufficient — no database dependency needed, matching Principle V (Simplicity).

**Alternatives considered**:
- SQLite: rejected as unnecessary weight for a small flat list with no querying needs.
- Plist via macOS `NSUserDefaults`-style storage: rejected — adds a platform-specific dependency
  for no benefit over plain JSON, and JSON is easier to unit test and hand-inspect/back up.

## Decision: Packaging via py2app, with PyInstaller as a documented fallback

**Rationale**: py2app is the more macOS-native path for producing a `.app` bundle from a Python/
PySide6 project and integrates well with `setup.py`-based builds. PyInstaller is noted as an
acceptable alternative (constitution allows either) if py2app proves incompatible with a
dependency during implementation.

**Alternatives considered**:
- Manual `.app` bundle assembly: rejected — reinvents what py2app/PyInstaller already solve
  (embedding the Python runtime, Info.plist generation, code signing hooks).

## Decision: Mounted-volume and nested-path checks done with `pathlib`/`os.path` before invoking rsync

**Rationale**: Checking that source/destination `Path.exists()` (and, for external drives, that
the path resolves under `/Volumes/...` and is currently reachable) before building the rsync
command lets the app fail fast with a clear message (FR-010) instead of surfacing a raw rsync
error. Nested/identical-path detection (FR-011) is a simple `Path.resolve()` prefix comparison —
no external library needed.

**Alternatives considered**:
- Relying solely on rsync's own error output for these cases: rejected — rsync's errors for a
  disconnected volume or self-nested sync are not consistently user-readable, conflicting with
  the edge cases called out in the spec.

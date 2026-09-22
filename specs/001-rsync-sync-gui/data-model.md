# Data Model: Rsync Folder Sync GUI

## Job

A saved, named sync configuration. Persisted as one entry in the jobs JSON store.

| Field | Type | Notes |
|---|---|---|
| `id` | string (UUID) | Stable identity independent of name, so renames don't break references |
| `name` | string | User-facing label; must be non-empty and unique among saved jobs |
| `source` | string (absolute path) | Folder to sync from |
| `destination` | string (absolute path) | Folder to sync to |
| `mirror_enabled` | boolean | Default `false`. When `true`, sync runs with delete-capable rsync flags and always requires a dry-run preview + confirmation (FR-005, FR-006) |
| `created_at` | ISO 8601 timestamp | For display/sorting only |
| `updated_at` | ISO 8601 timestamp | Updated on rename/option change |

**Validation rules** (enforced before save and before each run):
- `source` and `destination` must both be non-empty absolute paths.
- `source` and `destination` must not be equal, and neither may be an ancestor of the other (FR-011).
- `name` must be unique (case-insensitive) among currently saved jobs (FR-009).

**Availability (derived, not stored)**: at load/display time, a job's `source`/`destination` are checked for existence; a job whose folder is currently missing is flagged unavailable in the UI (FR-010) but remains in the saved list untouched.

## Sync Run

A single execution, either from a saved Job or an ad-hoc one-off source/destination pair. Not persisted across app restarts — it exists only for the duration of showing progress/results to the user.

| Field | Type | Notes |
|---|---|---|
| `source` | string (absolute path) | Copied from the Job or the ad-hoc selection at start time |
| `destination` | string (absolute path) | Same |
| `mirror_enabled` | boolean | Same |
| `status` | enum: `pending`, `previewing`, `awaiting_confirmation`, `running`, `succeeded`, `failed`, `canceled` | Drives which UI is shown |
| `preview_changes` | list of `{path, change_type}` | Only populated when `mirror_enabled` is true; `change_type` ∈ `add`, `update`, `delete` (from `rsync --dry-run --itemize-changes` output) |
| `output_lines` | list of string | Raw rsync stdout/stderr lines, streamed live to the UI (FR-004) |
| `exit_code` | integer or null | rsync's process exit code once finished |
| `error_message` | string or null | Human-readable summary when `status == failed` (FR-012) |
| `summary` | `{files_transferred, bytes_transferred}` or null | Populated on success, parsed from rsync's final stats output |

**State transitions**:

```text
pending
  → previewing            (mirror_enabled == true; runs rsync --dry-run)
  → running               (mirror_enabled == false; runs rsync directly)
previewing → awaiting_confirmation   (dry-run finished, preview_changes populated)
awaiting_confirmation → running      (user confirms)
awaiting_confirmation → canceled     (user cancels; no destination changes made)
running → succeeded                  (exit_code == 0)
running → failed                     (exit_code != 0)
running → canceled                   (user cancels an in-progress run; process terminated)
```

No transition skips `previewing`/`awaiting_confirmation` when `mirror_enabled` is true — this is the mechanical enforcement of constitution Principle II / spec FR-006.

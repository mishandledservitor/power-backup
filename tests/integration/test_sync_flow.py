"""End-to-end sync tests against real temp folders and the real rsync binary. No GUI."""

from __future__ import annotations

from rsync_sync_gui.models.job import Job
from rsync_sync_gui.services.job_store import JobStore
from rsync_sync_gui.services.path_validation import is_available
from rsync_sync_gui.services.rsync_runner import RsyncProcess, parse_preview_changes


def _make_tree(root, files):
    for rel_path, content in files.items():
        p = root / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def test_non_destructive_sync_copies_files(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    _make_tree(src, {"a.txt": "hello", "sub/b.txt": "world"})

    proc = RsyncProcess(str(src), str(dst), mirror_enabled=False)
    list(proc.stream())

    assert proc.exit_code == 0
    assert (dst / "a.txt").read_text() == "hello"
    assert (dst / "sub" / "b.txt").read_text() == "world"


def test_non_mirror_sync_never_deletes_extra_dest_file(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    _make_tree(src, {"a.txt": "hello"})
    _make_tree(dst, {"extra.txt": "should survive"})

    proc = RsyncProcess(str(src), str(dst), mirror_enabled=False)
    list(proc.stream())

    assert (dst / "extra.txt").exists()


def test_mirror_dry_run_previews_deletion_without_deleting(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    _make_tree(src, {"a.txt": "hello"})
    _make_tree(dst, {"a.txt": "hello", "extra.txt": "will be removed"})

    proc = RsyncProcess(str(src), str(dst), mirror_enabled=True, dry_run=True)
    lines = list(proc.stream())

    assert proc.exit_code == 0
    assert (dst / "extra.txt").exists()  # dry-run must not touch the filesystem
    changes = parse_preview_changes(lines)
    deleted_paths = [c.path for c in changes if c.change_type == "delete"]
    assert "extra.txt" in deleted_paths


def test_mirror_confirmed_run_applies_previewed_deletion(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    _make_tree(src, {"a.txt": "hello"})
    _make_tree(dst, {"a.txt": "hello", "extra.txt": "will be removed"})

    # Preview first (per FR-006).
    preview = RsyncProcess(str(src), str(dst), mirror_enabled=True, dry_run=True)
    list(preview.stream())
    assert (dst / "extra.txt").exists()

    # Confirmed real run.
    real = RsyncProcess(str(src), str(dst), mirror_enabled=True, dry_run=False)
    list(real.stream())
    assert not (dst / "extra.txt").exists()


def test_unavailable_job_folder_detected_without_running_sync(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "missing-drive" / "dst"
    src.mkdir()

    job = Job(name="Offline", source=str(src), destination=str(dst))
    assert is_available(job.destination) is False


def test_saved_job_survives_reload(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    store = JobStore(path=tmp_path / "jobs.json")
    store.add(Job(name="Nightly", source=str(src), destination=str(dst)))

    reloaded_store = JobStore(path=tmp_path / "jobs.json")
    jobs = reloaded_store.load()
    assert len(jobs) == 1
    assert jobs[0].name == "Nightly"

from rsync_sync_gui.services.rsync_runner import (
    MACOS_VOLUME_METADATA_EXCLUDES,
    RsyncProcess,
    build_argv,
    parse_overall_progress,
    parse_preview_changes,
    parse_summary,
)


def test_non_mirror_argv_has_no_delete_flag():
    argv = build_argv("/src", "/dst", mirror_enabled=False)
    assert "--delete" not in argv


def test_mirror_argv_has_delete_flag():
    argv = build_argv("/src", "/dst", mirror_enabled=True)
    assert "--delete" in argv


def test_dry_run_always_adds_dry_run_flag():
    argv = build_argv("/src", "/dst", mirror_enabled=True, dry_run=True)
    assert "--dry-run" in argv


def test_non_dry_run_omits_dry_run_flag():
    argv = build_argv("/src", "/dst", mirror_enabled=True, dry_run=False)
    assert "--dry-run" not in argv


def test_argv_excludes_macos_volume_metadata_dirs():
    argv = build_argv("/src", "/dst", mirror_enabled=False)
    for pattern in MACOS_VOLUME_METADATA_EXCLUDES:
        assert f"--exclude={pattern}" in argv


def test_argv_is_a_list_not_a_shell_string():
    argv = build_argv("/src with spaces", "/dst", mirror_enabled=False)
    assert isinstance(argv, list)
    assert "/src with spaces/" in argv


def test_parse_preview_changes_detects_delete():
    lines = ["*deleting   old_file.txt"]
    changes = parse_preview_changes(lines)
    assert len(changes) == 1
    assert changes[0].change_type == "delete"
    assert changes[0].path == "old_file.txt"


def test_parse_preview_changes_detects_add():
    lines = [">f+++++++++ new_file.txt"]
    changes = parse_preview_changes(lines)
    assert len(changes) == 1
    assert changes[0].change_type == "add"


def test_parse_preview_changes_detects_update():
    lines = [">f.st...... changed_file.txt"]
    changes = parse_preview_changes(lines)
    assert len(changes) == 1
    assert changes[0].change_type == "update"


def test_parse_summary_extracts_files_and_bytes():
    lines = [
        "Number of files transferred: 3",
        "Total transferred file size: 1,024 bytes",
    ]
    result = parse_summary(lines)
    assert result == (3, 1024)


def test_parse_summary_none_when_missing():
    assert parse_summary(["some other output"]) is None


def test_cancel_terminates_running_process(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    for i in range(200):
        (src / f"file{i}.bin").write_bytes(b"x" * 200_000)

    process = RsyncProcess(str(src), str(dst), mirror_enabled=False)
    process.cancel()

    assert process.canceled is True
    assert process._process.poll() is not None  # process has exited


def test_argv_includes_progress_flag():
    argv = build_argv("/src", "/dst", mirror_enabled=False)
    assert "--progress" in argv


def test_parse_overall_progress_extracts_counts():
    line = "        20971520 100%  420.15MB/s    0:00:00 (xfer#3, to-check=5/12)"
    assert parse_overall_progress(line) == (3, 12)


def test_parse_overall_progress_none_for_unrelated_line():
    assert parse_overall_progress("some other output") is None


def test_cancel_on_already_finished_process_is_a_noop(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "a.txt").write_text("hi")

    process = RsyncProcess(str(src), str(dst), mirror_enabled=False)
    list(process.stream())
    process.cancel()  # should not raise even though the process already exited

    assert process.canceled is True

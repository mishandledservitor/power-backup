from rsync_sync_gui.services.path_validation import is_available, is_nested_or_equal


def test_is_available_true_for_existing_dir(tmp_path):
    assert is_available(str(tmp_path)) is True


def test_is_available_false_for_missing_dir(tmp_path):
    assert is_available(str(tmp_path / "does-not-exist")) is False


def test_equal_paths_rejected(tmp_path):
    assert is_nested_or_equal(str(tmp_path), str(tmp_path)) is not None


def test_destination_inside_source_rejected(tmp_path):
    dest = tmp_path / "sub"
    dest.mkdir()
    assert is_nested_or_equal(str(tmp_path), str(dest)) is not None


def test_source_inside_destination_rejected(tmp_path):
    src = tmp_path / "sub"
    src.mkdir()
    assert is_nested_or_equal(str(src), str(tmp_path)) is not None


def test_unrelated_paths_allowed(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    assert is_nested_or_equal(str(a), str(b)) is None

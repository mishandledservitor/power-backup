import pytest

from rsync_sync_gui.models.job import Job, JobValidationError


def test_valid_job_passes(tmp_path):
    src = tmp_path / "a"
    dst = tmp_path / "b"
    src.mkdir()
    dst.mkdir()
    job = Job(name="Test", source=str(src), destination=str(dst))
    job.validate()  # should not raise


def test_empty_name_rejected(tmp_path):
    job = Job(name="", source=str(tmp_path / "a"), destination=str(tmp_path / "b"))
    with pytest.raises(JobValidationError):
        job.validate()


def test_duplicate_name_rejected(tmp_path):
    src = tmp_path / "a"
    dst = tmp_path / "b"
    src.mkdir()
    dst.mkdir()
    job = Job(name="Backup", source=str(src), destination=str(dst))
    with pytest.raises(JobValidationError):
        job.validate(existing_names=["backup"])


def test_nested_paths_rejected_via_job_validate(tmp_path):
    dst = tmp_path / "sub"
    dst.mkdir()
    job = Job(name="Test", source=str(tmp_path), destination=str(dst))
    with pytest.raises(JobValidationError):
        job.validate()


def test_round_trip_to_dict_from_dict(tmp_path):
    job = Job(name="Test", source=str(tmp_path / "a"), destination=str(tmp_path / "b"))
    data = job.to_dict()
    restored = Job.from_dict(data)
    assert restored.id == job.id
    assert restored.name == job.name

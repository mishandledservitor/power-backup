import pytest

from rsync_sync_gui.models.job import Job, JobValidationError
from rsync_sync_gui.services.job_store import JobStore


@pytest.fixture
def store(tmp_path):
    return JobStore(path=tmp_path / "jobs.json")


def _job(tmp_path, name="Test"):
    src = tmp_path / f"{name}-src"
    dst = tmp_path / f"{name}-dst"
    src.mkdir(exist_ok=True)
    dst.mkdir(exist_ok=True)
    return Job(name=name, source=str(src), destination=str(dst))


def test_add_and_load_round_trip(store, tmp_path):
    store.add(_job(tmp_path))
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].name == "Test"


def test_duplicate_name_rejected(store, tmp_path):
    store.add(_job(tmp_path, "Backup"))
    with pytest.raises(JobValidationError):
        store.add(_job(tmp_path, "Backup"))


def test_rename_persists(store, tmp_path):
    job = _job(tmp_path)
    store.add(job)
    store.rename(job.id, "Renamed")
    loaded = store.load()
    assert loaded[0].name == "Renamed"


def test_delete_persists(store, tmp_path):
    job = _job(tmp_path)
    store.add(job)
    store.delete(job.id)
    assert store.load() == []


def test_load_missing_file_returns_empty(tmp_path):
    store = JobStore(path=tmp_path / "does-not-exist.json")
    assert store.load() == []

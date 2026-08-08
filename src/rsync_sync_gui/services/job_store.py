"""Loads/saves Job entities to a single JSON file (FR-007, FR-008, FR-009)."""

from __future__ import annotations

import json
from pathlib import Path

from rsync_sync_gui.models.job import Job

DEFAULT_STORE_PATH = (
    Path.home() / "Library" / "Application Support" / "RsyncSyncGui" / "jobs.json"
)


class JobStore:
    def __init__(self, path: Path = DEFAULT_STORE_PATH):
        self.path = path

    def load(self) -> list[Job]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        return [Job.from_dict(entry) for entry in data.get("jobs", [])]

    def save(self, jobs: list[Job]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"jobs": [job.to_dict() for job in jobs]}
        self.path.write_text(json.dumps(data, indent=2))

    def add(self, job: Job) -> None:
        jobs = self.load()
        job.validate(existing_names=[j.name for j in jobs])
        jobs.append(job)
        self.save(jobs)

    def rename(self, job_id: str, new_name: str) -> None:
        jobs = self.load()
        others = [j.name for j in jobs if j.id != job_id]
        for job in jobs:
            if job.id == job_id:
                job.name = new_name
                job.validate(existing_names=others)
        self.save(jobs)

    def delete(self, job_id: str) -> None:
        jobs = [j for j in self.load() if j.id != job_id]
        self.save(jobs)

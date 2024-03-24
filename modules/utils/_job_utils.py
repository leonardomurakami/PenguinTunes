import datetime
from typing import Callable, Dict, Any
from sqlalchemy import select
from modules.utils._database_utils import get_session

class Job:
    def __init__(self, name: str, interval: datetime.timedelta, action: Callable, config: Dict[str, Any] = None, last_run: datetime.datetime = None):
        self.name = name
        self.interval = interval
        self.action = action
        self.config = config or {}
        self.last_run = last_run or datetime.datetime.utcnow()

    def should_run(self, current_time: datetime.datetime) -> bool:
        if current_time - self.last_run >= self.interval:
            self.last_run = current_time
            return True
        return False
    
    async def run(self) -> None:
        try:
            await self.action()
        except Exception as e:
            print(f"Error running job {self.name}: {e}")

    @classmethod
    def from_db_model(cls, job_db) -> 'Job':
        return cls(
            name=job_db.job_name,
            interval=datetime.timedelta(seconds=job_db.interval_seconds),
            action=job_db.action,
            config=job_db.config,
            last_run=job_db.last_run
        )

class JobManager:
    def __init__(self):
        self.jobs = []

    async def load_jobs(self) -> None:
        """Load jobs from the database."""
        async with get_session() as session:
            async with session.begin():
                result = await session.execute(select(Job))
                jobs_db = result.scalars().all()
                for job_db in jobs_db:
                    self.add_job(Job.from_db_model(job_db))

    def add_job(self, job: Job) -> None:
        """Add a job to the list."""
        self.jobs.append(job)

    async def run_jobs(self) -> None:
        """Run jobs that should be executed."""
        current_time = datetime.datetime.utcnow()
        for job in self.jobs:
            if job.should_run(current_time):
                await job.run()

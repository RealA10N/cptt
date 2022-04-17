from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from dataclasses import field
from subprocess import PIPE

from cptt.process import MemoryLimitExceeded
from cptt.process import MonitoredProcess
from cptt.process import TimeLimitExceeded
from cptt.validate import ValidationError
from cptt.validate import Validator


@dataclass
class JobEvent:
    job: Job


@dataclass
class JobStartEvent(JobEvent):
    pass


@dataclass
class JobEndEvent(JobEvent):
    success: bool
    time: float
    memory: float
    message: str


@dataclass
class Job:
    program: list[str]
    time_limit: float = None
    memory_limit: float = None
    input: str = None
    validators: list[Validator] = field(default_factory=list)

    manager: JobManager = field(init=False, default=None)

    def execute(self) -> None:
        self.manager.push_event(JobStartEvent(job=self))

        process = MonitoredProcess(
            self.program,
            encoding='utf8',
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
        )

        try:
            out, err = process.communicate(
                input=self.input,
                time_limit=self.time_limit,
                memory_limit=self.memory_limit,
            )

            for validator in self.validators:
                validator.validate(
                    stdout=out, stderr=err,
                    returncode=process.returncode,
                )

        except TimeLimitExceeded:
            self.manager.push_event(
                JobEndEvent(
                    job=self,
                    success=False,
                    time=process.duration,
                    memory=process.memory_used,
                    message='Time Limit Exceeded',
                ),
            )

        except MemoryLimitExceeded:
            self.manager.push_event(
                JobEndEvent(
                    job=self,
                    success=False,
                    time=process.duration,
                    memory=process.memory_used,
                    message='Memory Limit Exceeded',
                ),
            )

        except ValidationError:
            self.manager.push_event(
                JobEndEvent(
                    job=self,
                    success=False,
                    time=process.duration,
                    memory=process.memory_used,
                    message='Wrong Answer',
                ),
            )

        else:
            self.manager.push_event(
                JobEndEvent(
                    job=self,
                    success=True,
                    time=process.duration,
                    memory=process.memory_used,
                    message='Passed',
                ),
            )


class JobManager:

    def __init__(self) -> None:
        self._events: queue.Queue[JobEvent] = queue.Queue()

    def push_event(self, event: JobEvent) -> None:
        self._events.put(event, block=True)

    def next_event(self) -> JobEvent:
        return self._events.get(block=True)


class Runner:

    def __init__(self, threads: int = 1) -> None:
        self._threads = threads
        self._queue: queue.Queue[Job] = queue.Queue()
        self._manager = JobManager()

    def collect(self, job: Job) -> None:
        job.manager = self._manager
        self._queue.put(job)

    def _execute_thread(self) -> None:
        while True:
            try:
                self._queue.get_nowait().execute()
            except queue.Empty:
                break

    def _handle_job_event(self, event: JobEvent) -> None:
        pass

    def execute(self) -> None:
        """ Execute all collected jobs in all avaliable threads, by order
        of collection. Block execution of calling thread until all jobs are
        finished executing. """

        self.__active_jobs = self._queue.qsize()

        for _ in range(self._threads):
            t = threading.Thread(target=self._execute_thread, daemon=True)
            t.start()

        while self.__active_jobs:
            event = self._manager.next_event()
            if isinstance(event, JobEndEvent):
                self.__active_jobs -= 1
            self._handle_job_event(event)

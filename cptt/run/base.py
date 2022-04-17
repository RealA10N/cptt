from __future__ import annotations

import threading
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from queue import Empty
from queue import Queue

from cptt.run.events import JobEndEvent
from cptt.run.events import JobEvent
from cptt.run.events import JobStartEvent


class JobEventManager:

    def __init__(self) -> None:
        self._events: Queue[JobEvent] = Queue()

    def push_event(self, event: JobEvent) -> None:
        self._events.put(event, block=True)

    def next_event(self) -> JobEvent:
        return self._events.get(block=True)


@dataclass
class Job(ABC):
    manager: JobEventManager = field(init=False, default=None)

    @abstractmethod
    def execute(self) -> None:
        """ The function that will be executed when the job runs in its own
        thread. You can assume that `self.manager` is initialized correctly
        and avaliable for message passing using the `self.manager.push_event`
        method. """


class Runner:

    def __init__(self, threads: int = 1) -> None:
        self._threads = threads
        self._queue: Queue[Job] = Queue()
        self._manager = JobEventManager()

    def collect(self, job: Job) -> None:
        job.manager = self._manager
        self._queue.put(job)

    def _execute_thread(self) -> None:
        while True:
            try:
                job = self._queue.get_nowait()
            except Empty:
                break
            job.manager.push_event(JobStartEvent(job))
            try:
                job.execute()
            finally:
                job.manager.push_event(JobEndEvent(job))

    def _handle_job_event(self, event: JobEvent) -> None:
        """ This method will get called during the blocking execution of the
        jobs from the main thread, reacting to different events from the child
        threads. Avaliable to be overwritten. """

    def execute(self) -> None:
        """ Execute all collected jobs in all avaliable threads, by order
        of collection. Block execution of calling thread until all jobs are
        finished executing. """

        # although the documentation states the the qsize method is only an
        # estimate for the size of the queue, I find it useful and accurate.
        # if we find out that it it causes bugs, we should count the jobs
        # independently.
        active_jobs = self._queue.qsize()

        for _ in range(self._threads):
            t = threading.Thread(target=self._execute_thread, daemon=True)
            t.start()

        while active_jobs:
            event = self._manager.next_event()
            if isinstance(event, JobEndEvent):
                active_jobs -= 1
            self._handle_job_event(event)

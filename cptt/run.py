from __future__ import annotations

import queue
import threading
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class JobEvent:
    job: Job


class JobEndEvent(JobEvent):
    pass


class Job(ABC):

    @abstractmethod
    def execute(self, events: queue.Queue[JobEvent]) -> None:
        """ The function to be executed as a part of the job. """


class Runner:

    def __init__(self, threads: int = 1) -> None:
        self._threads = threads
        self._queue: queue.Queue[Job] = queue.Queue()
        self._events: queue.Queue[JobEvent] = queue.Queue()

    def collect(self, job: Job) -> None:
        self._queue.put(job)

    def _execute_thread(self) -> None:
        while True:
            try:
                job = self._queue.get_nowait()
            except queue.Empty:
                return
            try:
                job.execute(self._events)
            finally:
                self._events.put(JobEndEvent(job))

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
            event = self._events.get(block=True)
            if isinstance(event, JobEndEvent):
                self.__active_jobs -= 1
            else:
                self._handle_job_event(event)

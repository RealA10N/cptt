from __future__ import annotations

import queue
import threading
from abc import ABC
from abc import abstractmethod


class Job(ABC):

    @abstractmethod
    def execute(self) -> None:
        """ The function to be executed as a part of the job. """


class Runner(ABC):

    @abstractmethod
    def collect(self, job: Job) -> None:
        """ Collect a single job. """

    @abstractmethod
    def execute(self) -> None:
        """ Execute all jobs collected. """


class SimpleRunner(Runner):

    def __init__(self) -> None:
        self._queue: queue.SimpleQueue[Job] = queue.SimpleQueue()

    def collect(self, job: Job) -> None:
        self._queue.put(job)

    def execute(self) -> None:
        """ Execute all jobs collected one by one, in the order that they have
        been collected in. Blocks execution and returns only after all jobs are
        executed. """

        while not self._queue.empty():
            job = self._queue.get()
            job.execute()


class ParallelRunner(Runner):

    def __init__(self, threads: int) -> None:
        self._threads = threads
        self._queue: queue.Queue[Job] = queue.Queue()

    def collect(self, job: Job) -> None:
        self._queue.put(job)

    def _execute_thread(self) -> None:
        while not self._queue.empty():
            job = self._queue.get()
            try:
                job.execute()
            finally:
                self._queue.task_done()

    def execute(self) -> None:
        """ Execute all collected jobs in all avaliable threads, by order
        of collection. Block execution of calling thread until all jobs are
        finished executing. """

        for _ in range(self._threads):
            threading.Thread(target=self._execute_thread).start()
        self._queue.join()

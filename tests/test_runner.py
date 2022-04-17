from __future__ import annotations

from cptt.run import Job
from cptt.run import JobEndEvent
from cptt.run import JobEvent
from cptt.run import JobStartEvent
from cptt.run import Runner
from testing import python_script


class RecordingRunner(Runner):

    def __init__(self, threads: int = 1) -> None:
        super().__init__(threads)
        self.events = list()

    def _handle_job_event(self, event: JobEvent) -> None:
        self.events.append(event)


def test_single_job():
    runner = RecordingRunner()
    job = Job(
        python_script(
            "name = input(); print(f'hello, {name}!')",
        ),
        input='cptt',
    )

    runner.collect(job)
    runner.execute()

    assert len(runner.events) == 2

    assert runner.events[0].job == job
    assert isinstance(runner.events[0], JobStartEvent)

    assert runner.events[1].job == job
    assert isinstance(runner.events[1], JobEndEvent)
    assert runner.events[1].success
    assert runner.events[1].message == 'Passed'


def test_multiple_jobs():
    THREADS = 3
    SLEEPFOR = 0.5
    runner = RecordingRunner(THREADS)

    order = list()

    for i in range(1, THREADS + 1):
        job = Job(python_script(f"from time import sleep; sleep({i*SLEEPFOR})"))
        order.append(job)
        runner.collect(job)

    runner.execute()
    assert len(runner.events) == THREADS * 2

    for event, job in zip(runner.events[THREADS:], order):
        assert isinstance(event, JobEndEvent)
        assert event.job is job


def test_parallel_jobs():
    from time import time

    THREADS = 10
    SLEEPFOR = 0.1

    runner = RecordingRunner(THREADS)

    for _ in range(THREADS):
        job = Job(python_script(f'from time import sleep; sleep({SLEEPFOR})'))
        runner.collect(job)

    start = time()
    runner.execute()
    took = time() - start

    assert SLEEPFOR <= took < THREADS * SLEEPFOR


def test_time_limit():

    TIME_LIMIT = 0.1

    runner = RecordingRunner()
    job = Job(
        python_script('from time import sleep; sleep(1)'),
        time_limit=TIME_LIMIT,
    )

    runner.collect(job)
    runner.execute()

    assert len(runner.events) == 2

    tle = runner.events[-1]
    assert isinstance(tle, JobEndEvent)
    assert not tle.success
    assert tle.time > TIME_LIMIT
    assert tle.message == 'Time Limit Exceeded'


def test_memory_limit():

    MEMORY_LIMIT = 100_000_000  # 100mb

    job = Job(
        python_script(
            """
            from random import random
            l = list()
            while True: l.append(random())
            """,
        ),
        memory_limit=MEMORY_LIMIT,
    )

    runner = RecordingRunner()
    runner.collect(job)
    runner.execute()

    assert len(runner.events) == 2

    mle = runner.events[-1]
    assert isinstance(mle, JobEndEvent)
    assert not mle.success
    assert mle.memory > MEMORY_LIMIT
    assert mle.message == 'Memory Limit Exceeded'

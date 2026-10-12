from __future__ import annotations

import random

from cptt.run import JobEndEvent
from cptt.run import JobStartEvent
from cptt.run.process import ProcessJob
from cptt.run.process import ProcessStatus
from cptt.run.process import ProcessStatusEvent
from testing import python_script
from testing.runners import RecordingRunner


def test_single_job():
    runner = RecordingRunner()
    job = ProcessJob(
        python_script(
            "name = input(); print(f'hello, {name}!')",
        ),
        input='cptt',
    )

    runner.collect(job)
    runner.execute()

    assert len(runner.events) == 3
    start, update, end = runner.events

    assert start.job is job
    assert isinstance(start, JobStartEvent)

    assert update.job is job
    assert isinstance(update, ProcessStatusEvent)
    assert update.status is ProcessStatus.FINISHED
    assert update.time > 0
    assert update.memory > 0

    assert end.job is job
    assert isinstance(end, JobEndEvent)


def test_multiple_jobs():
    THREADS = 3
    SLEEPFOR = 0.5
    runner = RecordingRunner(THREADS)

    no_order = list()
    order = list()

    for i in range(1, THREADS + 1):
        job = ProcessJob(
            python_script(
                f"from time import sleep; sleep({i * SLEEPFOR})",
            ),
        )

        no_order.append(job)
        order.append(job)

    order.reverse()
    random.shuffle(no_order)

    for job in no_order:
        runner.collect(job)

    runner.execute()
    assert len(runner.events) == THREADS * 3

    # each job contributes 3 events to the event list.
    # the first n events should be the starting events of the jobs.
    # the other 2n events should be 'process status' and 'job ends' events

    for event in runner.events[THREADS:]:
        assert not isinstance(event, JobStartEvent)

        if event.job in order:
            assert event.job is order[-1]
            order.pop()


def test_parallel_jobs():
    from time import time

    THREADS = 10
    SLEEPFOR = 0.5

    runner = RecordingRunner(THREADS)

    for _ in range(THREADS):
        job = ProcessJob(
            python_script(
                f'from time import sleep; sleep({SLEEPFOR})',
            ),
        )
        runner.collect(job)

    start = time()
    runner.execute()
    took = time() - start

    assert SLEEPFOR <= took < THREADS * SLEEPFOR


def test_time_limit():

    TIME_LIMIT = 0.1

    runner = RecordingRunner()
    job = ProcessJob(
        python_script('from time import sleep; sleep(1)'),
        time_limit=TIME_LIMIT,
    )

    runner.collect(job)
    runner.execute()

    assert len(runner.events) == 3
    status = runner.events[1]
    assert isinstance(status, ProcessStatusEvent)
    assert status.status is ProcessStatus.TIME_LIMIT
    assert status.time > TIME_LIMIT


def test_memory_limit():

    MEMORY_LIMIT = 100_000_000  # 100mb

    job = ProcessJob(
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

    assert len(runner.events) == 3

    status = runner.events[1]
    assert isinstance(status, ProcessStatusEvent)
    assert status.status is ProcessStatus.MEMORY_LIMIT
    assert status.memory > MEMORY_LIMIT

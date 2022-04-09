from __future__ import annotations

import time

from cptt.run import Job
from cptt.run import JobEvent
from cptt.run import Runner


class LambdaJob(Job):
    def __init__(self, func, args=(), kwargs={}) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def execute(self, *_) -> None:
        self.func(*self.args, **self.kwargs)


def test_single_job():
    runner = Runner()
    items = list()
    runner.collect(LambdaJob(lambda: items.append('hi')))
    runner.execute()
    assert items == ['hi']


def test_multiple_jobs():
    runner = Runner()
    items = list()
    for i in range(10):
        runner.collect(LambdaJob(lambda i: items.append(i), args=(i,)))
    runner.execute()
    assert items == list(range(10))


def test_parallel_jobs():
    items = set()

    def func(id):
        items.add(id)
        time.sleep(1)

    start = time.time()
    runner = Runner(threads=10)
    for i in range(10):
        runner.collect(LambdaJob(func, args=(i,)))

    runner.execute()
    exectime = time.time() - start

    assert items == set(range(10))
    assert 1 < exectime < 2


def test_parallel_order():
    items = list()

    def func(i):
        time.sleep(i)
        items.append(i)

    runner = Runner(threads=3)
    times = list(range(3))
    for i in reversed(times):
        runner.collect(LambdaJob(func, args=(i,)))

    runner.execute()
    assert items == times


class EventRecorder(Runner):
    def __init__(self, threads: int = 1) -> None:
        super().__init__(threads)
        self.record = list()

    def _handle_job_event(self, event: JobEvent) -> None:
        self.record.append(event)


def test_no_events():
    runner = EventRecorder(threads=3)
    for _ in range(3):
        runner.collect(LambdaJob(print, args=('hello!',)))
    runner.execute()
    assert runner.record == []


def test_adding_custom_events():

    class JobWithEvents(LambdaJob):
        def execute(self, events) -> None:
            super().execute(events)
            events.put(JobEvent(self))

    sleeps = [0.2, 0.3, 0.1]
    runner = EventRecorder(threads=len(sleeps))

    for t in sleeps:
        runner.collect(JobWithEvents(time.sleep, args=(t,)))

    runner.execute()
    expected = sorted(sleeps)
    got = [i.job.args[0] for i in runner.record]

    assert expected == got

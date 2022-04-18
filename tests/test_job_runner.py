from __future__ import annotations

import time

from cptt.run import Job
from cptt.run import JobEvent
from cptt.run import Runner
from cptt.run.events import JobStartEvent
from testing.runners import RecordingRunner


class LambdaJob(Job):
    def __init__(self, func, args=None, kwargs=None) -> None:
        self.func = func
        self.args = args if args else tuple()
        self.kwargs = kwargs if kwargs else dict()

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


def test_order_of_events():
    JOBS = 3

    runner = RecordingRunner(threads=JOBS)
    jobs = [
        LambdaJob(print, args=('hello!',))
        for _ in range(JOBS)
    ]

    for job in jobs:
        runner.collect(job)
    runner.execute()

    for job in jobs:
        started = False
        for event in runner.events:
            if event.job is job:
                if isinstance(event, JobStartEvent):
                    started = True
                else:
                    assert started


def test_adding_custom_events():

    class MyEvent(JobEvent):
        pass

    class MyJob(LambdaJob):
        def execute(self) -> None:
            super().execute()
            self.manager.push_event(MyEvent(self))

    sleeps = [0.2, 0.3, 0.1]
    runner = RecordingRunner(threads=len(sleeps))

    for t in sleeps:
        runner.collect(MyJob(time.sleep, args=(t,)))

    runner.execute()
    expected = sorted(sleeps)
    got = [e.job.args[0] for e in runner.events if isinstance(e, MyEvent)]
    assert expected == got

from __future__ import annotations

import time

from cptt.run import Job
from cptt.run import ParallelRunner
from cptt.run import SimpleRunner


class LambdaJob(Job):
    def __init__(self, func, args=(), kwargs={}) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def execute(self) -> None:
        self.func(*self.args, **self.kwargs)


def test_simple_single_job():
    runner = SimpleRunner()
    items = list()
    runner.collect(LambdaJob(lambda: items.append('hi')))
    runner.execute()
    assert items == ['hi']


def test_simple_multiple_jobs():
    runner = SimpleRunner()
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
    runner = ParallelRunner(threads=10)
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

    runner = ParallelRunner(threads=3)
    times = list(range(3))
    for i in reversed(times):
        runner.collect(LambdaJob(func, args=(i,)))

    runner.execute()
    assert items == times

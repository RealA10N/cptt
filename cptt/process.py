from __future__ import annotations

import threading
import time
from typing import AnyStr
from typing import IO
from typing import Optional

import psutil  # pip install psutil


class TimeLimitExceeded(RuntimeError):
    pass


class MemoryLimitExceeded(RuntimeError):
    pass


class MonitoredProcess(psutil.Popen):

    def __init__(self, *args, **kwargs) -> None:
        self.duration = 0
        self.memory_used = 0
        self._start_time = time.time()
        # We do not use psutils 'create_time' method because it is inaccurate,
        # and uses the time of the operatin system instead of Python's time,
        # which is consistant for our usage.

        return super().__init__(*args, **kwargs)

    def _time_guard(self, time_limit: float | None) -> None:
        """ Asserts that the process is still running in his given timeframe.
        If the current time is pass the allowed time for the process, a
        `TimeLimitExceeded` exception is raised. """

        self.duration = time.time() - self._start_time
        if time_limit is not None and self.duration > time_limit:
            raise TimeLimitExceeded(
                f'process running {self.duration} seconds '
                f'(limited to {time_limit})',
            )

    def _memory_guard(self, memory_limit: float | None) -> None:
        """ Asserts that the process uses no more memory then he is allowed to.
        If the process is caught using more memory than he is allowed to, a
        `MemoryLimitExceeded` exception is raised. """

        try:
            usage = self.memory_info().rss
        except psutil.NoSuchProcess:
            return

        self.memory_used = max(self.memory_used, usage)

        if memory_limit is not None and usage > memory_limit:
            raise MemoryLimitExceeded(
                f'process caught using {usage} bytes '
                f'(limited to {memory_limit})',
            )

    def wait(
        self,
        time_limit: float = None,
        memory_limit: float = None,
    ) -> None:
        """ Waits until the given process terminates, while constantly checking
        for violations of the time and memory constrains. If one of the
        constrains is violated, an exception is thrown and the process is
        killed.

        Be aware that similarly to subprocess's `Popen.wait` method, if you are
        piping `stdout` or `stderr` and they are very large, the program might
        get into a deadlock state caused by the operating system. In that case,
        use the `communicate` method instead. """

        delay = 0.001
        # similar delay constant is used in the subprocess implementation
        # https://tinyurl.com/ydc9kjy4
        # using a delay (even a small one) significantly improves performance,
        # because the operating system doesn't think that we are busy, but
        # actually just waiting for an event and doing some checks now and then.

        try:
            while self.poll() is None:
                self._memory_guard(memory_limit)
                self._time_guard(time_limit)
                time.sleep(delay)

        finally:
            try:
                self.kill()
            except psutil.NoSuchProcess:
                pass

        return self.returncode

    @staticmethod
    def _consume_stream(stream: IO[AnyStr]) -> None:
        stream._buffer = stream.read()
        stream.close()

    @staticmethod
    def _feed_stream(stream: IO[AnyStr], input: AnyStr) -> None:
        stream.write(input)
        stream.close()

    def communicate(
        self,
        input: AnyStr = None,
        time_limit: float = None,
        memory_limit: float = None,
    ) -> tuple[Optional[AnyStr], Optional[AnyStr]]:
        """ Comminicate with the process, and wait until it terminates.
        Returns the buffered stdout and stderr stream values, after they
        have been consumed and closed (if they were piped). """

        threads: list[threading.Thread] = list()

        if input:
            threads.append(
                threading.Thread(
                    target=self._feed_stream,
                    args=(self.stdin, input),
                ),
            )

        def create_consuming_thread(stream):
            threads.append(
                threading.Thread(
                    target=self._consume_stream,
                    args=(stream,),
                ),
            )

        if self.stdout is not None:
            create_consuming_thread(self.stdout)

        if self.stderr is not None:
            create_consuming_thread(self.stderr)

        for thread in threads:
            thread.daemon = True
            thread.start()

        try:
            self.wait(time_limit, memory_limit)
        finally:
            for thread in threads:
                thread.join()
            try:
                self.kill()
            except psutil.NoSuchProcess:
                pass

        return (
            None if self.stdout is None else self.stdout._buffer,
            None if self.stderr is None else self.stderr._buffer,
        )

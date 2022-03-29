from __future__ import annotations

import time

import psutil  # pip install psutil


class TimeLimitExceeded(RuntimeError):
    pass


class MemoryLimitExceeded(RuntimeError):
    pass


class MonitoredProcess(psutil.Popen):

    def _time_guard(self, start: float, time_limit: float) -> None:
        """ Asserts that the process is still running in his given timeframe.
        If the current time is pass the allowed time for the process, a
        `TimeLimitExceeded` exception is raised. """

        cur = time.time()
        if cur - start > time_limit:
            raise TimeLimitExceeded(
                f'process running {cur-start} seconds '
                f'(limited to {time_limit})',
            )

    def _memory_guard(self, memory_limit: float) -> None:
        """ Asserts that the process uses no more memory then he is allowed to.
        If the process is caught using more memory than he is allowed to, a
        `MemoryLimitExceeded` exception is raised. """

        try:
            usage = self.memory_info().rss
        except psutil.NoSuchProcess:
            return

        if usage > memory_limit:
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
        you will have to use threads to read from the stream and free up space
        in the buffer. """

        start_time = time.time()

        delay = 0.001
        # similar delay constant is used in the subprocess implementation
        # https://tinyurl.com/ydc9kjy4
        # using a delay (even a small one) significantly improves performance,
        # because the operating system doesn't think that we are busy, but
        # actually just waiting for an event and doing some checks now and then.

        try:
            while self.poll() is None:
                time.sleep(delay)
                if time_limit:
                    self._time_guard(start_time, time_limit)
                if memory_limit:
                    self._memory_guard(memory_limit)

        finally:
            try:
                self.kill()
            except psutil.NoSuchProcess:
                pass

        return self.returncode

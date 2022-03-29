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
        use the `communicate` method instead. """

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

    @staticmethod
    def _consume_stream(stream: IO[AnyStr], to: list) -> None:
        to.append(stream.read())
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

        if input:
            self.stdin.write(input)
            self.stdin.close()

        threads: list[threading.Thread] = list()

        if self.stdout is not None:
            self._stdout_buf = list()
            threads.append(
                threading.Thread(
                    target=self._consume_stream,
                    args=(self.stdout, self._stdout_buf),
                ),
            )

        if self.stderr is not None:
            self._stderr_buf = list()
            threads.append(
                threading.Thread(
                    target=self._consume_stream,
                    args=(self.stderr, self._stderr_buf),
                ),
            )

        for thread in threads:
            thread.daemon = True
            thread.start()

        try:
            self.wait(time_limit, memory_limit)
        finally:
            for thread in threads:
                thread.join()

        stdout = self._stdout_buf[0] if self.stdout else None
        stderr = self._stderr_buf[0] if self.stderr else None
        return (stdout, stderr)

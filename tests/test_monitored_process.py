from __future__ import annotations

import subprocess

import pytest

from cptt.process import MemoryLimitExceeded
from cptt.process import MonitoredProcess
from cptt.process import TimeLimitExceeded


def requires_cli(name: str):
    import shutil

    return pytest.mark.skipif(
        shutil.which(name) is None,
        reason=f'required CLI {name!r} is not present',
    )


def python_script(code: str) -> list[str]:
    """ Stores the given code in a temporary file, and returns the argument
    list for executing the file with the running Python executable. """
    import sys
    import tempfile
    import inspect

    with tempfile.NamedTemporaryFile(
        mode='w',
            suffix='.py', encoding='utf8', delete=False,
    ) as f:
        f.write(inspect.cleandoc(code))

    return (sys.executable, f.name)


@requires_cli('echo')
def test_echo():
    process = MonitoredProcess(
        ['echo', 'hi'],
        encoding='utf8',
        stdout=subprocess.PIPE,
    )
    process.wait()
    assert process.stdout.read() == 'hi\n'


def test_hello_world():
    process = MonitoredProcess(
        python_script("""
            print("Hello, World!")
        """),
        encoding='utf8',
        stdout=subprocess.PIPE,
    )

    print(process, process.name(), process.memory_info())
    process.wait()
    assert process.stdout.read() == 'Hello, World!\n'
    assert 0 < process.duration
    assert 0 < process.memory_used


def test_communicate_streams():
    process = MonitoredProcess(
        python_script("""
        import sys
        sys.stdout.write('stdout (:')
        sys.stderr.write('stderr ):')
        """),
        encoding='utf8',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = process.communicate()
    assert out == 'stdout (:'
    assert err == 'stderr ):'


def test_wait_streams():
    process = MonitoredProcess(
        python_script("""
        import sys
        sys.stdout.write('stdout (:')
        sys.stderr.write('stderr ):')
        """),
        encoding='utf8',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    process.wait()
    assert process.stdout.read() == 'stdout (:'
    assert process.stderr.read() == 'stderr ):'


def test_communicate_large_output():
    process = MonitoredProcess(
        python_script("""
        for i in range(20_000):
            print(i)
        """),
        encoding='utf8',
        stdout=subprocess.PIPE,
    )

    out, _ = process.communicate()
    assert len(out) > 100_000


def test_memory_limit():
    process = MonitoredProcess(
        python_script("""
            array = bytes(b'0123456789' * 1_000_000) # 10MB
        """),
    )

    with pytest.raises(MemoryLimitExceeded):
        process.wait(time_limit=10, memory_limit=10_000_000)

    assert process.memory_used > 10_000_000


def test_time_limit():
    process = MonitoredProcess(
        python_script("""
        import time
        time.sleep(1)
        """),
    )

    with pytest.raises(TimeLimitExceeded):
        process.wait(time_limit=0.5)

    assert process.duration > 0.5

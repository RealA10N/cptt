from __future__ import annotations

import pytest


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

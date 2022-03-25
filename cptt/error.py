from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestingError:
    code: str  # a short unique code that that represents the error type
    priority: int  # positive, 0 is highest priority
    message: str

    ERRORS = {
        'F001': (1, 'output shorter than expected'),
        'F002': (1, 'output longer then expected'),
    }

    @classmethod
    def construct(cls, code: str, *args, **kwargs):
        info = cls.ERRORS.get(code)
        if info is None:
            raise ValueError(f"Invalid error code {code!r}")
        return cls(
            code=code,
            priority=info[0],
            message=info[1].format(*args, **kwargs),
        )

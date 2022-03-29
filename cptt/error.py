from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TestingError:
    code: str  # a short unique code that that represents the error type
    priority: int  # positive, 0 is highest priority
    message: str

    ERRORS = {
        'MORE': (1, 'output shorter than expected'),
        'LESS': (1, 'output longer then expected'),
        'EXNU': (2, 'expected number, got token'),
        'DIFF': (3, 'outputs differ'),
        'TOKD': (3, 'tokens differ'),
        'NUMD': (3, 'numbers differ'),
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

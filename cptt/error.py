from __future__ import annotations

from cmath import inf
from dataclasses import dataclass


@dataclass
class TestingError:
    code: str  # a short unique code that that represents the error type
    priority: int = inf  # positive, 0 is highest priority
    message: str = None

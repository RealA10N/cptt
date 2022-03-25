from dataclasses import dataclass
from cmath import inf


@dataclass
class TestingError:
    code: str  # a short unique code that that represents the error type
    priority: int = inf  # positive, 0 is highest priority
    message: str = None

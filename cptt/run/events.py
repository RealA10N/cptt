from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cptt.run.base import Job


@dataclass
class JobEvent:
    job: Job


@dataclass
class JobStartEvent(JobEvent):
    pass


@dataclass
class JobEndEvent(JobEvent):
    pass

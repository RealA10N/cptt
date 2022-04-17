from __future__ import annotations

import enum
from dataclasses import dataclass
from dataclasses import field
from subprocess import PIPE

from cptt.process import MemoryLimitExceeded
from cptt.process import MonitoredProcess
from cptt.process import TimeLimitExceeded
from cptt.run.base import Job
from cptt.run.events import JobEvent
from cptt.validate import ValidationError
from cptt.validate import Validator


class ProcessStatus(enum.Enum):
    FINISHED = enum.auto()
    TIME_LIMIT = enum.auto()
    MEMORY_LIMIT = enum.auto()
    WRONG_ANSWER = enum.auto()
    RUNTIME_ERROR = enum.auto()
    KILLED = enum.auto()


@dataclass
class ProcessStatusEvent(JobEvent):
    status: ProcessStatus
    time: float
    memory: float


@dataclass
class ProcessJob(Job):
    program: list[str]
    time_limit: float = None
    memory_limit: float = None
    input: str = None
    validators: list[Validator] = field(default_factory=list)

    def execute(self) -> None:

        process = MonitoredProcess(
            self.program,
            encoding='utf8',
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
        )

        try:
            out, err = process.communicate(
                input=self.input,
                time_limit=self.time_limit,
                memory_limit=self.memory_limit,
            )

            for validator in self.validators:
                validator.validate(
                    stdout=out, stderr=err,
                    returncode=process.returncode,
                )

        except TimeLimitExceeded:
            self.manager.push_event(
                ProcessStatusEvent(
                    job=self,
                    status=ProcessStatus.TIME_LIMIT,
                    time=process.duration,
                    memory=process.memory_used,
                ),
            )

        except MemoryLimitExceeded:
            self.manager.push_event(
                ProcessStatusEvent(
                    job=self,
                    status=ProcessStatus.MEMORY_LIMIT,
                    time=process.duration,
                    memory=process.memory_used,
                ),
            )

        except ValidationError:
            self.manager.push_event(
                ProcessStatusEvent(
                    job=self,
                    status=ProcessStatus.WRONG_ANSWER,
                    time=process.duration,
                    memory=process.memory_used,
                ),
            )

        else:
            self.manager.push_event(
                ProcessStatusEvent(
                    job=self,
                    status=ProcessStatus.FINISHED,
                    time=process.duration,
                    memory=process.memory_used,
                ),
            )

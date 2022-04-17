from __future__ import annotations

from typing import TYPE_CHECKING

from cptt.run import Runner

if TYPE_CHECKING:
    from cptt.run.events import JobEvent


class RecordingRunner(Runner):

    def __init__(self, threads: int = 1) -> None:
        super().__init__(threads)
        self.events = list()

    def _handle_job_event(self, event: JobEvent) -> None:
        self.events.append(event)

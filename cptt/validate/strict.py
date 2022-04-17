from __future__ import annotations

from cptt.validate import ValidationError
from cptt.validate.base import OutputValidator


class StrictValidator(OutputValidator):

    def validate(self, stdout: str, *_, **__) -> None:
        if stdout != self._expected:
            raise ValidationError('Output does not match expectations')

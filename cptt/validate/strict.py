from __future__ import annotations

from typing import Generator

from cptt.error import TestingError
from cptt.validate.base import Validator

ErrorGenerator = Generator[TestingError, None, None]


class StrictValidator(Validator):

    def validate(self, output: str, expected: str) -> ErrorGenerator:
        if output != expected:
            yield TestingError.construct('DIFF')

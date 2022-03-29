from __future__ import annotations

from io import DEFAULT_BUFFER_SIZE
from typing import Generator
from typing import TextIO

from cptt.error import TestingError
from cptt.validate.base import Validator

ErrorGenerator = Generator[TestingError, None, None]


class StrictValidator(Validator):

    BUFSIZE = DEFAULT_BUFFER_SIZE

    def validate(self, output: TextIO, expected: TextIO) -> ErrorGenerator:
        out = exp = ''
        while out or exp:
            if out != exp:
                yield TestingError.construct('DIFF')
                return
            out = output.read(self.BUFSIZE)
            exp = expected.read(self.BUFSIZE)

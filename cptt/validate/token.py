from __future__ import annotations

import string
from typing import Generator
from typing import TextIO
from itertools import zip_longest

from cptt.error import TestingError
from cptt.validate.base import Validator

ErrorGenerator = Generator[TestingError, None, None]
StrGenerator = Generator[str, None, None]


class TokenValidator(Validator):

    @staticmethod
    def tokenize(stream: TextIO) -> StrGenerator:
        """ Consumes tokens (continuous words) from the given text stream and
        yields them one after another. """

        c = stream.read(1)
        tok = ''

        while c:
            if c in string.whitespace:
                if tok: yield tok
                tok = ''
            else: tok += c
            c = stream.read(1)

        if tok: yield tok

    def validate(self, output: TextIO, expected: TextIO) -> ErrorGenerator:
        for outtok, exptok in zip_longest(
                self.tokenize(output), self.tokenize(expected)):
            if outtok is None: yield TestingError.construct('F001')
            elif exptok is None: yield TestingError.construct('F002')

from __future__ import annotations

import re
import string
from itertools import zip_longest
from typing import Generator
from typing import TextIO

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
                if tok:
                    yield tok
                tok = ''
            else:
                tok += c
            c = stream.read(1)

        if tok:
            yield tok

    NUMBER_REGEX = re.compile(r'[\-\+]?0*\d{,20}(\.\d{,20})?')

    @classmethod
    def token_to_number(cls, token: str) -> float | None:
        """ Converts the given token into a floating number. Returns None if
        the given token is not recognized as a number. We use a custom regular
        expression before passing the token to the `float` constructor to
        disallow tokens such as 'inf' and other Python specifics. """

        match = cls.NUMBER_REGEX.fullmatch(token)
        if match:
            return float(token)

    def compare_tokens(self, out: str, exp: str) -> ErrorGenerator:
        """ Compare two strings and yield errors if there are any. """
        pass

    def validate(self, output: TextIO, expected: TextIO) -> ErrorGenerator:
        outtoks, exptoks = self.tokenize(output), self.tokenize(expected)
        for out, exp in zip_longest(outtoks, exptoks):
            if out is None:
                yield TestingError.construct('F001')
                return
            elif exp is None:
                yield TestingError.construct('F002')
                return
            else:
                yield from self.compare_tokens(out, exp)

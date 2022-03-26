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

        # from my knowledge, python's file `read` method is buffered.
        # this means that is it ok to read one character at a time.

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

    NUMBERS_EQUALITY_DELTA = 1e-5
    NUMBER_REGEX = re.compile(r'[\-\+]?0{,20}\d{,20}(\.\d{,20})?')

    @classmethod
    def token_to_number(cls, token: str) -> float | None:
        """ Converts the given token into a floating number. Returns None if
        the given token is not recognized as a number. We use a custom regular
        expression before passing the token to the `float` constructor to
        disallow tokens such as 'inf', and long strings that look like a number
        but actually should be treated as strings (bitstrings for example). """

        match = cls.NUMBER_REGEX.fullmatch(token)
        if match:
            return float(token)

    @classmethod
    def compare_tokens(cls, out: str, exp: str) -> ErrorGenerator:
        """ Compare two strings and yield errors if there are any. """

        exp_num = cls.token_to_number(exp)
        if exp_num is None:
            if out != exp:
                yield TestingError.construct('TOKD')

        else:
            out_num = cls.token_to_number(out)

            if out_num is None:
                yield TestingError.construct('EXNU')

            elif abs(out_num - exp_num) > cls.NUMBERS_EQUALITY_DELTA:
                yield TestingError.construct('NUMD')

    def validate(self, output: TextIO, expected: TextIO) -> ErrorGenerator:
        outtoks, exptoks = self.tokenize(output), self.tokenize(expected)
        for out, exp in zip_longest(outtoks, exptoks):
            if out is None:
                yield TestingError.construct('LESS')
                return
            elif exp is None:
                yield TestingError.construct('MORE')
                return
            else:
                yield from self.compare_tokens(out, exp)

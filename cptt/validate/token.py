from __future__ import annotations

import string
from typing import Generator
from typing import TextIO

from cptt.validate.base import Validator

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

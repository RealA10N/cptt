from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generator
from typing import TextIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cptt.error import TestingError
    ErrorGenerator = Generator[TestingError, None, None]


class Validator(ABC):
    """ Comperes the programs output with the expected one. """

    @abstractmethod
    def validate(self, output: TextIO, expected: TextIO) -> ErrorGenerator:
        """ Comperes the programs output with the expected one. 'output' is the
        stream that the program writes it's output to. 'expected' is a stream
        that contains expected output that the validator uses as a reference
        for compering. """

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TextIO, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from cptt.error import TestingError


class Validator(ABC):
    """ Comperes the programs output with the expected one. """

    @abstractmethod
    def validate(self,
                 output: TextIO,
                 expected: TextIO,
                 ) -> Generator[TestingError, None, None]:
        """ Comperes the programs output with the expected one. 'output' is the
        stream that the program writes it's output to. 'expected' is a stream
        that contains expected output that the validator uses as a reference
        for compering. """

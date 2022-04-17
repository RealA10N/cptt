from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class ValidationError(Exception):
    """ Raised by a validation if there is any sort of validation error. """
    message: str


class Validator(ABC):
    """ Comperes the programs output with the expected one. """

    @abstractmethod
    def validate(self, *, stdout: str, stderr: str, returncode: int) -> None:
        """ Recives the output that is produced by a process and validates
        it. """


class OutputValidator(Validator):
    """ Validators that compare the output of the program with some
    expected output. """

    def __init__(self, expected: str) -> None:
        self._expected = expected

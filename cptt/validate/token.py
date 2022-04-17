from __future__ import annotations

from cptt.validate.base import OutputValidator
from cptt.validate.base import ValidationError


class TokenValidator(OutputValidator):

    MAX_NUMBER_LENGTH = 20
    MAX_ALLOWED_ERROR = 1e-5

    @classmethod
    def compare_tokens(cls, got: str, exp: str) -> None:
        if got.lower() == exp.lower():
            return

        try:
            assert len(got) <= cls.MAX_NUMBER_LENGTH
            assert len(exp) <= cls.MAX_NUMBER_LENGTH
            got_num, exp_num = float(got), float(exp)
            assert abs(got_num - exp_num) <= cls.MAX_ALLOWED_ERROR

        except (ValueError, AssertionError):
            raise ValidationError('Tokens differ') from None

    def validate(self, stdout: str, *_, **__) -> None:
        stdout = stdout.split()
        expected = self._expected.split()

        if len(stdout) != len(expected):
            raise ValidationError(
                f'Got {len(stdout)} tokens, expected {len(expected)}',
            )

        for out, exp in zip(stdout, expected):
            self.compare_tokens(out, exp)

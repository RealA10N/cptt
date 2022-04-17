from __future__ import annotations

import pytest

from cptt.validate import TokenValidator
from cptt.validate import ValidationError


def test_more_tokens():
    validator = TokenValidator(expected='hello')
    with pytest.raises(ValidationError) as err:
        validator.validate(stdout='hello 123', stderr='', returncode=0)
    assert err.value.message == 'Got 2 tokens, expected 1'


def test_long_token():
    output = '123456789' * 100_000
    expect = '123456789' * 100_000
    validator = TokenValidator(expect)
    validator.validate(output, stderr='', returncode=0)


def test_lots_of_tokens():
    output = 'tOkEn \n' * 100_000
    expect = ' ToKen' * 100_000
    validator = TokenValidator(expect)
    validator.validate(output, stderr='', returncode=0)

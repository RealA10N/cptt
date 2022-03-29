from __future__ import annotations

from cptt.validate import TokenValidator


def test_more_tokens():
    validator = TokenValidator()
    errors = list(validator.validate(output='hello 123', expected='hello'))
    assert len(errors) == 1
    assert errors[0].code == 'MORE'


def test_less_tokens():
    validator = TokenValidator()
    errors = list(validator.validate(output='hello', expected='hello 123'))
    assert len(errors) == 1
    assert errors[0].code == 'LESS'


def test_long_token():
    validator = TokenValidator()
    output = '123456789' * 100_000
    expect = '123456789' * 100_000
    errors = list(validator.validate(output, expect))
    assert errors == []


def test_lots_of_tokens():
    validator = TokenValidator()
    output = 'tOkEn \n' * 100_000
    expect = ' ToKen' * 100_000
    errors = list(validator.validate(output, expect))
    assert errors == []

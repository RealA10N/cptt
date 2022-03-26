from __future__ import annotations

import io

from cptt.validate import TokenValidator


def test_more_tokens():
    validator = TokenValidator()
    output = io.StringIO('hello 123')
    expect = io.StringIO('hello')
    errors = list(validator.validate(output, expect))
    assert len(errors) == 1
    assert errors[0].code == 'MORE'


def test_less_tokens():
    validator = TokenValidator()
    output = io.StringIO('hello')
    expect = io.StringIO('hello 123')
    errors = list(validator.validate(output, expect))
    assert len(errors) == 1
    assert errors[0].code == 'LESS'


def test_long_token():
    validator = TokenValidator()
    output = io.StringIO('123456789' * 100_000)
    expect = io.StringIO('123456789' * 100_000)
    errors = list(validator.validate(output, expect))
    assert errors == []


def test_lots_of_tokens():
    validator = TokenValidator()
    output = io.StringIO('tOkEn \n' * 100_000)
    expect = io.StringIO(' ToKen' * 100_000)
    errors = list(validator.validate(output, expect))
    assert errors == []

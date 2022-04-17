from __future__ import annotations

import pytest

from cptt.validate import TokenValidator
from cptt.validate import ValidationError

compare_tokens = TokenValidator.compare_tokens


def test_matching_integers():
    compare_tokens('123', '123')


def test_different_integers():
    with pytest.raises(ValidationError) as err:
        compare_tokens('123', '124')
    assert err.value.message == 'Tokens differ'


def test_matching_zero_padded():
    compare_tokens('123.0', '0123')


def test_floating_equality():
    compare_tokens('0.123456789', '0.123456')


def test_token_equality():
    compare_tokens('abc', 'abc')


def test_case_insensitivity():
    compare_tokens('hello', 'HELLO')


def test_not_equal_bitstrings():
    tok = '01' * 100
    tok2 = '0' + tok
    with pytest.raises(ValidationError):
        compare_tokens(tok, tok2)

from __future__ import annotations

from cptt.validate import TokenValidator
compare_tokens = TokenValidator.compare_tokens


def test_matching_integers():
    assert list(compare_tokens('123', '123')) == []


def test_different_integers():
    errors = list(compare_tokens('123', '124'))
    assert len(errors) == 1
    assert errors[0].code == 'NUMD'


def test_matching_zero_padded():
    assert list(compare_tokens('123.0', '0123')) == []


def test_floating_equality():
    assert list(compare_tokens('0.123456789', '0.123456')) == []


def test_token_equality():
    assert list(compare_tokens('abc', 'abc')) == []


def test_not_equal_bitstrings():
    tok = '01' * 100
    tok2 = '0' + tok
    errors = list(compare_tokens(tok, tok2))
    assert len(errors) == 1
    assert errors[0].code == 'TOKD'

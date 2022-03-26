from __future__ import annotations

from cptt.validate import TokenValidator


def test_long_bitstring():
    assert TokenValidator.token_to_number('10' * 20) is None


def test_long_zero_bitstrong():
    assert TokenValidator.token_to_number('0' * 50) is None


def test_short_integer():
    assert TokenValidator.token_to_number('12345') == 12345


def test_zero():
    num = TokenValidator.token_to_number('0')
    assert num is not None
    assert num == 0


def test_floating_zero():
    num = TokenValidator.token_to_number('0.0')
    assert num is not None
    assert num == 0


def test_short_float():
    assert 12345.56789 == TokenValidator.token_to_number('12345.56789')


def test_float_no_whole():
    assert 0.123 == TokenValidator.token_to_number('.123')


def test_negative_zero():
    assert 0 == TokenValidator.token_to_number('-0')


def test_not_a_number():
    assert TokenValidator.token_to_number('abc') is None


def test_no_scientific_notation():
    assert TokenValidator.token_to_number('1e6') is None


def test_no_inf():
    assert TokenValidator.token_to_number('inf') is None

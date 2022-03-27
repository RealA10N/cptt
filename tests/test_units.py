from __future__ import annotations

import pytest

from cptt.units import information_unit
from cptt.units import time_unit


def test_regular_word():
    assert time_unit('100minutes') == 6_000


def test_no_unit_name():
    assert time_unit('123') == 123


def test_empty_string():
    assert time_unit('') == 1


def test_only_unit():
    assert time_unit('h') == 3600


def test_default_info():
    assert information_unit('') == 1000 ** 2


def test_info():
    assert information_unit('32') == 32_000_000


def test_not_in_format():
    with pytest.raises(ValueError) as err:
        information_unit('mb32')
    assert 'format' in str(err.value)


def test_invalid_information_unit():
    with pytest.raises(ValueError) as err:
        information_unit('23dag')
    assert 'invalid unit' in str(err.value)


def test_invalid_time_unit():
    with pytest.raises(ValueError) as err:
        time_unit('week')
    assert 'invalid unit' in str(err.value)

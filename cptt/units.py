from __future__ import annotations

import argparse
import re

INFORMATION_UNITS_IN_BYTES = {
    'b': 1,
    'byte': 1,
    'bytes': 1,
    'kib': 1024,
    'kibi': 1024,
    'kibibyte': 1024,
    'kibibytes': 1024,
    'mib': 1024 ** 2,
    'mebi': 1024 ** 2,
    'mebibyte': 1024 ** 2,
    'mebibytes': 1024 ** 2,
    'gib': 1024 ** 3,
    'gibi': 1024 ** 3,
    'gibibyte': 1024 ** 3,
    'gibibytes': 1024 ** 3,
    'tib': 1024 ** 4,
    'tebi': 1024 ** 4,
    'tebibyte': 1024 ** 4,
    'tebibytes': 1024 ** 4,
    'kb': 1000,
    'kilo': 1000,
    'kilobyte': 1000,
    'kilobytes': 1000,
    'mb': 1000 ** 2,
    'mega': 1000 ** 2,
    'megabyte': 1000 ** 2,
    'megabytes': 1000 ** 2,
    'gb': 1000 ** 3,
    'giga': 1000 ** 3,
    'gigabyte': 1000 ** 3,
    'gigabytes': 1000 ** 3,
    'tb': 1000 ** 4,
    'tera': 1000 ** 4,
    'terabyte': 1000 ** 4,
    'terabytes': 1000 ** 4,
}


TIME_UNITS_IN_SECONDS = {
    'ms': 0.001,
    'millisecond': 0.001,
    'milliseconds': 0.001,
    's': 1,
    'sec': 1,
    'seconds': 1,
    'm': 60,
    'min': 60,
    'minutes': 60,
    'h': 60 ** 2,
    'hour': 60 ** 2,
    'hours': 60 ** 2,
}

NUM_UNIT_PATTERN = re.compile(r'(?P<num>\d*(\.\d*)?)(?P<unit>\D*)')


def _parse_unit_word(word: str) -> tuple[int, str]:
    match = NUM_UNIT_PATTERN.fullmatch(word.strip())
    if not match:
        raise ValueError(f'{word!r} not in <NUMBER><UNIT> format')
    return match.group('num'), match.group('unit').lower()


def unit_type(unit):
    """ Returns a function that is a wrapper around the given unit function,
    which can be used as a argparse type. This replaces all `ValueError`
    exceptions with ArgumentTypeError expections that show up with a custom
    error message when argparse handles them. """

    def constructor(word: str):
        try:
            return unit(word)
        except ValueError as err:
            raise argparse.ArgumentTypeError(*err.args)
    return constructor


def information_unit(word: str, default_unit='mb') -> float:
    num, unit = _parse_unit_word(word)
    if not unit:
        unit = default_unit
    factor = INFORMATION_UNITS_IN_BYTES.get(unit)
    if factor is None:
        raise ValueError(f'invalid unit {unit!r}')
    return float(num) * factor


def time_unit(word: str, default_unit='s') -> float:
    num, unit = _parse_unit_word(word)
    if not unit:
        unit = default_unit
    factor = TIME_UNITS_IN_SECONDS.get(unit)
    if factor is None:
        raise ValueError(f'invalid unit {unit!r}')
    return float(num) * factor

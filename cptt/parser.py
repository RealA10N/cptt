from __future__ import annotations

import argparse

import cptt
from cptt.units import information_unit
from cptt.units import time_unit
from cptt.units import unit_type

parser = argparse.ArgumentParser(
    prog='cptt',
    description=cptt.__description__,
)

parser.add_argument(
    'program',
    help='program to be executed. to pass arguments with the command, use '
    '"program foo bar ..." (with quotes).',
)

parser.add_argument(
    '-i', '--input',
    help='a text file, an executable program, or a string literal. '
    'if a a path to a text file is provided, this file will be piped into '
    'the standard input of the program. if the string is a valid shell '
    'command, the output of the command will be piped instead. otherwise, '
    'uses the string as the input to the program.',
    action='append',
)

parser.add_argument(
    '-o', '--output',
    help='a text file that contains the expected output of the program, '
    'and the output of the program is compared to the data inside this file. '
    'the number of `output` arguments should be less or equal to the number of '
    '`input` arguments. ',
    action='append',
    metavar='FILE',
)

parser.add_argument(
    '-m', '--memory',
    help='an upper bound for the memory that the program is allowed to '
    'consume. if unit metric is not given, MB (1 million bytes) is assumed.',
    type=unit_type(information_unit),
)

parser.add_argument(
    '-t', '--time',
    help='an upper bound for the time that the program is allowed to run. if '
    'the program does not exit after the specified time, it will get killed.',
    type=unit_type(time_unit),
)

parser.add_argument(
    '-s', '--strict',
    help='compare the output of the program with the specified outputs '
    'strictly, character by character, and raise errors for any mismatches.',
    action='store_true',

)

parser.add_argument(
    '-e', '--epsilon',
    help='a small floating number that is used to determine of two floating '
    'numbers (x, y) are equal using the formula: abs(x-y) < eps. This value is '
    'ignored if "strict" mode is enabled.',
    type=float, default=1e-5,
)

parser.add_argument(
    '-p', '--parallel',
    help='run multiple subprocesses of the program in parallel, one process '
    'for each provided input. ',
    action='store_true',
)

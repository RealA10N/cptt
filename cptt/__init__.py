__version__ = '0.1.0a0'
__author__ = 'Alon Krymgand Osovsky'
__author_email__ = 'downtown2u@gmail.com'
__description__ = ' '.join((
    'Execute programs and enforce certain behavior such as',
    'time and memory constrains, output format and validation, etc.',
))

from .__main__ import main, run_main
__all__ = ['main', 'run_main']

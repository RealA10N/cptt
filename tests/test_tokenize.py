from __future__ import annotations

import io

from cptt.validate import TokenValidator


def test_single_token():
    assert list(TokenValidator.tokenize(io.StringIO('token'))) == ['token']


def test_sentence():
    tokens = list(TokenValidator.tokenize(io.StringIO('hello there!')))
    assert tokens == ['hello', 'there!']


def test_unicode():
    tokens = list(TokenValidator.tokenize(io.StringIO('שלום עולם 😀🌍️')))
    assert tokens == ['שלום', 'עולם', '😀🌍️']


def test_sentence_with_whitespaces():
    tokens = list(TokenValidator.tokenize(io.StringIO(' Hello\n There?  ')))
    assert tokens == ['Hello', 'There?']


def test_no_tokens():
    assert list(TokenValidator.tokenize(io.StringIO(''))) == []


def test_whitespaces_only():
    assert list(TokenValidator.tokenize(io.StringIO(' \n \t'))) == []

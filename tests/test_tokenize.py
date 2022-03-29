from __future__ import annotations

from cptt.validate import TokenValidator


def test_single_token():
    assert list(TokenValidator.tokenize('token')) == ['token']


def test_sentence():
    tokens = list(TokenValidator.tokenize('hello there!'))
    assert tokens == ['hello', 'there!']


def test_unicode():
    tokens = list(TokenValidator.tokenize('שלום עולם 😀🌍️'))
    assert tokens == ['שלום', 'עולם', '😀🌍️']


def test_sentence_with_whitespaces():
    tokens = list(TokenValidator.tokenize(' Hello\n There?  '))
    assert tokens == ['Hello', 'There?']


def test_no_tokens():
    assert list(TokenValidator.tokenize('')) == []


def test_whitespaces_only():
    assert list(TokenValidator.tokenize(' \n \t')) == []

import pytest
from grammar.classes import GrammarReader, GrammarConverter


@pytest.fixture
def read_grammar():
    def _read_grammar(filename):
        reader = GrammarReader()
        reader.get_grammar(filename)

        return reader.grammar()

    return _read_grammar


@pytest.fixture
def get_converter():
    def _get_converter(grammar):
        converter = GrammarConverter()
        converter.get_grammar(grammar)

        return converter

    return _get_converter

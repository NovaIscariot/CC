import pytest
import os

PARENT_DIR = os.path.dirname(os.getcwd())


@pytest.mark.parametrize("string", ['n + n', 'n * n', 'n * ( n + n )', '( ( ( n ) ) )'])
def test_positive(string, read_grammar):
    grammar = read_grammar(PARENT_DIR + '/grammars/recursive_decent_parse.txt')

    assert grammar.recursive_decent_parse(string) is True


@pytest.mark.parametrize("string", ['', 'n - n', 'n * + n', '( + n )', '+ n'])
def test_negative(string, read_grammar):
    grammar = read_grammar(PARENT_DIR + '/grammars/recursive_decent_parse.txt')

    assert grammar.recursive_decent_parse(string) is False

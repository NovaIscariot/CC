import pytest
import os

PARENT_DIR = os.path.dirname(os.getcwd())


@pytest.mark.parametrize("string", ['a + a', 'a * a', 'a * ( a + a )', '( ( ( a ) ) )'])
def test_positive(string, read_grammar, get_lr_parser):
    g0_opr_table = {
        ")": {"(": "e3", "a": "e3", "*": ">", "+": ">", ")": ">", "$": ">"},
        "a": {"(": "e3", "a": "e3", "*": ">", "+": ">", ")": ">", "$": ">"},
        "*": {"(": "<", "a": "<", "*": ">", "+": ">", ")": ">", "$": ">"},
        "+": {"(": "<", "a": "<", "*": "<", "+": ">", ")": ">", "$": ">"},
        "(": {"(": "<", "a": "<", "*": "<", "+": "<", ")": "=", "$": "e4"},
        "$": {"(": "<", "a": "<", "*": "<", "+": "<", ")": "e2", "$": "e1"},
    }

    grammar = read_grammar('operator_precedence_1.txt')
    parser = get_lr_parser(grammar, g0_opr_table)

    assert parser.parse(string) is True


@pytest.mark.parametrize("string", ['', 'a - a', 'a * + a', '( + a )', '+ a'])
def test_negative(string, read_grammar, get_lr_parser):
    g0_opr_table = {
        ")": {"(": "e3", "a": "e3", "*": ">", "+": ">", ")": ">", "$": ">"},
        "a": {"(": "e3", "a": "e3", "*": ">", "+": ">", ")": ">", "$": ">"},
        "*": {"(": "<", "a": "<", "*": ">", "+": ">", ")": ">", "$": ">"},
        "+": {"(": "<", "a": "<", "*": "<", "+": ">", ")": ">", "$": ">"},
        "(": {"(": "<", "a": "<", "*": "<", "+": "<", ")": "=", "$": "e4"},
        "$": {"(": "<", "a": "<", "*": "<", "+": "<", ")": "e2", "$": "e1"},
    }

    grammar = read_grammar('operator_precedence_1.txt')
    parser = get_lr_parser(grammar, g0_opr_table)

    assert parser.parse(string) is False

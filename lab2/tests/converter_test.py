import pytest
import os

PARENT_DIR = os.path.dirname(os.getcwd())


def test_ll_rec_deleting1(read_grammar, get_converter):
    res = "E -> T A|T\nA -> + T A|+ T\nT -> F B|F\nB -> * F B|* F\nF -> a|( E )\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/left_recursion_1.txt')
    converter = get_converter(grammar)
    converter.delete_left_rec()

    assert str(converter.grammar()) == res


def test_ll_rec_deleting2(read_grammar, get_converter):
    res = "S -> A a|b\nA -> b d B|B|b d|eps\nB -> c B|a d B|c|a d\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/left_recursion_2.txt')
    converter = get_converter(grammar)
    converter.delete_left_rec()

    assert str(converter.grammar()) == res


def test_ll_rec_deleting3(read_grammar, get_converter):
    res = "A -> B C|a\nB -> C A D|a b D|C A|a b\nD -> C b D|C b\n" \
          "C -> a B E|a b D C B E|a b C B E|a E|a B|a b D C B|a b C B|a\nE -> A D C B E|A C B E|C E|A D C B|A C B|C\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/left_recursion_3.txt')
    converter = get_converter(grammar)
    converter.delete_left_rec()

    assert str(converter.grammar()) == res


def test_delete_eps_1(read_grammar, get_converter):
    res = "S -> a S b S|a S b|a b S|a b|b S a S|b S a|b a S|b a|eps\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/eps_1.txt')
    converter = get_converter(grammar)
    converter.delete_eps_moves()

    assert str(converter.grammar()) == res


def test_delete_eps_2(read_grammar, get_converter):
    res = "S -> A B C d|A B d|A C d|A d|B C d|B d|C d|d\nA -> a\nB -> A C|A|C\nC -> c\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/eps_2.txt')
    converter = get_converter(grammar)
    converter.delete_eps_moves()

    assert str(converter.grammar()) == res


def test_chomsky_form_1(read_grammar, get_converter):
    res = "S -> A S_1\nS_1 -> X S_2|b|A_1 X\nX -> A Y|A_1 Y\n" \
          "S_2 -> A_1 X|b\nY -> A_1 Y|A Y|A_2 A_2\nA -> a\nA_1 -> b\nA_2 -> c\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/chomsky_form_1.txt')
    converter = get_converter(grammar)
    converter.convert_to_normal_homskiy_form()

    assert str(converter.grammar()) == res


def test_chomsky_form_2(read_grammar, get_converter):
    res = "S -> C S_1|B A\nS_1 -> A B\nB -> A S|b\nA -> B A_1|a\nA_1 -> B B\nC -> a\n"

    grammar = read_grammar(PARENT_DIR + '/grammars/chomsky_form_2.txt')
    converter = get_converter(grammar)
    converter.convert_to_normal_homskiy_form()

    assert str(converter.grammar()) == res

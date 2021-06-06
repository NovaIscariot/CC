from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from queue import SimpleQueue, LifoQueue
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_next_char(char, union):
    next_char = chr(ord(char) + 1)
    syms = [x.mark for x in union]
    while next_char in syms:
        next_char = get_next_char(next_char, union)
    return next_char


class GrammarSymbol(object):
    def __init__(self, mark, idx=0):
        self.mark = mark
        self.idx = idx

    def __str__(self):
        res = f"{self.mark}"
        if self.idx:
            res += f"_{self.idx}"
        return res

    def __eq__(self, another):
        return self.mark == another.mark and self.idx == another.idx

    def get_next_idx(self):
        return GrammarSymbol(self.mark, self.idx + 1)


EPS_SYM = GrammarSymbol('eps')
FIN_SYM = GrammarSymbol('$')


class GrammarRule(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        if len(rhs) > 1:
            self.rhs = [x for x in rhs if x != EPS_SYM]
        else:
            self.rhs = rhs

    def __str__(self):
        res = f"{self.lhs} ->"
        for sym in self.rhs:
            res += f" {sym}"
        return res


class Grammar(object):
    def __init__(self, nonterminal, terminal, rules: List[GrammarRule], start_symbol) -> None:
        self.nonterminal = nonterminal
        self.terminal = terminal + [EPS_SYM]
        self.rules = rules
        self.start_symbol = start_symbol
        self.first_table = None
        self.follow_table = None

    def recursive_decent_parse(self, string):
        is_eval, num, tree = self.recursive_decent_parse_iter(self.start_symbol, string.split())
        return (is_eval and num == len(string.split())), tree

    def recursive_decent_parse_iter(self, nonterm: GrammarSymbol, string: List[str]):
        productions = [rule for rule in self.rules if rule.lhs == nonterm]
        productions.sort(key=lambda x: len(x.rhs), reverse=True)
        evaled = 0
        for rule in productions:
            idx_string = 0
            idx_rhs = 0
            cur_tree = CommonTree(rule.lhs)
            while idx_rhs < len(rule.rhs):
                if rule.rhs[0] == EPS_SYM:
                    return True, evaled, CommonTree(EPS_SYM)
                if not string:
                    break
                if rule.rhs[idx_rhs] in self.terminal:
                    if string[idx_string] == str(rule.rhs[idx_rhs]):
                        cur_tree.children.append(CommonTree(rule.rhs[idx_rhs]))
                        idx_rhs += 1
                        idx_string += 1
                    else:
                        break
                else:
                    is_eval, num_evaled, new_tree = self.recursive_decent_parse_iter(rule.rhs[idx_rhs],
                                                                                     string[idx_string:])
                    if is_eval:
                        idx_string += num_evaled
                        idx_rhs += 1
                        cur_tree.children.append(new_tree)
                    else:
                        break

            if idx_rhs == len(rule.rhs):
                evaled = idx_string
                return True, evaled, cur_tree

        return False, evaled, None


    def sort_rules(self):
        self.rules = sorted(self.rules, key=lambda x: self.nonterminal.index(x.lhs))

    def __str__(self):
        res = ""
        for nonterm in self.nonterminal:
            rules = [rule for rule in self.rules if rule.lhs == nonterm]
            res += f"{nonterm} -> "
            res += '|'.join([' '.join([str(x) for x in rule.rhs]) for rule in rules])
            res += '\n'
        return res

    def first(self, syms: List[GrammarSymbol]):
        res = []
        if not syms:
            return [EPS_SYM]
        if syms[0] in self.terminal:
            res.append(syms[0])
        else:
            out_rules = [rule for rule in self.rules if rule.lhs == syms[0]]
            eps_rules = [rule for rule in out_rules if  EPS_SYM in rule.rhs]

            for rule in out_rules:
                res.extend([x for x in self.first(rule.rhs) if x not in res])

            if eps_rules:
                res.extend([x for x in self.first(syms[1:]) if x not in res])
        return res

    def calc_first_table(self):
        first_sets = [list() for sym in self.nonterminal]

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                idx = self.nonterminal.index(rule.lhs)
                old_len = len(first_sets[idx])

                first_sets[idx].extend([x for x in self.first(rule.rhs) if x not in first_sets[idx]])

                if len(first_sets[idx]) > old_len:
                    changed = True

        self.first_table = first_sets
        return first_sets

    def calc_follow_table(self):
        follow_sets = [list() for sym in self.nonterminal]

        follow_sets[self.nonterminal.index(self.start_symbol)].append(FIN_SYM)

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                for idx in range(len(rule.rhs)):
                    if rule.rhs[idx] in self.nonterminal:
                        follow_sets_idx = self.nonterminal.index(rule.rhs[idx])
                        follow_len = len(follow_sets[follow_sets_idx])

                        rest_first = self.first(rule.rhs[idx+1:])

                        for sym in rest_first:
                            if sym == EPS_SYM:
                                lhs_follow = follow_sets[self.nonterminal.index(rule.lhs)]
                                for x in lhs_follow:
                                    if x not in follow_sets[follow_sets_idx]:
                                        follow_sets[follow_sets_idx].append(x)
                            elif sym not in follow_sets[follow_sets_idx]:
                                follow_sets[follow_sets_idx].append(sym)

                        if len(follow_sets[follow_sets_idx]) > follow_len:
                            changed = True

        self.follow_table = follow_sets
        return follow_sets


class GrammarBuilder(ABC):
    @property
    @abstractmethod
    def grammar(self) -> Grammar:
        pass

    @abstractmethod
    def get_grammar(self, arg) -> None:
        pass


class GrammarReader(GrammarBuilder):
    def __init__(self) -> None:
        self._grammar = None

    def reset(self) -> None:
        self._grammar = None

    def grammar(self) -> Grammar:
        return self._grammar

    def get_grammar(self, filename) -> None:
        with open(f"{BASE_DIR}\\grammars\\{filename}", "r") as f:
            nonterminal_count = int(f.readline())
            nonterminal = [GrammarSymbol(symb) for symb in f.readline().split()]

            terminal_count = int(f.readline())
            terminal = [GrammarSymbol(symb) for symb in f.readline().split()]

            rules_count = int(f.readline())
            rules = []
            for i in range(rules_count):
                lhs, rhs = f.readline().split(" -> ")
                lhs = [GrammarSymbol(symb) for symb in lhs.split()][0]
                rhs = [GrammarSymbol(symb) for symb in rhs.split()]
                rules.append(GrammarRule(lhs, rhs))
            rules = sorted(rules, key=lambda x: nonterminal.index(x.lhs))
            start_symbol = GrammarSymbol(f.readline())

        self._grammar = Grammar(nonterminal, terminal, rules, start_symbol)


class GrammarConverter(GrammarBuilder):
    def __init__(self) -> None:
        self._grammar = None

    def reset(self):
        self._grammar = None

    def grammar(self) -> Grammar:
        return self._grammar

    def get_grammar(self, grammar: Grammar) -> None:
        self._grammar = grammar

    def delete_left_rec(self):
        grammar = self._grammar

        new_rules = []
        new_nonterm = [x for x in grammar.nonterminal]
        # next char to @ - A
        next_char = GrammarSymbol(get_next_char('@', grammar.nonterminal + grammar.terminal))

        for nonterm in grammar.nonterminal:
            rules = [y for y in grammar.rules if y.lhs == nonterm]
            cleared_rules = []
            for rule in rules:
                q = SimpleQueue()
                q.put(rule)
                while not q.empty():
                    cur_rule = q.get()
                    if cur_rule.rhs[0] in grammar.terminal or (new_nonterm.index(cur_rule.rhs[0])
                                                               >= new_nonterm.index(cur_rule.lhs)):
                        cleared_rules.append(cur_rule)
                    else:
                        rules_to_insert = [y.rhs + cur_rule.rhs[1:] for y in new_rules if y.lhs == cur_rule.rhs[0]]
                        if not rules_to_insert:
                            rules_to_insert = [y.rhs + cur_rule.rhs[1:] for y in grammar.rules if
                                               y.lhs == cur_rule.rhs[0]]
                        for i in rules_to_insert:
                            q.put(GrammarRule(cur_rule.lhs, i))

            rules = cleared_rules

            rec_rules = [rule for rule in rules if nonterm == rule.rhs[0]]
            if rec_rules:
                com_rules = [rule for rule in rules if rule not in rec_rules]

                new_rules.extend([GrammarRule(nonterm, rule.rhs + [next_char]) for rule in com_rules])
                new_rules.extend([GrammarRule(nonterm, rule.rhs) for rule in com_rules])
                new_rules.extend([GrammarRule(next_char, rule.rhs[1:] + [next_char]) for rule in rec_rules])
                new_rules.extend([GrammarRule(next_char, rule.rhs[1:]) for rule in rec_rules])
                new_nonterm.insert(new_nonterm.index(nonterm) + 1, next_char)
                next_char = GrammarSymbol(get_next_char(next_char.mark, new_nonterm + grammar.terminal))
            else:
                new_rules.extend(rules)

        self._grammar.rules = new_rules
        self._grammar.nonterminal = new_nonterm

    def delete_long_moves(self):
        grammar = self._grammar

        new_rules = []
        new_nonterm = [x for x in grammar.nonterminal]

        q = SimpleQueue()
        for rule in grammar.rules:
            q.put(rule)
            while not q.empty():
                rule = q.get()
                next_char = rule.lhs.get_next_idx()
                if len(rule.rhs) < 3:
                    new_rules.append(rule)
                else:
                    new_nonterm.append(next_char)
                    new_rules.append(GrammarRule(rule.lhs, [rule.rhs[0], next_char]))
                    q.put(GrammarRule(next_char, rule.rhs[1:]))

        self._grammar.rules = new_rules
        self._grammar.nonterminal = new_nonterm

    def delete_eps_moves(self):
        grammar = self._grammar

        is_eps = {str(k): False for k in grammar.nonterminal}
        checked = {str(k): False for k in grammar.nonterminal}
        concerned_rules = {str(k): [i for i in range(len(grammar.rules)) if k in grammar.rules[i].rhs]
                           for k in grammar.nonterminal}
        q = SimpleQueue()
        counter = {}
        eps_nonterms = []
        for rule in grammar.rules:
            str_rule = str(rule)
            counter[str_rule] = 0
            for sym in rule.rhs:
                if sym in grammar.nonterminal:
                    counter[str_rule] += 1

            if not counter[str_rule] and EPS_SYM in rule.rhs:
                q.put(rule.lhs)
                eps_nonterms.append(rule.lhs)
                is_eps[str(rule.lhs)] = True
                checked[str(rule.lhs)] = True

        while not q.empty():
            nonterm = q.get()
            checked[str(nonterm)] = True
            for rule in concerned_rules[str(nonterm)]:
                rule = grammar.rules[rule]
                counter[str(rule)] -= 1
                if not counter[str(rule)] and not checked[str(rule.lhs)]:
                    is_eps[str(rule.lhs)] = True
                    for x in rule.rhs:
                        if x in grammar.terminal and x != EPS_SYM:
                            is_eps[str(rule.lhs)] = False
                    if is_eps[str(rule.lhs)]:
                        q.put(rule.lhs)

        new_rules = []
        for rule in grammar.rules:
            if EPS_SYM in rule.rhs:
                continue
            rules_for_extend = [GrammarRule(rule.lhs, [])]
            for sym in rule.rhs:
                if sym in grammar.nonterminal:
                    if is_eps[str(sym)]:
                        if is_eps[str(rule.lhs)] and grammar.nonterminal.index(rule.lhs) \
                                < grammar.nonterminal.index(sym) and sym not in eps_nonterms:
                            rules_for_extend = [GrammarRule(x.lhs, x.rhs + [sym]) for x in rules_for_extend]
                        else:
                            rules_for_extend = [GrammarRule(rule.lhs, x.rhs + [y]) for x in rules_for_extend
                                                for y in [sym, EPS_SYM]]
                    else:
                        rules_for_extend = [GrammarRule(x.lhs, x.rhs + [sym]) for x in rules_for_extend]
                else:
                    rules_for_extend = [GrammarRule(x.lhs, x.rhs + [sym]) for x in rules_for_extend]

            new_rules.extend(rules_for_extend)
        new_rules = [rule for rule in new_rules if len(rule.rhs) > 0 and EPS_SYM not in rule.rhs]

        start_rules = [rule for rule in grammar.rules if rule.lhs == grammar.start_symbol]
        for rule in start_rules:
            if EPS_SYM in rule.rhs:
                new_rules.append(rule)

        self._grammar.rules = new_rules

    def delete_chain_rules(self):
        grammar = self._grammar

        new_rules = []
        q = LifoQueue()
        for rule in grammar.rules[::-1]:
            q.put(rule)

        while not q.empty():
            rule = q.get()
            if len(rule.rhs) == 1 and rule.rhs[0] in grammar.nonterminal:
                if rule.lhs != rule.rhs[0]:
                    next_chain_rules = [x for x in grammar.rules if x.lhs == rule.rhs[0]]
                    for next_rule in next_chain_rules:
                        q.put(GrammarRule(rule.lhs, next_rule.rhs))
            else:
                new_rules.append(rule)

        self._grammar.rules = new_rules

    def delete_non_gen_rules(self):
        grammar = self._grammar

        is_gen = {str(k): False for k in grammar.nonterminal}
        checked = {str(k): False for k in grammar.nonterminal}
        concerned_rules = {str(k): [i for i in range(len(grammar.rules)) if k in grammar.rules[i].rhs]
                           for k in grammar.nonterminal}
        q = SimpleQueue()
        counter = {}
        for rule in grammar.rules:
            str_rule = str(rule)
            counter[str_rule] = 0
            for sym in rule.rhs:
                if sym in grammar.nonterminal:
                    counter[str_rule] += 1

            if not counter[str_rule]:
                q.put(rule.lhs)
                is_gen[str(rule.lhs)] = True
                checked[str(rule.lhs)] = True

        while not q.empty():
            nonterm = q.get()
            for rule in concerned_rules[str(nonterm)]:
                rule = grammar.rules[rule]
                for i in range(rule.rhs.count(nonterm)):
                    counter[str(rule)] -= 1
                if not counter[str(rule)] and not checked[str(rule.lhs)]:
                    q.put(rule.lhs)
                    checked[str(rule.lhs)] = True
                    is_gen[str(rule.lhs)] = True

        new_rules = []
        for rule in grammar.rules:
            not_get = False
            for sym in rule.rhs:
                if sym in grammar.nonterminal:
                    if not is_gen[str(sym)]:
                        not_get = True
            if not not_get:
                new_rules.append(rule)

        self._grammar.rules = new_rules

    def delete_unreachable_rules(self):
        grammar = self._grammar

        reachable = [grammar.start_symbol]
        q = SimpleQueue()
        q.put(grammar.start_symbol)

        while not q.empty():
            nonterm = q.get()
            for rule in grammar.rules:
                if nonterm == rule.lhs:
                    for x in rule.rhs:
                        if x in grammar.nonterminal and x not in reachable:
                            q.put(x)
                            reachable.append(x)

        new_rules = [rule for rule in grammar.rules if rule.lhs in reachable]

        self._grammar.rules = new_rules
        self._grammar.nonterminal = reachable

    def delete_useless_rules(self):
        self.delete_non_gen_rules()
        self.delete_unreachable_rules()

    def delete_two_det_rules(self):
        grammar = self._grammar

        new_rules = []
        new_nonterm = [x for x in grammar.nonterminal]
        term_map = dict()
        next_char = GrammarSymbol(get_next_char('@', grammar.nonterminal + grammar.terminal))

        for rule in grammar.rules:
            if len(rule.rhs) < 2:
                new_rules.append(rule)
            elif rule.rhs[0] not in grammar.terminal and rule.rhs[1] not in grammar.terminal:
                new_rules.append(rule)
            else:
                new_rhs = []
                for sym in rule.rhs:
                    if sym not in grammar.terminal:
                        new_rhs.append(sym)
                    else:
                        if not term_map.get(str(sym)):
                            term_map[str(sym)] = next_char
                            new_rules.append(GrammarRule(next_char, [sym]))
                            new_nonterm.append(next_char)
                            next_char = next_char.get_next_idx()
                        new_rhs.append(term_map[str(sym)])
                new_rules.append(GrammarRule(rule.lhs, new_rhs))

        self._grammar.rules = new_rules
        self._grammar.nonterminal = new_nonterm

    def convert_to_normal_homskiy_form(self):
        self.delete_long_moves()
        self.delete_eps_moves()
        self.delete_chain_rules()
        self.delete_useless_rules()
        self.delete_two_det_rules()


class GrammarParser(ABC):
    @abstractmethod
    def parse(self, sting):
        pass


class Tree(object):
    @abstractmethod
    def meta(self):
        pass


class CommonTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data

    def meta(self):
        return None


class ProgTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "PROG"

    def meta(self):
        return self.meta


class BlockTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "BLOCK"

    def meta(self):
        return self.meta


class OperatorListTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "OPERATOR_LIST"

    def meta(self):
        return self.meta


class OperatorTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "OPERATOR"

    def meta(self):
        return self.meta


class ExpressionTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "EXPRESSION"

    def meta(self):
        return self.meta


class SimpleExpressionTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "SIMPLE_EXPRESSION"

    def meta(self):
        return self.meta


class RelationTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "OPERATOR"

    def meta(self):
        return self.meta


class TermTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "EXPRESSION"

    def meta(self):
        return self.meta


class FactorTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "SIMPLE_EXPRESSION"

    def meta(self):
        return self.meta


class SymTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "OPERATOR"

    def meta(self):
        return self.meta


class SymOpTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "EXPRESSION"

    def meta(self):
        return self.meta


class MulOpTree(Tree):
    def __init__(self, data=None):
        self.children = []
        self.data = data
        self.meta = "SIMPLE_EXPRESSION"

    def meta(self):
        return self.meta


class RecursiveDecentParser(GrammarParser):
    def parse(self, string):
        return self.eval_prog(string)

    def eval_prog(self, string):
        res_tree = ProgTree('PROG')
        evaled, num, new_tree = self.eval_block(string.split())
        if evaled:
            res_tree.children.append(new_tree)
            if len(string.split()) == num:
                return True, res_tree
        return False, None

    def eval_block(self, string):
        if len(string) < 3:
            return False, 0, None
        if string[0] == 'begin' and string[-1] == 'end':
            evaled, ol_num, ol_tree = self.eval_operator_list(string[1:-1])
            if evaled:
                res_tree = BlockTree('BLOCK')
                res_tree.children.append(CommonTree('begin'))
                res_tree.children.append(ol_tree)
                res_tree.children.append(CommonTree('end'))
                return True, ol_num + 2, res_tree

        return False, 0, None

    def eval_operator_list(self, string):
        if len(string) < 1:
            return False, 0, None
        evaled, o_num, o_tree = self.eval_operator(string)
        if evaled:
            res_tree = OperatorListTree('OPERATOR_LIST')
            res_tree.children.append(o_tree)

            if len(string) > o_num:
                evaled, a_num, a_tree = self.eval_a(string[o_num:])
                if evaled:
                    res_tree.children.append(a_tree)
                return True, o_num + a_num, res_tree
            return True, o_num, res_tree

        return False, 0, None

    def eval_a(self, string):
        if len(string) < 2:
            return False, 0, None
        if string[0] == ';':
            evaled, o_num, o_tree = self.eval_operator(string[1:])
            if evaled:
                res_tree = OperatorListTree('A')
                res_tree.children.append(CommonTree(';'))
                res_tree.children.append(o_tree)

                if len(string) > o_num + 1:
                    evaled, a_num, a_tree = self.eval_a(string[o_num + 1:])
                    if evaled:
                        res_tree.children.append(a_tree)
                    return True, o_num + a_num + 1, res_tree
                return True, o_num + 1, res_tree

        return False, 0, None

    def eval_operator(self, string):
        if len(string) < 3:
            return False, 0, None
        if string[0] == 'id' and string[1] == '=':
            evaled, e_num, e_tree = self.eval_expression(string[2:])
            if evaled:
                res_tree = OperatorTree('OPERATOR')
                res_tree.children.append(CommonTree('id'))
                res_tree.children.append(CommonTree('='))
                res_tree.children.append(e_tree)
                return True, e_num + 2, res_tree

        return False, 0, None

    def eval_expression(self, string):
        if len(string) < 1:
            return False, 0, None
        evaled, se_num, se_tree = self.eval_simple_expression(string)
        if evaled:
            res_tree = ExpressionTree('EXPRESSION')
            res_tree.children.append(se_tree)
            if len(string) > se_num + 1:
                evaled, _, r_tree = self.eval_relation(string[se_num:])
                if evaled:
                    evaled, se1_num, se1_tree = self.eval_simple_expression(string[se_num + 1:])
                    if evaled:
                        res_tree.children.append(r_tree)
                        res_tree.children.append(se1_tree)
                    return True, se1_num + se_num + 1, res_tree
            return True, se_num, res_tree

        return False, 0, None

    def eval_simple_expression(self, string):
        if len(string) < 1:
            return False, 0, None
        res_tree = SimpleExpressionTree('SIMPLE_EXPRESSION')
        evaled, s_num, s_tree = self.eval_sym(string)
        if evaled:
            res_tree.children.append(s_tree)
        if len(string) > s_num:
            evaled, t_num, t_tree = self.eval_term(string[s_num:])
            if evaled and len(string) > s_num:
                res_tree.children.append(t_tree)
                if len(string) > t_num + s_num:
                    evaled, b_num, b_tree = self.eval_b(string[s_num + t_num:])
                    if evaled:
                        res_tree.children.append(b_tree)
                    return True, b_num + t_num + s_num, res_tree
                return True, t_num + s_num, res_tree

        return False, 0, None

    def eval_b(self, string):
        if len(string) < 2:
            return False, 0, None
        evaled, _, so_tree = self.eval_sym_op(string)
        if evaled:
            evaled, t_num, t_tree = self.eval_term(string[1:])
            if evaled:
                res_tree = SimpleExpressionTree('B')
                res_tree.children.append(so_tree)
                res_tree.children.append(t_tree)

                if len(string) > t_num + 1:
                    evaled, b_num, b_tree = self.eval_b(string[t_num + 1:])
                    if evaled:
                        res_tree.children.append(b_tree)
                    return True, b_num + t_num + 1, res_tree
                return True, t_num + 1, res_tree

        return False, 0, None

    def eval_relation(self, string):
        if len(string) < 1:
            return False, 0, None
        if string[0] == '=':
            return True, 1, CommonTree('=')
        if string[0] == '<>':
            return True, 1, CommonTree('<>')
        if string[0] == '<':
            return True, 1, CommonTree('<')
        if string[0] == '<=':
            return True, 1, CommonTree('<=')
        if string[0] == '>':
            return True, 1, CommonTree('>')
        if string[0] == '>=':
            return True, 1, CommonTree('>=')
        return False, 0, None

    def eval_term(self, string):
        if len(string) < 1:
            return False, 0, None
        evaled, f_num, f_tree = self.eval_factor(string)
        if evaled:
            res_tree = TermTree('TERM')
            res_tree.children.append(f_tree)

            if len(string) > f_num:
                evaled, c_num, c_tree = self.eval_c(string[f_num:])
                if evaled:
                    res_tree.children.append(c_tree)
                return True, c_num + f_num, res_tree
            return True, f_num, res_tree

        return False, 0, None

    def eval_c(self, string):
        if len(string) < 2:
            return False, 0, None
        evaled, _, mo_tree = self.eval_mul_op(string)
        if evaled:
            evaled, f_num, f_tree = self.eval_factor(string[1:])
            if evaled:
                res_tree = TermTree('C')
                res_tree.children.append(mo_tree)
                res_tree.children.append(f_tree)

                if len(string) > 2:
                    evaled, c_num, c_tree = self.eval_c(string[f_num + 1:])
                    if evaled:
                        res_tree.children.append(c_tree)
                    return True, f_num + c_num + 1, res_tree
                return True, f_num + 1, res_tree
        return False, 0, None

    def eval_factor(self, string):
        if len(string) < 1:
            return False, 0, None
        res_tree = FactorTree('FACTOR')
        if len(string) > 2:
            if string[0] == '(':
                evaled, num, se_tree = self.eval_simple_expression(string[1:])
                if evaled and string[num + 1] == ')':
                    res_tree.children.append(CommonTree('('))
                    res_tree.children.append(se_tree)
                    res_tree.children.append(CommonTree(')'))
                    return True, num + 2, res_tree
        if len(string) > 1:
            if string[0] == 'not':
                evaled, num, f_tree = self.eval_factor(string[1:])
                if evaled:
                    res_tree.children.append(CommonTree('not'))
                    res_tree.children.append(f_tree)
                    return True, num + 1, res_tree
        if string[0] == 'id':
            res_tree.children.append(CommonTree('id'))
            return True, 1, res_tree
        if string[0] == 'const':
            res_tree.children.append(CommonTree('const'))
            return True, 1, res_tree

        return False, 0, None

    def eval_sym(self, string):
        if len(string) < 1:
            return False, 0, None
        if string[0] == '+':
            return True, 1, CommonTree('+')
        if string[0] == '-':
            return True, 1, CommonTree('-')
        return False, 0, None

    def eval_sym_op(self, string):
        if len(string) < 1:
            return False, 0, None
        if string[0] == '+':
            return True, 1, CommonTree('+')
        if string[0] == '-':
            return True, 1, CommonTree('-')
        if string[0] == 'or':
            return True, 1, CommonTree('or')
        return False, 0, None

    def eval_mul_op(self, string):
        if len(string) < 1:
            return False, 0, None
        if string[0] == '*':
            return True, 1, CommonTree('*')
        if string[0] == '/':
            return True, 1, CommonTree('/')
        if string[0] == 'div':
            return True, 1, CommonTree('div')
        if string[0] == 'mod':
            return True, 1, CommonTree('mod')
        if string[0] == 'and':
            return True, 1, CommonTree('and')
        return False, 0, None

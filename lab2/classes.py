from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict
from queue import SimpleQueue, LifoQueue
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

    def eval(self, string: str):
        pass

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
        with open(f"{filename}", "r") as f:
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

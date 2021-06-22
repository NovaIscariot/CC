from abc import ABC, abstractmethod

#####
#
# Recursive decent parser for g1_pascal_extended grammar
# To write parser for your own grammar you need to write your own Tree classes for each nonterminal and write eval
#  functions.
#
####


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

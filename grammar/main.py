from grammar.classes import *
from print_tree import print_tree


class PrintTree(print_tree):
    def get_children(self, node):
        return node.children

    def get_node_str(self, node):
        return str(node.data)


def main():
    reader = GrammarReader()
    converter = GrammarConverter()
    reader.get_grammar('g1_pascal_extended.txt')
    converter.get_grammar(reader.grammar())
    choice = 1
    while choice:
        print('\nChoose action from menu below: ')
        print('   1) Print grammar')
        print('   2) Read new grammar from file')
        print('   3) Delete left recursion')
        print('   4) Convert to сhomsky normal form ')
        print('   5) Evaluate string (only bool res)')
        print('   6) Evaluate string (print tree)')
        print('   0) Exit from program')
        try:
            choice = int(input())
        except Exception:
            raise Exception('Wrong command')
        if choice == 1:
            converter.grammar().sort_rules()
            print(converter.grammar())
        if choice == 2:
            string = input("Enter grammar filename: ")
            reader.get_grammar(string)
            converter.get_grammar(reader.grammar())
        if choice == 3:
            converter.delete_left_rec()
            converter.delete_useless_rules()
        if choice == 4:
            converter.convert_to_normal_homskiy_form()
        if choice == 5:
            string = input("Enter string to evaluate: ")
            parser = RecursiveDecentParser()
            res, tree = parser.parse(string)
            if res:
                print("String evaluated successfully")
            else:
                print("String cannot be evaluated with grammar")
        if choice == 6:
            string = input("Enter string to evaluate: ")
            parser = RecursiveDecentParser()
            res, tree = parser.parse(string)
            if res:
                PrintTree(tree)
            else:
                print("String cannot be evaluated with grammar")


main()

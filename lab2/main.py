from lab2.classes import *


def main():
    reader = GrammarReader()
    converter = GrammarConverter()
    choice = 1
    while choice:
        print('\nChoose action from menu below: ')
        print('   1) Print grammar')
        print('   2) Read grammar from file')
        print('   3) Delete left recursion')
        print('   4) Convert to сhomsky normal form ')
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
        if choice == 4:
            converter.convert_to_normal_homskiy_form()


main()

import sys
from antlr4 import *
from sql_parser.gen.SQLiteLexer import SQLiteLexer
from sql_parser.gen.SQLiteParser import SQLiteParser
from sql_parser.gen.SQLiteListener import SQLiteListener


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = SQLiteLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = SQLiteParser(stream)
    tree = parser.parse()
    printer = SQLiteListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    print()


if __name__ == '__main__':
    main(sys.argv)



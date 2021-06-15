from grammar.classes import *
builder = GrammarReader()
converter = GrammarConverter()
builder.get_grammar("operator_precedence_2.txt")
a = builder.grammar()
parser = OperatorPrecedenceParser(a, g1_pascal_opr_table)
parser.parse("begin  id =  const  *  id ; id =  const + const  * const <= id ; id =  ( const + const )  * const <= id end", True)
print(parser.terminal_stack)

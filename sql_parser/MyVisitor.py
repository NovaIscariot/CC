from antlr4 import *
from sql_parser.config import *
from sql_parser.gen.SQLiteParser import SQLiteParser
from sql_parser.gen.SQLiteLexer import SQLiteLexer


class SQLiteVisitor(ParseTreeVisitor):
    def visitParse(self, node, recompiled=False):
        return node, recompiled

    def visitSql_stmt_list(self, node, recompiled):
        return node, recompiled

    def visitSql_stmt(self, node, recompiled):
        return node, recompiled

    def visitAnalyze_stmt(self, node, recompiled):
        return node, recompiled

    def visitAttach_stmt(self, node, recompiled):
        return node, recompiled

    def visitBegin_stmt(self, node, recompiled):
        return node, recompiled

    def visitCommit_stmt(self, node, recompiled):
        return node, recompiled

    def visitCompound_select_stmt(self, node, recompiled):
        return node, recompiled

    def visitDelete_stmt(self, node, recompiled):
        return node, recompiled

    def visitDelete_stmt_limited(self, node, recompiled):
        return node, recompiled

    def visitDetach_stmt(self, node, recompiled):
        return node, recompiled

    def visitFactored_select_stmt(self, node, recompiled):
        return node, recompiled

    def visitInsert_stmt(self, node, recompiled):
        return node, recompiled

    def visitPragma_stmt(self, node, recompiled):
        return node, recompiled

    def visitRelease_stmt(self, node, recompiled):
        return node, recompiled

    def visitRollback_stmt(self, node, recompiled):
        return node, recompiled

    def visitSavepoint_stmt(self, node, recompiled):
        return node, recompiled

    def visitSimple_select_stmt(self, node, recompiled):
        return node, recompiled

    def visitSelect_stmt(self, node, recompiled):
        return node, recompiled

    def visitSelect_or_values(self, node, recompiled):
        return node, recompiled

    def visitUpdate_stmt(self, node, recompiled):
        return node, recompiled

    def visitUpdate_stmt_limited(self, node, recompiled):
        return node, recompiled

    def visitVacuum_stmt(self, node, recompiled):
        return node, recompiled

    def visitType_name(self, node, recompiled):
        return node, recompiled

    def visitExpr(self, node, recompiled):
        return node, recompiled

    def visitRaise_function(self, node, recompiled):
        return node, recompiled

    def visitWith_clause(self, node, recompiled):
        return node, recompiled

    def visitQualified_table_name(self, node, recompiled):
        return node, recompiled

    def visitOrdering_term(self, node, recompiled):
        return node, recompiled

    def visitPragma_value(self, node, recompiled):
        return node, recompiled

    def visitCommon_table_expression(self, node, recompiled):
        return node, recompiled

    def visitResult_column(self, node, recompiled):
        return node, recompiled

    def visitTable_or_subquery(self, node, recompiled):
        return node, recompiled

    def visitJoin_clause(self, node, recompiled):
        return node, recompiled

    def visitJoin_operator(self, node, recompiled):
        return node, recompiled

    def visitJoin_constraint(self, node, recompiled):
        return node, recompiled

    def visitSelect_core(self, node, recompiled):
        text = node.getText()
        if '*' in text:
            text = text.replace("*", ",".join(TABLE_COLUMNS))
            lexer = SQLiteLexer(InputStream(text))
            stream = CommonTokenStream(lexer)
            parser = SQLiteParser(stream)
            node = parser.select_core()
            recompiled = True
        return node, recompiled

    def visitCompound_operator(self, node, recompiled):
        return node, recompiled

    def visitCte_table_name(self, node, recompiled):
        return node, recompiled

    def visitSigned_number(self, node, recompiled):
        return node, recompiled

    def visitLiteral_value(self, node, recompiled):
        return node, recompiled

    def visitUnary_operator(self, node, recompiled):
        return node, recompiled

    def visitError_message(self, node, recompiled):
        return node, recompiled

    def visitColumn_alias(self, node, recompiled):
        return node, recompiled

    def visitKeyword(self, node, recompiled):
        return node, recompiled

    def visitName(self, node, recompiled):
        return node, recompiled

    def visitFunction_name(self, node, recompiled):
        return node, recompiled

    def visitDatabase_name(self, node, recompiled):
        return node, recompiled

    def visitTable_name(self, node, recompiled):
        return node, recompiled

    def visitTable_or_index_name(self, node, recompiled):
        return node, recompiled

    def visitColumn_name(self, node, recompiled):
        return node, recompiled

    def visitCollation_name(self, node, recompiled):
        return node, recompiled

    def visitIndex_name(self, node, recompiled):
        return node, recompiled

    def visitPragma_name(self, node, recompiled):
        return node, recompiled

    def visitSavepoint_name(self, node, recompiled):
        return node, recompiled

    def visitTable_alias(self, node, recompiled):
        return node, recompiled

    def visitTransaction_name(self, node, recompiled):
        return node, recompiled

    def visitAny_name(self, node, recompiled):
        return node, recompiled


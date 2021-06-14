from antlr4 import *

if __name__ is not None and "." in __name__:
    from .SQLiteParser import SQLiteParser
else:
    from SQLiteParser import SQLiteParser


class SQLiteVisitor(ParseTreeVisitor):

    def visitParse(self, ctx: SQLiteParser.ParseContext):
        return self.visitChildren(ctx)

    def visitSql_stmt_list(self, ctx: SQLiteParser.Sql_stmt_listContext):
        return self.visitChildren(ctx)

    def visitSql_stmt(self, ctx: SQLiteParser.Sql_stmtContext):
        return self.visitChildren(ctx)

    def visitAnalyze_stmt(self, ctx: SQLiteParser.Analyze_stmtContext):
        return self.visitChildren(ctx)

    def visitAttach_stmt(self, ctx: SQLiteParser.Attach_stmtContext):
        return self.visitChildren(ctx)

    def visitBegin_stmt(self, ctx: SQLiteParser.Begin_stmtContext):
        return self.visitChildren(ctx)

    def visitCommit_stmt(self, ctx: SQLiteParser.Commit_stmtContext):
        return self.visitChildren(ctx)

    def visitCompound_select_stmt(self, ctx: SQLiteParser.Compound_select_stmtContext):
        return self.visitChildren(ctx)

    def visitDelete_stmt(self, ctx: SQLiteParser.Delete_stmtContext):
        return self.visitChildren(ctx)

    def visitDelete_stmt_limited(self, ctx: SQLiteParser.Delete_stmt_limitedContext):
        return self.visitChildren(ctx)

    def visitDetach_stmt(self, ctx: SQLiteParser.Detach_stmtContext):
        return self.visitChildren(ctx)

    def visitFactored_select_stmt(self, ctx: SQLiteParser.Factored_select_stmtContext):
        return self.visitChildren(ctx)

    def visitInsert_stmt(self, ctx: SQLiteParser.Insert_stmtContext):
        return self.visitChildren(ctx)

    def visitPragma_stmt(self, ctx: SQLiteParser.Pragma_stmtContext):
        return self.visitChildren(ctx)

    def visitRelease_stmt(self, ctx: SQLiteParser.Release_stmtContext):
        return self.visitChildren(ctx)

    def visitRollback_stmt(self, ctx: SQLiteParser.Rollback_stmtContext):
        return self.visitChildren(ctx)

    def visitSavepoint_stmt(self, ctx: SQLiteParser.Savepoint_stmtContext):
        return self.visitChildren(ctx)

    def visitSimple_select_stmt(self, ctx: SQLiteParser.Simple_select_stmtContext):
        return self.visitChildren(ctx)

    def visitSelect_stmt(self, ctx: SQLiteParser.Select_stmtContext):
        return self.visitChildren(ctx)

    def visitSelect_or_values(self, ctx: SQLiteParser.Select_or_valuesContext):
        return self.visitChildren(ctx)

    def visitUpdate_stmt(self, ctx: SQLiteParser.Update_stmtContext):
        return self.visitChildren(ctx)

    def visitUpdate_stmt_limited(self, ctx: SQLiteParser.Update_stmt_limitedContext):
        return self.visitChildren(ctx)

    def visitVacuum_stmt(self, ctx: SQLiteParser.Vacuum_stmtContext):
        return self.visitChildren(ctx)

    def visitType_name(self, ctx: SQLiteParser.Type_nameContext):
        return self.visitChildren(ctx)

    def visitExpr(self, ctx: SQLiteParser.ExprContext):
        return self.visitChildren(ctx)

    def visitRaise_function(self, ctx: SQLiteParser.Raise_functionContext):
        return self.visitChildren(ctx)

    def visitWith_clause(self, ctx: SQLiteParser.With_clauseContext):
        return self.visitChildren(ctx)

    def visitQualified_table_name(self, ctx: SQLiteParser.Qualified_table_nameContext):
        return self.visitChildren(ctx)

    def visitOrdering_term(self, ctx: SQLiteParser.Ordering_termContext):
        return self.visitChildren(ctx)

    def visitPragma_value(self, ctx: SQLiteParser.Pragma_valueContext):
        return self.visitChildren(ctx)

    def visitCommon_table_expression(self, ctx: SQLiteParser.Common_table_expressionContext):
        return self.visitChildren(ctx)

    def visitResult_column(self, ctx: SQLiteParser.Result_columnContext):
        return self.visitChildren(ctx)

    def visitTable_or_subquery(self, ctx: SQLiteParser.Table_or_subqueryContext):
        return self.visitChildren(ctx)

    def visitJoin_clause(self, ctx: SQLiteParser.Join_clauseContext):
        return self.visitChildren(ctx)

    def visitJoin_operator(self, ctx: SQLiteParser.Join_operatorContext):
        return self.visitChildren(ctx)

    def visitJoin_constraint(self, ctx: SQLiteParser.Join_constraintContext):
        return self.visitChildren(ctx)

    def visitSelect_core(self, ctx: SQLiteParser.Select_coreContext):
        return self.visitChildren(ctx)

    def visitCompound_operator(self, ctx: SQLiteParser.Compound_operatorContext):
        return self.visitChildren(ctx)

    def visitCte_table_name(self, ctx: SQLiteParser.Cte_table_nameContext):
        return self.visitChildren(ctx)

    def visitSigned_number(self, ctx: SQLiteParser.Signed_numberContext):
        return self.visitChildren(ctx)

    def visitLiteral_value(self, ctx: SQLiteParser.Literal_valueContext):
        return self.visitChildren(ctx)

    def visitUnary_operator(self, ctx: SQLiteParser.Unary_operatorContext):
        return self.visitChildren(ctx)

    def visitError_message(self, ctx: SQLiteParser.Error_messageContext):
        return self.visitChildren(ctx)

    def visitColumn_alias(self, ctx: SQLiteParser.Column_aliasContext):
        return self.visitChildren(ctx)

    def visitKeyword(self, ctx: SQLiteParser.KeywordContext):
        return self.visitChildren(ctx)

    def visitName(self, ctx: SQLiteParser.NameContext):
        return self.visitChildren(ctx)

    def visitFunction_name(self, ctx: SQLiteParser.Function_nameContext):
        return self.visitChildren(ctx)

    def visitDatabase_name(self, ctx: SQLiteParser.Database_nameContext):
        return self.visitChildren(ctx)

    def visitTable_name(self, ctx: SQLiteParser.Table_nameContext):
        return self.visitChildren(ctx)

    def visitTable_or_index_name(self, ctx: SQLiteParser.Table_or_index_nameContext):
        return self.visitChildren(ctx)

    def visitColumn_name(self, ctx: SQLiteParser.Column_nameContext):
        return self.visitChildren(ctx)

    def visitCollation_name(self, ctx: SQLiteParser.Collation_nameContext):
        return self.visitChildren(ctx)

    def visitIndex_name(self, ctx: SQLiteParser.Index_nameContext):
        return self.visitChildren(ctx)

    def visitPragma_name(self, ctx: SQLiteParser.Pragma_nameContext):
        return self.visitChildren(ctx)

    def visitSavepoint_name(self, ctx: SQLiteParser.Savepoint_nameContext):
        return self.visitChildren(ctx)

    def visitTable_alias(self, ctx: SQLiteParser.Table_aliasContext):
        return self.visitChildren(ctx)

    def visitTransaction_name(self, ctx: SQLiteParser.Transaction_nameContext):
        return self.visitChildren(ctx)

    def visitAny_name(self, ctx: SQLiteParser.Any_nameContext):
        return self.visitChildren(ctx)


del SQLiteParser

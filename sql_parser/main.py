from antlr4 import *
from sql_parser.gen.SQLiteLexer import SQLiteLexer
from sql_parser.gen.SQLiteParser import SQLiteParser
from sql_parser.MyVisitor import SQLiteVisitor
from graphviz import Digraph
import psycopg2
from .config import *

DIR = 'C:\\Users\\giena\\PycharmProjects\\CC\\sql_parser\\'


def main():
    source_query = '''
    SELECT "id", "C" FROM "T1";
    '''
    tree = sql_to_ast(source_query)
    # get_graph(tree, 'source.gv')
    tree = change_ast(tree)
    # get_graph(tree, 'recompiled.gv')
    query = ast_to_sql(tree)
    for row in query.split('; '):
        print(f"{row}")
    do_query(query)


def do_query(query):
    conn = psycopg2.connect(database="coursework", user="postgres", password="123456", host="localhost", port=5432)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    try:
        print(cur.fetchall())
    except Exception:
        pass


def sql_to_ast(query):
    lexer = SQLiteLexer(InputStream(query))
    stream = CommonTokenStream(lexer)
    parser = SQLiteParser(stream)
    tree = parser.parse()
    return tree


def get_graph(tree, filename='ast.gv'):
    f = Digraph('AST', filename=DIR+filename)
    ast_to_graph(tree, 1, f)
    f.view()
    pass


def ast_to_graph(tree, next_idx, graph):
    if tree.__class__.__name__ != TERMINAL_NODE_CLASS_NAME:
        graph.node(str(next_idx), tree.__class__.__name__)
        parent_idx = next_idx
        for child in tree.children:
            next_idx += 1
            graph.edge(str(parent_idx), str(next_idx))
            next_idx = ast_to_graph(child, next_idx, graph)
    else:
        graph.node(str(next_idx), tree.symbol.text)
    return next_idx + 1


def ast_to_sql(tree):
    if tree.__class__.__name__ != TERMINAL_NODE_CLASS_NAME:
        query = ""
        for child in tree.children:
            query += ast_to_sql(child)
        return query
    else:
        if tree.symbol.text != '<EOF>':
            return tree.symbol.text + " "
        return ""


def change_ast(tree):
    parse_node = tree
    stmt_list = tree.children[0].children
    new_stmt_list = []
    for stmt in stmt_list:
        visited, _ = visit_sql_stmt_context(stmt)
        if visited.__class__.__name__ == 'Sql_stmt_listContext':
            new_stmt_list.extend(visited.children)
        elif visited.__class__.__name__ == 'Sql_stmtContext':
            if visited.children[0]:
                if visited.children[0].__class__.__name__ == 'Sql_stmt_listContext':
                    new_stmt_list.extend(visited.children[0].children)
                else:
                    new_stmt_list.append(visited)
        else:
            new_stmt_list.append(visited)
    parse_node.children[0].children = new_stmt_list
    return parse_node


def get_parser(string):
    lexer = SQLiteLexer(InputStream(string))
    stream = CommonTokenStream(lexer)
    return SQLiteParser(stream)


def visit_sql_stmt_context(tree, recompiled=False):
    if tree.__class__.__name__ != TERMINAL_NODE_CLASS_NAME:
        if tree.children[0].__class__.__name__ == 'Insert_stmtContext':
            tree.children[0], _ = visit_insert_context(tree.children[0], recompiled)
        if tree.children[0].__class__.__name__ == 'Delete_stmtContext':
            tree.children[0], _ = visit_delete_context(tree.children[0], recompiled)
        if tree.children[0].__class__.__name__ == 'Update_stmtContext':
            tree.children[0], _ = visit_update_context(tree.children[0], recompiled)
        if tree.children[0].__class__.__name__ == 'Factored_select_stmtContext':
            tree.children[0].children[0], _ = visit_select_core_context(tree.children[0].children[0], recompiled)
        if tree.children[0].__class__.__name__ == 'Select_coreContext':
            tree.children[0], _ = visit_select_core_context(tree.children[0], recompiled)
    return tree, recompiled


def visit_select_core_context(tree, recompiled):
    text = tree.getText()
    # difficult case
    if '*' in text and SOURCE_TABLE_NAME in text:
        column_names = []
        for column in TABLE_COLUMNS:
            if column not in t1_to_t2_schema_map.keys():
                column_names.append(f"{RESULT_TABLE_NAME}.{column}")
            else:
                column_names.append(f"{RESULT_TABLE_DICT_NAME}.{column}")
        text = text.replace("*", ",".join(column_names))
        lexer = SQLiteLexer(InputStream(text))
        stream = CommonTokenStream(lexer)
        parser = SQLiteParser(stream)
        tree = parser.select_core()
        recompiled = True

    # analyze
    for token in text:
        if token in t1_to_t2_schema_map.keys():
            recompiled = True

    for idx in range(len(tree.children)):
        if tree.children[idx].__class__.__name__ == 'Result_columnContext':
            tree.children[idx], child_recompiled = visit_result_column_context(tree.children[idx], recompiled)
            recompiled |= child_recompiled
        if tree.children[idx].__class__.__name__ == 'Table_or_subqueryContext':
            tree.children[idx], child_recompiled = visit_table_or_subquery_context(tree.children[idx], recompiled)
            recompiled |= child_recompiled
    return tree, recompiled


def visit_result_column_context(tree, recompiled):
    if tree.children[0].__class__.__name__ == 'ExprContext':
        if tree.children[0].children[0].__class__.__name__ == 'Column_nameContext':
            tree.children[0].children[0], child_recompiled = visit_column_name(tree.children[0].children[0], recompiled)
            recompiled |= child_recompiled
        if tree.children[0].children[0].__class__.__name__ == 'Table_nameContext':
            tree.children[0].children[0], child_recompiled = visit_table_name(tree.children[0].children[0], recompiled)
            recompiled |= child_recompiled
    return tree, recompiled


def visit_column_name(tree, recompiled):
    column_name = tree.getText()
    if column_name in t1_to_t2_schema_map.keys():
        lexer = SQLiteLexer(InputStream(f"{RESULT_TABLE_DICT_NAME}.{column_name}"))
        recompiled = True
    else:
        lexer = SQLiteLexer(InputStream(f"{RESULT_TABLE_NAME}.{column_name}"))
    stream = CommonTokenStream(lexer)
    parser = SQLiteParser(stream)
    tree = parser.result_column()
    return tree, recompiled


def visit_table_name(tree, recompiled):
    table_name = tree.getText()
    if table_name == SOURCE_TABLE_NAME:
        parser = get_parser(RESULT_TABLE_NAME)
        tree = parser.table_name()
        recompiled = True
    return tree, recompiled


def visit_table_or_subquery_context(tree, recompiled):
    text = tree.getText()
    if text == SOURCE_TABLE_NAME:
        if recompiled:
            text = f"{RESULT_TABLE_NAME} JOIN {RESULT_TABLE_DICT_NAME} on {next(iter(t2_to_t1_schema_map))} =" \
                   f" {RESULT_TABLE_DICT_NAME}.\"id\""
            parser = get_parser(text)
            tree = parser.join_clause()
        else:
            tree.children[0], _ = visit_table_name(tree.children[0], recompiled)
    return tree, recompiled


def visit_insert_context(tree, recompiled):
    columns = []
    expressions = []
    for node in tree.children:
        if node.__class__.__name__ == 'Table_nameContext':
            if node.getText() != SOURCE_TABLE_NAME:
                return tree, recompiled
        if node.__class__.__name__ == 'Column_nameContext':
            columns.append(node.getText())
        if node.__class__.__name__ == 'ExprContext':
            expressions.append(node.getText())

    dict_columns = []
    dict_expressions = []
    target_columns = []
    target_expressions = []
    for i in range(len(columns)):
        if columns[i] in t1_to_t2_schema_map.keys():
            dict_columns.append(columns[i])
            dict_expressions.append(expressions[i])
        else:
            target_columns.append(columns[i])
            target_expressions.append(expressions[i])
    for i in t2_to_t1_schema_map.keys():
        target_columns.append(i)
        target_expressions.append(f'{RESULT_TABLE_DICT_NAME}."id"')

    dict_insert_stmt = f"INSERT INTO {RESULT_TABLE_DICT_NAME} ({', '.join(dict_columns)}) SELECT " \
            f"{', '.join(dict_expressions)} WHERE NOT EXISTS ( SELECT * FROM {RESULT_TABLE_DICT_NAME} " \
            f"WHERE {' and '.join([dict_columns[i] + ' = ' + dict_expressions[i] for i in range(len(dict_columns))])});"

    insert_stmt = f"INSERT INTO {RESULT_TABLE_NAME} ({', '.join(target_columns)})" \
                  f" SELECT {', '.join(target_expressions)} FROM {RESULT_TABLE_DICT_NAME} WHERE " \
            f"{' and '.join([dict_columns[i] + ' = ' + dict_expressions[i] for i in range(len(dict_columns))])}"

    lexer = SQLiteLexer(InputStream(dict_insert_stmt + insert_stmt))
    stream = CommonTokenStream(lexer)
    parser = SQLiteParser(stream)
    tree = parser.sql_stmt_list()
    tree.__setattr__("extend_smtm_list", True)
    return tree, recompiled


def visit_delete_context(tree, recompiled=False):
    for idx in range(len(tree.children)):
        if tree.children[idx].__class__.__name__ == 'Qualified_table_nameContext':
            if tree.children[idx].getText() != SOURCE_TABLE_NAME:
                return tree, recompiled
            else:
                lexer = SQLiteLexer(InputStream(RESULT_TABLE_NAME))
                stream = CommonTokenStream(lexer)
                parser = SQLiteParser(stream)
                tree.children[idx] = parser.qualified_table_name()
                recompiled = True
        if tree.children[idx].__class__.__name__ == 'ExprContext' and recompiled:
            tree.children[idx], recompiled = visit_expr_context(tree.children[idx], True)
    return tree, recompiled


def visit_expr_context(tree, recompiled):
    if len(tree.children) == 3:
        if tree.children[1].getText() == '=' and recompiled:
            left = tree.children[0].getText()
            right = tree.children[2].getText()
            if tree.children[0].children[0].__class__.__name__ == 'Column_nameContext' and \
                    left in t1_to_t2_schema_map.keys():
                lexer = SQLiteLexer(InputStream(
                    f"{RESULT_TABLE_NAME}.{t1_to_t2_schema_map[left]} in (SELECT \"id\" FROM {RESULT_TABLE_DICT_NAME} "
                    f"WHERE {left} = {right})"
                ))
                stream = CommonTokenStream(lexer)
                parser = SQLiteParser(stream)
                tree = parser.expr()
                return tree, True
    for idx in range(len(tree.children)):
        if tree.children[idx].__class__.__name__ == 'ExprContext' and recompiled:
            tree.children[idx], recompiled = visit_expr_context(tree.children[idx], recompiled)
        if tree.children[idx].__class__.__name__ == 'Column_nameContext':
            tree.children[idx], recompiled = visit_column_name(tree.children[idx], recompiled)
    return tree, recompiled


def visit_update_context(tree, recompiled):
    # analyze step
    table_to_update = RESULT_TABLE_NAME
    has_source_columns = False
    for idx in range(len(tree.children)):
        if tree.children[idx].__class__.__name__ == 'Column_nameContext':
            if tree.children[idx].getText() in t1_to_t2_schema_map.keys():
                table_to_update = RESULT_TABLE_DICT_NAME
        if tree.children[idx].__class__.__name__ == 'ExprContext':
            for token in tree.children[idx].getText():
                if token not in t1_to_t2_schema_map.keys():
                    has_source_columns = True
    if table_to_update == RESULT_TABLE_DICT_NAME and has_source_columns:
        print('This type of update is forbidden, you can not modify archived columns with source columns in expressions')
        return None, False
    # recompile step
    for idx in range(len(tree.children)):
        if tree.children[idx].__class__.__name__ == 'Qualified_table_nameContext':
            if tree.children[idx].getText() != SOURCE_TABLE_NAME:
                return tree, recompiled
            else:
                lexer = SQLiteLexer(InputStream(table_to_update))
                stream = CommonTokenStream(lexer)
                parser = SQLiteParser(stream)
                tree.children[idx] = parser.qualified_table_name()
                recompiled = True
        if tree.children[idx].__class__.__name__ == 'ExprContext':
            need_recompile = table_to_update == RESULT_TABLE_NAME
            tree.children[idx], child_recompiled = visit_expr_context(tree.children[idx], need_recompile)
            recompiled |= child_recompiled
    return tree, recompiled


if __name__ == '__main__':
    main()

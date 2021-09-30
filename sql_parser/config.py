TERMINAL_NODE_CLASS_NAME = 'TerminalNodeImpl'
SELECT_CORE_CONTEXT = 'Select_coreContext'
SOURCE_TABLE_NAME = '"T1"'
RESULT_TABLE_NAME = '"T2"'
RESULT_TABLE_DICT_NAME = '"T2dict"'


t1_to_t2_schema_map = {
    '"A"': '"D"',
    '"B"': '"D"'
}
t2_to_t1_schema_map = {
    '"D"': ['"A"', '"B"']
}
TABLE_COLUMNS = ['"id"', '"A"', '"B"', '"C"']

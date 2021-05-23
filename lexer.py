from ply import lex


reserved = {
        'def':'DEF',
        'return':'RETURN',
        'and':'AND',
        'or':'OR',
        'not':'NOT',
        'print':'PRINT',
        'while':'WHILE',
        'do':'DO',
        'if':'IF',
        'then':'THEN',
        'else':'ELSE',
        'break':'BREAK',
        'continue':'CONTINUE',
        'int':'INT',
        'float':'FLOAT',
        'string':'STR',
        'boolean':'BOOLEAN',
        'var':'VAR',
        'start':'START',
        'end':'END'
}

tokens = list(reserved.values()) + [
        'EQUALITY',
        'DOUBLE_POINT',
        'COMA',
        'OPEN_SKOBKA',
        'CLOSE_SKOBKA',
        'ASSiGNSYMBOL',
        'SEMI_COLON',
        'PLUS',
        'MINUS',
        'MULTIPLICATION',
        'DIV',
        'MORE',
        'LESS',
        'INTEGER',
        'FLOAT_NUM',
        'ID',
        'STRING'
        ]



t_DOUBLE_POINT = r'\:'
t_STRING = r'\'[^\'\n]*\''
t_EQUALITY = r'\='
t_PRINT = r'print'
t_OPEN_SKOBKA = r'\('
t_CLOSE_SKOBKA = r'\)'
t_COMA = r'\,'
t_ASSiGNSYMBOL = r'\:='
t_SEMI_COLON = r'\;'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLICATION = r'\*'
t_DIV = r'\/'
t_MORE = r'\>'
t_LESS = r'\<'
t_INTEGER = r'\d+'
t_FLOAT_NUM = r'\d+\.\d+'


def t_comment(t):
    r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
    pass


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)



t_ignore  = ' \t'


def t_error(t):
    print ("Недопустимый символ '%s'" % t.value[0])

lex.lex()

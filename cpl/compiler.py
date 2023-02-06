import ply.lex as lex
import ply.yacc as yacc
from cpl.compiler_fnc import *
from cpl.combine import *
from cpl.phi2pi import *

#################
tokens = (
    'IF', 'THEN', 'ELSE', 'FI', 'FROM', 'DO', 'LOOP', 'UNTIL', 'COBEGIN', 'COEND',
    'LOCAL', 'DELOCAL', 'SET', 'WAIT', 'SKIP', 'M',

    'EXCHANGE', 'COSEP', 'EQUAL',
    'PLUS', 'MINUS', 'XOR',
    'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',

    'LBRACK', 'RBRACK',

    'IDENT', 'NUMBER',
)

reserved = {
    'if': 'IF', 'then': 'THEN', 'else': 'ELSE', 'fi': 'FI',
    'from': 'FROM', 'do': 'DO', 'loop': 'LOOP', 'until': 'UNTIL',
    'cobegin': 'COBEGIN', 'coend': 'COEND',
    'call': 'CALL',
    'local': 'LOCAL', 'delocal': 'DELOCAL',
    'set': 'SET', 'wait': 'WAIT',
    'skip': 'SKIP',
    'M': 'M'
}

t_EXCHANGE = '<=>'
t_COSEP = '//'
t_EQUAL = '='
t_PLUS = '\+'
t_MINUS = '\-'
t_XOR = '\^'
t_EQ = '=='
t_NEQ = '!='
t_LT = '<'
t_GT = '>'
t_LE = '<='
t_GE = '>='
t_LBRACK = '\['
t_RBRACK = '\]'

t_ignore_COMMENT = '\#.*'
t_ignore = ' \t'


def t_IDENT(t):
    '[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t


def t_NUMBER(t):
    '[1-9][0-9]*|0'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("不正な文字「", t.value[0], "」")
    t.lexer.skip(1)


def p_error(p):
    if p:
        print("Syntax error")
        print(" lineno: ", end='')
        print(p.lineno)
        print(" type:   ", end='')
        print(p.type)
        print(" value:  ", end='')
        print(p.value)
        exit(1)
    else:
        print("Syntax error at EOF")


#################

#################
def p_program(p):
    """program : ss"""
    proc = sandwiched(p[1])
    p[0] = proc


def p_ss(p):
    """ss : s
          | ss s"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = series(p[1], p[2])


def p_s(p):
    """s : local
         | if
         | loop
         | co
         | update
         | exchange
         | excmem
         | set
         | wait
         | skip"""
    p[0] = p[1]


#################
def p_local(p):
    """local : LOCAL IDENT EQUAL expr ss DELOCAL IDENT EQUAL expr"""
    block_local = sole_inst(Local(p[2], p[4]))
    block_delocal = sole_inst(Delocal(p[7], p[9]))
    p[0] = series(series(block_local, p[5]), block_delocal)


def p_if(p):
    """if : IF expr THEN ss ELSE ss FI expr"""
    p[0] = sandwiched_if(IfBlock(p[2]), FiBlock(p[8]), p[4], p[6])


def p_loop(p):
    """loop : FROM expr DO ss LOOP ss UNTIL expr"""
    p[0] = sandwiched_loop(FromBlock(p[2]), UntilBlock(p[8]), p[4], p[6])


def p_co(p):
    """co : COBEGIN LBRACK vs RBRACK threads COEND LBRACK vs RBRACK"""
    p[0] = sandwiched_co(p[5])


def p_threads(p):
    """threads : ss
               | threads COSEP ss"""
    if len(p) == 2:
        p[0] = [sandwiched(p[1])]
    else:
        p[1].append(sandwiched(p[3]))
        p[0] = p[1]


#################

#################
def p_update(p):
    """update : r btype EQUAL expr"""
    subgraph = sole_inst(Update(p[1], p[2], p[4]))
    p[0] = subgraph


def p_exchange(p):
    """exchange : r EXCHANGE r"""
    subgraph = sole_inst(Exchange(p[1], p[3]))
    p[0] = subgraph


def p_excmem(p):
    """excmem : r EXCHANGE M LBRACK r RBRACK"""
    subgraph = sole_inst(Excmem(p[1], p[5]))
    p[0] = subgraph


def p_set(p):
    """set : SET IDENT"""
    p[0] = sole_inst(Set(p[2]))


def p_wait(p):
    """wait : WAIT IDENT"""
    p[0] = sole_inst(Wait(p[2]))


def p_skip(p):
    """skip : SKIP"""
    p[0] = sole_inst(Skip())


#################

#################
def p_expr(p):
    """expr : r btype r"""
    p[0] = Expr(p[1], p[2], p[3])


def p_btype(p):
    """btype : PLUS
             | MINUS
             | XOR
             | EQ
             | NEQ
             | LT
             | GT
             | LE
             | GE"""
    p[0] = Btype.str2btype(p[1])


def p_r(p):
    """r : IDENT
         | NUMBER"""
    p[0] = p[1]


def p_vs(p):
    """vs :
          | vs IDENT"""
    if len(p) == 1:
        p[0] = []
    else:
        p[1].append(p[2])
        p[0] = p[1]


#################
def compile(path: str):
    lexer = lex.lex(debug=0)
    yacc.yacc()
    data = open(path).read()
    return yacc.parse(data, lexer=lexer)

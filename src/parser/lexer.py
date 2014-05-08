import ply.lex as lex
import ply.yacc

tokens = ['LITERAL', 'AND', 'OR', 'NOT', 'IMPLICATION', 'EQUALS', 'GLOBAL', 'FUTURE', 'NEXT', 'UNTIL', 'RELEASE', 'WEAK_UNTIL']

t_ignore = ' /t'
t_AND = r'&'
t_OR = r'\|'
t_NOT = r'!'
t_IMPLICATION = r'->'
t_EQUALS = r'='
t_GLOBAL = r'G'
t_FUTURE = r'F'
t_NEXT = r'X'
t_UNTIL = r'U'
t_RELEASE = r'R'
t_WEAK_UNTIL = r'W'
t_LITERAL = r'[a-zA-Z_][a-zA-Z0-9_]*'

# Error handling rule
def t_error(t):
		print "Illegal character '%s'" % t.value[0]
		t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

import ply.lex as lex
import ply.yacc
import re


class BaseSymbolSet(object):
    '''
    base symbol class
    '''

    symbols = {'AND' : r'&',
        'OR' : r'|',
        'GLOBALLY' : r'G',
        'EVENTUALLY' : r'F',
        'NEXT' : r'X',
        'UNTIL' : r'U',
        'RELEASE' : r'R',
        'WEAK_UNTIL' : r'W',
        'IMPLICATION' : r'->',
        'EQUALITY' : r'<->',
        'NOT' : r'!',
        'TRUE' : r'1',
        'FALSE' : r'0'}

class Lexer(object):
    tokens = ['LITERAL', 'AND', 'OR', 'NOT', 'IMPLICATION', 'EQUALITY',
        'GLOBALLY', 'EVENTUALLY', 'NEXT', 'UNTIL', 'RELEASE',
        'WEAK_UNTIL', 'LPAREN', 'RPAREN', 'TRUE', 'FALSE']


# Error handling rule
    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # No return value. Token discarded
    def t_error(self, t):
            print "Illegal character '%s'" % t.value[0]
            t.lexer.skip(1)


    def __init__(self, symbolSetCls = BaseSymbolSet):

        self.t_ignore = ' /t'
        self.t_AND = symbolSetCls.symbols['AND']
        self.t_OR =  re.escape(symbolSetCls.symbols['OR'])
        self.t_NOT = symbolSetCls.symbols['NOT']
        self.t_IMPLICATION = symbolSetCls.symbols['IMPLICATION']
        self.t_EQUALITY = symbolSetCls.symbols['EQUALITY']
        self.t_GLOBALLY= symbolSetCls.symbols['GLOBALLY']
        self.t_EVENTUALLY= symbolSetCls.symbols['EVENTUALLY']
        self.t_NEXT = symbolSetCls.symbols['NEXT']
        self.t_UNTIL = symbolSetCls.symbols['UNTIL']
        self.t_RELEASE = symbolSetCls.symbols['RELEASE']
        self.t_WEAK_UNTIL = symbolSetCls.symbols['WEAK_UNTIL']
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_TRUE = symbolSetCls.symbols['TRUE']
        self.t_FALSE = symbolSetCls.symbols['FALSE']
        self.t_LITERAL = r'[a-zA-Z_][a-zA-Z0-9_]*'

        self.__build()

# Build the lexer
    def __build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)




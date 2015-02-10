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
        'FALSE' : r'0',
        'LPAREN' : r'\(',
        'RPAREN' : r'\)'
        }

class Lexer(object):
    tokens = ['LITERAL', 'AND', 'OR', 'NOT', 'IMPLICATION', 'EQUALITY',
        'GLOBALLY', 'EVENTUALLY', 'NEXT', 'UNTIL', 'RELEASE',
        'WEAK_UNTIL', 'LPAREN', 'RPAREN', 'TRUE', 'FALSE']


    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Error handling rule
    # No return value. Token discarded
    def t_error(self, t):
            print "Illegal character '%s'" % t.value[0]
            t.lexer.skip(1)
            #raise IllegalValueError(t.value[0])



    def __init__(self, symbol_set_cls = BaseSymbolSet):

        self.t_ignore = ' \t'
        self.t_AND = symbol_set_cls.symbols['AND']
        self.t_OR =  re.escape(symbol_set_cls.symbols['OR'])
        self.t_NOT = symbol_set_cls.symbols['NOT']
        self.t_IMPLICATION = symbol_set_cls.symbols['IMPLICATION']
        self.t_EQUALITY = symbol_set_cls.symbols['EQUALITY']
        self.t_GLOBALLY= symbol_set_cls.symbols['GLOBALLY']
        self.t_EVENTUALLY= symbol_set_cls.symbols['EVENTUALLY']
        self.t_NEXT = symbol_set_cls.symbols['NEXT']
        self.t_UNTIL = symbol_set_cls.symbols['UNTIL']
        self.t_RELEASE = symbol_set_cls.symbols['RELEASE']
        self.t_WEAK_UNTIL = symbol_set_cls.symbols['WEAK_UNTIL']
        self.t_LPAREN = symbol_set_cls.symbols['LPAREN']
        self.t_RPAREN = symbol_set_cls.symbols['RPAREN']
        self.t_TRUE = symbol_set_cls.symbols['TRUE']
        self.t_FALSE = symbol_set_cls.symbols['FALSE']
        self.t_LITERAL = r'[a-z_][a-z0-9_]*'

        self.__build()

# Build the lexer
    def __build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


#class IllegalValueError(Exception):
#    pass

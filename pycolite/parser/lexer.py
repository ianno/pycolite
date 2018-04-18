import ply.lex as lex
import re

from pycolite import LOG

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
        'DOUBLE_IMPLICATION' : r'<->',
        'EQUALITY' : r'=',
        'NOT' : r'!',
        'TRUE' : r'true',
        'FALSE' : r'false',
        'LPAREN' : r'(',
        'RPAREN' : r')',
        'GE' : r'>',
        'GEQ' : r'>=',
        'LE' : r'<',
        'LEQ' : r'<=',
        'ADD' : r'+',
        'SUB' : r'-',
        'MUL' : r'*',
        'DIV' : r'/'
        }

class Lexer(object):


    tokens = ['LITERAL', 'CONSTANT', 'AND', 'OR',
        'NOT', 'IMPLICATION', 'DOUBLE_IMPLICATION', 'EQUALITY',
        'GLOBALLY', 'EVENTUALLY', 'NEXT', 'UNTIL', 'RELEASE',
        'WEAK_UNTIL', 'LPAREN', 'RPAREN', 'TRUE', 'FALSE',
        'GE', 'GEQ', 'LE', 'LEQ', 'ADD', 'SUB', 'MUL', 'DIV']


    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Error handling rule
    # No return value. Token discarded
    def t_error(self, t):
        LOG.debug("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        #raise IllegalValueError(t.value[0])

    def t_LITERAL(self, t):
        r'[a-z_][a-zA-Z0-9_]*'
        #check for illegal values
        t.type = self.reserved.get(t.value, 'LITERAL')
        return t

    def t_CONSTANT(self, t):
        r'\d+'
        t.type = self.reserved.get(t.value, 'CONSTANT')
        return t

    def __init__(self, symbol_set_cls=BaseSymbolSet):

        self.symbol_set_cls = symbol_set_cls
        self.reserved = {key:value for (value,key) in
                         symbol_set_cls.symbols.items()}

        self.t_ignore = " \t\n"
        self.t_AND = symbol_set_cls.symbols['AND']
        self.t_OR =  re.escape(symbol_set_cls.symbols['OR'])
        self.t_NOT = symbol_set_cls.symbols['NOT']
        self.t_IMPLICATION = symbol_set_cls.symbols['IMPLICATION']
        self.t_DOUBLE_IMPLICATION = symbol_set_cls.symbols['DOUBLE_IMPLICATION']
        self.t_EQUALITY = re.escape(symbol_set_cls.symbols['EQUALITY'])
        self.t_GLOBALLY= symbol_set_cls.symbols['GLOBALLY']
        self.t_EVENTUALLY= symbol_set_cls.symbols['EVENTUALLY']
        self.t_NEXT = symbol_set_cls.symbols['NEXT']
        self.t_UNTIL = symbol_set_cls.symbols['UNTIL']
        self.t_RELEASE = symbol_set_cls.symbols['RELEASE']
        self.t_WEAK_UNTIL = symbol_set_cls.symbols['WEAK_UNTIL']
        self.t_LPAREN = re.escape(symbol_set_cls.symbols['LPAREN'])
        self.t_RPAREN = re.escape(symbol_set_cls.symbols['RPAREN'])
        self.t_TRUE = symbol_set_cls.symbols['TRUE']
        self.t_FALSE = symbol_set_cls.symbols['FALSE']
        self.t_GE = re.escape(symbol_set_cls.symbols['GE'])
        self.t_GEQ = re.escape(symbol_set_cls.symbols['GEQ'])
        self.t_LE = re.escape(symbol_set_cls.symbols['LE'])
        self.t_LEQ = re.escape(symbol_set_cls.symbols['LEQ'])
        self.t_ADD = re.escape(symbol_set_cls.symbols['ADD'])
        self.t_SUB = re.escape(symbol_set_cls.symbols['SUB'])
        self.t_MUL = re.escape(symbol_set_cls.symbols['MUL'])
        self.t_DIV = re.escape(symbol_set_cls.symbols['DIV'])
        #self.t_LITERAL = r'[a-z_][a-zA-Z0-9_]*'

        self.__build()

# Build the lexer
    def __build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)


#class IllegalValueError(Exception):
#    pass

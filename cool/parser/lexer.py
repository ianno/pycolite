import ply.lex as lex
import re

BASE_SYMBOL_SET = {
    'AND' : '&',
    'OR' : '|',
    'GLOBALLY' : 'G',
    'EVENTUALLY' : 'F',
    'NEXT' : 'X',
    'UNTIL' : 'U',
    'RELEASE' : 'R',
    'WEAK_UNTIL' : 'W',
    'IMPLIES' : '->',
    'EQUALS' : '<->',
    'NOT' : '!',
    'TRUE' : '1',
    'FALSE' : '0'
}

class Lexer(object):
    tokens = ['LITERAL', 'AND', 'OR', 'NOT', 'IMPLIES', 'EQUALS', 
        'GLOBALLY', 'EVENTUALLY', 'NEXT', 'UNTIL', 'RELEASE', 
        'WEAK_UNTIL', 'LPAREN', 'RPAREN', 'TRUE', 'FALSE'] 


# Error handling rule
    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)


    def __init__(self, symbolSet = BASE_SYMBOL_SET):

        self.symbolSet = symbolSet
        
        self.t_ignore = ' \t\n\r\f\v' 
        self.t_AND = re.escape(symbolSet['AND']) 
        self.t_OR =  re.escape(symbolSet['OR'])
        self.t_NOT = re.escape(symbolSet['NOT'])
        self.t_IMPLIES = re.escape(symbolSet['IMPLIES'])
        self.t_EQUALS = re.escape(symbolSet['EQUALS'])
        self.t_GLOBALLY= re.escape(symbolSet['GLOBALLY'])
        self.t_EVENTUALLY= re.escape(symbolSet['EVENTUALLY'])
        self.t_NEXT = re.escape(symbolSet['NEXT'])
        self.t_UNTIL = re.escape(symbolSet['UNTIL'])
        self.t_RELEASE = re.escape(symbolSet['RELEASE'])
        self.t_WEAK_UNTIL = re.escape(symbolSet['WEAK_UNTIL'])
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_TRUE = re.escape(symbolSet['TRUE'])
        self.t_FALSE = re.escape(symbolSet['FALSE'])
        self.t_LITERAL = r'[a-z_][a-zA-Z0-9_]*'
        self.t_ignore_COMMENT = r'\#.*'
        
        self.lexer = None
        self.__build()
        

# Build the lexer
    def __build(self,**kwargs):
        self.lexer = lex.lex(optimize=1, module=self, **kwargs)




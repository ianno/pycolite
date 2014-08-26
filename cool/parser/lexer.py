import ply.lex as lex


class BaseSymbolSet(object):
    '''
    base symbol class
    '''

    AND = r'&'
    OR = r'\|'
    GLOBALLY = r'G'
    EVENTUALLY = r'F'
    NEXT = r'X'
    UNTIL = r'U'
    RELEASE = r'R'
    WEAK_UNTIL = r'W'
    IMPLICATION = r'->'
    EQUALS = r'<->'
    NOT = r'!'
    TRUE = r'1'
    FALSE = r'0'

class Lexer(object):
    tokens = ['LITERAL', 'AND', 'OR', 'NOT', 'IMPLICATION', 'EQUALS', 
        'GLOBALLY', 'EVENTUALLY', 'NEXT', 'UNTIL', 'RELEASE', 
        'WEAK_UNTIL', 'LPAREN', 'RPAREN', 'TRUE', 'FALSE'] 


# Error handling rule
    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)


    def __init__(self, symbolSetCls = BaseSymbolSet):

        self.t_ignore = ' /t' 
        self.t_AND = symbolSetCls.AND 
        self.t_OR =  symbolSetCls.OR
        self.t_NOT = symbolSetCls.NOT
        self.t_IMPLICATION = symbolSetCls.IMPLICATION
        self.t_EQUALS = symbolSetCls.EQUALS
        self.t_GLOBALLY= symbolSetCls.GLOBALLY
        self.t_EVENTUALLY= symbolSetCls.EVENTUALLY
        self.t_NEXT = symbolSetCls.NEXT
        self.t_UNTIL = symbolSetCls.UNTIL
        self.t_RELEASE = symbolSetCls.RELEASE
        self.t_WEAK_UNTIL = symbolSetCls.WEAK_UNTIL
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_TRUE = symbolSetCls.TRUE
        self.t_FALSE = symbolSetCls.FALSE
        self.t_LITERAL = r'[a-zA-Z_][a-zA-Z0-9_]*'
        self.t_ignore_COMMENT = r'\#.*'
        
        self.lexer = None
        self.__build()

# Build the lexer
    def __build(self,**kwargs):
        self.lexer = lex.lex(optimize=1, module=self, **kwargs)




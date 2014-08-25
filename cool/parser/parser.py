import ply.yacc as yacc
import lexer


        
class Parser(object):

    precedence = (
        ('left', 'IMPLICATION', 'EQUALS'),
        ('left', 'AND', 'OR'),
        ('left', 'UNTIL', 'RELEASE', 'WEAK_UNTIL'),   
        ('left', 'GLOBALLY', 'EVENTUALLY'),
        ('right', 'NOT', 'NEXT'),
    )


    def __init__(self):
        self.lexer = None
        
        #tokens have to be always the same. Lexers have to inherit from Lexer class
        self.tokens = lexer.Lexer.tokens
        
        self.__build()

#     def p_expr(self, p):
#         '''expr : expr AND expr
#                 | expr OR expr
#                 | NOT expr
#                 | expr IMPLICATION expr
#                 | expr EQUALS expr
#                 | GLOBALLY expr
#                 | EVENTUALLY expr
#                 | NEXT expr
#                 | expr UNTIL expr
#                 | expr RELEASE expr
#                 | expr WEAK_UNTIL expr
#                 | TRUE
#                 | FALSE
#                 | COMMENT
#                 | LITERAL
#                 | LPAREN expr RPAREN '''
# 
# 
#         print p[1]
#         #print p[2]
#         #print p[3]

    def p_error(self, p):
        print 'Error'
        print p
        

# Build the parser
    def __build(self,**kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, str, lexer = lexer.Lexer(), **kwargs):
        ''' s '''
        self.lexer = lexer
        return self.parser.parse(str, lexer = self.lexer.lexer, **kwargs)




if __name__ == '__main__':
    yacc_i = Parser()
    variable = yacc_i.parse("hello | boob -> h & Xe & (v|e & (sss -> q)) #fiu")
    print variable 
    
    

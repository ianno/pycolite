from cool import formula
import lexer
import ply.yacc as yacc


class Parser(object):

    precedence = formula.PRECEDENCE_TUPLE


    def __init__(self):
        self.lexer = None
        
        #tokens have to be always the same. Lexers have to inherit from Lexer class
        self.tokens = lexer.Lexer.tokens
        
        #self.formula = None
        
        self.__build()

    def p_error(self, p):
        print 'Error'
        print p
        
    def p_and(self, p):
        '''expr : expr AND expr'''
        p[0] = formula.Conjunction(p[1], p[3])
        
    def p_or(self, p):
        '''expr : expr OR expr'''
        p[0] = formula.Disjunction(p[1], p[3])
        
    def p_not(self, p):
        '''expr : NOT expr'''
        p[0] = formula.Negation(p[2])
        
    def p_implies(self, p):
        '''expr : expr IMPLIES expr'''
        p[0] = formula.Implication(p[1], p[3])
        
    def p_equals(self, p):
        '''expr : expr EQUALS expr'''
        p[0] = formula.Equivalence(p[1], p[3])
        
    def p_globally(self, p):
        '''expr : GLOBALLY expr'''
        p[0] = formula.Globally(p[2])
        
    def p_eventually(self, p):
        '''expr : EVENTUALLY expr'''
        p[0] = formula.Eventually(p[2])
        
    def p_next(self, p):
        '''expr : NEXT expr'''
        p[0] = formula.Next(p[2])
        
    def p_until(self, p):
        '''expr : expr UNTIL expr'''
        raise NotImplementedError
        
    def p_release(self, p):
        '''expr : expr RELEASE expr'''
        raise NotImplementedError
        
    def p_weak_until(self, p):
        '''expr : expr WEAK_UNTIL expr'''
        raise NotImplementedError
        
    def p_true(self, p):
        '''expr : TRUE'''
        p[0] = p[1]
        
    def p_false(self, p):
        '''expr : FALSE'''
        p[0] = p[1]
        
    def p_literal(self, p):
        '''expr : LITERAL'''
        #add more here on literals
        p[0] = formula.Literal(p[1])
        #print p[1]
        
    def p_parenthesis(self, p):
        '''expr : LPAREN expr RPAREN'''
        p[0] = p[2]
        

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
    print variable.generate()
    
    

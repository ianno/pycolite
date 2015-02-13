from .. import formula
import lexer
import ply.yacc as yacc

import logging
LOG = logging.getLogger()


class Parser(object):

    precedence = formula.PRECEDENCE_TUPLE


    def __init__(self):
        self.lexer = None

        #tokens have to be always the same. Lexers have to inherit from Lexer class
        self.tokens = lexer.Lexer.tokens

        #self.formula = None

        self.__build()

    def p_error(self, p):
        LOG.debug('Error')
        print p
        raise GeneralError(p)

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
        '''expr : expr IMPLICATION expr'''
        p[0] = formula.Implication(p[1], p[3])

    def p_equals(self, p):
        '''expr : expr EQUALITY expr'''
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
        p[0] = formula.TrueFormula()

    def p_false(self, p):
        '''expr : FALSE'''
        p[0] = formula.FalseFormula()

    def p_literal(self, p):
        '''expr : LITERAL'''
        #add more here on literals
        p[0] = formula.Literal(p[1], self.context)

    def p_parenthesis(self, p):
        '''expr : LPAREN expr RPAREN'''
        p[0] = p[2]


# Build the parser
    def __build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, string, context = None, symbol_set_cls = lexer.BaseSymbolSet, **kwargs):
        ''' s '''

        self.lexer = lexer.Lexer(symbol_set_cls)
        self.context = context

        return self.parser.parse(string, lexer = self.lexer.lexer, **kwargs)


#define a module-level parser object
LTL_PARSER = Parser()


class GeneralError(Exception):
    '''
    Exception to be raised in case of a generic
    parsing error
    '''
    pass



if __name__ == '__main__':
    yacc_i = Parser()
    variable = yacc_i.parse("G(hello |   test) -> h & Xe & (v|e & (sss -> q)) #fiu")
    print variable
    print variable.generate()



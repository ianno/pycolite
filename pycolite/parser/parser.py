from pycolite import formula
from pycolite.parser import lexer
import ply.yacc as yacc

from pycolite import LOG


class Parser(object):

    precedence = formula.PRECEDENCE_TUPLE


    def __init__(self):
        self.lexer = None

        #tokens have to be always the same. Lexers have to inherit from Lexer class
        self.tokens = lexer.Lexer.tokens

        #self.formula = None

        self.__build()

    def p_error(self, p):
        #LOG.debug('Error')
        print p.value
        raise GeneralError(p)

    def p_expr_and(self, p):
        '''expr : expr AND expr'''
        p[0] = formula.Conjunction(p[1], p[3])

    def p_expr_or(self, p):
        '''expr : expr OR expr'''
        #LOG.debug(p[1])
        p[0] = formula.Disjunction(p[1], p[3])

    def p_expr_not(self, p):
        '''expr : NOT expr'''
        p[0] = formula.Negation(p[2])

    def p_expr_implies(self, p):
        '''expr : expr IMPLICATION expr'''
        p[0] = formula.Implication(p[1], p[3])

    def p_expr_iff(self, p):
        '''expr : expr DOUBLE_IMPLICATION expr'''
        p[0] = formula.DoubleImplication(p[1], p[3])

    def p_expr_equals(self, p):
        '''expr : expr EQUALITY expr'''
        p[0] = formula.Equivalence(p[1], p[3])

    def p_expr_globally(self, p):
        '''expr : GLOBALLY expr'''

        #LOG.debug(p[2])
        p[0] = formula.Globally(p[2])

    def p_expr_eventually(self, p):
        '''expr : EVENTUALLY expr'''
        p[0] = formula.Eventually(p[2])

    def p_expr_next(self, p):
        '''expr : NEXT expr'''
        p[0] = formula.Next(p[2])

    def p_expr_until(self, p):
        '''expr : expr UNTIL expr'''
        p[0] = formula.Until(p[1], p[3])

    def p_expr_release(self, p):
        '''expr : expr RELEASE expr'''
        raise NotImplementedError

    def p_expr_weak_until(self, p):
        '''expr : expr WEAK_UNTIL expr'''
        raise NotImplementedError

    def p_expr_prop(self, p):
        '''expr : prop'''
        p[0] = p[1]

    def p_prop_true(self, p):
        '''prop : TRUE'''
        p[0] = formula.TrueFormula()

    def p_prop_false(self, p):
        '''prop : FALSE'''
        p[0] = formula.FalseFormula()

    def p_expr_parenthesis(self, p):
        '''expr : LPAREN expr RPAREN'''
        p[0] = p[2]

    def p_prop_parenthesis(self, p):
        '''prop : LPAREN prop RPAREN'''
        p[0] = p[2]

    def p_prop_ge(self, p):
        '''prop : prop GE prop'''
        p[0] = formula.Ge(p[1], p[3])

    def p_prop_geq(self, p):
        '''prop : prop GEQ prop'''
        #LOG.debug(p[1])
        #LOG.debug(p[3])
        p[0] = formula.Geq(p[1], p[3])

    def p_prop_le(self, p):
        '''prop : prop LE prop'''
        p[0] = formula.Le(p[1], p[3])

    def p_prop_leq(self, p):
        '''prop : prop LEQ prop'''
        p[0] = formula.Leq(p[1], p[3])

    def p_prop_add(self, p):
        '''prop : prop ADD prop'''
        p[0] = formula.Addition(p[1], p[3])

    def p_prop_sub(self, p):
        '''prop : prop SUB prop'''
        # LOG.debug(len(p))
        # LOG.debug(p[0])
        p[0] = formula.Subtraction(p[1], p[3])

    def p_prop_mul(self, p):
        '''prop : prop MUL prop'''
        p[0] = formula.Multiplication(p[1], p[3])

    def p_prop_div(self, p):
        '''prop : prop DIV prop'''
        p[0] = formula.Division(p[1], p[3])

    def p_prop_unary(self, p):
        '''prop : unary'''
        p[0] = p[1]

    def p_unary_pos(self, p):
        '''unary : CONSTANT'''
        #print p[1]
        # LOG.debug(p[1])
        try:
            val = int(p[1])
        except ValueError:
            val = float(p[1])
        p[0] = formula.Constant(val)

    def p_unary_neg(self, p):
        '''unary : SUB CONSTANT'''
        #print p[1]
        # LOG.debug(p[2].value)
        try:
            val = int(p[2])
        except ValueError:
            val = float(p[2])
        p[0] = formula.Constant(0-val)

    def p_unary_literal(self, p):
        '''unary : LITERAL'''
        #add more here on literals
        #LOG.debug(p[1])
        p[0] = formula.Literal(p[1], context=self.context)

    def p_unary_neg_literal(self, p):
        '''unary : SUB LITERAL'''
        #add more here on literals
        #LOG.debug(p[1])
        zero = formula.Constant(0)
        lit = formula.Literal(p[2], context=self.context)
        p[0] = formula.Subtraction(zero, lit)


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

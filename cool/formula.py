'''
Created on Jan 17, 2013

This module contains the classes which implement the Interpreter pattern
used for the generation of the LTL specs.

@author: antonio
'''

from cool.parser.lexer import BASE_SYMBOL_SET


PRECEDENCE_TUPLE = (
        ('left', 'IMPLIES', 'EQUALS'),
        ('left', 'AND', 'OR'),
        ('left', 'UNTIL', 'RELEASE', 'WEAK_UNTIL'),   
        ('left', 'GLOBALLY', 'EVENTUALLY'),
        ('right', 'NOT', 'NEXT'),
    )

class NotFoundError(Exception):
    pass

def find_precedence_index(symbol, precedence_tuple = PRECEDENCE_TUPLE):
    
    for i in range(0, len(precedence_tuple)):
        if symbol in precedence_tuple[i]:
            direction = precedence_tuple[i][0]
            return i, direction
    raise NotFoundError
 


class LTLFormula(object):
    '''
    Abstract class
    '''

    Symbol = None
    
    def __init__(self):
        '''
        Constructor
        '''
                
        pass
             
        
    def generate(self, symbol_set = BASE_SYMBOL_SET):
        '''
        doc
        '''
        return symbol_set[self.Symbol]
    

    
class Literal(LTLFormula):
    '''
    doc
    '''
    
    def __init__(self, base_str_formula):
        '''
        doc
        '''
        LTLFormula.__init__(self)
        self.__base_str_formula = base_str_formula
        
    def generate(self, symbol_set = BASE_SYMBOL_SET):
        '''
        doc
        '''
        return self.__base_str_formula
    
    
class TrueFormula(LTLFormula):
    '''
    doc
    '''
    
    Symbol = 'TRUE'
    
    
    
class FalseFormula(LTLFormula):
    '''
    doc
    '''
    
    Symbol = 'FALSE'
        
    
class BinaryFormula(LTLFormula):
    '''
    doc
    '''
    
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        LTLFormula.__init__(self)
        self.__left_formula = left_formula
        self.__right_formula = right_formula

        
    def generate(self, symbol_set = BASE_SYMBOL_SET):
        '''
        doc
        '''
        
        left_symbol = self.__left_formula.Symbol
        right_symbol = self.__right_formula.Symbol
        
        current_symbol_index, current_symbol_direction = find_precedence_index(self.Symbol)
        
        try:
            left_index, _ = find_precedence_index(left_symbol)
        except NotFoundError:
            left_index = len(PRECEDENCE_TUPLE)  
        
        try:
            right_index, _ = find_precedence_index(right_symbol)
        except NotFoundError:
            right_index = len(PRECEDENCE_TUPLE)
        
        
        left_string = self.__left_formula.generate(symbol_set)
        right_string = self.__right_formula.generate(symbol_set)
        
        if current_symbol_direction == 'left':
            if left_index < current_symbol_index:
                left_string = '(%s)' % left_string
            if right_index <= current_symbol_index:
                right_string = '(%s)' % right_string
        elif current_symbol_direction == 'right':
            if left_index <= current_symbol_index:
                left_string = '(%s)' % left_string
            if right_index < current_symbol_index:
                right_string = '(%s)' % right_string
        else:
            raise NotImplementedError
        
        return '%s %s %s' % (left_string, symbol_set[self.Symbol], right_string)
    
    
    
class UnaryFormula(LTLFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        LTLFormula.__init__(self)
        self.__right_formula = formula
        
    
    def generate(self, symbol_set = BASE_SYMBOL_SET):
        '''
        doc
        '''
        
        right_symbol = self.__right_formula.Symbol
        
        current_symbol_index, current_symbol_direction = find_precedence_index(self.Symbol)
        
        try:
            right_index, _ = find_precedence_index(right_symbol)
        except NotFoundError:
            right_index = len(PRECEDENCE_TUPLE)
        
        right_string = self.__right_formula.generate(symbol_set)
        
        if current_symbol_direction == 'right':
            if right_index < current_symbol_index:
                right_string = '(%s)' % right_string
        else:
            raise NotImplementedError
        
        return '%s %s' % (symbol_set[self.Symbol], right_string)
        
    
class Conjunction(BinaryFormula):
    '''
    doc
    '''
    
    Symbol = 'AND'
        

class Disjunction(BinaryFormula):
    '''
    doc
    '''
    Symbol = 'OR'
    
    

class Implication(BinaryFormula):
    '''
    doc
    '''
    Symbol = 'IMPLIES'
    
    

class Equivalence(BinaryFormula):
    '''
    doc
    '''
    Symbol = 'EQUALS'
    
    

class Globally(UnaryFormula):
    '''
    doc
    '''
    Symbol = 'GLOBALLY'
    
    
class Eventually(UnaryFormula):
    '''
    doc
    '''
    Symbol = 'EVENTUALLY'
    
    
class Next(UnaryFormula):
    '''
    doc
    '''
    Symbol = 'NEXT'
    
    

class Negation(UnaryFormula):
    '''
    doc
    '''
    Symbol = 'NOT'
    
    
    
class InvalidFormulaException(Exception):
    '''
    doc
    '''
    pass  
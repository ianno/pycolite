'''
Created on Jan 17, 2013

This module contains the classes which implement the Interpreter pattern
used for the generation of the LTL specs.

@author: antonio
'''

import exceptions
import parser

from cool.parser.lexer import BaseSymbolSet


class LTLFormula(object):
    '''
    Abstract class
    '''

    def __init__(self):
        '''
        Constructor
        '''
                
        pass
             
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        abstract method
        '''
        raise exceptions.NotImplementedError
    

    
class Literal(LTLFormula):
    '''
    doc
    '''
    
    def __init__(self, base_str_formula):
        '''
        doc
        '''

        self.__base_str_formula = base_str_formula
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self.__base_str_formula
    
    
class TrueFormula(LTLFormula):
    '''
    doc
    '''
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return symbol_set.true
    
class FalseFormula(LTLFormula):
    '''
    doc
    '''
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return symbol_set.false
    
class BinaryFormula(LTLFormula):
    '''
    doc
    '''
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        
        self.__left_formula = left_formula
        self.__right_formula = right_formula
        
    def _generate_with_symbol(self, symbol_set, binary_symbol):
        '''
        doc
        '''
        return '(%s) %s (%s) ' % (self.__left_formula.generate(symbol_set), binary_symbol, self.__right_formula.generate(symbol_set))
    
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        abstract method
        '''
        raise exceptions.NotImplementedError
    
    
class UnaryFormula(LTLFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        
        self.__formula = formula
        
    def _generate_with_symbol(self, symbol_set, unary_symbol):
        '''
        doc
        '''
        return '%s(%s) ' % (unary_symbol, self.__formula.generate(symbol_set))
    
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        abstract method
        '''
        raise exceptions.NotImplementedError    
    
class Conjunction(BinaryFormula):
    '''
    doc
    '''
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        
        BinaryFormula.__init__(self, left_formula, right_formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.conjunction)


class Disjunction(BinaryFormula):
    '''
    doc
    '''
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        
        BinaryFormula.__init__(self, left_formula, right_formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.disjunction)

class Implication(BinaryFormula):
    '''
    doc
    '''
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        
        BinaryFormula.__init__(self, left_formula, right_formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.implication)

class Equivalence(BinaryFormula):
    '''
    doc
    '''
    
    def __init__(self, left_formula, right_formula):
        '''
        doc
        '''
        
        BinaryFormula.__init__(self, left_formula, right_formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.equivalence)

class Globally(UnaryFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        
        UnaryFormula.__init__(self, formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.globally)
    
class Eventually(UnaryFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        
        UnaryFormula.__init__(self, formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.eventually)
    
class Next(UnaryFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        
        UnaryFormula.__init__(self, formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.next)

class Negation(UnaryFormula):
    '''
    doc
    '''
    
    def __init__(self, formula):
        '''
        doc
        '''
        
        UnaryFormula.__init__(self, formula)
        
    def generate(self, symbol_set = BaseSymbolSet()):
        '''
        doc
        '''
        return self._generate_with_symbol(symbol_set, symbol_set.negation)
    

    
class InvalidFormulaException(Exception):
    '''
    doc
    '''
    pass  
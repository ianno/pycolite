'''
Created on Jan 17, 2013

This module contains the classes which implement the Interpreter pattern
used for the generation of the LTL specs.

@author: antonio
'''

from cool.parser.lexer import BaseSymbolSet
from cool.attribute import Attribute, AttributeNamePool
from abc import abstractmethod

PRECEDENCE_TUPLE = (
    ('left', 'IMPLICATION', 'EQUALITY'),
    ('left', 'AND', 'OR'),
    ('left', 'UNTIL', 'RELEASE', 'WEAK_UNTIL'),
    ('left', 'GLOBALLY', 'EVENTUALLY'),
    ('right', 'NOT', 'NEXT'),
)

class NotFoundError(Exception):
    '''
    doc
    '''
    pass

def find_precedence_index(symbol, precedence_tuple=None):
    '''
    doc
    '''
    if precedence_tuple == None:
        precedence_tuple = PRECEDENCE_TUPLE

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

    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet

        return symbol_set.symbols[self.Symbol]


class Literal(Attribute, LTLFormula):
    '''
    Extend Attribute class to generate the correct name in the formula factory
    '''

    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet

        return self.unique_name


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


    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet


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

        return '%s %s %s' % (left_string, symbol_set.symbols[self.Symbol], right_string)



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


    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet

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

        return '%s %s' % (symbol_set.symbols[self.Symbol], right_string)


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
    Symbol = 'IMPLICATION'



class Equivalence(BinaryFormula):
    '''
    doc
    '''
    Symbol = 'EQUALITY'



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





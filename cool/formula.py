'''
Created on Jan 17, 2013

This module contains the classes which implement the Interpreter pattern
used for the generation of the LTL specs.

@author: antonio
'''

from cool.parser.lexer import BaseSymbolSet
from cool.attribute import Attribute, AttributeNamePool
from abc import abstractmethod
from observer import Observer

PRECEDENCE_TUPLE = (
    ('left', 'IMPLICATION', 'EQUALITY'),
    ('left', 'AND', 'OR'),
    ('left', 'UNTIL', 'RELEASE', 'WEAK_UNTIL'),
    ('right', 'GLOBALLY', 'EVENTUALLY'),
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



class LTLFormula(Observer):
    '''
    Abstract class
    '''

    Symbol = None

    is_literal = False

    def __init__(self):
        '''
        LTLFormula constructor
        '''
        self.literals = {}

    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet

        return symbol_set.symbols[self.Symbol]

    def update(self, updated_subject):
        '''
        Implementation of the update method from a attribute according to
        the observer pattern
        '''

        updated_attribute = updated_subject.get_state()

        if updated_attribute.base_name not in self.literals:
            raise KeyError('attribute not in literals dict for the furmula')

        #attach to the new attribute
        updated_attribute.attach(self)

        #detach from the current attribute
        self.literals[ updated_attribute.base_name  ].detach(self)

        #update the literals list
        self.literals[updated_attribute.base_name] = updated_attribute



    def get_literal_items(self):
        '''
        Returns a dictionary view including all the literals in the formula
        '''

        return self.literals.viewitems()


class Literal(Attribute, LTLFormula):
    '''
    Extend Attribute class to generate the correct name in the formula factory
    '''

    is_literal = True

    def __init__(self, base_name, context = None):
        '''
        instantiate a new literal.

        :paramenter base_name: literal name, ok if not unique
        :type base_name: string
        :parameter context: context realative to the unique literal name
        generation
        :type context: object
        '''
        LTLFormula.__init__(self)
        Attribute.__init__(self, base_name, context)

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
        self.left_formula = left_formula
        self.right_formula = right_formula

        self.process_literals()

    def update(self, updated_subject):
        '''
        override of the update method from LTLFormula.
        We need to propagate an update also to left or right formulae
        '''

        #security check. Here if right_formula and right_formula have the same
        #base name, they should be the same object
        assert (self.left_formula.base_name != self.right_formula.base_name) \
                or (self.left_formula == self.right_formula)

        if updated_subject == self.left_formula:

            #security check. updated subject shouldn't be also equal to
            #right_formula
            assert updated_subject != self.right_formula

            self.left_formula = updated_subject.get_state()
        elif updated_subject == self.right_formula:
            self.right_formula = updated_subject.get_state()

        #call superclass update
        LTLFormula.update(self, updated_subject)

    def get_literal_items(self):
        '''
        Returns all literals looking recursively in all the formula
        object structure
        '''
        return self.literals.viewitems() | self.left_formula.get_literal_items() \
                | self.right_formula.get_literal_items()


    def get_conflicting_literals(self):
        '''
        Returns a list of tuples containing all the literals which have the
        same base name but are different object whithin the formula.
        '''

        conflict_list = []
        left_side_literals = dict(self.left_formula.get_literal_items())
        right_side_literals = dict(self.right_formula.get_literal_items())

        for key in (left_side_literals.viewkeys() & right_side_literals.viewkeys()):

            conflict_list.append( (left_side_literals[key], right_side_literals[key]) )

        return conflict_list


    def process_literals(self):
        '''
        add a new literal to the internal dict if it is the case and process
        literals in left and right sides of the formula
        '''

        #check for immediate conflict. If so, discard a literal
        if self.left_formula.is_literal and self.right_formula.is_literal and \
                self.left_formula.base_name == self.right_formula.base_name:

            self.right_formula = self.right_formula

            self.left_formula.attach(self)
            self.literals[self.left_formula.base_name] = self.left_formula

        else:
            #if either side is a literal, add it to the internal list
            if self.left_formula.is_literal:

                self.left_formula.attach(self)
                self.literals[self.left_formula.base_name] = self.left_formula

            if self.right_formula.is_literal:

                self.right_formula.attach(self)
                self.literals[self.right_formula.base_name] = self.right_formula

        #get the list of conflicting literals
        conflicts = self.get_conflicting_literals()

        #process them
        for (left_literal, right_literal) in conflicts:

            #policy to make the left_literal to be chosen over the other
            right_literal.merge( left_literal )


    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet


        left_symbol = self.left_formula.Symbol
        right_symbol = self.right_formula.Symbol

        current_symbol_index, current_symbol_direction = find_precedence_index(self.Symbol)

        try:
            left_index, _ = find_precedence_index(left_symbol)
        except NotFoundError:
            left_index = len(PRECEDENCE_TUPLE)

        try:
            right_index, _ = find_precedence_index(right_symbol)
        except NotFoundError:
            right_index = len(PRECEDENCE_TUPLE)


        left_string = self.left_formula.generate(symbol_set)
        right_string = self.right_formula.generate(symbol_set)

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
        self.right_formula = formula

        #process literal, if any:
        if self.right_formula.is_literal:
            self.right_formula.attach(self)
            self.literals[self.right_formula.base_name] = self.right_formula

    def get_literal_items(self):
        '''
        Returns all literals looking recursively in all the formula
        object structure
        '''

        return self.literals.viewitems() | self.right_formula.get_literal_items()


    def update(self, updated_subject):
        '''
        override of the update method from LTLFormula.
        We need to propagate an update also to left or right formulae
        '''

        #if we receive an update for a literal we don't are
        #linked to, that's an error
        assert updated_subject == self.right_formula

        self.right_formula = updated_subject.get_state()

        #call superclass update
        LTLFormula.update(self, updated_subject)



    def generate(self, symbol_set = None):
        '''
        doc
        '''
        if symbol_set == None:
            symbol_set = BaseSymbolSet

        right_symbol = self.right_formula.Symbol

        current_symbol_index, current_symbol_direction = find_precedence_index(self.Symbol)

        try:
            right_index, _ = find_precedence_index(right_symbol)
        except NotFoundError:
            right_index = len(PRECEDENCE_TUPLE)

        right_string = self.right_formula.generate(symbol_set)

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





'''
Basic implementation of contract

Author: Antonio Iannopollo
'''

from cool.parser.parser import LTL_PARSER
from cool.parser.lexer import BaseSymbolSet

class Contract(object):
    '''
    This class implements the basic concept of contract. This object is able
    to process input formulas (one for the assumptions, and one for the
    guarantees). The biggest difference with respect to the theoretical entity
    of a contract is that here we require also the list of input and output
    ports to be provided.
    This implementation supports the basic operation on contracts, such as
    refinement check, composition, compatibility and consistency checks.
    No requirement of GR1 formulas needed.
    '''

    def __init__(self, input_ports, output_ports, assume_formula, guarantee_formula, symbolSetCls = BaseSymbolSet):
        '''
        Instantiate a contract.

        :param input_ports: set of input ports associated with the contract
        :type input_ports: set or list  of strings, each of them being an
        environment-controlled literal
        :param output_ports: set of output ports associated with the contract
        :type output_ports: set or list of string , each of them being a
        contract-controlled literal
        :param assume_formula: assume part of the contract specification
        :type assume_formula: string or LTLFormula object
        :param guarantee_formula: guarantee part of the contract specification
        :type guarantee_formula: string or LTLFormula object
        :param symbolSetCls: symbol set class, used to decode furmula strings
        and to generate string representation of LTLFormula objects
        :type symbolSetCls: class, preferably extending
        cool.parser.lexer.BaseSymbolSet
        '''

        #first, we need to retrieve formulas and literals from formulas
        #possibilities are that formulae will be either string or LTLFormula
        #object
        #Let's assume they are string, then LTLFormula objects
        #Also, in case they are strings, we need to insure that the same
        #literal in either formula is associated to the same attribute.
        #This means the context of both formulae is the current Contract obj
        try:
            self.assume_formula = LTL_PARSER.parse(assume_formula, context = self)
        except TypeError:
            #the formula is not a string, we assume is a LTLFormula object
            self.assume_formula = assume_formula

        try:
            self.guarantee_formula = LTL_PARSER.parse(guarantee_formula, context = self)
        except TypeError:
            self.guarantee_formula = guarantee_formula

        self.input_ports = set(input_ports)
        self.output_ports = set(output_ports)

        #we need to make sure there are not ports which are both input and
        #output
        if not self.input_ports.isdisjoint(self.output_ports):
            raise PortDeclarationError(self.input_ports & self.output_ports)

        #now we need to check that the declared input and output ports
        #match the formulae.
        #It is possible, however, that some ports are not mentioned at all
        #in the formulae (meaning no costraints on values), or that both
        #input and output ports are mentioned as literal in either assume
        #or guarantee formulae.
        #What we can do, is making sure that there are not literals in 
        #assumptions and guarantees which do not match ports

        current_literal_items = self.assume_formula.get_literal_items() | \
                                self.guarantee_formula.get_literal_items()
 
        #get only the base_name of the literals, use the reverse zip
        #function
        current_literal_base_names, _ = zip(*current_literal_items)

        contract_ports = self.input_ports | self.output_ports

        for literal in current_literal_base_names:
            if literal not in contract_ports:
                raise PortMappingError(literal)


class PortDeclarationError(Exception):
    '''
    Raised if there are incosistencies in port declaration
    '''
    pass

class PortMappingError(Exception):
    '''
    Raised if a formula uses an undeclared port
    '''
    pass

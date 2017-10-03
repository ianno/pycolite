'''
Basic implementation of ports and basic types

Author: Antonio Iannopollo
'''

from pycolite.formula import Literal, Conjunction, Disjunction, Negation
from pycolite.observer import Observer
from copy import deepcopy
#from pycolite.ltl3ba import (Ltl3baRefinementStrategy, Ltl3baCompatibilityStrategy,
#                         Ltl3baConsistencyStrategy)

from abc import ABCMeta, abstractmethod
from pycolite import LOG
from pycolite.types import Int, Bool, Float

LOG.debug('in port.py')


class Port(Observer):
    '''
    This class implements a port for a contract. It contains a literal but it
    keeps constant its base name
    '''

    def __init__(self, base_name, l_type=Bool(), contract=None, literal=None, context=None):
        '''
        Creates a new port and associates a literal.
        If no literal is provided, a new one will be created.

        :param base_name: base name of the port
        :type base_name: string
        :param literal: literal to be associated with the port. If None, a
            new Literal will be created
        :type literal: LTLFormula.Literal
        :param context: a context object to define the scope of literal unique
            naming
        :type context: object
        '''


        self.base_name = base_name
        self.l_type = l_type
        self.context = context

        self._contract = contract
        #it's  property
        #self.contract = contract

        if literal is None:
            literal = Literal(base_name, l_type=l_type, context=context)

        self.literal = literal
        #import pdb
        #pdb.set_trace()
        self.literal.attach(self)


    def update(self, updated_subject):
        '''
        Implementation of the update method from a attribute according to
        the observer pattern
        '''

        updated_literal = updated_subject.get_state()

        #if updated_name not in self.port_names:
        #    raise KeyError('attribute not in literals dict for the formula')

        #attach to the new literal
        updated_literal.attach(self)

        #detach from the current literal
        self.literal.detach(self)

        #update the literals
        self.literal = updated_literal

    def merge(self, port):
        '''
        Merges the current port literal with another port or literal
        '''

        assert (self.l_type <= port.l_type or
                port.l_type <= self.l_type)

        # LOG.debug(self.literal.l_type)
        # LOG.debug(port.literal.l_type)

        if self.literal != port.literal:
            self.literal.merge(port.literal)
        else:
            LOG.warning('merging port with its own literal: %s'
                        % self.literal.unique_name)

        if self.l_type <= port.l_type:
            port.l_type = self.l_type
        else:
            self.l_type = port.l_type

        return self

    def is_connected_to(self, port):
        '''
        Returns true if self references the same literal than port
        '''
        if self.unique_name == port.unique_name:
            return True
        else:
            return False

    def reinitialize(self, new_contract=None):
        '''
        Generate a new unique _name and propagates it
        '''
        new_literal = Literal(self.literal.base_name, l_type=self.l_type, context=self.context)

        self.literal.merge(new_literal)

        if new_contract is not None:
            self._contract = new_contract


    @property
    def contract(self):
        '''
        contract using the port
        '''
        return self._contract

    @contract.setter
    def contract(self, value):
        '''
        fails if assign multiple times
        '''
        if self._contract is not None:
            raise PortDeclarationError('assigning port to contract multiple times')

        #check the contract has this port
        #if value is not None and self not in value.ports_dict.viewvalues():
        #    raise PortDeclarationError('contract does not contain this port')

        self._contract = value

    @property
    def unique_name(self):
        '''
        return unique_name associated to self.literal
        '''
        return self.literal.unique_name

    @property
    def is_input(self):
        '''
        Returns true if the port is a input of the connected contract
        '''

        if self.contract is None:
            raise PortDeclarationError('port is not used by any contract')
        else:
            if self.base_name in self.contract.input_ports_dict:
                return True
            else:
                return False

    @property
    def is_output(self):
        '''
        Returns True if the port is an output
        '''
        return not self.is_input



class PortMapping:
    '''
    Encapsulate the information needed to remap a set of ports
    to another
    '''

    __metaclass__ = ABCMeta

    def __init__(self):
        '''
        cannot instantiate an abstract PortMapping
        '''
        raise NotImplementedError()

    @abstractmethod
    def _validate_port(self, port):
        '''
        validate port. It is good practise to always provide a validation procedure
        '''
        raise NotImplementedError()

    @abstractmethod
    def add(self, port, other_port):
        '''
        basic method to add constraints
        '''
        raise NotImplementedError()


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

class PortNotFoundError(Exception):
    '''
    Raised if a port name is not found
    '''
    pass

class PortConnectionError(Exception):
    '''
    Raised in case of attemp of connecting two output ports
    '''


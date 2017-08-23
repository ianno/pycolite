'''
Basic implementation of contract

Author: Antonio Iannopollo
'''

from pycolite.parser.parser import LTL_PARSER
from pycolite.parser.lexer import BaseSymbolSet
from pycolite.attribute import Attribute
from pycolite.formula import Literal, Conjunction, Disjunction, Negation
from pycolite.observer import Observer
from copy import deepcopy
#from pycolite.ltl3ba import (Ltl3baRefinementStrategy, Ltl3baCompatibilityStrategy,
#                         Ltl3baConsistencyStrategy)

from pycolite.nuxmv import (NuxmvRefinementStrategy, NuxmvCompatibilityStrategy,
                         NuxmvConsistencyStrategy, NuxmvApproximationStrategy)
from abc import ABCMeta, abstractmethod
from pycolite import LOG
from pycolite.types import Int, Bool

LOG.debug('in contract.py')


def verify_refinement(refined, abstract, refinement_mapping=None, strategy_obj=None):
    '''
    Verifies that refined refines abstract.

    :returns: boolean
    '''
    if refinement_mapping is None:
        refinement_mapping = RefinementMapping([refined, abstract])
    #get copies
    contract_copies, mapping_copy = refinement_mapping.get_mapping_copies()

    refined_copy = contract_copies[refined]
    abstract_copy = contract_copies[abstract]

    # LOG.debug(refined_copy.type_dir)
    # for p in refined_copy.ports_dict.values():
    #     LOG.debug(p.base_name)
    #     LOG.debug(p.literal.l_type)


    #connect ports previously connected and not in the mapping
    #TODO
    #inefficient
    for port_a in refined.ports_dict.values():
        for port_b in abstract.ports_dict.values():
            if port_a.is_connected_to(port_b):
                refined_copy.connect_to_port(refined_copy.ports_dict[port_a.base_name],
                                     abstract_copy.ports_dict[port_b.base_name])

    #connect ports according to mapping relation
    for (port_a, port_b) in mapping_copy.mapping:
        port_a.contract.connect_to_port(port_a, port_b)

    #If a strategy is not defined, uses Nuxmv
    if strategy_obj is None:
        strategy_obj = NuxmvRefinementStrategy(refined_copy, delete_files=False)

    #LOG.debug('refinement')
    #LOG.debug(refined)
    #LOG.debug(refined_copy)
    #LOG.debug(abstract)
    #LOG.debug(abstract_copy)
    #LOG.debug(refined_copy.assume_formula.generate())

    if not strategy_obj.check_refinement(abstract_copy):
        raise NotARefinementError(refinement_mapping)



def verify_approximation(approximate, more_defined, approximation_mapping=None, strategy_obj=None):
    '''
    Verifies that refined refines abstract.

    :returns: boolean
    '''
    if approximation_mapping is None:
        approximation_mapping = ApproximationMapping([more_defined, approximate])
    #get copies
    contract_copies, mapping_copy = approximation_mapping.get_mapping_copies()

    defined_copy = contract_copies[more_defined]
    approximate_copy = contract_copies[approximate]


    #connect ports previously connected and not in the mapping
    #TODO
    #inefficient
    for port_a in more_defined.ports_dict.values():
        for port_b in approximate.ports_dict.values():
            if port_a.is_connected_to(port_b):
                defined_copy.connect_to_port(defined_copy.ports_dict[port_a.base_name],
                                     approximate_copy.ports_dict[port_b.base_name])

    #connect ports according to mapping relation
    for (port_a, port_b) in mapping_copy.mapping:
        port_a.contract.connect_to_port(port_a, port_b)

    #If a strategy is not defined, uses Nuxmv
    if strategy_obj is None:
        strategy_obj = NuxmvApproximationStrategy(approximate_copy, delete_files=False)

    #LOG.debug('refinement')
    #LOG.debug(refined)
    #LOG.debug(refined_copy)
    #LOG.debug(abstract)
    #LOG.debug(abstract_copy)
    #LOG.debug(refined_copy.assume_formula.generate())

    if not strategy_obj.check_approximation(defined_copy):
        raise NotAnApproximationError(defined_copy)

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

        assert self.l_type == port.l_type

        # LOG.debug(self.literal.l_type)
        # LOG.debug(port.literal.l_type)

        if self.literal != port.literal:
            self.literal.merge(port.literal)
        else:
            LOG.warning('merging port with its own literal: %s'
                        % self.literal.unique_name)

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

    def __init__(self, base_name, input_ports, output_ports, assume_formula,
                 guarantee_formula, symbol_set_cls=BaseSymbolSet, context=None,
                 saturated=True, infer_ports=True):
        '''
        Instantiate a contract.

        :param base_name: a name for the contract. If the name is not unique,
            a unique name will be provided as an Attribute
        :type base_name: string
        :param input_ports: set of input ports associated with the contract
        :type input_ports: set or list  of strings, each of them being an
            environment-controlled literal, or a list of pairs (name, Literal)
        :param output_ports: set of output ports associated with the contract
        :type output_ports: set or list of string , each of them being a
            contract-controlled literal, or a list of pairs (name, Literal)
        :param assume_formula: assume part of the contract specification
        :type assume_formula: string or LTLFormula object
        :param guarantee_formula: guarantee part of the contract specification
        :type guarantee_formula: string or LTLFormula object
        :param symbol_set_cls: symbol set class, used to decode furmula strings
            and to generate string representation of LTLFormula objects
        :type symbol_set_cls: class, preferably extending
            pycolite-lite-dev.parser.lexer.BaseSymbolSet
        :param context: fomrula context for unique variable naming
        :type context: object
        '''
        #TODO
        #check for saturated formulas automatically

        self.symbol_set_cls = symbol_set_cls
        self.context = context

        #define attribute name for the contract
        self.name_attribute = Attribute(base_name, self.context)

        self.infer_ports = infer_ports

        self.type_dir = {}

        #first, we need to retrieve formulas and literals from formulas
        #possibilities are that formulae will be either string or LTLFormula
        #object
        #Let's assume they are string, then LTLFormula objects
        #Also, in case they are strings, we need to insure that the same
        #literal in either formula is associated to the same attribute.
        #This means the context of both formulae is the current Contract obj
        try:
            self.assume_formula = LTL_PARSER.parse(assume_formula, \
                    context=self.context, symbol_set_cls=symbol_set_cls)
        except TypeError:
            #the formula is not a string, we assume is a LTLFormula object
            self.assume_formula = assume_formula
            self.guarantee_formula = guarantee_formula
        else:
            self.guarantee_formula = LTL_PARSER.parse(guarantee_formula, \
                    context=self.context, symbol_set_cls=symbol_set_cls)

            #if from strings, equalize formulas:
            self.assume_formula.equalize_literals_with(self.guarantee_formula)

        #put it in saturated form
        if not saturated:
            not_assumpt = Negation(self.assume_formula)
            self.guarantee_formula = \
                    Disjunction(not_assumpt, self.guarantee_formula)


        #the contract has to mantain a detailed list of ports.
        #It means that it needs to be an observer of literals in formulae
        #and it needs to create new attributes for ports which are not mentioned
        #in formulae

        #start assuming the input and output lists are including literals
        try:
            self.input_ports_dict = \
                    {key: value for (key, value) in input_ports.items()}

            if any([isinstance(val, str)
                    for val in self.input_ports_dict.values()]):
                raise AttributeError

        #in case input_ports is a list of string, we'll try to match
        #literals in the formula
        except AttributeError:
            input_ports = set(input_ports)

            #check for types
            temp_list = []
            for elem in input_ports:
                if isinstance(elem, (list, tuple)) and len(elem) >= 3:
                    name = elem[0]
                    lower = elem[1]
                    upper = elem[2]

                    self.type_dir[name] = Int(lower, upper)

                    temp_list.append(name)
                else:
                    self.type_dir[elem] = Bool()
                    temp_list.append(elem)

            input_ports = set(temp_list)


            self.input_ports_dict = {key : None for key in input_ports}
        else:
            #set_types
            for (key, value) in input_ports.items():
                self.type_dir[key] = value.l_type
            #register this contract as the port owner
            for port in self.input_ports_dict.viewvalues():
                port.contract = self
        #and outputs
        try:
            self.output_ports_dict = \
                    {key: value for (key, value) in output_ports.items()}

            if any([isinstance(val, str) for val in self.output_ports_dict.values()]):
                raise AttributeError
        #in case input_ports is a list of string, we'll try to match
        #literals in the formula
        except AttributeError:
            output_ports = set(output_ports)

            #check for types
            temp_list = []
            for elem in output_ports:
                if isinstance(elem, (list, tuple)) and len(elem) >= 3:
                    name = elem[0]
                    lower = elem[1]
                    upper = elem[2]

                    self.type_dir[name] = Int(lower, upper)

                    temp_list.append(name)
                else:
                    self.type_dir[elem] = Bool()
                    temp_list.append(elem)

            output_ports = set(temp_list)


            self.output_ports_dict = {key : None for key in output_ports}
        else:
            #set_types
            for (key, value) in output_ports.items():
                self.type_dir[key] = value.l_type
            #register this contract as the port owner
            for port in self.output_ports_dict.viewvalues():
                port.contract = self

        #try process input and outport ports
        #if a port is associated with None, a literal will be searched
        #in formulae, otherwise a new Port is created
        for literal_name in self.ports_dict.viewkeys():
            #port lookup looks for the correct dictionary
            port_dict = self.port_lookup(literal_name)

            if port_dict[literal_name] is None:
                #try to associate by base_name
                if literal_name in self.formulae_dict:
                    #update type
                    self.formulae_dict[literal_name].l_type = self.type_dir[literal_name]

                    port_dict[literal_name] = \
                        Port(literal_name, l_type=self.type_dir[literal_name], contract=self, literal=\
                        self.formulae_dict[literal_name], \
                        context=self.context)
                #otherwise create new Port
                else:
                    port_dict[literal_name] = \
                        Port(literal_name, l_type=self.type_dir[literal_name], contract=self, context=self.context)

            ##observer pattern - attach to the subject
            #port_dict[literal_name].attach(self)

        #check if there is something wrong

        #we need to make sure there are not ports which are both input and
        #output
        if not set(self.input_ports_dict.viewkeys()).isdisjoint( \
                set(self.output_ports_dict.viewkeys())):
            raise PortDeclarationError(self.input_ports_dict.viewkeys() & \
                    self.output_ports_dict.viewkeys())


        #now we need to check that the declared input and output ports
        #match the formulae.
        #It is possible, however, that some ports are not mentioned at all
        #in the formulae (meaning no costraints on values), or that both
        #input and output ports are mentioned as literal in either assume
        #or guarantee formulae.
        #What we can do, is making sure that there are not literals in
        #assumptions and guarantees which do not match ports


        #LOG.debug(self.type_dir)
        #sometimes some literals in formulae do not have a match
        #we can try to match them with known ports based on their base_name
        if self.infer_ports:
            for key in self.formulae_reverse_dict.viewkeys() - \
                    self.reverse_ports_dict.viewkeys():

                literals = self.formulae_reverse_dict[key]
                for literal in literals:
                    try:
                        literal.l_type = self.ports_dict[literal.base_name].l_type
                        literal.merge(self.ports_dict[literal.base_name].literal)
                    except KeyError:
                        raise PortMappingError(key)


        #Initialize a dict in which there is a reference to all the contracts
        #used to obtain this contract through composition.
        #The dict is inializated as empty
        self.origin_contracts = {}


    def copy(self):
        '''
        create a copy, with new disconnected ports, of the current contract
        Preserves feedback loops
        '''
        #LOG.debug(self)
        #new_contract = deepcopy(self)
        #new_contract.assume_formula.reinitialize()
        #new_contract.guarantee_formula.reinitialize()
        new_name = self.base_name
        new_guarantees = self.guarantee_formula.generate()
        new_assumptions = self.assume_formula.generate()

        new_guarantees = LTL_PARSER.parse(new_guarantees, \
                    context=self.context,
                    symbol_set_cls=self.symbol_set_cls)
        new_assumptions = LTL_PARSER.parse(new_assumptions, \
                    context=self.context,
                    symbol_set_cls=self.symbol_set_cls)

        new_assumptions.equalize_literals_with(new_guarantees)

        literals = dict(new_guarantees.get_literal_items() |
                        new_assumptions.get_literal_items())

        #create ports
        new_inputs = {}
        for name, port in self.input_ports_dict.items():

            if port.unique_name in literals:
                #set types
                literals[port.unique_name].l_type = port.l_type

                new_inputs[name] = Port(name, l_type=port.l_type,
                                    literal=literals[port.unique_name])
            else:
                new_inputs[name] = Port(name,l_type=port.l_type)


        new_outputs = {}
        for name, port in self.output_ports_dict.items():
            if port.unique_name in literals:
                #set types
                literals[port.unique_name].l_type = port.l_type

                new_outputs[name] = Port(name, l_type=port.l_type,
                                    literal=literals[port.unique_name])
            else:
                new_outputs[name] = Port(name, l_type=port.l_type)

        new_contract = type(self)(new_name, new_inputs, new_outputs, new_assumptions,
                                    new_guarantees, self.symbol_set_cls, self.context,
                                    saturated=True, infer_ports=False)

        #new_contract.name_attribute = \
        #        Attribute(self.name_attribute.base_name, self.context)

        #reinitialize contract Ports
        #for port in new_contract.ports_dict.values():
        #    port.reinitialize(new_contract)

        #LOG.debug(self)
        #LOG.debug(new_contract)

        return new_contract


    def compose(self, contract_list, new_name=None, composition_mapping=None):
        '''
        Compose the current contract with the one passed as a parameter.
        The operations to be done are: merge the literals, and merge the
        formulae.
        Given a contract C = (A, G) and a contract C1 = (A1, G1), the
        composition of the two will be a contract
        C2 = ((A & A1) | !(G & G1) , G & G1)

        :param other_contract: contract to be used for composition
        :type other_contract: Contract
        :param connection_list: optional list of pairs of base_names specifying
            the ports to be connected
        :type connection_list: list of tuples (pairs)
        '''

        try:
            contracts = set(contract_list)
        except TypeError:
            #in case it is a single contract without list
            contracts = set()
            contracts.add(contract_list)

        #if the list is empty, return self
        if not contracts:
            return self

        contracts.add(self)

        if composition_mapping is None:
            composition_mapping = CompositionMapping(contracts, self.context)
        if new_name is None:
            new_name = '-x-'.join([contract.name_attribute.base_name for contract in contracts])

        try:
            (new_inputs, new_outputs) = composition_mapping.define_composed_contract_ports()
        except PortMappingError:
            raise
        else:
            all_pairs = [(contract.assume_formula, contract.guarantee_formula)
                         for contract in contracts]
            (part_assumptions, new_guarantees) = reduce(self._reduce_composition_formulae, all_pairs)


            new_assumptions = Disjunction(
                                part_assumptions,
                                Negation(new_guarantees),
                                merge_literals=False)

            #LOG.debug('c type')
            #LOG.debug(type(self))
            new_contract = type(self)(new_name, new_inputs, new_outputs, new_assumptions,
                                    new_guarantees, self.symbol_set_cls, self.context,
                                    saturated=True, infer_ports=False)

            #add the two contracts as source contracts
            new_contract.origin_contracts = {contract.name_attribute.unique_name: contract for
                                             contract in contracts}


            return new_contract


    def _reduce_composition_formulae(self, ag_pair_a, ag_pair_b):
        '''
        get a new pair of formulae obtained by composing the input pairs
        '''

        assumption_a = ag_pair_a[0]
        guarantee_a = ag_pair_a[1]

        assumption_b = ag_pair_b[0]
        guarantee_b = ag_pair_b[1]

        and_of_assumptions = Conjunction(assumption_a, assumption_b, merge_literals=False)

        new_guarantees = Conjunction(guarantee_a, guarantee_b, merge_literals=False)

        #neg_guarantees = Negation(new_guarantees)

        #new_assumptions = Disjunction(and_of_assumptions, neg_guarantees,
        #                              merge_literals=False)

        return (and_of_assumptions, new_guarantees)



    def connect_to_port(self, port_ref, other_port_ref):
        '''
        Connect a port of the current contract with a port of another contract.
        Here it is allowed connecting two output ports.

        :param port_name: base name of the current contract port
        :type port_name: string
        :param other_contract: contract to be connected to
        :type other_contract: Contract object
        :param other_port_name: name of the port to be connected to
        :type other_port_name: string
        '''
        #merge only if the contract is the rightful owner of the port
        if port_ref.contract is self:
            port_ref.merge(other_port_ref)
        else:
            raise PortDeclarationError()

    def is_refinement(self, abstract_contract, refinement_mapping=None, strategy_obj=None):
        '''
        Checks whether the calling contract refines abstract_contract

        :returns: boolean
        '''
        #TODO
        #move these methods (also consistency and compatibility)
        #to module level
        try:
            verify_refinement(self, abstract_contract, refinement_mapping=refinement_mapping,
                              strategy_obj=strategy_obj)
        except NotARefinementError:
            return False
        else:
            return True

    def is_approximation(self, more_defined_contract, approximation_mapping=None, strategy_obj=None):
        '''
        Checks whether the calling contract refines abstract_contract

        :returns: boolean
        '''
        #TODO
        #move these methods (also consistency and compatibility)
        #to module level
        try:
            verify_approximation(self, more_defined_contract, approximation_mapping=approximation_mapping,
                              strategy_obj=strategy_obj)
        except NotAnApproximationError:
            return False
        else:
            return True

    def is_consistent(self, strategy_obj=None):
        '''
        Returns True if the contract is consistent. False otherwise.
        A contract is consistent iff it is not self-contradicting. In case of a
        self-contradicting contract, it is impossible to find an implementation
        that satisfies it. Thus to verify consistency, we need to check that the
        guarantee formula is not an empty formula
        '''
        if strategy_obj is None:
            strategy_obj = NuxmvConsistencyStrategy(self, delete_files=False)

        return strategy_obj.check_consistency()

    def is_compatible(self, strategy_obj=None):
        '''
        Returns True if the contract is compatible, False otherwise.
        A contract is compatible iff there is at least a valid environment in
        which it can operate. Therefore we need to verify that the assumption
        formula is not empty.
        '''

        if strategy_obj is None:
            strategy_obj = NuxmvCompatibilityStrategy(self, delete_files=False)

        return strategy_obj.check_compatibility()

    def __str__(self):
        '''
        Defining print representation for a contract
        '''
        description = []
        description.append('Contract %s ( %s )\n' % \
            (self.name_attribute.unique_name, self.name_attribute.base_name))

        description.append('\tInput ports:\n')

        for base_name, port in self.input_ports_dict.items():

            description.append('\t\t%s ( %s ) : %s\n' % \
                    (port.unique_name, base_name, port.l_type))

        description.append('\tOutput ports:\n')

        for base_name, port in self.output_ports_dict.items():
            description.append('\t\t%s ( %s ) : %s\n' % \
                    (port.unique_name, base_name, port.l_type))

        description.append('\tAssumption\n')
        description.append('\t\t%s\n' % \
                self.assume_formula.generate(self.symbol_set_cls))

        description.append('\tGuarantee\n')
        description.append('\t\t%s\n' % \
                self.guarantee_formula.generate(self.symbol_set_cls))

        return ''.join(description)


    def port_lookup(self, literal_name):
        '''
        Given a literal name, returns the dictionary (either input or output)
        in which it is defined
        '''

        if literal_name in self.input_ports_dict.viewkeys():
            port_dict = self.input_ports_dict
        elif literal_name in self.output_ports_dict.viewkeys():
            port_dict = self.output_ports_dict
        else:
            raise KeyError('port not defined for literal %s' % literal_name)

        return port_dict


    def __getattr__(self, port_name):
        '''
        Checks if port_name is in ports_dict and consider it as a Contract attribute.
        IF it is present, returns the
        requested port, otherwise raises a AttributeError exception
        '''

        if port_name in self.ports_dict:
            return self.ports_dict[port_name]
        else:
            raise AttributeError


    @property
    def port_names(self):
        '''
        Returns an updated set of port names
        '''
        return self.input_ports_dict.viewkeys() | \
                self.output_ports_dict.viewkeys()


    @property
    def ports_dict(self):
        '''
        Return an update dict of all the contract ports
        '''
        return dict( self.input_ports_dict.items() + \
                        self.output_ports_dict.items() )

    @property
    def reverse_ports_dict(self):
        '''
        Returns a dict which has uniques names as keys, and ports as values
        '''
        return dict( self.reverse_input_ports_dict.items() + \
                        self.reverse_output_ports_dict.items())

    @property
    def reverse_input_ports_dict(self):
        '''
        Returns a dict which has uniques names as keys, and ports as values
        '''
        return {key_port.unique_name:
                [port for port in self.input_ports_dict.values()
                 if port.unique_name == key_port.unique_name]
                for key_port in self.input_ports_dict.viewvalues()}

        #return {key: value for (key, value) in zip( \
        #        [port.unique_name \
        #            for port in self.input_ports_dict.viewvalues()], \
        #        self.input_ports_dict.viewvalues() )}

    @property
    def reverse_output_ports_dict(self):
        '''
        Returns a dict which has uniques names as keys, and ports as values
        '''
        return {key_port.unique_name:
                [port for port in self.output_ports_dict.values()
                 if port.unique_name == key_port.unique_name]
                for key_port in self.output_ports_dict.viewvalues()}

        #return {key: value for (key, value) in zip( \
        #        [port.unique_name \
        #            for port in self.output_ports_dict.viewvalues()], \
        #        self.output_ports_dict.viewvalues() )}


    @property
    def formulae_dict(self):
        '''
        return a dict of literals used in contract formulae, indexed by
        base_name
        '''
        return dict(self.assume_formula.get_literal_items() | \
                    self.guarantee_formula.get_literal_items() )

    @property
    def formulae_reverse_dict(self):
        '''
        return a dict of lterals used in contract formulae, indexed by
        unique_name
        '''
        #use the formulae instead of the dict because the dicts
        #overrides duplicates

        try:
            #unzip
            _, values = zip(* (self.assume_formula.get_literal_items() | \
                            self.guarantee_formula.get_literal_items()))
        except ValueError:
            LOG.debug('no literals??')
            return {}
        else:
            return {key_lit.unique_name:
                    [literal for literal in values if literal.unique_name == key_lit.unique_name]
                    for key_lit in set(values)}

            #return {key: value for (key, value) in zip( \
            #    [literal.unique_name for literal in values], \
            #        values)}

    def non_composite_origin_set(self):
        '''
        Return the set of noncomposite origin contracts
        '''
        if self.origin_contracts == {}:
            raise NonCompositeContractError()

        origin_set = set()
        look_list = self.origin_contracts.values()

        for contract in look_list:
            try:
                #access the composite list of c.
                #if c has no origin contracts, is what we are looking for.
                #otherwise expand look_list
                look_list += contract.origin_contracts.values()
            except NonCompositeContractError:
                origin_set.add(contract)

        return origin_set

    @property
    def base_name(self):
        '''
        Returns contract base_name
        '''
        return self.name_attribute.base_name

    @property
    def unique_name(self):
        '''
        Returns contract unnique name
        '''
        return self.name_attribute.unique_name



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

class RefinementMapping(object):
    '''
    This class stores the information about mapping a certain number
    of ports among a set of contracts.
    This can be seen as a generalization of the concept of port conncetion.
    The main difference is that while the connection is a strong bond among
    contracts (e.g. a design constraint), a mapping relation is a loose
    reference, used in verification and synthesis, where a connection is not
    a absolute constraint and can be modified or deleted.
    '''

    def __init__(self, contracts):
        '''
        Instantiate a mapping constraint.

        :param *args: instances of type Contract
        '''

        self.contracts = set(contracts)

        self.mapping = set()
        '''
        mapping is a list of pairs, which are port
        base_names who needs to be equivalent.
        '''

    def _validate_port(self, port):
        '''
        raises an exception if port is not related to one of the mapped contract
        '''
        if port.contract not in self.contracts:
            raise PortMappingError(port)

    def add(self, port_a, port_b):
        '''
        Add a map constraint between ports in contract_a and contract_b.

        :param base_name_a: base_name of port in contract_a
        :param base_name_b: base_name of port in contract_b
        '''
        self._validate_port(port_a)
        self._validate_port(port_b)
        self.mapping.add((port_a, port_b))


    def get_mapping_copies(self):
        '''
        returns a copy of the contracts and an updated
        LibraryPortMapping object related to those copies

        :returns: a pair, in which the first element is a dictionary containing a reference
                  to the copied contracts, and a LibraryPortMapping object
        '''

        new_contracts = {contract: contract.copy() for contract in self.contracts}

        #create a new mapping in a polymorphic fashion
        new_mapping = type(self)(new_contracts.values())
        for (port_a, port_b) in self.mapping:
            new_mapping.add(new_contracts[port_a.contract].ports_dict[port_a.base_name],
                            new_contracts[port_b.contract].ports_dict[port_b.base_name])

        return (new_contracts, new_mapping)


PortMapping.register(RefinementMapping)

class ApproximationMapping(RefinementMapping):
    '''
    mapping for ApproximationMapping
    '''
    pass

class CompositionMapping(object):
    '''
    Collects the information abou port mapping during a contract composition.
    During composition, it may happen that two original contracts have ports
    with the same name.
    This class helps defining explicit relations between ports before and after
    composition
    '''

    def __init__(self, contracts, context=None):
        '''
        Init port mapping
        '''
        self.mapping = {}
        self.context = context
        try:
            self.contracts = set(contracts)
        except TypeError:
            #if contracts is a single element not in a list
            self.contracts = set()
            self.contracts.add(contracts)

    def _validate_port(self, port):
        '''
        raises an exception if port is not related to one of the mapped contract
        '''
        if port.contract not in self.contracts:
            raise PortMappingError()

    def add(self, port, mapped_base_name):
        '''
        Add the new constraint
        '''
        self._validate_port(port)

        #check that the port is not in the list with another name
        #if port in self.reverse_mapping:
        #    raise PortMappingError('Port already renamed')

        try:
            self.mapping[mapped_base_name].add(port)
        except KeyError:
            self.mapping[mapped_base_name] = set()
            self.mapping[mapped_base_name].add(port)

    def connect(self, port, other_port, mapped_name=None):
        '''
        Connects two ports.
        It means that the ports will be connected to the same
        new port
        '''
        self._validate_port(port)
        self._validate_port(other_port)

        if mapped_name is None:
            mapped_name = port.base_name

        self.add(port, mapped_name)
        self.add(other_port, mapped_name)

    def find_conflicts(self):
        '''
        detects possible name conflicts
        '''
        #find ports with same name
        #assuming that there are no ports with the same name in the same contract
        #this means that at most 2 ports have the same name

        list_of_names = [key for contract in self.contracts for key in contract.ports_dict]
        #take a name only if it is listed at least twice
        all_multiple_ports = set([x for x in list_of_names if list_of_names.count(x) >= 2])


        conflict_ports = {name: [contract.ports_dict[name]
                                 for contract in self.contracts if name in contract.ports_dict]
                          for name in all_multiple_ports}

        reverse_map = self.reverse_mapping

        fixed = set()
        for name in all_multiple_ports:
            #ports with conflincting name
            ports = conflict_ports[name]
            #conflicting names not in the mapping set
            missing_ports = [port for port in ports if port not in reverse_map]

            #if all ports are explicitely mapped, no problem:
            if len(missing_ports) == 0:
                fixed.add(name)
            #if only one port is missing, and the base name is not taken, we can fix it
            elif len(missing_ports) == 1 and name not in self.mapping:
                self.add(missing_ports[0], name)
                fixed.add(name)
            else:
                #raise PortMappingError()
                pass

        #LOG.debug('in find conflicts')
        #LOG.debug([conflict_ports[name] for name in all_multiple_ports - fixed])
        #LOG.debug(fixed)
        return [set(conflict_ports[name]) for name in all_multiple_ports - fixed]


    def define_composed_contract_ports(self):
        '''
        Identifies and defines the input and output ports of the composed
        contract.
        Raises an exception in case of conflicts.
        Ports mapped on the same port will be connected.
        In case of missing mapping, this method will try to automatically
        derive new contract ports in case of no conflict.
        '''

        new_input_ports = {}
        new_output_ports = {}

        #associate new var for performance (reverse_mapping is computed each time)
        reverse_map = self.reverse_mapping

        #returns a set of tuples
        conflict_set = self.find_conflicts()

        for port_set in conflict_set:
            if port_set > set(reverse_map.viewkeys()):
                #this means a conflict is not explicitely solved
                LOG.debug(['%s - %s' %(port.contract.base_name, port.base_name)
                           for port in (port_set - reverse_map.viewkeys())])
                LOG.debug(reverse_map)
                raise PortMappingError()

        #connect and check port consistency
        #LOG.debug(self.mapping)
        for (name, port_set) in self.mapping.viewitems():

            #we need to connects all the ports in port_set
            #error if we try to connect mulptiple outputs

            outputs = [port for port in port_set if port.is_output]

            if len(outputs) > 1:
                LOG.critical(name)
                for p in port_set:
                    LOG.critical(p.base_name)
                raise PortConnectionError('cannot connect multiple outputs')
            else:
                #merge port literals
                #LOG.debug([p.unique_name + ':'+p.l_type + ':'+p.literal.l_type for p in port_set])
                port = port_set.pop()
                for p in port_set:
                    port.merge(p)
                #port = reduce(lambda x, y: x.merge(y), port_set)

                if len(outputs) == 0:
                    #all inputs -> input
                    new_input_ports[name] = Port(name, l_type = port.l_type, literal=port.literal, context=self.context)
                else:
                    #1 output -> output
                    new_output_ports[name] = Port(name, l_type = port.l_type, literal=port.literal, context=self.context)


        #complete with implicit ports from contracts
        #we have disjoint ports or ports which have been previously connected
        #however we are sure, from the previous step, that there are not conflicting
        #port names
        input_pool = {name: Port(name, l_type = port.l_type, literal=port.literal, context=self.context)#port
                      for contract in self.contracts
                      for (name, port) in contract.input_ports_dict.viewitems()}

        output_pool = {name: Port(name, l_type = port.l_type, literal=port.literal, context=self.context)#port
                       for contract in self.contracts
                       for (name, port) in contract.output_ports_dict.viewitems()}



        mapped_ports = set([port.base_name for port in reverse_map])
        #LOG.debug(mapped_ports)

        implicit_input_names = input_pool.viewkeys() - mapped_ports
        implicit_output_names = output_pool.viewkeys() - mapped_ports

        filtered_inputs = implicit_input_names - implicit_output_names

        #LOG.debug(implicit_input_names)

        for name in filtered_inputs:
            #also, check for feedback loops or connected I/O and do not add inputs in case
            if not any([input_pool[name].is_connected_to(port) for port in output_pool.viewvalues()]):
                new_input_ports[name] = Port(name, l_type = input_pool[name].l_type, literal=input_pool[name].literal,
                                             context=self.context)
        for name in implicit_output_names:
            new_output_ports[name] = Port(name, l_type = output_pool[name].l_type, literal=output_pool[name].literal,
                                          context=self.context)


        #import pdb
        #pdb.set_trace()

        return (new_input_ports, new_output_ports)


    @property
    def reverse_mapping(self):
        '''
        Returns a dictionary with port as key and mapped name as value
        '''
        #LOG.debug(self.mapping.viewitems())
        return {port: name for (name, port_set) in self.mapping.viewitems() for port in port_set}

PortMapping.register(CompositionMapping)

class NonCompositeContractError(Exception):
    '''
    Raised when accessing the origin_contract property
    but contract is not obtained as a composition of others
    '''
    pass

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


class NotARefinementError(Exception):
    '''
    Raised in case of wrong refinement assertion
    '''
    pass

class NotAnApproximationError(Exception):
    '''
    Raised in case of wrong approximation assertion
    '''
    pass

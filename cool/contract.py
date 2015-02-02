'''
Basic implementation of contract

Author: Antonio Iannopollo
'''

from cool.parser.parser import Parser
from cool.parser.lexer import BaseSymbolSet
from cool.attribute import Attribute
from cool.formula import Literal
from cool.observer import Observer

class Contract(Observer):
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
            guarantee_formula, symbol_set_cls = BaseSymbolSet, context = None):
        '''
        Instantiate a contract.

        :param base_name: a name for the contract. If the name is not unique,
        a unique name will be provided as an Attribute
        :type base_name: string
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
        :param symbol_set_cls: symbol set class, used to decode furmula strings
        and to generate string representation of LTLFormula objects
        :type symbol_set_cls: class, preferably extending
        cool.parser.lexer.BaseSymbolSet
        :param context: fomrula context for unique variable naming
        :type context: object
        '''

        self.parser = Parser()

        self.symbol_set_cls = symbol_set_cls
        self.context = context

        #define attribute name for the contract
        self.name_attribute = Attribute(base_name, self.context)


        #cleanup input and output lists/sets
        input_ports = set(input_ports)
        output_ports = set(output_ports)

        #first, we need to retrieve formulas and literals from formulas
        #possibilities are that formulae will be either string or LTLFormula
        #object
        #Let's assume they are string, then LTLFormula objects
        #Also, in case they are strings, we need to insure that the same
        #literal in either formula is associated to the same attribute.
        #This means the context of both formulae is the current Contract obj
        try:
            self.assume_formula = self.parser.parse(assume_formula,
                    context = self.context, symbol_set_cls = symbol_set_cls)
        except TypeError:
            #the formula is not a string, we assume is a LTLFormula object
            self.assume_formula = assume_formula

        try:
            self.guarantee_formula = self.parser.parse(guarantee_formula,
                    context = self.context, symbol_set_cls = symbol_set_cls)
        except TypeError:
            self.guarantee_formula = guarantee_formula

        #we need to make sure there are not ports which are both input and
        #output
        if not input_ports.isdisjoint(output_ports):
            raise PortDeclarationError(input_ports & output_ports)

        #now we need to check that the declared input and output ports
        #match the formulae.
        #It is possible, however, that some ports are not mentioned at all
        #in the formulae (meaning no costraints on values), or that both
        #input and output ports are mentioned as literal in either assume
        #or guarantee formulae.
        #What we can do, is making sure that there are not literals in
        #assumptions and guarantees which do not match ports

        current_literal_items_dict = dict( \
                                self.assume_formula.get_literal_items() | \
                                self.guarantee_formula.get_literal_items() )

        contract_ports = input_ports | output_ports

        if not current_literal_items_dict.viewkeys() <= contract_ports:
            raise PortMappingError( \
                    current_literal_items_dict.viewkeys() - contract_ports)

        #the contract has to mantain a detailed list of ports.
        #It means that it needs to be an observer of literals in formulae
        #and it needs to create new attributes for ports which are not mentioned
        #in formulae

        #create two dictionaries for contract ports, and initialize to None
        self.input_ports_dict = {key : None for key in input_ports}
        self.output_ports_dict = {key: None for key in output_ports}

        #process input and outport ports
        for literal_name in input_ports | output_ports:
            #port lookup looks for the correct dictionary
            port_dict = self.port_lookup(literal_name)

            if literal_name in current_literal_items_dict:
                port_dict[literal_name] = \
                        current_literal_items_dict[literal_name]
            else:
                port_dict[literal_name] = \
                        Literal(literal_name, self.context)

            #observer pattern - attach to the subject
            port_dict[literal_name].attach(self)
        
    def compose(self, other_contract, connection_list = []):
        '''
        Compose the current contract with the one passed as a parameter.
        The operations to be done are: 
        
        :param other_contract: contract to be used for composition
        :type other_contract: Contract
        :param connection_list: optional list of pairs of base_names specifying the ports to be connected
        :type connection_list: list of tuples (pairs)
        '''

    def connect_to_port(self, port_name, other_contract, other_port_name):
        '''
        Connect a port of the current contract with a port of another contract.
        The only constraint is that we cannot connect two output ports.
        
        :param port_name: base name of the current contract port
        :type port_name: string
        :param other_contract: contract to be connected to
        :type other_contract: Contract object
        :param other_port_name: name of the port to be connected to
        :type other_port_name: string
        '''
        
        assert 
        
        

    def __str__(self):
        '''
        Defining print representation for a contract
        '''
        description = []
        description.append('Contract %s ( %s )\n' % \
            ( self.name_attribute.unique_name, self.name_attribute.base_name ) )

        description.append('\tInput ports:\n')

        for base_name, port in self.input_ports_dict.items():

            description.append('\t\t%s ( %s )\n' % \
                    (port.unique_name, base_name ) )

        description.append('\tOutput ports:\n')

        for base_name, port in self.output_ports_dict.items():
            description.append('\t\t%s ( %s )\n' % \
                    (port.unique_name, base_name ) )

        description.append('\tAssumption\n')
        description.append('\t\t%s\n' % \
                self.assume_formula.generate(self.symbol_set_cls))

        description.append('\tGuarantee\n')
        description.append('\t\t%s\n' % \
                self.guarantee_formula.generate(self.symbol_set_cls))

        return ''.join(description)

    def update(self, updated_subject):
        '''
        Implementation of the update method from a attribute according to
        the observer pattern
        '''

        updated_literal = updated_subject.get_state()
        updated_name = updated_literal.base_name

        if updated_name not in self.port_names:
            raise KeyError('attribute not in literals dict for the furmula')

        #attach to the new literal
        updated_literal.attach(self)

        #detach from the current literal
        self.ports_dict[ updated_name ].detach()

        #update the literals list
        port_dict = self.port_lookup(updated_name)
        port_dict[ updated_name] = updated_literal


    def port_lookup(self, literal_name):
        '''
        Given a literal name, returns the dictionary (either input or output)
        in which it is defined
        '''

        if literal_name in self.input_ports_dict.viewkeys():
            port_dict =  self.input_ports_dict
        elif literal_name in self.output_ports_dict.viewkeys():
            port_dict = self.output_ports_dict
        else:
            raise KeyError('port not defined for literal %s' % literal_name)

        return port_dict

    def getport_names(self):
        '''
        get method of property port_names.
        Returns an updated set of port names
        '''
        return self.input_ports_dict.viewkeys() | self.output_ports_dict.viewkeys()

    port_names = property(fget = getport_names, doc = 'set of contract port names')

    def getports_dict(self):
        '''
        Get method of property ports_dict.
        Return an update dict of all the contract ports
        '''
        return dict( self.input_ports_dict.items() + \
                        self.output_ports_dict.items() )

    ports_dict = property(fget = getports_dict, doc = 'a single dictionary \
                    containing both input and output ports')

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
    
    

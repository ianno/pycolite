'''
This module inlcudes all the classes and operations related to ltl3ba

Author: Antonio Iannopollo
'''

from pyco.interface_strategy import RefinementStrategy, \
            CompatibilityStrategy, ConsistencyStrategy
from tempfile import NamedTemporaryFile
from subprocess import check_output
from pyco.formula import Negation, Implication
from pyco.symbol_sets import Ltl3baSymbolSet
from ConfigParser import SafeConfigParser
from pyco.util.util import CONFIG_FILE_RELATIVE_PATH, TOOL_SECT, LTL3BA_OPT
import os
from pyco import LOG

TEMP_FILES_PATH = '/tmp/'
#LTL3BA_PATH = 'resources/ltl3ba/'
LTL3BA_FALSE = 'T0_init:\n\tfalse;\n}\n'

class Ltl3baPathLoader(object):
    '''
    Loads ltl3ba path from config file the first time
    it is called,
    '''
    ltl3ba_path = None

    @classmethod
    def get_path(cls):
        '''
        gets the path
        '''
        if cls.ltl3ba_path is None:

            here = os.path.abspath(os.path.dirname(__file__))

            config_path = os.path.join(here, os.pardir, CONFIG_FILE_RELATIVE_PATH)

            config = SafeConfigParser()
            filep = open(config_path)

            config.readfp(filep)

            cls.ltl3ba_path = config.get(TOOL_SECT, LTL3BA_OPT)

        return cls.ltl3ba_path


def verify_tautology(formula, prefix='',
                     tool_location=Ltl3baPathLoader.get_path(),
                     delete_file=True):
    '''
    Verifies if a LTLFormula object represents a tautology
    '''

    #to check if formula implication is valid, we negate it
    #and check that the negation is an empty automaton
    n_formula = Negation(formula)

    return is_empty_formula(n_formula, prefix=prefix, \
            tool_location=tool_location, delete_file=delete_file)

def is_empty_formula(formula, prefix='',
                     tool_location=Ltl3baPathLoader.get_path(),
                     delete_file=True):
    '''
    Verifies if a LTLFormula object represents an empty formula
    '''

    temp_file = NamedTemporaryFile( \
            prefix='%s' % prefix,
            dir=TEMP_FILES_PATH, suffix='.ltl', delete=delete_file)

    with temp_file:
        formula_str = formula.generate(symbol_set=Ltl3baSymbolSet, \
                ignore_precedence=True)

        temp_file.write(formula_str)
        temp_file.seek(0)

        output = check_output([tool_location, '-F', temp_file.name])

        if output.endswith(LTL3BA_FALSE):
            return True
        else:
            #LOG.debug(output)
            return False

class Ltl3baContractInterface(object):
    '''
    Base class to interface a contract with ltl3ba
    '''

    def __init__(self, contract, tool_location=Ltl3baPathLoader.get_path()):
        '''
        constructor. Loads the basic information on how to locate
        and launch the script
        '''
        self.contract = contract
        self.tool_location = tool_location


class Ltl3baRefinementStrategy(Ltl3baContractInterface):
    '''
    Interface with ltl3ba for refinement check
    '''

    def __init__(self, contract, tool_location=Ltl3baPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(Ltl3baRefinementStrategy, self).__init__(contract, tool_location)

    def check_refinement(self, abstract_contract):
        '''
        Override of abstract method
        '''
        contract_name = self.contract.name_attribute.unique_name
        #create formulae to be checked
        assumption_check_formula = self._get_assumptions_check_formula(abstract_contract)
        guarantee_check_formula = self._get_guarantee_check_formula(abstract_contract)

        #check assumptions
        output = verify_tautology(assumption_check_formula, \
                    prefix='%s_assumptions_ltl3ba_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)
        if output:
            #check guarantees
            #LOG.debug('assumptions are ok')
            #LOG.debug(assumption_check_formula.generate())
            output = verify_tautology(guarantee_check_formula, \
                    prefix='%s_guarantees_ltl3ba_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)


        return output

    def _get_assumptions_check_formula(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_assume = abstract_contract.assume_formula
        refining_assume = self.contract.assume_formula

        return Implication(abstract_assume, refining_assume, merge_literals=False)

    def _get_guarantee_check_formula(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_guarantee = abstract_contract.guarantee_formula
        refining_guarantee = self.contract.guarantee_formula

        return Implication(refining_guarantee, abstract_guarantee, merge_literals=False)


RefinementStrategy.register(Ltl3baRefinementStrategy)


class Ltl3baCompatibilityStrategy(Ltl3baContractInterface):
    '''
    Defines an object used to check compatibility of a contract
    interfacing with ltl3ba
    '''
    def __init__(self, contract, tool_location=Ltl3baPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(Ltl3baCompatibilityStrategy, self).__init__(contract, tool_location)


    def check_compatibility(self):
        '''
        Override from CompatibilityStrategy
        '''

        contract_name = self.contract.name_attribute.unique_name

        return not is_empty_formula(self.contract.assume_formula, \
                prefix='%s_compatibility_ltl3ba_' % contract_name, \
                tool_location=self.tool_location, \
                delete_file=self.delete_files)


CompatibilityStrategy.register(Ltl3baCompatibilityStrategy)


class Ltl3baConsistencyStrategy(Ltl3baContractInterface):
    '''
    Defines an object used to check consistency of a contract
    interfacing with ltl3ba
    '''
    def __init__(self, contract, tool_location=Ltl3baPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(Ltl3baConsistencyStrategy, self).__init__(contract, tool_location)

    def check_consistency(self):
        '''
        Override from ConsistencyStrategy
        '''

        contract_name = self.contract.name_attribute.unique_name

        return not is_empty_formula(self.contract.guarantee_formula, \
                prefix='%s_consistency_ltl3ba_' % contract_name, \
                tool_location=self.tool_location, \
                delete_file=self.delete_files)


ConsistencyStrategy.register(Ltl3baConsistencyStrategy)


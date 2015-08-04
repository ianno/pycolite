'''
This module inlcudes all the classes and operations related to nuxmv

Author: Antonio Iannopollo
'''

from pyco.interface_strategy import (RefinementStrategy,
            CompatibilityStrategy, ConsistencyStrategy)
from tempfile import NamedTemporaryFile
from subprocess import check_output
from pyco.formula import Negation, Implication
from pyco.symbol_sets import NusmvSymbolSet
from ConfigParser import SafeConfigParser
from pyco.util.util import CONFIG_FILE_RELATIVE_PATH, TOOL_SECT, NUXMV_OPT
import os
from pyco import LOG

#OPT_NUXMV = '-coi'
CMD_OPT = '-dcx'

#trace delimiters
#TR_INIT = 'Trace Type: Counterexample'
#TR_COMMENT = '--'
#TR_STATE = '->'

MODULE_TEMPLATE = '''
MODULE main()
    VAR
    %s

LTLSPEC (

%s

);
'''

TEMP_FILES_PATH = '/tmp/'
NUXMV_FALSE = 'is false\n'

def trace_parser(trace):
    '''
    Parses the output of nuxmv and give a list of the involved variables/contracts
    '''
    pass

class NuxmvPathLoader(object):
    '''
    Loads nuxmv path from config file the first time
    it is called,
    '''
    nuxmv_path = None

    @classmethod
    def get_path(cls):
        '''
        gets the path
        '''
        if cls.nuxmv_path is None:

            here = os.path.abspath(os.path.dirname(__file__))

            config_path = os.path.join(here, os.pardir, CONFIG_FILE_RELATIVE_PATH)

            config = SafeConfigParser()
            filep = open(config_path)

            config.readfp(filep)

            cls.nuxmv_path = config.get(TOOL_SECT, NUXMV_OPT)

        return cls.nuxmv_path

def is_empty_formula(formula, prefix='',
                     tool_location=NuxmvPathLoader.get_path(),
                     delete_file=True):
    '''
    Verifies if a LTLFormula object represents an empty formula
    '''

    #to check if formula implication is valid, we negate it
    #and check that the negation is an empty automaton
    n_formula = Negation(formula)

    return verify_tautology(n_formula, prefix=prefix, \
            tool_location=tool_location, delete_file=delete_file)

def verify_tautology(formula, prefix='',
                     tool_location=NuxmvPathLoader.get_path(),
                     delete_file=True):
    '''
    Verifies if a LTLFormula object represents a tautology
    '''

    temp_file = NamedTemporaryFile( \
            prefix='%s' % prefix,
            dir=TEMP_FILES_PATH, suffix='.smv', delete=delete_file)

    formula_str = formula.generate(symbol_set=NusmvSymbolSet, \
                ignore_precedence=True)

    literals = [l for (_, l) in formula.get_literal_items()]
    #LOG.debug(literals)
    var_list = ['\t%s: boolean;\n' %l.unique_name for l in literals]
    var_str = ''.join(var_list)

    with temp_file:


        #LOG.debug(MODULE_TEMPLATE % (var_str, formula_str))

        temp_file.write(MODULE_TEMPLATE % (var_str, formula_str))
        temp_file.seek(0)

        output = check_output([tool_location, CMD_OPT, temp_file.name])
        #LOG.debug(output)
        #LOG.debug(output.endswith(NUXMV_FALSE))
        if output.endswith(NUXMV_FALSE):
            return False
        else:
            #LOG.debug(output)
            return True

class NuxmvContractInterface(object):
    '''
    Base class to interface a contract with nuxmv
    '''

    def __init__(self, contract, tool_location=NuxmvPathLoader.get_path()):
        '''
        constructor. Loads the basic information on how to locate
        and launch the script
        '''
        self.contract = contract
        self.tool_location = tool_location


class NuxmvRefinementStrategy(NuxmvContractInterface):
    '''
    Interface with nuxmv for refinement check
    '''

    def __init__(self, contract, tool_location=NuxmvPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(NuxmvRefinementStrategy, self).__init__(contract, tool_location)

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
                    prefix='%s_assumptions_nuxmv_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)

        #LOG.debug('assumptions are ok')
        #LOG.debug(assumption_check_formula.generate())
        if output:
            #check guarantees
            output = verify_tautology(guarantee_check_formula, \
                    prefix='%s_guarantees_nuxmv_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)

            #LOG.debug('guarantees')
            #LOG.debug(guarantee_check_formula.generate())

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


RefinementStrategy.register(NuxmvRefinementStrategy)


class NuxmvCompatibilityStrategy(NuxmvContractInterface):
    '''
    Defines an object used to check compatibility of a contract
    interfacing with nuxmv
    '''
    def __init__(self, contract, tool_location=NuxmvPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(NuxmvCompatibilityStrategy, self).__init__(contract, tool_location)


    def check_compatibility(self):
        '''
        Override from CompatibilityStrategy
        '''

        contract_name = self.contract.name_attribute.unique_name

        return not is_empty_formula(self.contract.assume_formula, \
                prefix='%s_compatibility_nuxmv_' % contract_name, \
                tool_location=self.tool_location, \
                delete_file=self.delete_files)


CompatibilityStrategy.register(NuxmvCompatibilityStrategy)


class NuxmvConsistencyStrategy(NuxmvContractInterface):
    '''
    Defines an object used to check consistency of a contract
    interfacing with nuxmv
    '''
    def __init__(self, contract, tool_location=NuxmvPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(NuxmvConsistencyStrategy, self).__init__(contract, tool_location)

    def check_consistency(self):
        '''
        Override from ConsistencyStrategy
        '''

        contract_name = self.contract.name_attribute.unique_name
        return not is_empty_formula(self.contract.guarantee_formula, \
                prefix='%s_consistency_nuxmv_' % contract_name, \
                tool_location=self.tool_location, \
                delete_file=self.delete_files)


ConsistencyStrategy.register(NuxmvConsistencyStrategy)


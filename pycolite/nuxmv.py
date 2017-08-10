'''
This module inlcudes all the classes and operations related to nuxmv

Author: Antonio Iannopollo
'''

from pycolite.interface_strategy import (RefinementStrategy,
            CompatibilityStrategy, ConsistencyStrategy, ApproximationStrategy)
from tempfile import NamedTemporaryFile
from subprocess import check_output, STDOUT
from pycolite.formula import Negation, Implication, Conjunction
from pycolite.symbol_sets import NusmvSymbolSet
from ConfigParser import SafeConfigParser
from pycolite.util.util import CONFIG_FILE_RELATIVE_PATH, TOOL_SECT, NUXMV_OPT
import os
from pycolite import LOG
from pycolite.types import Bool, Int

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
NUXMV_TRUE = 'is true\n'

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
                     delete_file=True,
                     return_trace=False):
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
    var_list = []
    for l in literals:
        if isinstance(l.l_type, Bool):
            var_list.append('\t%s: boolean;\n' %l.unique_name)
        elif isinstance(l.l_type, Int):
            var_list.append('\t%s: %d..%d;\n' % (l.unique_name, l.l_type.lower, l.l_type.upper))

    var_list = set(var_list)
    #var_list = set(['\t%s: boolean;\n' %l.unique_name for l in literals])
    var_str = ''.join(var_list)

    with temp_file:


        LOG.debug(MODULE_TEMPLATE % (var_str, formula_str))

        temp_file.write(MODULE_TEMPLATE % (var_str, formula_str))
        temp_file.seek(0)

        #output = check_output([tool_location, CMD_OPT, temp_file.name])
        output = check_output([tool_location, temp_file.name],
                              stderr=STDOUT,)
        #LOG.debug(output)
        #LOG.debug(output.endswith(NUXMV_FALSE))
        if output.endswith(NUXMV_TRUE):
            val = True
        else:
            #LOG.debug(output)
            val = False

        if return_trace:
            return val, output
        else:
            return val

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
        both_formulas = self.get_refinement_formula(abstract_contract)

        #check both formulas
        output = verify_tautology(both_formulas, \
                    prefix='%s_assumptions_nuxmv_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)


        return output

    def get_refinement_formula(self, abstract_contract):
        '''
        returns the formual object to be verified
        :param abstract_contract:
        :return:
        '''

        # create formulae to be checked
        assumption_check_formula = self._get_assumptions_check_formula(abstract_contract)
        guarantee_check_formula = self._get_guarantee_check_formula(abstract_contract)

        both_formulas = Conjunction(assumption_check_formula, guarantee_check_formula,
                                    merge_literals=False)

        return both_formulas

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


class NuxmvApproximationStrategy(NuxmvContractInterface):
    '''
    Interface with nuxmv for approximation check
    '''

    def __init__(self, contract, tool_location=NuxmvPathLoader.get_path(), delete_files=True):
        '''
        override constructor
        '''
        self.delete_files = delete_files

        super(NuxmvApproximationStrategy, self).__init__(contract, tool_location)

    def check_approximation(self, more_defined_contract):
        '''
        Override of abstract method
        '''
        contract_name = self.contract.name_attribute.unique_name
        #create formulae to be checked
        assumption_check_formula = self._get_assumptions_check_formula(more_defined_contract)
        guarantee_check_formula = self._get_guarantee_check_formula(more_defined_contract)


        both_formulas = Conjunction(assumption_check_formula, guarantee_check_formula)

        #check both formulas
        output = verify_tautology(both_formulas, \
                    prefix='%s_assumptions_nuxmv_' % contract_name, \
                    tool_location=self.tool_location, \
                    delete_file=self.delete_files)


        return output

    def _get_assumptions_check_formula(self, more_defined_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        more_defined_contract.assumption -> approximate_contract.assumption
        '''

        more_defined_assume = more_defined_contract.assume_formula
        approximate_assume = self.contract.assume_formula

        return Implication(more_defined_assume, approximate_assume, merge_literals=False)

    def _get_guarantee_check_formula(self, more_defined_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        more_defined_contract.assumption -> approximate_contract.assumption
        '''

        more_defined_guarantee = more_defined_contract.guarantee_formula
        approximate_guarantee = self.contract.guarantee_formula

        return Implication(more_defined_guarantee, approximate_guarantee, merge_literals=False)


ApproximationStrategy.register(NuxmvApproximationStrategy)

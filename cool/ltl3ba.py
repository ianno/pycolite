'''
This module inlcudes all the classes and operations related to ltl3ba

Author: Antonio Iannopollo
'''

from cool.refinement_strategy import RefinementStrategy
from tempfile import NamedTemporaryFile
from subprocess import check_output
from cool.formula import Negation, Implication
from cool.symbol_sets import Ltl3baSymbolSet
from re import sub

TEMP_FILES_PATH = 'resources/temp/'
LTL3BA_PATH = 'resources/ltl3ba/'
LTL3BA_FALSE = 'T0_init:\n\tfalse;\n}\n'


class Ltl3baRefinementStrategy(object):
    '''
    Interface with ltl3ba for refinement check
    '''

    def __init__(self, refining_contract, tool_location=LTL3BA_PATH, exec_name='ltl3ba'):
        '''
        constructor. Loads the basic information on how to locate
        and launch the script
        '''
        self.refining_contract = refining_contract
        self.tool_location = tool_location
        self.exec_name = exec_name

    def check_refinement(self, abstract_contract, delete_files=True):
        '''
        Override of abstract method
        '''
        #create temp files
        contract_name = self.refining_contract.name_attribute.unique_name

        #create formulae to be checked
        assumption_check_formula = self._get_assumptions_check_formula(abstract_contract)
        guarantee_check_formula = self._get_guarantee_check_formula(abstract_contract)

        #check assumptions
        output = verify_tautology(assumption_check_formula, \
                    prefix='%s_assumptions_ltl3ba_' % contract_name, \
                    tool_location=self.tool_location, \
                    exec_name=self.exec_name,
                    delete_file=delete_files)
        if output:
            #check guarantees
            output = verify_tautology(guarantee_check_formula, \
                    prefix='%s_guarantees_ltl3ba_' % contract_name, \
                    tool_location=self.tool_location,
                    exec_name=self.exec_name,
                    delete_file=delete_files)


        return output

    def _get_assumptions_check_formula(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_assume = abstract_contract.assume_formula
        refining_assume = self.refining_contract.assume_formula

        return Implication(abstract_assume, refining_assume)

    def _get_guarantee_check_formula(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_guarantee = abstract_contract.guarantee_formula
        refining_guarantee = self.refining_contract.guarantee_formula

        return Implication(refining_guarantee, abstract_guarantee)


def verify_tautology(formula, prefix='', tool_location=LTL3BA_PATH, \
                                exec_name='ltl3ba', delete_file=True):
    '''
    Verifies if a LTLFormula object represents a tautology
    '''

    #to check if formula implication is valid, we negate it
    #and check that the negation is an empty automaton

    n_formula = Negation(formula)

    temp_file = NamedTemporaryFile( \
            prefix='%s' % prefix,
            dir=TEMP_FILES_PATH, suffix='.ltl', delete=delete_file)

    ltl3ba_location = tool_location + exec_name

    with temp_file:
        formula_str = n_formula.generate(symbol_set=Ltl3baSymbolSet, \
                ignore_precedence=True)

        temp_file.write(formula_str)
        temp_file.seek(0)

        output = check_output([ltl3ba_location, '-F', temp_file.name])

        if output.endswith(LTL3BA_FALSE):
            return True
        else:
            print output
            return False





RefinementStrategy.register(Ltl3baRefinementStrategy)


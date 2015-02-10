'''
This module inlcudes all the classes and operations related to ltl3ba

Author: Antonio Iannopollo
'''

from cool.refinement_strategy import RefinementStrategy
from tempfile import NamedTemporaryFile
from subprocess import check_output
from cool.formula import Negation, Implication
from cool.symbol_sets import SpinSymbolSet
from re import sub

TEMP_FILES_PATH = 'resources/temp/'
LTL3BA_PATH = 'resources/ltl3ba/'
LTL3BA_FALSE = '''T0_init:\n    false;\n}\n0\n'''


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
        assumption_file = NamedTemporaryFile( \
                prefix='%s_assumptions_ltl3ba_' % contract_name, \
                dir=TEMP_FILES_PATH, suffix='.ltl', delete=delete_files)
        guarantee_file = NamedTemporaryFile( \
                prefix='%s_guarantees_ltl3ba_' % contract_name,
                dir=TEMP_FILES_PATH, suffix='.ltl', delete=delete_files)

        #create formulae to be checked
        assumption_str = self._get_assumptions_check_str(abstract_contract)
        guarantee_str = self._get_guarantee_check_str(abstract_contract)

        ltl3ba_location = self.tool_location + self.exec_name

        #check assumptions
        with assumption_file:
            assumption_file.write(assumption_str)
            assumption_file.seek(0)

            output = check_output([ltl3ba_location, '-F', assumption_file.name])

        #to check if formula implication is valid, we negate it
        #and check that the negation is an empty automaton
        if output.endswith(LTL3BA_FALSE):
            #check guarantees

            with guarantee_file:

                guarantee_file.write(guarantee_str)
                guarantee_file.seek(0)

                output = check_output([ltl3ba_location, '-F', guarantee_file.name])

            if output.endswith(LTL3BA_FALSE):
                return True
        return False

    def _get_assumptions_check_str(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_assume = abstract_contract.assume_formula
        refining_assume = self.refining_contract.assume_formula

        return self._create_ltl3ba_str(abstract_assume, refining_assume)

    def _get_guarantee_check_str(self, abstract_contract):
        '''
        Returns a string representing the implication of the two contracts
        assumptions:
        abstract_contract.assumption -> refining_contract.assumption
        '''

        abstract_guarantee = abstract_contract.guarantee_formula
        refining_guarantee = self.refining_contract.guarantee_formula

        return self._create_ltl3ba_str(refining_guarantee, abstract_guarantee)


    def _create_ltl3ba_str(self, left_formula, right_formula):
        '''
        Create the negation of an implication given the left
        and right formulae
        '''

        implication = Implication(left_formula, right_formula)
        negation = Negation(implication)

        check_str = negation.generate(symbol_set=SpinSymbolSet)

        #make sure file is on a single line and all variables are lowercase
        #(required by ltl3ba)
        #check_str = check_str.lower()
        check_str = check_str.replace('\n', '')
        check_str = check_str.replace('\r', '')
        check_str = sub(' +', ' ', check_str)

        return check_str


RefinementStrategy.register(Ltl3baRefinementStrategy)

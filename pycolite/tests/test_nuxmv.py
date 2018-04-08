'''
This module takes care of Contract class related tests

author: Antonio Iannopollo
'''

import pytest
from pycolite.nuxmv import ltl2smv
from pycolite.parser.parser import Parser, GeneralError

from pycolite import LOG

@pytest.fixture()
def a_formula():
    '''
    a formula
    '''
    p = Parser()
    formula = "hello + 2  | test -> h & Xe & (v|e & (sss -> q)) & x|y | G(this & (is) | a & !X(correct & formula)) -> F(everything & is | fine)"
    return p.parse(formula)


def test_formula(a_formula):
    literals = [l for (_, l) in a_formula.get_literal_items()]
    LOG.debug('test ltl2smv')
    LOG.debug(ltl2smv(a_formula, '3', literals[:2], literals[2:]))

    assert True


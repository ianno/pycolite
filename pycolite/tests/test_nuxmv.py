'''
This module takes care of Contract class related tests

author: Antonio Iannopollo
'''

import pytest
from pycolite.nuxmv import ltl2smv, verify_tautology
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

@pytest.fixture()
def b_formula():
    '''
    b formula
    '''
    p = Parser()
    formula = """
                (
                    G( 
                        ( p -> X(v & !t)  ) & 
                        ( !p -> X(!v & t) ) & 
                        ( v -> X(!w0 & z) ) & 
                        ( !v -> X(w0 & !z)) 
                    )
                    & 
                    G( 
                        ( p -> X(v0 & !t0) ) & 
                        ( !p -> X(!v0 & t0)) & 
                        ( v0 -> X(!w & z0) ) & 
                        ( !v0 -> X(w & !z0))
                    )  
                ) 
                -> 
                G( 
                    ( p -> X( v & !t) ) & 
                    (!p -> X(!v &  t) ) & 
                    ( v -> X(!w &  z) ) & 
                    (!v -> X( w & !z) ) 
                )
                    """
    return p.parse(formula)


def test_b_formula(b_formula):
    literals = [l for (_, l) in b_formula.get_literal_items()]
    LOG.debug('test ltl2smv')
    l_passed, trace = verify_tautology(b_formula, return_trace=True, delete_file=False)
    assert(not l_passed)
    LOG.critical(l_passed)    
    LOG.critical(trace)

    assert True

@pytest.fixture()
def c_formula():
    '''
    c formula
    '''
    p = Parser()
    formula = """
                ( 
                    G((v <-> v0) & (t <-> t0) )  |  G( (v <-> v0) & (z <-> z0))  |  G((t <-> t0) & (z <-> z0)) 
                )
                -> 
                ( 
                    (
                        G( 
                            ( p -> X(v & !t)  ) & 
                            ( !p -> X(!v & t) ) & 
                            ( v -> X(!w0 & z) ) & 
                            ( !v -> X(w0 & !z)) 
                        )
                        & 
                        G( 
                            ( p -> X(v0 & !t0) ) & 
                            ( !p -> X(!v0 & t0)) & 
                            ( v0 -> X(!w & z0) ) & 
                            ( !v0 -> X(w & !z0))
                        )  
                    ) 
                    -> 
                    G( 
                        ( p -> X( v & !t) ) & 
                        (!p -> X(!v &  t) ) & 
                        ( v -> X(!w &  z) ) & 
                        (!v -> X( w & !z) ) 
                    )
                )
                    """
    return p.parse(formula)


def test_c_formula(c_formula):
    literals = [l for (_, l) in c_formula.get_literal_items()]
    LOG.debug('test ltl2smv')
    l_passed, trace = verify_tautology(b_formula, return_trace=True)
    assert(l_passed)
'''
This module takes care of Contract class related tests

author: Antonio Iannopollo
'''

import pytest
from cool.contract import Contract, PortDeclarationError, PortMappingError

@pytest.fixture()
def basic_params():
    '''
    Define a very simnple contract set of parameters.
    two inputs, two outputs, and two simple formulas
    '''
    input_ports = set(['a', 'b'])
    output_ports = ['c', 'd']
    assume_formula = 'G(a) | F(b)'
    guarantee_formula = 'GF(X(c | d))'

    return (input_ports, output_ports, assume_formula, guarantee_formula)

def test_constructor(basic_params):
    '''
    test basic Contract constructor, no errors expected
    '''
    contract = Contract('C', basic_params[0], basic_params[1], basic_params[2], basic_params[3])
    assert True

@pytest.fixture()
def wrong_ports():
    '''
    returns a faulty set of parameters, in which a port is both input
    and output
    '''
    params = basic_params()
    params[1].append('b')
    return params

def test_wrong_ports(wrong_ports):
    '''
    expects a PortDeclarationError exception
    '''
    with pytest.raises(PortDeclarationError):
        contract = Contract('C', wrong_ports[0], wrong_ports[1], wrong_ports[2], wrong_ports[3])

@pytest.fixture()
def wrong_mapping():
    '''
    returns a faulty set of parameters, in which a port is both input
    and output
    '''
    params = basic_params()
    params[0].remove('b')
    return params

def test_wrong_mapping(wrong_mapping):
    '''
    expects a PortMappingError exception
    '''
    with pytest.raises(PortMappingError):
        contract = Contract('C', wrong_mapping[0], wrong_mapping[1], wrong_mapping[2], wrong_mapping[3])

'''
This module takes care of Contract class related tests

author: Antonio Iannopollo
'''

import pytest
from cool.contract import Contract, PortDeclarationError, PortMappingError, \
                        PortConnectionError

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
def contract_1():
    input_p = set(('a','b','c'))
    output_p = set(('d', 'e'))

    assume = 'X(b) -> FX!(G(a|b) & F(c))'
    guarantee = 'd & XXXc -> GF(e&d)'

    return Contract('C1', input_p, output_p, assume, guarantee)

@pytest.fixture()
def contract_2():
    input_p = set(('f','b','c'))
    output_p = set(('g', 'e'))

    assume = 'G(f & Xb | XXc)'
    guarantee = 'F(g|e)'

    return Contract('C2', input_p, output_p, assume, guarantee)



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



def test_print(basic_params):
    '''
    Test print function of two identical contracts
    '''
    contract = Contract('C', basic_params[0], basic_params[1], basic_params[2], basic_params[3])
    print contract

    contract2 = Contract('C', basic_params[0], basic_params[1], basic_params[2], basic_params[3])
    print contract2
    assert True

def test_composition_no_common(contract_1, contract_2):
    '''
    test composition of two contracts
    '''
    print 'no common ports'
    print 'before composition'
    print contract_1
    print contract_2

    contract_3 = contract_1.compose(contract_2)

    print contract_3

    assert len(contract_3.input_ports_dict) == \
            len(contract_1.input_ports_dict) + len(contract_2.input_ports_dict)

    assert len(contract_3.output_ports_dict) == \
            len(contract_1.output_ports_dict) + \
            len(contract_2.output_ports_dict)

    for port in contract_1.ports_dict.viewvalues():
        assert port.unique_name not in \
                [p.unique_name for p in contract_2.ports_dict.viewvalues()]

    for port in contract_2.ports_dict.viewvalues():
        assert port.unique_name not in \
                [p.unique_name for p in contract_1.ports_dict.viewvalues()]


def test_composition(contract_1, contract_2):
    '''
    test composition of two contracts
    '''
    print 'merge (b, b) and (a, g)'
    print 'before composition'
    print contract_1
    print contract_2

    contract_3 = contract_1.compose(contract_2, connection_list = \
            (('a', 'g'), ('b', 'b')))

    print contract_3

    print 'after_composition'
    print contract_1
    print contract_2

    #a is not input anymore and b is merged
    assert len(contract_3.input_ports_dict) == \
            len(contract_1.input_ports_dict) + \
            len(contract_2.input_ports_dict) - 2

    assert len(contract_3.output_ports_dict) == \
            len(contract_1.output_ports_dict) + \
            len(contract_2.output_ports_dict)

    for port in contract_1.ports_dict.viewvalues():
        if port.base_name not in ('a', 'b'):
            assert port.unique_name not in \
                [p.unique_name for p in contract_2.ports_dict.viewvalues()]
        else:
            assert port.unique_name in \
                [p.unique_name for p in contract_2.ports_dict.viewvalues()]

    for port in contract_2.ports_dict.viewvalues():
        if port.base_name not in ('g', 'b'):
            assert port.unique_name not in \
                [p.unique_name for p in contract_1.ports_dict.viewvalues()]
        else:
            assert port.unique_name in \
                [p.unique_name for p in contract_1.ports_dict.viewvalues()]

def test_out_to_out(contract_1, contract_2):
    '''
    try to compose a contract connecting two outputs
    '''

    with pytest.raises(PortConnectionError):
         contract_3 = contract_1.compose(contract_2, connection_list = \
            [('e', 'g')])












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
    contract = Contract('C', basic_params[0],
            basic_params[1], basic_params[2], basic_params[3], saturated = False)
    assert True

@pytest.fixture()
def contract_1():
    input_p = set(('a','b','c'))
    output_p = set(('d', 'e'))

    assume = 'X(b) -> FX!(G(a|b) & F(c))'
    guarantee = 'd & XXXc -> GF(e&d)'

    return Contract('C1', input_p, output_p, assume, guarantee, saturated = False)

@pytest.fixture()
def contract_2():
    input_p = set(('f','b','c'))
    output_p = set(('g', 'e'))

    assume = 'G(f & Xb | XXc)'
    guarantee = 'F(g|e)'

    return Contract('C2', input_p, output_p, assume, guarantee, saturated = False)



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
        contract = Contract('C', wrong_ports[0], wrong_ports[1],
                wrong_ports[2], wrong_ports[3], saturated = False)

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
        contract = Contract('C', wrong_mapping[0], wrong_mapping[1],
                wrong_mapping[2], wrong_mapping[3], saturated = False)



def test_print(basic_params):
    '''
    Test print function of two identical contracts
    '''
    contract = Contract('C', basic_params[0], basic_params[1],
            basic_params[2], basic_params[3], saturated = False)
    print contract

    contract2 = Contract('C', basic_params[0], basic_params[1],
            basic_params[2], basic_params[3], saturated = False)
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


def test_copy(contract_1, contract_2):
    '''
    test copy of contract after composition
    '''
    print 'copy C1, then merge (b, b) and (a, g) and compose copy'
    print 'before composition'
    print contract_1
    print contract_2

    c1c = contract_1.copy()
    print 'copy:'
    print c1c

    contract_3 = c1c.compose(contract_2, connection_list = \
            (('a', 'g'), ('b', 'b')))

    print contract_3
    c3c = contract_3.copy()

    print 'copy of C3'
    print c3c

    print 'after_composition'
    print contract_1
    print 'copy'
    print c1c

    assert contract_1.__str__() != c1c.__str__()
    assert contract_3.__str__() != c3c.__str__()

def test_refinement_false(contract_1, contract_2):
    '''
    Test refinment for two contracts which do not refine each other
    '''

    assert not contract_1.is_refinement(contract_2)
    assert not contract_2.is_refinement(contract_1)

def test_self_refinement(contract_1):
    '''
    A contract always refines itself
    '''
    print 'dddd'
    print contract_1.is_refinement(contract_1)


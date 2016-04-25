'''
This module takes care of Contract class related tests

author: Antonio Iannopollo
'''

import pytest
from pyco.contract import Contract, PortDeclarationError, PortMappingError, \
                        PortConnectionError, CompositionMapping
from pyco import LOG

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
            basic_params[1], basic_params[2], basic_params[3], saturated=False)
    assert True

@pytest.fixture()
def contract_1():
    input_p = set(('a','b','c'))
    output_p = set(('d', 'e'))

    assume = 'b & X(b) -> FX!(G(a|b) & F(c))'
    guarantee = 'd & XXXc -> GF(e&d)'

    return Contract('C1', input_p, output_p, assume, guarantee, saturated=False)

@pytest.fixture()
def contract_2():
    input_p = set(('f','b','c'))
    output_p = set(('g', 'e'))

    assume = 'G(f & b & Xb | XXc)'
    guarantee = 'F(g|e)'

    return Contract('C2', input_p, output_p, assume, guarantee, saturated=False)

@pytest.fixture()
def fault_assume_contract():
    '''
    Returns a contract with empty assumptions and guarantees
    '''
    input_p = set(('z'))
    output_p = set(('w'))

    assume = 'Gz & F!z'
    guarantee = 'Gw'

    return Contract('Cf', input_p, output_p, assume, guarantee, saturated=False)

@pytest.fixture()
def fault_guarantee_contract():
    '''
    Returns a contract with empty assumptions and guarantees
    '''
    input_p = set(('z'))
    output_p = set(('w'))

    assume = 'true'
    guarantee = 'Gw & X!w'

    return Contract('Cf', input_p, output_p, assume, guarantee, saturated=False)


@pytest.fixture
def contract_next():
    '''
    Returns a contract that assumes true and guaratees Xb
    '''

    input_p = ['a']
    output_p = ['b']
    assume = 'true'
    guarantee = 'Xb'

    return Contract('X', input_p, output_p, assume, guarantee)


@pytest.fixture
def contract_future():
    '''
    Returns a contract that assumes true and guaratees Fb
    '''

    input_p = ['a']
    output_p = ['b']
    assume = 'true'
    guarantee = 'Fb'

    return Contract('X', input_p, output_p, assume, guarantee)


@pytest.fixture()
def c1_compose_c2(contract_1, contract_2):
    '''
    returns a composition of c1 and c2
    '''
    composition_mapping = CompositionMapping([contract_1, contract_2])
    composition_mapping.connect(contract_1.a, contract_2.g)
    composition_mapping.connect(contract_1.b, contract_2.b)
    composition_mapping.add(contract_1.c, 'c1')
    composition_mapping.add(contract_2.c, 'c2')
    composition_mapping.add(contract_1.e, 'e1')
    composition_mapping.add(contract_2.e, 'e2')
    #composition_mapping.add(contract_2.b, 'b2')
    return contract_1.compose(contract_2, composition_mapping=composition_mapping)



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

@pytest.fixture()
def composition_easy_peasy():
    '''
    Very simple composition, only two outputs
    '''
    inp = []
    outp = ['x']

    a1 = 'true'
    g1 = 'Gx'
    g2 = 'Fx'

    c1 = Contract('easy', inp, outp, a1, g1, saturated=False)
    c2 = Contract('peasy', inp, outp, a1, g2, saturated=False)

    mapp = CompositionMapping([c1,c2])
    mapp.add(c2.x, 'x2')

    c12 = c1.compose(c2, composition_mapping=mapp)

    return (c1,c2,c12)

@pytest.fixture()
def composition_hotzi_totzi():
    '''
    Very simple composition, only two outputs
    '''
    inp = ['y']
    outp = ['x']

    a1 = 'Fy'
    g1 = 'Gx'
    a2 = 'Gy'
    g2 = 'Fx'

    c1 = Contract('hotzi', inp, outp, a1, g1, saturated=False)
    c2 = Contract('totzi', inp, outp, a2, g2, saturated=False)

    mapp = CompositionMapping([c1,c2])
    mapp.add(c2.x, 'x2')
    mapp.add(c2.y, 'y2')

    c12 = c1.compose(c2, composition_mapping=mapp)

    return (c1,c2,c12)

@pytest.fixture()
def contract_less_ports():
    '''
    to test literal hiding
    '''
    input_p = set(('a','b'))
    output_p = set(('d', 'e'))

    assume = 'X(b) -> FX!(G(a|b) & F(c))'
    guarantee = 'd & XXXc -> GF(e&d)'

    return Contract('Cports', input_p, output_p, assume, guarantee, saturated=False, infer_ports=False)

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

def test_composition_no_common_err(contract_1, contract_2):
    '''
    test composition of two contracts
    '''
    with pytest.raises(PortMappingError):
        contract_3 = contract_1.compose(contract_2)


def test_composition_no_common(contract_1, contract_2):
    '''
    test composition of two contracts
    '''
    print 'no common ports'
    print 'before composition'
    print contract_1
    print contract_2

    composition_mapping = CompositionMapping([contract_1, contract_2])
    composition_mapping.add(contract_1.c, 'c1')
    composition_mapping.add(contract_2.c, 'c2')
    composition_mapping.add(contract_1.e, 'e1')
    composition_mapping.add(contract_2.e, 'e2')
    composition_mapping.add(contract_2.b, 'b2')


    contract_3 = contract_1.compose(contract_2, composition_mapping=composition_mapping)

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

    composition_mapping = CompositionMapping([contract_1, contract_2])
    composition_mapping.connect(contract_1.a, contract_2.g)
    composition_mapping.connect(contract_1.b, contract_2.b)
    composition_mapping.add(contract_1.c, 'c1')
    composition_mapping.add(contract_2.c, 'c2')
    composition_mapping.add(contract_1.e, 'e1')
    composition_mapping.add(contract_2.e, 'e2')


    contract_3 = contract_1.compose(contract_2, composition_mapping=composition_mapping)

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
        composition_mapping = CompositionMapping([contract_1, contract_2])
        composition_mapping.connect(contract_1.e, contract_2.g)
        composition_mapping.add(contract_1.c, 'c1')
        composition_mapping.add(contract_2.c, 'c2')
        composition_mapping.add(contract_2.e, 'e2')
        composition_mapping.add(contract_1.b, 'b1')

        contract_3 = contract_1.compose(contract_2, composition_mapping=composition_mapping)


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

    composition_mapping = CompositionMapping([c1c, contract_2])
    composition_mapping.connect(c1c.a, contract_2.g)
    composition_mapping.connect(c1c.b, contract_2.b)
    composition_mapping.add(c1c.c, 'c1')
    composition_mapping.add(c1c.c, 'c2')
    composition_mapping.add(c1c.e, 'e1')
    composition_mapping.add(c1c.e, 'e2')

    contract_3 = c1c.compose(contract_2, composition_mapping=composition_mapping)

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
    c_test = contract_1.is_refinement(contract_1)
    assert c_test


def test_refinement(contract_next, contract_future):
    '''
    contract_next should refine contract_future
    '''
    contract_future.connect_to_port(contract_future.a, contract_next.a)
    contract_future.connect_to_port(contract_future.b, contract_next.b)

    assert contract_next.is_refinement(contract_future)

def test_not_refinement(contract_next, contract_future):
    '''
    contract_future shouldn't refine contract_next
    '''
    contract_future.connect_to_port(contract_future.a, contract_next.a)
    contract_future.connect_to_port(contract_future.b, contract_next.b)

    assert not contract_future.is_refinement(contract_next)

def test_compatible_ok(contract_1):
    '''
    Contract_1 should be compatible
    '''
    assert contract_1.is_compatible()

def test_consistent_ok(contract_1):
    '''
    Contract_1 should be consistent
    '''
    assert contract_1.is_consistent()

def test_compatible_fault(fault_assume_contract):
    '''
    Fault_contract shouldn't be compatible
    '''
    assert not fault_assume_contract.is_compatible()

def test_consistent_fault(fault_guarantee_contract):
    '''
    fault_contract shouldn't be consistent
    '''
    assert not fault_guarantee_contract.is_consistent()

def test_composition_compatible(c1_compose_c2):
    '''
    c1 x c2 should be compatible
    '''
    assert c1_compose_c2.is_compatible()

def test_composition_consistent(c1_compose_c2):
    '''
    c1 x c2 should be consistent
    '''
    assert c1_compose_c2.is_consistent()


def test_easy_peasy(composition_easy_peasy):
    '''
    just check everything is in order.
    Tests true only for these contracts(refinement of composition)
    '''
    (c1, c2, c12) = composition_easy_peasy

    LOG.debug(c1)
    LOG.debug(c2)
    LOG.debug(c12)

    assert c12.is_compatible()
    assert c12.is_consistent()
    assert c12.is_refinement(c1)
    assert c12.is_refinement(c2)

def test_hotzi_totzi(composition_hotzi_totzi):
    '''
    just check everything is in order
    tests true only for these contracts (refinement of composition)
    '''
    (c1, c2, c12) = composition_hotzi_totzi

    LOG.debug(c1)
    LOG.debug(c2)
    LOG.debug(c12)

    assert c12.is_compatible()
    assert c12.is_consistent()
    assert not c12.is_refinement(c1)
    assert not c12.is_refinement(c2)


def test_port_literal_hiding(contract_less_ports):

    assert True

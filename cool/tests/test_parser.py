import pytest

from cool.parser.parser import Parser, GeneralError

@pytest.fixture(scope = 'session')
def parser():
    return Parser()

@pytest.fixture(params=["hello | test -> h & Xe & (v|e & (sss -> q))", "x|y", "G(this & (is) | a & !X(correct & formula)) -> F(everything & is | fine) "])
def test_formula(request):
    return request.param


def test_parser(test_formula, parser):
    variable = parser.parse(test_formula)
    print variable
    print test_formula
    print variable.generate()

    assert True


@pytest.fixture()
def wrong_string():
    return 'test string. this is not a formula'

def test_parser_string(wrong_string, parser):

    try:
        parser.parse(wrong_string)
    except GeneralError as error:
        print 'test found the expected error %s' % error
        assert True
    else:
       assert False


@pytest.fixture()
def string_formula():
    return "G(this & (is) | a & !X(correct & formula)) -> F(everything & is | fine) "

def test_str_formula(string_formula, parser):
    try:
        formula = parser.parse(string_formula)
    except Exception as error:
        print 'here %s' % error
        assert False 
    else:
        print formula.generate()
        assert True

@pytest.fixture(params=[Parser(), int(3)])
def random_object(request):
    return request.param

def test_object(random_object, parser):
    try:
        parser.parse(random_object)
    except TypeError  as error:
        print 'Found expected TypeError %s' % error
        assert True
    else:
        assert False



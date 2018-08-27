'''
This module inlcudes all the classes and operations related to nuxmv

Author: Antonio Iannopollo
'''

from pycolite.interface_strategy import (RefinementStrategy,
            CompatibilityStrategy, ConsistencyStrategy, ApproximationStrategy)
from tempfile import NamedTemporaryFile
from subprocess import check_output, STDOUT
from pycolite.formula import *
from pycolite.symbol_sets import NusmvSymbolSet
from ConfigParser import SafeConfigParser
from pycolite.util.util import CONFIG_FILE_RELATIVE_PATH, TOOL_SECT, NUXMV_OPT
import os
from pycolite import LOG
from pycolite.types import Bool, Int, FrozenInt, Float, FrozenBool
from pycolite.util.util import NUXMV_CMD_FILENAME, NUXMV_BOUND, LTL2SMV
from pycolite.attribute import Attribute

#OPT_NUXMV = '-coi'
# CMD_OPT = ['-dynamic', '-coi', '-df', '-bmc']
CMD_OPT = ['-source']

#CMD file content in util.py

#trace delimiters
#TR_INIT = 'Trace Type: Counterexample'
#TR_COMMENT = '--'
#TR_STATE = '->'

MODULE_TEMPLATE = '''
MODULE main()
    %s

LTLSPEC (

%s

);
'''

# CEX_MODULE_TEMPLATE = '''
# MODULE Cex_%d(%s)
#     %s
#
# LTLSPEC (
#
# %s
#
# );
# '''

TEMP_FILES_PATH = '/tmp/'
NUXMV_TRUE = 'is true\n'
NUXMV_BMC_OK = '-- Cannot verify the property'
NUXMV_BMC_OK_ALT = '-- terminating with bound %d.'%NUXMV_BOUND
NUXMV_BMC_OK_ALT2 = '-- no counterexample found with bound %d'%NUXMV_BOUND

SIMPLIFY_TEMPLATE_START = '''**** PROPERTY LIST [ Type, Status, Counter-example Number, Name ] ****
--------------------------  PROPERTY LIST  -------------------------
001 :'''
SIMPLIFY_TEMPLATE_END = '''
  [LTL            Unchecked      N/A    N/A]'''

LTL2SMV_TOP = '''MODULE ltl_spec_%d
VAR
'''
LTL2SMV_VARIABLES = 'VAR'
LTL2SMV_DEFINE = 'DEFINE'
LTL2SMV_INSERT_AT = 2


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
    source_path = None
    ltl2smv_path = None

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

    @classmethod
    def get_source_path(cls):
        '''
        gets the source cmd file path
        '''
        if cls.source_path is None:
            nuxmvpath = NuxmvPathLoader.get_path()
            dirpath = os.path.dirname(nuxmvpath)
            cls.source_path = os.path.join(dirpath, NUXMV_CMD_FILENAME)

        return cls.source_path

    @classmethod
    def get_ltl2smv_path(cls):
        '''
        gets the source cmd file path
        '''
        if cls.ltl2smv_path is None:
            nuxmvpath = NuxmvPathLoader.get_path()
            dirpath = os.path.dirname(nuxmvpath)
            cls.ltl2smv_path = os.path.join(dirpath, LTL2SMV)
        return cls.ltl2smv_path

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


def _process_var_decl(vars):
    '''
    return nuxmv premble for variables in vars
    :param vars:
    :return:
    '''

    # LOG.debug(literals)
    var_list = []
    for l in vars:
        if isinstance(l.l_type, Float):
            var_list.append('\tVAR %s: real;\n' % l.unique_name)
        elif isinstance(l.l_type, FrozenInt):
            var_list.append('\tFROZENVAR %s: integer;\n' % l.unique_name)
        elif isinstance(l.l_type, FrozenBool):
            var_list.append('\tFROZENVAR %s: boolean;\n' % l.unique_name)
        elif isinstance(l.l_type, Int):
            var_list.append('\tVAR %s: integer;\n' % l.unique_name)
        elif isinstance(l.l_type, Bool):
            var_list.append('\tVAR %s: boolean;\n' % l.unique_name)
            # var_list.append('\t%s: %d..%d;\n' % (l.unique_name, l.l_type.lower, l.l_type.upper))

    var_list = set(var_list)
    # var_list = set(['\t%s: boolean;\n' %l.unique_name for l in literals])
    var_str = ''.join(var_list)

    return var_str

def verify_tautology_smv(smv_txt, prefix='',
                     tool_location=NuxmvPathLoader.get_path(),
                     source_location=NuxmvPathLoader.get_source_path(),
                     delete_file=True,
                     return_trace=False):

    temp_file = NamedTemporaryFile(
        prefix='%s' % prefix,
        dir=TEMP_FILES_PATH, suffix='.smv', delete=delete_file)


    with temp_file:

        # LOG.critical(MODULE_TEMPLATE % (var_str, formula_str))

        temp_file.write(smv_txt)
        temp_file.seek(0)

        # output = check_output([tool_location, CMD_OPT, temp_file.name])
        output = check_output([tool_location] + CMD_OPT + [source_location] + [temp_file.name],
                              stderr=STDOUT, )
        # LOG.critical(output)
        # LOG.debug(output.endswith(NUXMV_FALSE))
        lines = output.splitlines()
        if (output.endswith(NUXMV_TRUE) or lines[-1].startswith(NUXMV_BMC_OK)
                or lines[-1].startswith(NUXMV_BMC_OK_ALT) or lines[-1].startswith(NUXMV_BMC_OK_ALT2)):
            val = True
        else:
            # LOG.debug(output)
            val = False

        if return_trace:
            return val, output
        else:
            return val

def verify_tautology(formula, prefix='',
                     tool_location=NuxmvPathLoader.get_path(),
                     source_location=NuxmvPathLoader.get_source_path(),
                     delete_file=True,
                     return_trace=False):
    '''
    Verifies if a LTLFormula object represents a tautology
    '''



    formula_str = formula.generate(symbol_set=NusmvSymbolSet,
                ignore_precedence=True)

    literals = [l for (_, l) in formula.get_literal_items()]

    var_str = _process_var_decl(literals)

    smv_txt = MODULE_TEMPLATE % (var_str, formula_str)
    #LOG.critical(smv_txt)
    return verify_tautology_smv(smv_txt, prefix=prefix,
                     tool_location=tool_location,
                     source_location=source_location,
                     delete_file=delete_file,
                     return_trace=return_trace)


def derive_valuation_from_trace(trace, variables, max_horizon=None):
    """
    Derives a formula encoding the input sequence used in the trace
    :param trace:
    :param variables:
    :return:
    """

    time_sequence = []
    i = -1

    unique_names = {p.unique_name: p for p in variables}

    # LOG.debug(trace)
    # LOG.debug(monitored_vars)

    #create structure to record values

    # #process only the first one
    # p = monitored_vars.keys()[0]
    # for p in input_variables:
    #     # LOG.debug(p.base_name)
    #     # LOG.debug(p.unique_name)
    #     c_vars[p.unique_name]= None
    #     var_assign[p] = set()
    #
    #     for v_p in input_variables[p]['ports']:
    #         # LOG.debug(v_p.base_name)
    #         # LOG.debug(v_p.unique_name)
    #         c_vars[v_p.unique_name] = None
    #         var_assign[p].add(v_p)


    # LOG.debug(c_vars)
    lines = trace.split('\n')

    after_preamble = False
    pre_trace = True
    lasso_index = -1

    for line in lines:
        line = line.strip()

        # LOG.debug(line)

        ## Only if with coi
        # if pre_trace:
        #     if not line.startswith('-- Trace was successfully completed.'):
        #         continue
        #     else:
        #         pre_trace = False
        if not after_preamble:
            if line.startswith('Trace Type: Counterexample'):
                after_preamble = True
                continue
                # LOG.debug('after preamble')
            continue
        # done with the preamble
        # analyze state by state
        if line.startswith('->'):
            i = i + 1
            #time_sequence.append({})
            if i == 0:
                time_sequence.append({x: None for x in unique_names})
            else:
                time_sequence.append({x: time_sequence[i-1][x] for x in unique_names})

            # new state, check consistency among vars
            # LOG.debug(c_vars)
            # for p in input_variables:
            #
            #     if i > 0:
            #         time_sequence[i][p.unique_name] = time_sequence[i-1][p.unique_name]
            #     else:
            #         time_sequence[i][p.unique_name] = Constant(0)

            # LOG.debug(diff)


        elif line.startswith('--'):
            if lasso_index > -1:
                continue #already have a loop
            # indicates loop in trace, skip line
            lasso_index = i+1
        else:
            line_elems = line.split('=')
            line_elems = [l.strip() for l in line_elems]

            # LOG.debug(line_elems)
            # LOG.debug(c_vars)

            if line_elems[0] in unique_names:
                # base_n = monitored_vars[line_elems[0]]

                if line_elems[1] == 'TRUE':
                    val = TrueFormula()
                elif line_elems[1] == 'FALSE':
                    val = FalseFormula()
                else:
                    try:
                        val = int(line_elems[1])
                    except ValueError:
                        val = float(line_elems[1])

                    val = Constant(val)

                time_sequence[i][line_elems[0]] = val

    # time_sequence = time_sequence[:-1]

    formula_bits = []
    for i in range(len(time_sequence)):

        inner = []

        for u_name, val in time_sequence[i].items():
            inner.append(Equivalence(unique_names[u_name].literal, val, merge_literals=False))

        if len(inner) > 0:
            inner = reduce(lambda x, y: Conjunction(x, y, merge_literals=False), inner)

            for j in range(i):
                inner = Next(inner)

            formula_bits.append(inner)

    # formula_bits has i elements. We need to replicate the lasso sequence
    diff = len(formula_bits) - lasso_index
    horizon = len(formula_bits)
    # LOG.debug(trace)
    LOG.debug(diff)

    #include full loops. use max_horizon to figure out how many loops you need.
    while diff > 0 and max_horizon is not None and horizon <= max_horizon:
        partial = []
        for j in range(diff, 0, -1):
            partial.append(formula_bits[-j])
        #add horizons

        for j in range(len(partial)):
            for h in range(diff):
                partial[j] = Next(partial[j])

        formula_bits += partial
        horizon = len(formula_bits)

        # if horizon > max_horizon+1:
        #     formula_bits = formula_bits[:max_horizon+1]


    try:
        conj = reduce(lambda x, y: Conjunction(x, y, merge_literals=False), formula_bits)
    except TypeError:
        formula = None
    else:
        # formula = Globally(Eventually(conj))
        formula = conj


    return formula, lasso_index

def trace_analysis_for_loc(trace, vars):
    """
    Analyize the counterexample do derive location vars
    :return:
    :param trace:
    :param checked_variables:
    :return:
    """
    # diff = set()
    # c_vars = {p.base_name: {} for p in monitored_vars.keys()}
    #
    # for u_name, b_name in monitored_vars.items():
    #     c_vars[b_name][u_name] = None

    c_vars = {}
    var_assign = {}


    for p in vars:
        # LOG.debug(p.base_name)
        # LOG.debug(p.unique_name)
        c_vars[p.unique_name]= None




    # LOG.debug(c_vars)
    lines = trace.split('\n')

    after_preamble = False
    pre_trace = True

    #seen = {p_name for p_name in c_vars}

    for line in lines:
        line = line.strip()
        #
        # LOG.debug(line)
        # LOG.debug(seen)
        if not pre_trace:
            if not line.startswith('-- Trace was successfully completed.'):
                continue
            else:
                pre_trace = True

        if not after_preamble:
            if not line.startswith('->'):
                continue
            else:
                after_preamble = True
                continue
                # LOG.debug('after preamble')

        # done with the preamble
        # analyze state by state
        if line.startswith('->'):
            break
        elif line.startswith('--'):
            # indicates loop in trace, skip line
            pass
        else:
            line_elems = line.split('=')
            line_elems = [l.strip() for l in line_elems]

            # LOG.debug(line_elems)
            # LOG.debug(c_vars)

            if line_elems[0] in c_vars:
                # seen.add(line_elems[0])
                # base_n = monitored_vars[line_elems[0]]

                val = int(line_elems[1])
                c_vars[line_elems[0]] = val


    for v in vars:
        var_assign[v] = c_vars[v.unique_name]

    # for c in var_assign:
    #     LOG.debug('**')
    #     LOG.debug(c.base_name)
    #     LOG.debug(c.unique_name)
    #     assert len(var_assign[c])==1
    #     for v in var_assign[c]:
    #         LOG.debug('.')
    #         LOG.debug(v.base_name)
    #         LOG.debug(v.unique_name)


    # #return assignement
    # ret_assign = {}
    #
    # for p in var_assign:
    #     orig_level, orig_port = monitored_vars[p]['orig']
    #     ret_assign[(orig_level, orig_port)] = set()
    #
    #     for v in var_assign[p]:
    #         origv_level, origv_port = monitored_vars[p]['ports'][v]
    #         ret_assign[(orig_level, orig_port)].add((origv_level, origv_port))
    #         break

    return var_assign

def build_module_from_trace(trace, variables, module_name='instance'):
    '''

    :param trace:
    :return:
    '''
    time_sequence = []
    i = -1

    unique_names = {p.unique_name: p for p in variables}

    lines = trace.split('\n')

    after_preamble = False
    pre_trace = True
    lasso_index = -1

    for line in lines:
        line = line.strip()

        # LOG.debug(line)

        ## Only if with coi
        # if pre_trace:
        #     if not line.startswith('-- Trace was successfully completed.'):
        #         continue
        #     else:
        #         pre_trace = False
        if not after_preamble:
            if line.startswith('Trace Type: Counterexample'):
                after_preamble = True
                continue
                # LOG.debug('after preamble')
            continue
        # done with the preamble
        # analyze state by state
        if line.startswith('->'):
            i = i + 1
            # time_sequence.append({})
            if i == 0:
                time_sequence.append({x: None for x in unique_names})
            else:
                time_sequence.append({x: time_sequence[i - 1][x] for x in unique_names})

            # new state, check consistency among vars
            # LOG.debug(c_vars)
            # for p in input_variables:
            #
            #     if i > 0:
            #         time_sequence[i][p.unique_name] = time_sequence[i-1][p.unique_name]
            #     else:
            #         time_sequence[i][p.unique_name] = Constant(0)

            # LOG.debug(diff)


        elif line.startswith('--'):
            if lasso_index > -1:
                continue  # already have a loop
            # indicates loop in trace, skip line
            lasso_index = i + 1
        else:
            line_elems = line.split('=')
            line_elems = [l.strip() for l in line_elems]

            # LOG.debug(line_elems)
            # LOG.debug(c_vars)

            if line_elems[0] in unique_names:
                # base_n = monitored_vars[line_elems[0]]

                val = line_elems[1]

                time_sequence[i][line_elems[0]] = val

    # time_sequence = time_sequence[:-1]
    states = len(time_sequence)
    # module = 'MODULE %s(s)\n  VAR state: 0..%d;\n' % (module_name, states)
    module = 'MODULE %s(s)\n  VAR state: integer;\n' % (module_name)
    init_vs = ['s.%s = %s' % (uname, val) for (uname, val) in time_sequence[0].items()]

    # we need to define the first variable assignment in the INIT section, otherwise the module
    # might deadlock. each state will then define the next variable step.
    # It is a problem, though, when we need to loop all the way to the first state, as we need to replicate the init
    # condition as a next statement.
    # We can solve setting the init state to 1 with var values of 0 and adding a state 0 in trans.
    init = '  INIT\n    state = 1 & %s\n' % (' & '.join(init_vs))

    module = module + init

    for i in range(0, len(time_sequence)):
        trans_vs = ['next(s.%s) = %s' % (uname, val) for (uname, val) in time_sequence[i].items()]

        next_state = i+1
        #manage last trans
        if i == len(time_sequence)-1:
            if lasso_index > -1:
                next_state = lasso_index

        trans = '  TRANS\n    state = %d -> %s & next(state) = %d\n' % (i, ' & '.join(trans_vs), next_state)
        module += trans

    #add final transition, loop in state
    trans = '  TRANS\n    state = %d -> next(state) = %d\n' % (states, states)
    module += trans

    #return
    module += '\n'
    return module

def ltl2smv(formula, prefix=None, include_vars=None, parameters=None, delete_file=True,
            ltl2smv_location=NuxmvPathLoader.get_ltl2smv_path()):
    '''
    returns a smv model from a ltl formula
    :param formula:
    :param prefix:
    :return:
    '''
    if prefix is None:
        prefix = '0'
    if include_vars is None:
        include_vars = []
    if parameters is None:
        parameters = []

    temp_file = NamedTemporaryFile(
        dir=TEMP_FILES_PATH, suffix='.smv', delete=delete_file)

    formula_str = formula.generate(symbol_set=NusmvSymbolSet,
                                   ignore_precedence=True)

    # LOG.critical(formula_str)
    var_str = _process_var_decl(include_vars).strip()

    with temp_file:
        temp_file.write(formula_str)
        temp_file.seek(0)

        # output = check_output([tool_location, CMD_OPT, temp_file.name])
        output = check_output([ltl2smv_location] + [prefix] + [temp_file.name],
                              stderr=STDOUT, )

        #now process string to add var declaration
        out_lines = output.split('\n')
        #remvove 'VAR' line, add additional variables, and add 'var' it before each declaration
        pre_lines = out_lines[:LTL2SMV_INSERT_AT-1] + [x.strip() for x in var_str.split('\n')]

        if out_lines[LTL2SMV_INSERT_AT] == LTL2SMV_VARIABLES:
            i = 0
            while out_lines[LTL2SMV_INSERT_AT+i] != LTL2SMV_DEFINE:
                out_lines[LTL2SMV_INSERT_AT + i] = 'VAR ' + out_lines[LTL2SMV_INSERT_AT+i].strip()
                i += 1
        else:
            pre_lines.append(out_lines[LTL2SMV_INSERT_AT-1])

        out_lines =  pre_lines + out_lines[LTL2SMV_INSERT_AT:]
        #and add parameters to first line
        out_lines[0] = out_lines[0] + '(%s)' % (', '.join([x.unique_name for x in parameters]))

        out_txt = '\n'.join(out_lines)
        # LOG.critical(out_txt)
        return out_txt

def simplify(formula, prefix='',
                     tool_location=NuxmvPathLoader.get_path(),
                     source_location=NuxmvPathLoader.get_source_path(),
                     delete_file=True,
                     return_trace=False):
    '''
    returns a simplified LTL formula
    '''

    return NotImplementedError
    # temp_file = NamedTemporaryFile( \
    #         prefix='%s' % prefix,
    #         dir=TEMP_FILES_PATH, suffix='.smv', delete=delete_file)
    #
    # formula_str = formula.generate(symbol_set=NusmvSymbolSet, \
    #             ignore_precedence=True)
    #
    # literals = [l for (_, l) in formula.get_literal_items()]
    # #LOG.debug(literals)
    # var_list = []
    # for l in literals:
    #     if isinstance(l.l_type, Float):
    #         var_list.append('\t%s: real;\n' %l.unique_name)
    #     elif isinstance(l.l_type, Int):
    #         var_list.append('\t%s: integer;\n' %l.unique_name)
    #     elif isinstance(l.l_type, Bool):
    #         var_list.append('\t%s: boolean;\n' %l.unique_name)
    #         # var_list.append('\t%s: %d..%d;\n' % (l.unique_name, l.l_type.lower, l.l_type.upper))
    #
    # var_list = set(var_list)
    # #var_list = set(['\t%s: boolean;\n' %l.unique_name for l in literals])
    # var_str = ''.join(var_list)
    #
    # with temp_file:
    #
    #
    #     # LOG.critical(MODULE_TEMPLATE % (var_str, formula_str))
    #
    #     temp_file.write(MODULE_TEMPLATE % (var_str, formula_str))
    #     temp_file.seek(0)
    #
    #     #output = check_output([tool_location, CMD_OPT, temp_file.name])
    #     output = check_output([tool_location]+CMD_OPT +[source_location] +[temp_file.name],
    #                           stderr=STDOUT,)
    #     # LOG.critical(output)
    #     #LOG.debug(output.endswith(NUXMV_FALSE))
    #     lines = output.splitlines()
    #     if (output.endswith(NUXMV_TRUE) or lines[-1].startswith(NUXMV_BMC_OK)
    #         or lines[-1].startswith(NUXMV_BMC_OK_ALT) or lines[-1].startswith(NUXMV_BMC_OK_ALT2)):
    #         val = True
    #     else:
    #         #LOG.debug(output)
    #         val = False
    #
    #     if return_trace:
    #         return val, output
    #     else:
    #         return val

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

        # f = Conjunction(self.contract.assume_formula, self.contract.guarantee_formula)
        f = self.contract.assume_formula
        #f = Negation(f)

        return not is_empty_formula(f, \
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
        f = Conjunction(self.contract.assume_formula, self.contract.guarantee_formula)

        contract_name = self.contract.name_attribute.unique_name
        return not is_empty_formula(f,
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

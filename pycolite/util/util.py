'''
This module includes a set of generic utilities functions.
Some code inspired and adapted from
http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
released under the CC BY-SA 3.0 license.

Author: Antonio Iannopollo
'''

import os
from ConfigParser import SafeConfigParser
import logging

LOG = logging.getLogger()
CONFIG_FILE_RELATIVE_PATH = os.path.join('resources', 'config.cfg')

TOOL_SECT = 'TOOLS'
PATH_SECT = 'PATHS'

LTL3BA_OPT = 'ltl3ba'
TEMP_OPT = 'temp_dir'

NUXMV_OPT = 'nuxmv'
NUXMV_CMD_SOURCE = """go_msat
build_simplified_property -n 0
# msat_check_ltlspec_inc_coi -n 1 #128.53s
msat_check_ltlspec_sbmc_inc  -n 1 #69.44s
#check ltlspec simplify -n 1
quit
"""
NUXMV_CMD_FILENAME = 'verify_tautology.cmd'

def create_main_config_file(filepath, section_list, option_dict):
    '''
    Create main config file given the current module path
    '''

    config = SafeConfigParser()

    for section in section_list:
        config.add_section(section)

    for section, (option, value) in option_dict.items():
        config.set(section, option, value)

    with open(filepath, 'w+') as fpointer:
        config.write(fpointer)

def is_exe(fpath):
    '''
    Checks if a file is executable.
    This method is released under the CC BY-SA 3.0 license.

    :returns: boolean
    '''
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    '''
    Mimics the behavior of the shell which command.
    This method is released under the CC BY-SA 3.0 license.

    :returns: the full path of a program, or None
    '''

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def create_nuxmv_cmd_file(sourcepath):
    '''
    Create cmd file for nuxmv if it doesn't exists
    :param sourcepath:
    :return:
    '''

    with open(sourcepath, 'w+') as fn:
        fn.write(NUXMV_CMD_SOURCE)

    return
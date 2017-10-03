'''
Created on Aug 19, 2014

@author: antonio
'''

import logging
import sys
import os
import pdb
from pycolite.util.util import create_nuxmv_cmd_file

sys.setrecursionlimit(10000)

LOG = logging.getLogger('pycolite')
LOG.setLevel(logging.CRITICAL)

ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d  - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add the handlers to the logger
LOG.addHandler(ch)

LOG.debug('PYCOLITE INIT')

#check tautology file is present

from pycolite.nuxmv import NuxmvPathLoader
sourcepath = NuxmvPathLoader.get_source_path()
create_nuxmv_cmd_file(sourcepath)

#pdb.set_trace()

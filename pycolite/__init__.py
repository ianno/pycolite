'''
Created on Aug 19, 2014

@author: antonio
'''

import logging
import sys
import os
import pdb

sys.setrecursionlimit(10000)

LOG = logging.getLogger('pycolite')
LOG.setLevel(logging.INFO)

ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d  - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add the handlers to the logger
LOG.addHandler(ch)

LOG.debug('PYCOLITE INIT')



#pdb.set_trace()

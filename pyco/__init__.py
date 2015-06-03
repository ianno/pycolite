'''
Created on Aug 19, 2014

@author: antonio
'''

import logging

LOG = logging.getLogger('pyco')
LOG.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add the handlers to the logger
LOG.addHandler(ch)

LOG.debug('INIT')

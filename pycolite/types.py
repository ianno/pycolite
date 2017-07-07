'''
This module contains a basic implementation for lite types

Author: Antonio Iannopollo
'''

from abc import ABCMeta

BOOL_TYPE = 'BOOL'
INT_TYPE = 'INT'


class LType:
    '''
    Abstract type class
    '''
    __metaclass__ = ABCMeta

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

class Bool(object):
    '''
    Bool type
    '''

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return True
        return False

    def __repr__(self):
        '''
        pretty print
        '''
        return BOOL_TYPE

LType.register(Bool)

class Int(object):
    '''
    Define bounded integer
    '''

    def __init__(self, lower_bound, upper_bound):
        '''
        initialize object
        '''

        self.lower = lower_bound
        self.upper = upper_bound

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        '''
        pretty print
        '''
        return '%s - %d..%d' % (INT_TYPE, self.lower, self.upper)

LType.register(Int)

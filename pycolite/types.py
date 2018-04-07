'''
This module contains a basic implementation for lite types

Author: Antonio Iannopollo
'''

from abc import ABCMeta

BOOL_TYPE = 'BOOL'
INT_TYPE = 'INT'
FROZEN_INT_TYPE = 'FROZEN_INT'
FLOAT_TYPE = 'FLOAT'


class LType(object):
    '''
    Abstract type class
    '''

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return True
        return False

    def __le__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return True
        return False

    def __ge__(self, other):
        """Override the default Equals behavior"""
        if isinstance(self, type(other)):
            return True
        return False

class Bool(LType):
    '''
    Bool type
    '''

    def __repr__(self):
        '''
        pretty print
        '''
        return BOOL_TYPE


class Int(Bool):
    '''
    Define integer
    '''

    def __repr__(self):
        '''
        pretty print
        '''
        return INT_TYPE

class FrozenInt(Int):
    '''
    Define integer
    '''

    def __repr__(self):
        '''
        pretty print
        '''
        return FROZEN_INT_TYPE

class Float(Int):
    '''
    Define float
    '''

    def __repr__(self):
        '''
        pretty print
        '''
        return FLOAT_TYPE


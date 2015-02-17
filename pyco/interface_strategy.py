'''
This module includes the definition of abstract classes to be used in
interfacing with external tools.
The strategy pattern is implemented to allow easy swap between different tools.

Author: Antonio Iannopollo
'''

from abc import ABCMeta, abstractmethod

class RefinementStrategy:
    '''
    Metaclass defining the refinement strategy operations
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def check_refinement(self, abstract_contract):
        '''
        Checks if refining_contract refines abstract_contract.
        A contract C1 refines a contract C2 if the assumptions of C2 are
        included in C1 assumptions and if C1 guaratees are included in C2
        guarantees

        :returns: boolean
        '''
        raise NotImplementedError

class CompatibilityStrategy:
    '''
    Metaclass defining the compatibility check set of operations
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def check_compatibility(self):
        '''
        Checks if the calling Contract object is compatible.
        A contract is compatible iff there exists at least one environment
        in which it can operate, that is, the assumption formula must not
        be empty
        '''
        raise NotImplementedError

class ConsistencyStrategy:
    '''
    Metaclass defining the consistency check set of operations
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def check_consistency(self):
        '''
        Checks if the calling Contract object is consistent.
        A contract is consistent iff it is not self-contradicting. In case of a
        self-contradicting contract, it is impossible to find an implementation
        that satisfies it. Thus to verify consistency, we need to check that the
        guarantee formula is not an empty formula

        '''
        raise NotImplementedError

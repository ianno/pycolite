'''
This module includes the implementation of the contract refinement operation.
Since an external tool is needed to perform such operation,
the strategy pattern is implemented to allow easy swap between different tools.

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


'''
This module define a generic version of the observer design pattern

Author: Antonio Iannopollo
'''
from abc import ABCMeta, abstractmethod
from pyco import LOG

class Subject:
    '''
    Define a subject
    '''

    __metaclass__ = ABCMeta

    def __init__(self):
        '''initialize internal data structures '''
        self.observers = set()

    def attach(self, observer):
        '''attach a new observer to the subject'''
        self.observers.add(observer)

    def detach(self, observer):
        '''detach a previusly attached observer from the subject'''
        try:
            self.observers.remove(observer)
        except:
            raise

    def notify(self):
        '''Notify observers that something changed'''

        #this version of the observer is not thread safe, however it may
        #happen that the observer list changes size while iterating
        #then, we need a copy
        #LOG.debug(self.observers)
        for observer in self.observers.copy():
            observer.update(self)

    @abstractmethod
    def get_state(self):
        '''retrieve subject state'''
        pass

    @abstractmethod
    def set_state(self, *args, **kwargs):
        '''set subject state'''
        pass

class Observer(object):
    '''
    Define a Observer
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, updated_subject):
        '''receive an update from a subject'''
        pass

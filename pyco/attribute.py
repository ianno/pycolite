'''
This module contains the attribute manager implementation.
Attributes are interesting animals.
In fact, we need a machanism to provide new literals, as well as
a mechanism to merge different attributes into the same one.
This module uses the observer pattern.

Author: Antonio Iannopollo
'''

from pyco.observer import Subject

class UniqueIdExtractor(object):
    '''
    This class returns a unique integer associated un a give object.
    It is use to generate unique attribute names.
    '''

    def __init__(self):
        '''
        Initialize index and dictionary
        '''

        self.__index = 0
        self.__dictionary = {}


    def get_id(self, registering_obj = None, reset = False):
        '''
        Given an object, this method return a unique integer.
        :param generic_object: object associated to the unique id generation
        :type generic_object: object
        '''

        obj_id = id(registering_obj)

        if (obj_id not in self.__dictionary) or reset:
            self.__dictionary[obj_id] = self.__index
        else:
            self.__dictionary[obj_id] +=  1

        return self.__dictionary[obj_id]

class AttributeNamePool(object):
    '''
    This class is used to generate unique names starting from a base string
    '''

    __dictionary = {}

    @classmethod
    def get_unique_name(cls, registering_obj = None, base_name = '', reset = False):
        '''
        Given a string and a reference object, this method will return
        a new string in which an integer is appended to the original
        string, creating a unique string for the reference object.

        :param cls: calling class
        :type cls:
        :param registering_obj: a generic object. Used in case
                                of multiple contexts
        :type registering_obj: object
        :param base_name: base string
        :type base_name: string
        '''

        try:
            number_extractor = cls.__dictionary[base_name]
        except KeyError:
            cls.__dictionary[base_name] = UniqueIdExtractor()
            number_extractor = cls.__dictionary[base_name]


        obj_number = number_extractor.get_id(registering_obj, reset)

        #if base_name != '' and obj_number == -1:
        #    return base_name

        return '%s_%d' % (base_name, obj_number)


class Attribute(Subject):
    '''
    This class implements the concept of attribute.
    An attribute is an entity which can be referenced by several objects.
    It can notify the referencing objects if two attribute are merged together.
    Whatever object is going to interact with a Attribute has to inherit from
    Observer.
    '''

    def __init__(self, base_name, context = None):
        '''
        Create a new attribute, initializing the Subject class structures and
        generating a new unique name.
        It is possible to assign also a context, in case there is the
        possibility of having same names for different contexts.

        :param base_name: base string
        :type base_name: string
        :param context: context object
        :type context: object
        '''
        Subject.__init__(self)

        self.merging_attribute = None
        self.base_name = base_name
        self.context = context
        self.unique_name = AttributeNamePool.get_unique_name(context, self.base_name)

    def set_state(self, merging_attribute):
        '''
        Set the new state. New state means that this attribute is going
        to be discarded and a new one is going to be used.
        Once set, this method notify all the observers

        :param merging_attribute: the new attribute all the observers should
                                switch to.
        :type merging_attribute: Attribute
        '''
        if merging_attribute == None:
            raise AttributeStateError('merging_attribute set to be None')

        self.merging_attribute = merging_attribute
        self.notify()

    def merge(self, merging_attribute):
        '''
        More user-friendly wrapper to the method set_state
        '''

        self.set_state(merging_attribute)

    def get_state(self):
        '''
        Returns the last new attribute
        '''
        if self.merging_attribute == None:
            raise AttributeStateError('requesting attribute state before it is set')
        return self.merging_attribute

class AttributeStateError(Exception):
    '''
    Exception returned if an Attribute is required his
    state before it has been set
    '''
    pass





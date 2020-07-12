import pdb
import datetime
from enum import Enum


class NoneEnum(Enum):
    NONE = None

class TrueEnum(Enum):
    TRUE = True

class FalseEnum(Enum):
    FALSE = False


class ModelComposed:
    pass


def make_dynamic_class(*bases):
    """
    Returns a new DynamicBaseClasses class that is made with the subclasses bases
    TODO: lru_cache this

    Args:
        bases (list): the base classes that DynamicBaseClasses inherits from
    """
    if issubclass(bases[-1], Enum):
        # enum based classes
        bases = list(bases)
        source_enum = bases.pop()
        assert issubclass(source_enum, Enum), "The last entry in bases must be a subclass of Enum"
        source_enum_bases = source_enum.__bases__
        assert (source_enum_bases[-1] is Enum), "The last entry in source_enum_bases must be Enum"
        bases.extend(source_enum_bases)
        # DynamicBaseClassesEnum cannot be used as a base class
        # TODO: also add any bases in source_enum to DynamicBaseClassesEnum
        class DynamicBaseClassesEnum(*bases):
            for choice in source_enum:
                # source_enum cannot be used as a base class, so copy its enum values into our new enum
                locals()[choice.name] = choice.value
        return DynamicBaseClassesEnum
    # object based classes
    new_cls = type('DynamicBaseClasses', bases, {})
    return new_cls


class IntModel(int):
    def __init__(self, *args, **kwargs):
        self.path = []


inheritable_primitive_types = (int, float, str, datetime.date, datetime.datetime)

class StringEnum(str, Enum):
    RED = 'red'


class Panther:
    def __init__(self, *args, **kwargs):
        self.color = kwargs.get('color')

class ListModel(list):
    pass

def add_to_inheritance_chain(inheritance_chain, self_class):
    inheritance_chain = list(inheritance_chain)
    inheritance_chain.append(self_class)
    return tuple(inheritance_chain)

def get_new_instance(self_class, cls, super_instance, *args, **kwargs):
    if cls == self_class:
        # we are making an instance of self, but instead of making self
        # make a new class, new_cls
        # which includes dynamic bases including self
        # return an instance of that new class
        new_cls = self_class._get_new_class(*args, **kwargs)
        new_inst = new_cls.__new__(new_cls, *args, **kwargs)
        return new_inst
    if issubclass(cls, Enum):
        # we are creating new instances of DynamicBaseClassesEnum, Enum based class
        # this sets enum values when we create the DynamicBaseClassesEnum
        new_instance_class = object
        for base_cls in cls.__bases__:
            if base_cls in inheritable_primitive_types:
                new_instance_class = base_cls
                break
        inst = new_instance_class.__new__(cls)
        inst._value_ = args[0]
        return inst
    elif issubclass(cls, inheritable_primitive_types):
        # we are creating new instances of inheritable_primitive_types
        inst = super_instance.__new__(cls, args[0])
        inst.value = args[0]
        return inst
    # we are creating new instances of DynamicBaseClasses, list based class
    if issubclass(cls, list):
        inst = super_instance.__new__(cls)
        inst.value = args[0]
        return inst
    # we are creating new instances of DynamicBaseClasses, object based class
    return super_instance.__new__(cls)

def mfg_new_class(cls, chosen_additional_classes, _inheritance_chain, _required_interface_cls, *args, **kwargs):
    real_additional_classes = []
    for chosen_cls in chosen_additional_classes:
        if issubclass(chosen_cls, ModelComposed):
            chosen_cls = chosen_cls._get_new_class(_inheritance_chain=_inheritance_chain, _required_interface_cls=_required_interface_cls, *args, **kwargs)
        real_additional_classes.append(chosen_cls)
    if any(issubclass(c, _required_interface_cls) for c in real_additional_classes) and cls is _required_interface_cls:
        if len(real_additional_classes) == 1:
            return real_additional_classes[0]
        return make_dynamic_class(*real_additional_classes)
    return make_dynamic_class(cls, *real_additional_classes)

def super_init(self, super_instance, *args, **kwargs):
    not_enum = Enum not in self.__class__.__bases__
    not_primitive = not issubclass(self.__class__, inheritable_primitive_types)
    if not_enum and not_primitive:
        classes_in_order = self.__class__.__mro__
        for i, cls in enumerate(classes_in_order):
            if cls == super_instance.__thisclass__:
                remainder_cls = type('_unused', classes_in_order[i+1:], {})
        super_init_is_object_init = remainder_cls.__init__ == object.__init__
        if not super_init_is_object_init:
            super_instance.__init__(*args, **kwargs)


class ComposedSchema(ModelComposed):
    def __new__(cls, *args, **kwargs):
        return get_new_instance(ComposedSchema, cls, super(), *args, **kwargs)

    @classmethod
    def _get_new_class(cls, *args, **kwargs):
        """
        For now we return dynamic classes of different bases depending upon the inputs
        In real life this function will use the class discriminator and composed schema info to determine
        the base classes that we will use to build new_cls

        Returns:
            new_cls (type): the new dynamic class that we have built
        """
        _required_interface_cls = kwargs.pop('_required_interface_cls', cls)
        _inheritance_chain = kwargs.pop('_inheritance_chain', ())
        if cls in _inheritance_chain:
            return cls
        _inheritance_chain = add_to_inheritance_chain(_inheritance_chain, cls)
        chosen_additional_classes = []
        if args and not kwargs and len(args) == 1:
            arg = args[0]
            if arg is None:
                # type(None) and bool cannot be subclassed so we must use Enums
                # to store None, True, and False
                chosen_additional_classes = [NoneEnum]
            elif arg is True:
                chosen_additional_classes = [TrueEnum]
            elif arg is False:
                chosen_additional_classes = [FalseEnum]
            elif isinstance(arg, int):
                chosen_additional_classes = [IntModel]
            elif isinstance(arg, float):
                chosen_additional_classes = [float]
            elif isinstance(arg, str):
                chosen_additional_classes = [StringEnum]
            elif isinstance(arg, list):
                if not arg:
                    chosen_additional_classes = [list]
                else:
                    chosen_additional_classes = [ListModel]
            else:
                raise ValueError('case not handled yet')
        elif kwargs:
            chosen_additional_classes = [Panther]
        if not chosen_additional_classes:
            raise ValueError('Arguments are required to make a new class')
        return mfg_new_class(cls, chosen_additional_classes, _inheritance_chain, _required_interface_cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        super_init(self, super(), *args, **kwargs)

    _nullable = True

# Panther (object type model)
a = ComposedSchema(color='black')
for cls in [ComposedSchema, Panther]:
    assert issubclass(a.__class__, cls)
    assert isinstance(a, cls)
assert a.color == "black"

# # None, True, and False
for value in {None, True, False}:
    a = ComposedSchema(value)
    bases = (ComposedSchema, Enum)
    assert a.__class__.__bases__ == bases
    # Note: for all bases isinstance and issubclass returns True when checking a and a.__class__ against them
    assert a.value is value

# IntModel
value = 5
a = ComposedSchema(value)
bases = (ComposedSchema, IntModel)
assert a.__class__.__bases__ == bases
assert a.value == value
assert a == value

# float
value = 3.14
a = ComposedSchema(value)
bases = (ComposedSchema, float)
assert a.__class__.__bases__ == bases
assert a.value == value
assert a == value

# Enum model
value = 'red'
a = ComposedSchema(value)
bases = (ComposedSchema, str, Enum)
assert a.__class__.__bases__ == bases
assert a.value == value

# list
value = []
a = ComposedSchema(value)
bases = (ComposedSchema, list)
assert a.__class__.__bases__ == bases
assert a.value == value
assert a == value

# ListModel
value = [0]
a = ComposedSchema(value)
bases = (ComposedSchema, ListModel)
assert a.__class__.__bases__ == bases
assert a.value == value
assert a == value


class Animal(ModelComposed):
    def __new__(cls, *args, **kwargs):
        return get_new_instance(Animal, cls, super(), *args, **kwargs)

    @classmethod
    def _get_new_class(cls, *args, **kwargs):
        _required_interface_cls = kwargs.pop('_required_interface_cls', cls)
        _inheritance_chain = kwargs.pop('_inheritance_chain', ())
        if cls in _inheritance_chain:
            return cls
        _inheritance_chain = add_to_inheritance_chain(_inheritance_chain, cls)
        animal_type = kwargs['animal_type']
        if animal_type == 'Cat':
            chosen_additional_classes = [Cat]
        elif animal_type == 'Dog':
            chosen_additional_classes = [Dog]
        return mfg_new_class(cls, chosen_additional_classes, _inheritance_chain, _required_interface_cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.kwargs = kwargs
        super_init(self, super(), *args, **kwargs)

class Cat(ModelComposed):
    def __new__(cls, *args, **kwargs):
        return get_new_instance(Cat, cls, super(), *args, **kwargs)

    @classmethod
    def _get_new_class(cls, *args, **kwargs):
        _required_interface_cls = kwargs.pop('_required_interface_cls', cls)
        _inheritance_chain = kwargs.pop('_inheritance_chain', ())
        if cls in _inheritance_chain:
            return cls
        _inheritance_chain = add_to_inheritance_chain(_inheritance_chain, cls)
        chosen_additional_classes = [Animal]
        return mfg_new_class(cls, chosen_additional_classes, _inheritance_chain, _required_interface_cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        super_init(self, super(), *args, **kwargs)

class Dog:
    def __init__(self, *args, **kwargs):
        pass


# composed schema contains composed schema with cycle
animal = Animal(name='Sprinkles', animal_type='Cat')
bases = (Cat, Animal)
assert animal.__class__.__bases__ == bases
assert animal.name == 'Sprinkles'

# Dog, basses has expected Animal ... order for non-composed oneOf model Dog
animal = Animal(name='Lassie', animal_type='Dog')
bases = (Animal, Dog)
assert animal.__class__.__bases__ == bases
assert animal.name == 'Lassie'

# # Difficult example
# Apple:
#     properties:
#     - apple_type
#     type: string
#
# Pear:
#     properties:
#     - pear_type
#     type: string
#
# Fruit:
# oneOf
# - Apple
# - Pear
#
# Food:
# allOf:
# - Fruit

# # for food we assume that our class would look like
# Food(Fruit)
# # but if we did that, then Food would not be including the required Apple or Pear
# we need (Fruit, Apple), which we get from running the __new__
# if get back DynamicBaseClasses then we need to grab all of those bases

# Question to self: can allOf clases be put in models as base classes automatically?
# Answer: no because that base class could be a composed schema in which case we would need
#       to convert that composed schema class into the real DynamicBaseClasses class
#       well it's possible but it would be painfull, best to handle it in the function
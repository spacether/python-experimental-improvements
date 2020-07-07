import pdb
from enum import Enum

class Cat:
    def __init__(self, *args, **kwargs):
        self.color = kwargs.get('color')


def make_dynamic_class(bases):
    """
    Returns a new DynamicBaseClasses class that is made with the subclasses bases
    TODO: lru_cache this

    Args:
        bases (tuple): the base classes that DynamicBaseClasses inherits from
        cls_dict (dict): the class dictionary
    """
    new_cls = type('DynamicBaseClasses', bases, {})
    return new_cls

def make_dynamic_enum(bases, value):
    """
    TODO: lru_cache this
    Make a dynamic enum to store the values True, False, and None
    because type(None), and bool may not be used as base classes
    and they may not be used as superclasses of Enum

    Args:
        bases (tuple): the base classes that DynamicBaseClasses inherits from
        value (None/bool): the value that we set as an enum
    """
    # this cannot be used as a base class
    class DynamicBaseClassesEnum(*bases, Enum):
        # TODO loop through the input enum and set it here with locals
        if value is None:
            NONE = None
        elif value is True:
            TRUE = True
        elif value is False:
            FALSE = False
        else:
            raise ValueError('Invalid value passed in')
    return DynamicBaseClassesEnum


import datetime


class IntModel(int):
    def __init__(self, *args, **kwargs):
        self.path = []

inheritable_primitive_types = (int, float, str, datetime.date, datetime.datetime)

class StringEnum(str, Enum):
    RED = 'red'


def get_new_class(cls, *args, **kwargs):
    """
    For now we return dynamic classes of different bases depending upon the inputs
    In real life this function will use the class discriminator and composed schema info to determine
    the base classes that we will use to build new_cls

    Returns:
        new_cls (type): the new dynamic class that we have built
    """
    if args and not kwargs and len(args) == 1:
        arg = args[0]
        is_none = args[0] is None
        is_bool = isinstance(arg, bool)
        if is_none or is_bool:
            # type(None) and bool cannot be subclassed so we must use Enums
            # to store None, True, and False
            return make_dynamic_enum(
                (cls, ), arg
            )
        elif isinstance(arg, int):
            return make_dynamic_class((cls, IntModel))
        elif isinstance(arg, float):
            return make_dynamic_class((cls, float))
        elif isinstance(arg, str):
            chosen_cls = StringEnum
            if issubclass(chosen_cls, StringEnum):
                # TODO get enum values
                pass
            return make_dynamic_class((cls, StringEnum))
        else:
            raise ValueError('case not handled yet')
    elif kwargs:
        return make_dynamic_class((cls, Cat))
    raise ValueError('Arguments are required to make a new class')


class ComposedSchema:
    def __new__(cls, *args, **kwargs):
        if cls == ComposedSchema:
            # we are making an instance of self, but instead of making self
            # make a new class, new_cls
            # which includes dynamic bases including self
            # return an instance of that new class
            new_cls = get_new_class(cls, *args, **kwargs)
            new_inst = new_cls.__new__(new_cls, *args, **kwargs)
            return new_inst
        if issubclass(cls, Enum):
            # we are creating new instances of DynamicBaseClassesEnum, Enum based class
            # this sets enum values when we create the DynamicBaseClassesEnum
            inst = object.__new__(cls)
            inst._value_ = args[0]
            return inst
        elif issubclass(cls, inheritable_primitive_types):
            # we are creating new instances of inheritable_primitive_types
            return super().__new__(cls, args[0])
        # we are creating new instances of DynamicBaseClasses, object based class
        return super().__new__(cls)

    _nullable = True

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        not_enum = Enum not in self.__class__.__bases__
        if not_enum:
            if len(args):
                self.value = args[0]
            if not issubclass(self.__class__, inheritable_primitive_types):
                super().__init__(*args, **kwargs)

# Cat
a = ComposedSchema(color='black')
for cls in [ComposedSchema, Cat]:
    assert issubclass(a.__class__, cls)
    assert isinstance(a, cls)
assert a.color == "black"

# None, True, and False
for value in {None, True, False}:
    a = ComposedSchema(value)
    for cls in [ComposedSchema, Enum]:
        assert issubclass(a.__class__, cls)
        assert isinstance(a, cls)
    assert a.value is value

# IntModel
value = 5
a = ComposedSchema(value)
for cls in [ComposedSchema, IntModel, int]:
    assert issubclass(a.__class__, cls)
    assert isinstance(a, cls)
assert a.value == value
assert a == value

# float
value = 3.14
a = ComposedSchema(value)
for cls in [ComposedSchema, float]:
    assert issubclass(a.__class__, cls)
    assert isinstance(a, cls)
assert a.value == value
assert a == value


# TODO subclass an enum
# value = 'red'
# a = ComposedSchema(value)
# for cls in [ComposedSchema, str, Enum]:
#     assert issubclass(a.__class__, cls)
#     assert isinstance(a, cls)
# assert a.value == value


# TODO get working for for composed class inside a composed class, where the innermost holds None
# if
# - we are setting a single value of type bool or type(None)
# - and our rightmost class is not Enum
# then
# get the bases of that class (must do it by making an instance)
# then replace those bases with our chosen class
# this only applies when our data is bool/type(None) or is a value from an enum
# this does not apply to array
# this does not apply to object models
# this does not apply to a composed schema containing non-composed schema models
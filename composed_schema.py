import pdb
import datetime
from composed.schemas import ComposedSchema, Enum, Panther, IntModel, ListModel, Animal, Cat, Dog

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

# TODO add date example
# TODO break into separate files

# TODO add validation (incl conversion) of
# simple non-array type models
# simple array type models
# object models
# composed models
# TODO get validate + convert working then see if I need to extract it into a metaclass call
# doing it there would allow: mutating input args once, validation once
# Not sure how I could do that without a metaclass conflict though...
# Maybe by setting the metaclass in the new class?
# __new__ -> completely new class that contains a metaclass, but to get to it we need to access call...
# prevent init from being called?
#
#
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
# -*- coding: utf-8 -*-
'''
Created on 6/30/2017

@author: ghou
'''
# Enum枚举的实现
from enum import Enum, unique
from enum import IntEnum
# ant 蚂蚁      bee密封
Animal = Enum('Animal', 'ant bee cat dog')
print Animal
print Animal.cat.name, '1111', Animal.cat.value


class Animals(Enum):
    ant = 1
    bee = 2
    cat = 3
    dog = 4


print Animals.ant.name, Animals.ant.value
print Animals(1)
print Animals['bee']
print Animals.cat
print repr(Animals.dog), Animals(4)
print list(Animals)
for name, member in Animals.__members__.items():
    print name, member


class Shape(Enum):
    square = 2
    diamond = 1
    circle = 3
    alias_for_square = 2
print Shape.square, Shape.alias_for_square, Shape(2)
for name, member in Shape.__members__.items():
    print name, member.name
print [name for name, member in Shape.__members__.items() if member.name != name]


# @unique
# class Mistake(Enum):
#     one = 1
#     two = 2
#     three = 3
#     four = 3


class Mood(Enum):
    funky = 1
    happy = 3
    def describe(self):
        # self is the member here
        return self.name, self.value

    def __str__(self):
        return 'my custom str! {0}'.format(self.value)

    @classmethod
    def favorite_mood(cls):
        # cls here is the enumeration
        return cls.happy


print Mood.favorite_mood()
print Mood.happy.describe()
print str(Mood.funky)


class Color(Enum):
    red = 1
    green = 2
    blue = 3


# 子类不能重新定义成员
# class MoreColor(Color):
#     red = 17


class Foo(Enum):
    def some_behavior(self):
        pass


class Bar(Foo):
    happy = 1
    sad = 2


class Shape1(IntEnum):
    circle = 1
    square = 2


class Request(IntEnum):
    post = 1
    get = 2


print Shape1 == 1
print Shape1.circle == 1
print Shape1.circle == Request.post
print Shape1.circle == Color.red
print int(Shape1.circle)
print ['a', 'b', 'c'][Shape1.circle]
print [i for i in range(Shape1.square)]


# AutoNumber
class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Color1(AutoNumber):
    red = ()
    green = ()
    blue = ()

print Color1.green.value == 2


# OrderedEnum
class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Grade(OrderedEnum):
    A = 5
    B = 4
    C = 3
    D = 2
    F = 1

print Grade.C < Grade.A

# DuplicateFreeEnum
# class DuplicateFreeEnum(Enum):
#     def __init__(self, *args):
#         cls = self.__class__
#         if any(self.value == e.value for e in cls):
#             a = self.name
#             e = cls(self.value).name
#             raise ValueError("aliases not allowed in DuplicateFreeEnum:  %r --> %r" % (a, e))
# 
# 
# class Color2(DuplicateFreeEnum):
#     red = 1
#     green = 2
#     blue = 3
#     grene = 2


def enum(**enums):
    return type('Enum', (), enums)


# 旧版Python用户可以充分发挥动态语言的优越性来构造枚举，有简单的：
Numbers = enum(ONE=1, TWO=2, THREE='three')
print Numbers.ONE


def enum1(*sequential, **named):
    print sequential, range(len(sequential))
    print zip(sequential, range(len(sequential)))
    print dict(zip(sequential, range(len(sequential))))
    enums = dict(zip(sequential, range(len(sequential))), **named)
    print enums, '99999'
    return type('Enum', (), enums)

Numbers1 = enum1('ZERO', 'ONE', 'TWO')


# 有带值到名称映射的：
def enum2(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    print enums, '1111111111111111'
    return type('Enum', (), enums)
Numbers2 = enum2('ZERO', 'ONE', 'TWO')


# 有用set实现的：
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

Animals = Enum(["DOG", "CAT", "HORSE"])
print Animals.DOG


# 有用range实现的：
dog, cat, rabbit = range(3)
# or
class Stationary:
    (Pen, Pencil, Eraser) = range(0, 3)
print Stationary.Pen
   
   
# 有用tuple实现的：
class Enum1(tuple): __getattr__ = tuple.index
State = Enum1(['Unclaimed', 'Claimed'])
print State.Claimed
   
   
# 有用namedtuple实现的：
from collections import namedtuple
def enum3(*keys):
    print keys, '2222', namedtuple('Enum', keys)
    return namedtuple('Enum', keys)(*keys)

MyEnum = enum3('FOO', 'BAR', 'BAZ') 
# 带字符数字映射的，像C/C++
def enum4(*keys):
    return namedtuple('Enum', keys)(*range(len(keys)))
# 带字典映射的，可以映射出各种类型，不局限于数字
def enum5(**kwargs):
    return namedtuple('Enum', kwargs.keys())(*kwargs.values())
# -*-coding:utf-8-*-


import urllib2
from copy import deepcopy
from math import ceil
from _pyio import __metaclass__

a = [1, 2, 3, 4]
b = deepcopy(a)
print b


class Singleton(object):

    def __new__(cls, *arg, **kwargs):

        if not hasattr(cls, '_instance'):
            obj = super(Singleton, cls)
            cls._instance = obj.__new__(cls, *arg, **kwargs)
        return cls._instance


class MyClass(Singleton):
    a = 1


one = MyClass()
two = MyClass()

two.a = 2
print one.a
print id(one), id(two)


class Borg(object):

    _state = {}

    def __new__(cls, *args, **kwargs):
        ob = super(Borg, cls).__new__(cls, *args, **kwargs)
        ob.__dict__ = cls._state
        return ob


class MyClass2(Borg):
    a = 5


thre = MyClass2()
fou = MyClass2()

fou.a = 6
print thre.a
print id(thre), id(fou)

print thre == fou, thre is fou
print id(thre.__dict__), id(fou.__dict__)
print "-" * 40


class Singleton2(type):

    def __init__(cls, name, bases, dict):
        super(Singleton2, cls).__init__(name, bases, dict)
        cls._instance = None


    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton2, cls).__call__(*args, **kwargs)
        return cls._instance


class MyClass3(object):
    __metaclass__ = Singleton2


six = MyClass3()
seven = MyClass3()

seven.a = 4
# print six.a

print id(six), id(seven)
print six == seven, six is seven
print 'T' * 30


# 装饰器形式的单例模式
def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class MyClass4(object):
    a = 1

    def __init__(self, x=0):
        self.x = x

e = MyClass4()
t = MyClass4()

t.a = 3
print e.a

print id(e), id(t)
print e == t, e is t

e.x = 1
print e.x
print t.x

print '*' * 30
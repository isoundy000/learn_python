#!/usr/bin/env python
# -*-encoding:utf-8-*-
'''
Created on 2017年7月30日

@author: houguangdong
'''
from types import MethodType


class Student(object):
    pass


def set_age(self, age):
    self.age = age


# 尝试给实例绑定一个方法：
s = Student()
s.name = 'ghou'
print s.name
s.set_age1 = MethodType(set_age, s, Student) # 给实例绑定一个方法
s.set_age1(25) # 调用实例方法
print s.age
# 但是，给一个实例绑定的方法，对另一个实例是不起作用的：
s2 = Student()
# s2.set_age(25)

# 为了给所有实例都绑定方法，可以给class绑定方法：
def set_score(self, score):
    self.score = score

Student.set_score = MethodType(set_score, None, Student)
# 给class绑定方法后，所有实例均可调用：
s.set_score(100)
print s.score
s2.set_score(99)
print s2.score
# 通常情况下，上面的set_score方法可以直接定义在class中，但动态绑定允许我们在程序运行的过程中动态给class加上功能，这在静态语言中很难实现。

# 使用__slots__
# 但是，如果我们想要限制class的属性怎么办？比如，只允许对Student实例添加name和age属性。
# 为了达到限制的目的，Python允许在定义class的时候，定义一个特殊的__slots__变量，来限制该class能添加的属性：
class Student3(object):
    __slots__ = ('name', 'age') # 用tuple定义允许绑定的属性名称
s3 = Student3()
Student3.score = 100000
print Student3.score
s3.name = 'Michael' # 绑定属性'name'
s3.age = 25 # 绑定属性'age'
# s3.score = 99 # 绑定属性'score'
# 由于'score'没有被放到__slots__中，所以不能绑定score属性，试图绑定score将得到AttributeError的错误。
# 使用__slots__要注意，__slots__定义的属性仅对当前类起作用，对继承的子类是不起作用的：
class GraduateStudent(Student):
    pass


g = GraduateStudent()
g.score = 9999
print g.score
# 除非在子类中也定义__slots__，这样，子类允许定义的属性就是自身的__slots__加上父类的__slots__。
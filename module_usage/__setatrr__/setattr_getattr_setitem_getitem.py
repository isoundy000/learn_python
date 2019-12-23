# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日 19:36

@author: houguangdong
'''

class Student:

    def __getattr__(self, item):
        return item + ' is not exits'

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]


s = Student()
print(s.name)       # 调用__getattr__方法 输出'name is not exits'
s.age = 1           # 调用__setattr__ 方法
print(s.age)
print(s['age'])     # 调用 __getitem__方法 输出1
s['name'] = 'ghou'  # 调用 __setitem__ 方法
print(s['name'])    # 调用 __getitem__ 方法 输出 'tom'






# -*-coding:utf-8-*-
'''
Created on 2017年3月21日

@author: ghou
'''

# Python标准库：内置函数issubclass(class, classinfo)
# 本函数用来判断类参数class是否是类型参数classinfo的子类。
#issubclass()  
class Line:
    pass  
class RedLine(Line):  
    pass
      
class Rect:  
    pass  
      
print(issubclass(RedLine, Line))  
print(issubclass(Rect, Line))

# 对象的类型
a = 10
print isinstance(a,(int,str))


class HouGuangDong(object):

    @classmethod
    def store(cls, xing, age, entities={}):
        print xing, age, entities


HouGuangDong.store('hou', 17, {'13':'12'})
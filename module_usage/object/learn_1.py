#!/usr/bin/env python
# -*-encoding:utf-8-*-
'''
Created on 2017年7月29日

@author: houguangdong
'''
import types

# 获取对象信息
print type(abs)
# Python把每种type类型都定义好了常量，放在types模块里，使用之前，需要先导入：
print type('abc') == types.StringType
print type(u'abc') == types.UnicodeType
print type([]) == types.ListType
print type(str) == types.TypeType

# 最后注意到有一种类型就叫TypeType，所有类型本身的类型就是TypeType，比如：
print type(int)==type(str)==types.TypeType
# 使用isinstance()
# 对于class的继承关系来说，使用type()就很不方便。我们要判断class的类型，可以使用isinstance()函数。
# object -> Animal -> Dog -> Husky
# 那么，isinstance()就可以告诉我们，一个对象是否是某种类型。先创建3种类型的对象：
# a = Animal()  d = Dog() h = Husky()
# print isinstance(d, Dog)

# 能用type()判断的基本类型也可以用isinstance()判断：
print isinstance('a', str)
print isinstance(u'a', unicode)
print isinstance('a', unicode)

# 并且还可以判断一个变量是否是某些类型中的一种，比如下面的代码就可以判断是否是str或者unicode：
print isinstance('a', (str, unicode))
print isinstance(u'a', (str, unicode))
# 由于str和unicode都是从basestring继承下来的，所以，还可以把上面的代码简化为：
print isinstance(u'a', basestring)
# 使用dir()
# 如果要获得一个对象的所有属性和方法，可以使用dir()函数，它返回一个包含字符串的list，比如，获得一个str对象的所有属性和方法：
list1 = dir('ABC')
for item in list1:
    print item
# 类似__xxx__的属性和方法在Python中都是有特殊用途的，比如__len__方法返回长度。在Python中，如果你调用len()函数试图获取一个对象的长度，实际上，在len()函数内部，它自动去调用该对象的__len__()方法，所以，下面的代码是等价的：
print len('ABC'), 'ABC'.__len__()

# 我们自己写的类，如果也想用len(myObj)的话，就自己写一个__len__()方法：
class MyObject(object):
    def __len__(self):
        return 100
obj = MyObject()
print len(obj)
# 剩下的都是普通属性或方法，比如lower()返回小写的字符串：
print 'ABC'.lower()

# 仅仅把属性和方法列出来是不够的，配合getattr()、setattr()以及hasattr()，我们可以直接操作一个对象的状态：
class MyOject1(object):
    def __init__(self):
        self.x = 9
    
    def power(self):
        return self.x * self.x

obj1 = MyOject1()
# 紧接着，可以测试该对象的属性：
print hasattr(obj1, 'x') # 有属性'x'吗？
print obj1.x
print hasattr(obj1, 'y') # 有属性'y'吗？
setattr(obj1, 'y', 19) # 设置一个属性'y'
print hasattr(obj1, 'y') # 有属性'y'吗？
print getattr(obj1, 'y') # 获取属性'y'
print obj1.y # 获取属性'y'
# 可以传入一个default参数，如果属性不存在，就返回默认值：
print getattr(obj, 'z', 404) # 获取属性'z'，如果不存在，返回默认值404
# 也可以获得对象的方法：
print hasattr(obj1, 'power') # 有属性'power'吗？
print getattr(obj1, 'power') # 获取属性'power'
fn = getattr(obj1, 'power') # 获取属性'power'并赋值到变量fn
print fn # fn指向obj.power
print fn() # 调用fn()与调用obj.power()是一样的

# def readImage(fp):
#     if hasattr(fp, 'read'):
#         return readData(fp)
#     return None

# 假设我们希望从文件流fp中读取图像，我们首先要判断该fp对象是否存在read方法，如果存在，则该对象是一个流，如果不存在，则无法读取。hasattr()就派上了用场。
# 请注意，在Python这类动态语言中，有read()方法，不代表该fp对象就是一个文件流，它也可能是网络流，也可能是内存中的一个字节流，但只要read()方法返回的是有效的图像数据，就不影响读取图像的功能。
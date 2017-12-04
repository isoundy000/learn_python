# -*- coding: utf-8 -*-
'''
Created on 2017年9月13日

@author: houguangdong
'''
# python中%r和%s的区别
# %r用rper()方法处理对象
# %s用str()方法处理对象
# 有些情况下，两者处理的结果是一样的，比如说处理int型对象。
# 例一：
print "I am %d years old." % 22
print "I am %s years old." % 22
print "I am %r years old." % 22


# 另外一些情况两者就不同了
# 例二：
text = "I am %d years old." % 22
print "I said: %s." % text
print "I said: %r." % text


# 再看一种情况
# 例三：
import datetime
d = datetime.date.today()
print "%s" % d
print "%r" % d

# 可见，%r打印时能够重现它所代表的对象(rper() unambiguously recreate the object it represents)
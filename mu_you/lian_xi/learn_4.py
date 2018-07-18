# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
from datetime import datetime

# Globals()  查看全局名称空间的内容
# Locals()   查看局部名称空间的内容
x = 1

def func():
    print "from func"
    x = 2
    print globals()
    print locals()

func()
print globals()
print locals()


# 闭包
x1 = 1000
def f1():
    x1 = 1
    def f2():
        print x1
    return f2

f = f1()
print f

# 闭包的__closure__变量
x2 = 1
def f2():
    x = 1000
    y = 2
    def f3():
        y
        print x
    return f3

f2 = f2()
print f2()
print f2.__closure__
print f2.__closure__[0]
print f2.__closure__[0].cell_contents
print f2.__closure__[1]
print f2.__closure__[1].cell_contents

# 将上面”爬百度”的程序修改成闭包模式：
from urllib.request import urlopen
def f1(url):
    def f2():
        print(urlopen(url).read())
    return f2
baidu = f1('http://www.baidu.com')
python = f1('http://www.python.org')
baidu()
python()

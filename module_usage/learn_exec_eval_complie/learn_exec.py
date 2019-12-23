# -*- encoding: utf-8 -*-
'''
Created on 2019年11月6日

@author: houguangdong
'''

a = '{1: 3}'
b = {}
exec ('b=a')
print b


x = 10
def func():
    y = 20
    exec ("print x + y")
    exec ("print x + y", {"x": 1, "y": 2})
    exec ("print x + y", {"x": 1, "y": 2}, {"y": 3, "z": 4})
    exec ("print x, y")
func()
print "*" * 50

k = 10
expr = """
z = 30
sum = k + y + z   #一大包代码
print(sum)
"""
def func():
    y = 20
    exec(expr)                              # 10 + 20 + 30
    exec(expr, {'k': 1, 'y': 2})            # 30 + 1 + 2
    exec(expr, {'k': 1, 'y': 2}, {'y': 3, 'z': 3})  # 30+1+3，k是定义全局变量1，y是局部变量

func()
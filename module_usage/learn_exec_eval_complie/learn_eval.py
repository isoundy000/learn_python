# -*- encoding: utf-8 -*-
'''
Created on 2019年11月11日

@author: houguangdong
'''

x = 10

def func():
    y = 20                                  # 局部变量y
    a = eval("x + y")
    print("a:", a)                          # x没有就调用全局变量
    b = eval("x + y", {"x": 1, "y": 2})     # 定义局部变量，优先调用
    print("b:", b)
    c = eval("x + y", {"x": 1, "y": 2}, {"y": 3, "z": 4})
    print("c:", c)
    f = eval("x + y + z", {"x": 1, "y": 2}, {"y": 3, "z": 4})
    print f
    # d = eval("print(x, y)")
    # print("d:", d)                          # 对于变量d，因为print()函数不是一个计算表达式，因此没有返回值

func()
#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# sys.stdin.readline( )会将标准输入全部获取，包括末尾的'\n'，input()会把‘\n’忽略.
import sys
line = sys.stdin.readline()
n = int(line)
print n


import sys
a = sys.stdin.readline()    # a = sys.stdin.readline().strip()
b = input()
print(len(a), len(b))


# python3中sys.stdin与input的区别
#     input()方法和stdin()类似，不同的是input()括号内可以直接填写说明文字。
#     可以看一个简单的例子：
while True:
    n = int(input('Please input a number:\n'))
    sn = list(map(int, input('Please input some numbers:\n').split()))
    print(n)
    print(sn, '\n')
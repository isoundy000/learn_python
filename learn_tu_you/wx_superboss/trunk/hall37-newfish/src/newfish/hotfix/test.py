#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/27


class A(object):

    def __init__(self):
        self.reload()

    def reload(self):
        if hasattr(self, 'd') and self.d[1] == 2:
            print self.d, 'fffffffff'
            return
        print 'kkkkkkkk'
        self.d = {}
        print 'zzzzzzzz'

    def clear(self):
        self.d = []


a = A()
a.d[1] = 2
print a.d
# a.clear()
c = A()
print c.d


# hex() 函数用于将10进制整数转换成16进制，以字符串形式表示。
a = 0x1000          # 1*16^3+0*16^2+0*16^1+0*16^0
print bin(a)
print bin(~a)
c = 0
c |= a
print bin(c)
c = c & ~a
print int(c)
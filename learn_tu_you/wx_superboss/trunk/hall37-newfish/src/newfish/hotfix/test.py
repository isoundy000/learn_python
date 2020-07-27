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
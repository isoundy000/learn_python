#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import time


class WingRoom(object):

    def __init__(self, uid=None):
        self.uid = None
        self.last_time = 0

    @classmethod
    def _install(cls, uid):
        room = cls()
        room.uid = uid
        room.last_time = time.localtime()
        return room


class Add:

    c = 1

    def __add__(self, other):
        print self.c, other.c
        return self.c + other.c


c = WingRoom._install(1)
print c.last_time, c.uid

a = Add()
b = Add()
print a + b
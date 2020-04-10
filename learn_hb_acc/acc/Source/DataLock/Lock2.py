#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

from Source.DataLock.Lock1 import Lock1


class Lock2:

    def __init__(self, lock):
        # print "lock"
        self._lock = lock
        self._lock.Lock()

    def __del__(self):
        # print "release"
        self._lock.Release()
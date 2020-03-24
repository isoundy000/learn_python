#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'ghou'

from Source.DataLock.Lock1 import Lock1


class Lock2:

    def __init__(self, lock):
        self._lock = lock
        self._lock.Lock()

    def __del__(self):
        self._lock.Release()
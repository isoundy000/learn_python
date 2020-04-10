#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

import gevent
# from gevent.coros import Semaphore
from gevent.lock import Semaphore


class Lock1:

    _gevent_locks = {}
    _gevent_lock = Semaphore()

    @staticmethod
    def AddCurrent(lock):
        pass
        # current = gevent.getcurrent()
        # Lock1._gevent_lock.acquire()
        # if not Lock1._gevent_locks.has_key(current):
        #     Lock1._gevent_locks[current] = set()
        #     Lock1._gevent_locks[current].add(lock)
        # Lock1._gevent_lock.release()

    @staticmethod
    def SubCurrent(lock):
        pass
        # current = gevent.getcurrent()
        # Lock1._gevent_lock.acquire()
        # Lock1._gevent_locks[current].discard(lock)
        # Lock1._gevent_lock.release()

    @staticmethod
    def ClearCurrent():
        pass
        # current = gevent.getcurrent()
        # Lock1._gevent_lock.acquire()
        # if Lock1._gevent_locks.has_key(current):
        #     while True:
        #         if len(Lock1._gevent_locks[current]) == 0:
        #             break
        #         locktmp = Lock1._gevent_locks[current].pop()
        #         locktmp.ReleaseEx()
        # Lock1._gevent_lock.release()

    def __init__(self):
        self._lock = Semaphore()
        self._current = None
        self._count = 0

    def Lock(self, tag=None):
        # if tag:
        #     print "[Lock1]" + tag + " 请求"
        # current = gevent.getcurrent()
        # if self._current == current:
        #    self._count += 1
        #    return
        # if not self._lock.acquire(timeout=1):
        #    raise Exception("lock error")
        # self._current = current
        # self._count = 1
        # Lock1.AddCurrent(self)
        pass

        # if tag:
        #     print "[Lock1]" + tag + " 确认"

    def Release(self, tag=None):
        # self._count -= 1
        # if self._count == 0:
        #    self._lock.release()
        #    self._current = None
        #    Lock1.SubCurrent(self)
        # if tag:
        #     print "[Lock1]" + tag + " 释放"
        pass

    def ReleaseEx(self):
        # self._lock.release()
        # self._current = None
        # self._count = 0
        pass
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
from contextlib import contextmanager
import functools
from stackless import tasklet
import stackless

from freetime.core.lock import FTLock
from freetime.core.reactor import mainloop
from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer


class KeyLock(object):
    
    def __init__(self):
        # key=key, value=FTLock('')
        self._lockMap = {}
        
    @contextmanager
    def lock(self, key):
        locker = self._findOrCreateLocker(key)
        locker.lock()
        
        
    def _findOrCreateLocker(self, key):
        """
        发现或者创建锁
        :param key: 
        :return: 
        """
        locker = self._lockMap.get(key)
        if not locker:
            locker = FTLock('%s_%s' % (id(self), key))
            self._lockMap[key] = locker
        return locker
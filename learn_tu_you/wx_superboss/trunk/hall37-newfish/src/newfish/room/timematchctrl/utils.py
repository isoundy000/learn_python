#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

import functools

from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog


class Logger(object):

    def __init__(self, kvs=None):
        self._args = []
        if kvs:
            for k, v in kvs:
                self.add(k, k)

    def add(self, k, v):
        self._args.append("%s=" % k)
        self._args.append(v)

    def hinfo(self, prefix=None, *args):
        self._log(prefix, ftlog.hinfo, *args)

    def info(self, prefix=None, *args):
        self._log(prefix, ftlog.info, *args)

    def debug(self, prefix=None, *args):
        self._log(prefix, ftlog.debug, *args)

    def warn(self, prefix=None, *args):
        self._log(prefix, ftlog.warn, *args)

    def error(self, prefix=None, *args):
        self._log(prefix, ftlog.error, *args)

    def isDebug(self):
        return ftlog.is_debug()

    def _log(self, prefix, func, *args):
        argl = []
        if prefix:
            argl.append(prefix)
        argl.extend(self._args)
        argl.extend(args)
        func(*argl)
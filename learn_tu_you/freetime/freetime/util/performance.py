#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2
from time import time
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
try:
    import psutil
    _myps = psutil.Process()
except:
    _myps = None
    ftlog.info('psutil not installed')

PERFORMANCE_NET = 0
SLOW_CALL_TIME = 0.2


def watchSlowCall(fun, funArgl, funArgd, slowTime, slowFun):
    pass

MSG_KEY = 'RPC.'
NET_KEY = 'xxxnettimexxx'
NET_KEY_LEN = len(NET_KEY)


def linkMsgTime(tag2, msg):
    pass


def threadInfo():
    pass


_ppsTimer = None
_ppsFunCounts = []


def regPPSCounter(funCount):
    pass


def _ppsCounter():
    pass

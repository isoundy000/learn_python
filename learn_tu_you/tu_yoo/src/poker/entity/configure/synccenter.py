#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21
import time

from freetime.core.tasklet import FTTasklet
import freetime.entity.config as ftcon
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.util import strutil, webpage
from freetime.core.lock import locked
from freetime.core.timer import FTLoopTimer

_DEBUG = 1
if _DEBUG:
    def debug(*argl, **argd):
        ftlog.info(*argl, **argd)
else:
    def debug(*argl, **argd):
        pass
_REPORT_OK = 0


def doSyncData(event):
    """同步数据"""
    _doReportStatus(event)
    _doCheckReloadConfig(event)


def _doReportStatus(event):
    """报告状态"""
    pass


class _lockobj():
    pass
_lockobj = _lockobj()


@locked
def _reportOnlineToSdk(_lockobj):
    '''
    向当前的SDK服务汇报自己的运行状态
    '''
    pass


def _doCheckReloadConfig(event):
    # 每15秒检查一次数据同步, event为None即为手工进行执行推送
    pass


_CHANGE_INDEX = -1
_CHANGE_KEYS_NAME = 'configitems.changekey.list'
_LAST_ERRORS = None


def _initialize():
    global _CHANGE_INDEX
    if _CHANGE_INDEX < 0:
        _CHANGE_INDEX = ftcon.getConfNoCache('LLEN', _CHANGE_KEYS_NAME)
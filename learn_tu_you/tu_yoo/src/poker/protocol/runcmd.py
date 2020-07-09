#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/4
import stackless

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.protocol import router, oldcmd, rpccore
from poker.protocol import _runenv
from poker.util import strutil
from freetime.core.lock import FTLock
import freetime.entity.service as ftsvr


def getMsgPack():
    '''
    取得当前TCP的消息
    '''
    return ftsvr.getTaskPack()  # stackless.getcurrent()._fttask.pack


def newOkMsgPack(code=1):
    pass
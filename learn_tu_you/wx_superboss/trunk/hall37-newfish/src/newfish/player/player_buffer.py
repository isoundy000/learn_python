# -*- coding=utf-8 -*-
"""
Created by hhx on 18/04/13.
"""

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util


class BUFFER_STATE:

    NOEFFECT = 0        # 没有效果
    START = 1           # 开始
    END = 2             # 结束


class FishPlayerBuffer(object):
    """回馈赛的buffer"""
    def __init__(self, player, bufferId):
        self.player = player
        self.bufferId = bufferId
        self._state = BUFFER_STATE.NOEFFECT
        self.startTime = 0
        self.bufferConf = config.getPlayerBufferConf(bufferId)
        self.checkTimer = FTLoopTimer(self.bufferConf["delayTime"], -1, self._bufferStart)
        self.checkTimer.start()

        self.sendMsgTimer = None

    def getBufferId(self):
        return self.bufferId

    def isStart(self):
        return self._state == BUFFER_STATE.START

    def _bufferStart(self):
        if self.checkTimer:
            self.checkTimer.cancel()
        self._state = BUFFER_STATE.START
        self.startTime = int(time.time())
        pass

# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/9/11.
"""

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer


class RainbowFishGroup(object):
    """
    彩虹鱼鱼群
    """
    def __init__(self, table):
        self.table = table
        self._interval = 100            # 间隔
        self._totalTime = 0             # 总时间
        self._nextRainbowTimer = None	# 下一波彩虹鱼
        self._setRainbowTimer()

    def clearTimer(self):
        if self._nextRainbowTimer:
            self._nextRainbowTimer.cancel()
            self._nextRainbowTimer = None

    def _setRainbowTimer(self):
        """启动彩虹鱼定时器"""
        self.clearTimer()
        self._nextRainbowTimer = FTLoopTimer(self._interval, -1,  self._addRainbowFishGroup)
        self._nextRainbowTimer.start()

    def _addRainbowFishGroup(self):
        """添加彩虹鱼"""
        self._totalTime += self._interval
        if self._totalTime % 3 == 0:
            return
        rainbowGroupId = random.choice(self.table.runConfig.allRainbowGroupIds)
        if rainbowGroupId:
            ftlog.debug("_addRainbowFishGroup", self.table.tableId, rainbowGroupId)
            self.table.insertFishGroup(rainbowGroupId)
# -*- coding=utf-8 -*-
"""
大奖赛鱼阵
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/10/12


import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class GrandPrixFishGroup(object):
    """
    grandprix鱼群
    """
    def __init__(self, table):
        self._fishTypes = config.getGrandPrixConf("group").values()
        self._interval = 60
        self.table = table
        self._idx = 0
        self._nextGrandPrixTimer = None
        self._setGrandPrixTimer()

    def clearTimer(self):
        """清理定时器"""
        if self._nextGrandPrixTimer:
            self._nextGrandPrixTimer.cancel()
            self._nextGrandPrixTimer = None

    def _setGrandPrixTimer(self):
        """设置大奖赛定时器"""
        self._idx = 0
        self.clearTimer()
        self._nextGrandPrixTimer = FTLoopTimer(self._interval, -1, self._addGrandPrixFishGroup)
        self._nextGrandPrixTimer.start()

    def _addGrandPrixFishGroup(self):
        """增加大奖赛鱼群"""
        for _val in self._fishTypes:
            _fishType = _val[self._idx % len(_val)]
            if _fishType in self.table.runConfig.allGrandPrixGroupIds:
                grandPrixGroupIds = self.table.runConfig.allGrandPrixGroupIds[_fishType]
                if grandPrixGroupIds:
                    grandPrixGroupId = random.choice(grandPrixGroupIds)
                    self.table.insertFishGroup(grandPrixGroupId)        # 召唤大奖赛鱼群
        self._idx += 1
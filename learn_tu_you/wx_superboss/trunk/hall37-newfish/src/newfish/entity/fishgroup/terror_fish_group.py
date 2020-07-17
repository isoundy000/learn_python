# -*- coding=utf-8 -*-
"""
恐怖鱼鱼群
"""
# @Author  : Kangxiaopeng
# @Time    : 2018/12/4

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class TerrorFishGroup(object):
    """
    terror鱼群
    """
    def __init__(self, table):
        self.table = table
        self._fishType = 0
        self._interval = 300
        self._terrorGroupId = None
        self._nextTerrorTimer = None
        self._setTerrorTimer()

    def clearTimer(self):
        if self._nextTerrorTimer:
            self._nextTerrorTimer.cancel()
            self._nextTerrorTimer = None

    def _setTerrorTimer(self):
        """启动恐怖鱼鱼群定时器"""
        self.clearTimer()
        self._fishType, self._interval = self._randomFishTypeAndInterval()
        self._nextTerrorTimer = FTLoopTimer(self._interval, -1, self._addTerrorFishGroup)
        self._nextTerrorTimer.start()

    def _addTerrorFishGroup(self):
        """添加恐怖鱼鱼群"""
        if self._fishType not in self.table.runConfig.allTerrorGroupIds:
            ftlog.debug("_addTerrorFishGroup, error", self.table.tableId, self._fishType, self.table.runConfig.allTerrorGroupIds)
            return
        terrorGroupIds = self.table.runConfig.allTerrorGroupIds[self._fishType]
        if terrorGroupIds:
            self._terrorGroupId = random.choice(terrorGroupIds)
            ftlog.debug("_addTerrorFishGroup", self.table.tableId, self._fishType, self.table.tableId, self._terrorGroupId)
            self.table.insertFishGroup(self._terrorGroupId)
        self._fishType, _ = self._randomFishTypeAndInterval()

    def _randomFishTypeAndInterval(self):
        """随机鱼Id和间隔"""
        fishType = 0
        interval = 300
        randomNum = random.randint(1, 10000)
        for terrorFishMap in config.getTerrorFishConf(self.table.runConfig.fishPool, self.table.gameMode):
            probb = terrorFishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = int(terrorFishMap["fishType"])
                interval = int(terrorFishMap["interval"])
                break
        ftlog.debug("_randomFishTypeAndInterval", self.table.tableId, fishType, interval)
        if interval != self._interval and self._nextTerrorTimer is not None:
            self._interval = interval
            self._setTerrorTimer()
        return fishType, interval
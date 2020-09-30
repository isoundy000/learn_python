#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/8/4
"""大盘鱼"""

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class PlatterFishGroup(object):
    """
    大盘鱼群
    """
    def __init__(self, table):
        self.table = table
        self._fishType = 0
        self._interval = 10
        self._platterGroupId = None
        self._nextPlatterTimer = None
        self._setPlatterTimer()

    def clearTimer(self):
        """清理定时器"""
        if self._nextPlatterTimer:
            self._nextPlatterTimer.cancel()
            self._nextPlatterTimer = None

    def _setPlatterTimer(self):
        """启动大盘鱼群定时器"""
        self.clearTimer()
        self._fishType, self._interval = self._randomFishTypeAndInterval()
        self._nextPlatterTimer = FTLoopTimer(self._interval, -1, self._addPlatterFishGroup)
        self._nextPlatterTimer.start()

    def _addPlatterFishGroup(self):
        """添加大盘鱼群"""
        if self._fishType not in self.table.runConfig.allPlatterGroupIds:
            return
        if self.table.hasTideFishGroup():   # 当前渔场存在鱼潮
            return
        platterGroupIds = self.table.runConfig.allPlatterGroupIds[self._fishType]
        if platterGroupIds:
            self._platterGroupId = random.choice(platterGroupIds)
            self.table.insertFishGroup(self._platterGroupId)
        self._fishType, _ = self._randomFishTypeAndInterval()

    def _randomFishTypeAndInterval(self):
        """随机鱼Id和间隔"""
        fishType = 0
        interval = 10
        randomNum = random.randint(1, 10000)
        for platterFishMap in config.getPlatterFishConf(self.table.runConfig.fishPool):
            probb = platterFishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = int(platterFishMap["fishType"])
                interval = int(platterFishMap["interval"])
                break
        if interval != self._interval and self._nextPlatterTimer is not None:
            self._interval = interval
            self._setPlatterTimer()
        return fishType, interval
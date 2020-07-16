#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/15

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class MultipleFishGroup(object):
    """
    倍率鱼群（比赛场专用）
    """

    def __init__(self, table):
        self.table = table
        self._tableRank = 0
        self._nextGroupTimer = None

    def clearTimer(self):
        if self._nextGroupTimer:
            self._nextGroupTimer.cancel()
            self._nextGroupTimer = None

    def initGroup(self, tableRank):
        """初始化倍率鱼群"""
        self._tableRank = tableRank
        self._setNextGroupTimer()

    def _setNextGroupTimer(self):
        """启动倍率鱼定时器"""
        self.clearTimer()
        interval = random.randint(25, int((1 - self._tableRank) * 30 + 30))
        self._nextGroupTimer = FTLoopTimer(interval, 0,  self._addMultipleFishGroup)
        self._nextGroupTimer.start()

    def _addMultipleFishGroup(self):
        """添加倍率鱼群"""
        randomNum = random.randint(1, 10000)
        for multipleFishMap in config.getRandomMultipleFishConf(self.table.runConfig.fishPool):
            probb = multipleFishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = multipleFishMap["fishType"]
                allMultipleGroupIds = self.table.runConfig.allMultipleGroupIds
                groupId = random.choice(allMultipleGroupIds[fishType])
                ftlog.debug("_addMultipleFishGroup", fishType, allMultipleGroupIds, groupId)
                self.table.insertFishGroup(groupId)
                self._setNextGroupTimer()
                break

    def cancelNextGroupTimer(self):
        """取消定时器"""
        if self._nextGroupTimer:
            self._nextGroupTimer.cancel()
            self._nextGroupTimer = None
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/13


import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class BufferFishGroup(object):
    """
    buffer鱼群（比赛场专用）
    """

    def __init__(self, table):
        self.table = table
        self._initData()
        self._tableRank = 0
        self._bufferGroupId = None
        self._nextBufferTimer = None

    def clearTimer(self):
        if self._nextBufferTimer:
            self._nextBufferTimer.cancel()
            self._nextBufferTimer = None

    def initGroup(self, tableRank):
        """初始化"""
        self._tableRank = tableRank
        self._setBufferTimer()

    def _initData(self):
        """初始化数据"""
        self.fishes = {}
        for bufferFishMap in config.getBufferFishConf(self.table.runConfig.fishPool):
            fishType = bufferFishMap["fishType"]
            self.fishes.setdefault(fishType, [])
            for groupId in self.table.runConfig.allBufferGroupIds:
                if fishType and str(fishType) in groupId:
                    self.fishes[fishType].append(groupId)
            self.fishes[fishType].sort(cmp=cmpGroupId)

    def _setBufferTimer(self):
        """设置buffer定时器"""
        if self._nextBufferTimer:
            self._nextBufferTimer.cancel()
            self._nextBufferTimer = None
        interval_ = random.randint(int(25 + (1 - self._tableRank) * 20), int((1 - self._tableRank) * 40 + 35))
        ftlog.debug("_setBufferTimer========>", self.table.tableId, interval_, self._tableRank)
        self._nextBufferTimer = FTLoopTimer(interval_, 0, self._addBufferFishGroup)

    def _addBufferFishGroup(self):
        """添加buffer鱼群"""
        fishType = 0
        randomNum = random.randint(1, 10000)
        ftlog.debug("_addBufferFishGroup", randomNum)
        for bufferFishMap in config.getBufferFishConf(self.table.runConfig.fishPool):
            probb = bufferFishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = bufferFishMap["fishType"]
                break

        allBufferGroupIds = self.fishes[fishType]
        ftlog.debug("_addBufferFishGroup", fishType, allBufferGroupIds, self.fishes)
        # 选择一个鱼阵
        if allBufferGroupIds:
            self._bufferGroupId = allBufferGroupIds[self.chooseOneGroup()]
            ftlog.debug("_addBufferFishGroup", self._bufferGroupId)
            self.table.insertFishGroup(self._bufferGroupId)
            self._setBufferTimer()

    def chooseOneGroup(self):
        """选择一个鱼群"""
        luckyNums = []
        for player_ in self.table.players:
            if player_:
                luckyNums.append(abs(player_.matchLuckyValue))
        w1 = 0.25 * 10000
        w2 = 0.5 * 10000
        w3 = 0.25 * 10000
        divisionNum = sum(luckyNums)
        if len(luckyNums) > 1 and divisionNum != 0:
            k1 = luckyNums[0] * 1.0 / (divisionNum)
            k1 = min(max(k1, 0.1), 0.9)                     # k1 和 k3的值最小是0.1
            k3 = 1 - k1
            k2 = k3/k1 if k1 >= k3 else k1/k3

            w1 = int(k1 / (k1 + k2 + k3) * 10000)
            w2 = int(k2 / (k1 + k2 + k3) * 10000)
            w3 = int(k3 / (k1 + k2 + k3) * 10000)

        randomNum = random.randint(1, w1 + w2 + w3)
        ftlog.debug("chooseOneBufferGroup========>", self.table.runConfig.fishPool, luckyNums, w1, w2, w3, randomNum)
        if 1 <= randomNum <= w1:
            return random.choice([0, 1])
        elif w1 + 1 <= randomNum <= w1 + w2:
            return random.choice([2, 3])
        elif w1 + w2 + 1 <= randomNum <= w1 + w2 + w3:
            return random.choice([4, 5])
        else:
            return random.choice([2, 3])

    def cancelNextGroupTimer(self):
        """取消定时器"""
        if self._nextBufferTimer:
            self._nextBufferTimer.cancel()
            self._nextBufferTimer = None


def cmpGroupId(key1, key2):
    return cmp(int(key1[01]), int(key2[-1]))
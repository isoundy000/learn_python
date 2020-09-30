# -*- coding: utf-8 -*-

# Created by xsy on 4th, August 2020

# 附带小游戏鱼阵（美人鱼）

import random
import time
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class MiniGameFishGroup(object):
    """
    小游戏鱼阵
    """
    def __init__(self, table):
        self.table = table
        self._fishType = 0
        self._interval = 180
        self._duration = 30
        self._groupId = None
        self._nextTimer = None
        self._autofillTimer = None
        self._fishId = 0
        self._group = None
        self._mermaidAppearTS = 0
        self._setTimer()

    def clearTimer(self):
        """
        清理定时器
        """
        if self._nextTimer:
            self._nextTimer.cancel()
            self._nextTimer = None
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None

    def _setTimer(self):
        """
        设置添加美人鱼定时器
        """
        self.clearTimer()
        self._fishType, self._interval, self._duration = self._randomFishTypeAndInterval()
        self._nextTimer = FTLoopTimer(self._interval, 0, self._addMermaidFishGroup, isDebut=True)
        self._nextTimer.start()


    def _addMermaidFishGroup(self, isDebut=False):
        """
        添加美人鱼
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        if not self._canAddMermaid():  # 新出场的美人鱼不满足出现条件
            return
        if self._fishType not in self.table.runConfig.allMiniGameGroupIds:
            return
        if self.table.hasTideFishGroup():   # 当前渔场存在鱼潮
            return
        if self.table.hasSuperBossFishGroup():  # 超级Boss已经存在或即将出现
            return
        self._dealAutoFillMermaid()
        if isDebut:
            self._mermaidAppearTS = int(time.time())
        if not self._fishType:
            ftlog.error("_addMermaidFishGroup error", self.table.tableId, self._fishType)
            return
        groupIds = self.table.runConfig.allMiniGameGroupIds[self._fishType]
        if ftlog.is_debug():
            ftlog.debug("_addMermaidFishGroup", self.table.tableId, isDebut, groupIds)
        if groupIds:
            self._groupId = random.choice(groupIds)
            self._group = self.table.insertFishGroup(self._groupId)
            self._fishId = self._group.startFishId
            if int(time.time()) + self._group.totalTime < self._mermaidAppearTS + self._duration:
                self._addAutoFillMermaid(self._group.totalTime + 1)

    def _canAddMermaid(self):
        """
        能否添加美人鱼（当渔场已存在自动填充美人鱼时，新出场的美人鱼不会被添加）
        """
        if self.table.fishMap.get(self._fishId, {}).get("alive"):
            return False
        return True

    def _dealAutoFillMermaid(self):
        """
        处理自动填充美人鱼相关逻辑
        """
        if self._group and self._group.extendGroupTime > 0:
            if int(time.time()) + self._group.extendGroupTime < self._mermaidAppearTS + self._duration:
                if ftlog.is_debug():
                    ftlog.debug("dealDelayAutoFill->", self.table.tableId, self._mermaidAppearTS,
                                self._group.extendGroupTime)
                self._addAutoFillMermaid(self._group.extendGroupTime)
                self._group.extendGroupTime = 0
            else:
                if ftlog.is_debug():
                    ftlog.debug("MermaidFishGroup._addMermaidFishGroup, cancel insert !", self.table.tableId, self._groupId)

    def _addAutoFillMermaid(self, interval):
        """
        延时添加自动填充美人鱼
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        self._autofillTimer = FTLoopTimer(interval, 0, self._addMermaidFishGroup)
        self._autofillTimer.start()

    def _randomFishTypeAndInterval(self):
        fishType = 0
        interval = 180
        duration = 30
        randomNum = random.randint(1, 10000)
        for fishMap in config.getMiniGameFishConf(self.table.runConfig.fishPool):
            probb = fishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = int(fishMap["fishType"])
                interval = int(fishMap["interval"])
                duration = int(fishMap["duration"])
                break
        if interval != self._interval and self._nextTimer is not None:
            self._interval = interval
            self._setTimer()
        return fishType, interval, duration
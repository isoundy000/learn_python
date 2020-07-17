# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/4/12.
"""

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class BossFishGroup(object):
    """
    boss鱼群
    """
    def __init__(self, table):
        self.table = table
        self._interval = 300                # 时间间隔
        self._bossGroupId = None            # boss鱼群Id
        self._nextBossTimer = None          # boss定时器
        self._setBossTimer()                # 启动定时器
        self._fishType = 0                  # bossId
        self._bossAppearTS = 0              # boss出现的时间
        self._autofillTimer = None          # 自动填充的时间
        self._group = None                  # 鱼群对象

    def clearTimer(self):
        if self._nextBossTimer:
            self._nextBossTimer.cancel()
            self._nextBossTimer = None
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None

    def _setBossTimer(self):
        """启动定时器"""
        if self._nextBossTimer:
            self._nextBossTimer.cancel()
            self._nextBossTimer = None
        self._nextBossTimer = FTLoopTimer(self._interval, -1, self._addBossFishGroup)
        self._nextBossTimer.start()

    def _addBossFishGroup(self, isSysTimerCall=True, isKilled=False):
        """
        添加boss鱼群
        :param isSysTimerCall: 系统自己调用的
        :param isKilled: 是否杀死了boss
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group and not isSysTimerCall and not isKilled and self._group.extendGroupTime > 0:
                if int(time.time()) + self._group.extendGroupTime < self._bossAppearTS + 60:
                    if ftlog.is_debug():
                        ftlog.debug("BossFishGroup._addBossFishGroup, delay !", self.table.tableId, self._bossGroupId,
                                self._group.extendGroupTime)
                    self._autofillTimer = FTLoopTimer(self._group.extendGroupTime, 0, self._addBossFishGroup, False, False)
                    self._autofillTimer.start()
                    self._group.extendGroupTime = 0
                else:
                    if ftlog.is_debug():
                        ftlog.debug("BossFishGroup._addBossFishGroup, cancel insert !", self.table.tableId, self._bossGroupId)
                return
        self._group = None
        # 超级boss已经或即将出现时不创建普通boss.
        if self.table.hasSuperBossFishGroup():
            return
        if isSysTimerCall:
            self._bossAppearTS = int(time.time())
            self._fishType = 0
            randomNum = random.randint(1, 10000)
            for bossFishMap in config.getBossFishConf(self.table.runConfig.fishPool):
                probb = bossFishMap["probb"]
                if probb[0] <= randomNum <= probb[-1]:
                    self._fishType = bossFishMap["fishType"]
                    break
        bossGroupIds = self.table.runConfig.allBossGroupIds[self._fishType]
        if bossGroupIds:
            if isSysTimerCall:
                self._bossGroupId = bossGroupIds[0]
            else:
                self._bossGroupId = random.choice(bossGroupIds[1:])
            if ftlog.is_debug():
                ftlog.debug("BossFishGroup._addBossFishGroup", self.table.tableId, self._bossGroupId, isSysTimerCall, isKilled)
            self._group = self.table.insertFishGroup(self._bossGroupId)
            if self._group:
                if int(time.time()) + self._group.totalTime < self._bossAppearTS + 60:
                    self._autofillTimer = FTLoopTimer(self._group.totalTime + 1, 0, self._addBossFishGroup, False, False)
                    self._autofillTimer.start()

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        if self._fishType in event.fishTypes and int(time.time()) < self._bossAppearTS + 60:
            if ftlog.is_debug():
                ftlog.debug("BossFishGroup.triggerCatchFishEvent", self.table.tableId)
            self._addBossFishGroup(False, True)
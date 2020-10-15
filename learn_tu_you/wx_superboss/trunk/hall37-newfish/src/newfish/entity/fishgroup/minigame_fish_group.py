# -*- coding: utf-8 -*-

# Created by xsy on 4th, August 2020

# 附带小游戏鱼阵（美人鱼）

import random
import time
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config
from newfish.entity.cron import FTCron


cronTime = {
    "days": {
        "count": 365,
        "first": "",
        "interval": "1d"
    },
    "times_in_day": {
        "count": 10000,
        "first": [
            "0:04:30",
            "0:07:30",
            "0:10:30"
        ],
        "interval": 12
    }
}


class MiniGameFishGroup(object):
    """
    小游戏鱼阵
    """
    def __init__(self, table):
        self.table = table
        # 美人鱼出现间隔
        self._interval = 180
        # 每轮持续时间
        self._duration = 30
        # 初始化配置定时器
        self._initConfTimer = None
        # 下个美人鱼出现定时器
        self._nextTimer = None
        # 在美人鱼存续期内自动填充定时器
        self._autofillTimer = None
        # 鱼阵文件名
        self._groupId = None
        # 当前美人鱼ID
        self._fishType = 0
        # 当前美人鱼阵对象
        self._group = None
        # 当前美人鱼ID
        self._fishId = 0
        # 美人鱼首次出现时间戳
        self._mermaidAppearTS = 0
        self._initConf()

    def clearTimer(self):
        """
        清理定时器
        """
        if self._initConfTimer:
            self._initConfTimer.cancel()
            self._initConfTimer = None
        if self._nextTimer:
            self._nextTimer.cancel()
            self._nextTimer = None
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None

    def _initConf(self):
        """
        初始化配置
        """
        if self._initConfTimer:
            self._initConfTimer.cancel()
            self._initConfTimer = None
        self.cronTime = cronTime
        self._cron = FTCron(self.cronTime)
        self._interval = self._cron.getNextLater()
        if self._interval > 0:
            self._setTimer()
            self._initConfTimer = FTLoopTimer(self._interval + 1, 0, self._initConf)
            self._initConfTimer.start()
        else:
            ftlog.error("MiniGameFishGroup initConf error", self._cron.getTimeList())

    def _setTimer(self):
        """
        设置添加美人鱼定时器
        """
        self._fishType, self._duration = self._randomFishType()
        self._nextTimer = FTLoopTimer(self._interval, 0, self._addMermaidFishGroup, isDebut=True)
        self._nextTimer.start()

    def _addMermaidFishGroup(self, isDebut=False):
        """
        添加美人鱼
        @param isDebut: 是否首次出现
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        if self._fishType not in self.table.runConfig.allMiniGameGroupIds:
            return
        if not self._canAddMermaid():  # 新出场的美人鱼不满足出现条件
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
        self._group = None
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
        处理自动填充美人鱼相关逻辑（因冰冻延迟填充）
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
        if ftlog.is_debug():
            ftlog.debug("_addAutoFillMermaid", self.table.tableId, interval)
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        self._autofillTimer = FTLoopTimer(interval, 0, self._addMermaidFishGroup)
        self._autofillTimer.start()

    def _randomFishType(self):
        """
        获取随机到的鱼ID
        """
        fishType = 0
        duration = 30
        randomNum = random.randint(1, 10000)
        for fishMap in config.getMiniGameFishConf(self.table.runConfig.fishPool):
            probb = fishMap["probb"]
            if probb[0] <= randomNum <= probb[-1]:
                fishType = int(fishMap["fishType"])
                duration = int(fishMap["duration"])
                break
        return fishType, duration
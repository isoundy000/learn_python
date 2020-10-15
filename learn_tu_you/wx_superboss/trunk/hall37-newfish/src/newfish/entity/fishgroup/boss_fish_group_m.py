# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/6/29.
"""

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config
from newfish.entity.cron import FTCron


# 测试配置
cronTime = {
    "days": {
        "count": 365,
        "first": "",
        "interval": "1d"
    },
    "times_in_day": {
        "count": 10000,
        "first": [
            "0:01"
        ],
        "interval": 1
    }
}


class BossFishGroup(object):
    """
    千炮模式boss鱼群
    """
    def __init__(self, table):
        self.table = table
        # 每个Boss出现间隔
        self._interval = 300
        # 每轮Boss的持续时间
        self._duration = 90
        # 初始化配置定时器
        self._initConfTimer = None
        # 下一个Boss出现定时器
        self._nextBossTimer = None
        # 在Boss存续期内自动填充定时器
        self._autofillTimer = None
        # Boss鱼阵文件名
        self._bossGroupId = None
        # 当前Boss鱼ID
        self._fishType = 0
        # 当前Boss鱼阵对象
        self._group = None
        # 当前Boss鱼的fishId
        self._fishId = 0
        # Boss首次出现时间戳
        self._bossAppearTS = 0
        # 深渊螃蟹
        self._crabFishType = 12233
        # 捕获深渊螃蟹的次数
        self._catchCrabNum = 0
        self._initConf()

    def clearTimer(self):
        """
        清理定时器
        """
        if self._initConfTimer:
            self._initConfTimer.cancel()
            self._initConfTimer = None
        if self._nextBossTimer:
            self._nextBossTimer.cancel()
            self._nextBossTimer = None
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
        if self.table.room.roomConf.get("bossConf"):
            self.cronTime = self.table.room.roomConf.get("bossConf").get("cronTime")
        self._cron = FTCron(self.cronTime)
        self._interval = self._cron.getNextLater()
        if self._interval > 0:
            self._setBossTimer()
            self._initConfTimer = FTLoopTimer(self._interval + 1, 0, self._initConf)
            self._initConfTimer.start()
        else:
            ftlog.error("BossFishGroup initConf error", self._cron.getTimeList())

    def _setBossTimer(self):
        """
        设置添加Boss定时器
        """
        if self._nextBossTimer:
            self._nextBossTimer.cancel()
            self._nextBossTimer = None
        self._nextBossTimer = FTLoopTimer(self._interval, 0, self._addBossFishGroup, isDebut=True)
        self._nextBossTimer.start()

    def _addBossFishGroup(self, isDebut=False):
        """
        添加Boss
        @param isDebut: 是否首次出现
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        if not self._canAddBoss():  # 新出场的Boss不满足出现条件
            return
        if self.table.hasSuperBossFishGroup():  # 超级Boss已经存在或即将出现时不创建普通Boss
            return
        if self.table.hasTideFishGroup():   # 当前渔场存在鱼潮
            return
        self._dealAutoFillBoss()
        if isDebut:
            # Boss新出场时，切换自动填充鱼随机分组
            self.table.autofillFishGroup and self.table.autofillFishGroup.refreshCategoryGroupConf()
            self._bossAppearTS = int(time.time())
            self._fishType = 0
            randomNum = random.randint(1, 10000)
            for bossFishMap in config.getBossFishConf(self.table.runConfig.fishPool, self.table.runConfig.gameMode):
                probb = bossFishMap["probb"]
                if probb[0] <= randomNum <= probb[-1]:
                    self._fishType = bossFishMap["fishType"]
                    break
        if not self._fishType:
            ftlog.error("_addBossFishGroup error", self.table.tableId, self._fishType)
            return
        self._group = None
        bossGroupIds = self.table.runConfig.allBossGroupIds[self._fishType]
        if bossGroupIds:
            self._bossGroupId = bossGroupIds[0] if isDebut else random.choice(bossGroupIds[1:])
            if ftlog.is_debug():
                ftlog.debug("BossFishGroup._addBossFishGroup", self.table.tableId, self._bossGroupId, isDebut)
            self._catchCrabNum = 0
            self._group = self.table.insertFishGroup(self._bossGroupId)
            self._fishId = self._group.startFishId
            if int(time.time()) + self._group.totalTime < self._bossAppearTS + self._duration:
                self._addAutoFillBoss(self._group.totalTime + 1)

    def _canAddBoss(self):
        """
        能否添加Boss（当渔场已存在自动填充Boss时，新出场的Boss不会被添加）
        """
        if self.table.fishMap.get(self._fishId, {}).get("alive"):
            return False
        return True

    def _dealAutoFillBoss(self):
        """
        处理自动填充Boss相关逻辑
        """
        if self._group and self._group.extendGroupTime > 0: # 存在冰冻延时
            if int(time.time()) + self._group.extendGroupTime < self._bossAppearTS + self._duration:    # 冰冻结束时间在Boss的持续时间内
                if ftlog.is_debug():
                    ftlog.debug("dealDelayAutoFill->", self.table.tableId, self._bossGroupId,
                            self._group.extendGroupTime)
                self._addAutoFillBoss(self._group.extendGroupTime)
                self._group.extendGroupTime = 0
            else:
                if ftlog.is_debug():
                    ftlog.debug("BossFishGroup._addBossFishGroup, cancel insert !", self.table.tableId, self._bossGroupId)

    def _addAutoFillBoss(self, interval):
        """
        延时添加自动填充Boss
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
        self._autofillTimer = FTLoopTimer(interval, 0, self._addBossFishGroup)
        self._autofillTimer.start()

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        if self._fishType in event.fishTypes and int(time.time()) < self._bossAppearTS + self._duration:
            if ftlog.is_debug():
                ftlog.debug("BossFishGroup.triggerCatchFishEvent_m", self.table.tableId, self._fishType)
            if self._fishType == self._crabFishType:                             # 深渊螃蟹一对
                self._catchCrabNum += 1
                if self._catchCrabNum >= 2:
                    self._addAutoFillBoss(4)
            else:
                self._addAutoFillBoss(4)
# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/6/16.
"""

import random
import math

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util


class AutofillFishGroup(object):
    """
    千炮模式自动填充鱼群
    """
    def __init__(self, table):
        self.table = table
        # 自动填充鱼配置
        self.autofillFishConf = {}
        # 各鱼种类别下鱼组index
        self._categoryGroupConf = {}
        # 各鱼种类别定时器
        self._checkCategoryTimerList = []
        # 各鱼种类别下的鱼群定时器
        self._checkShoalTimerList = []
        # 刷新分组配置定时器
        self._refreshGroupConfTimer = None
        self.startDefaultAutofillFish()
        # 大奖赛间隔5分钟刷新分组配置
        if self.table.typeName == config.FISH_GRAND_PRIX:
            self._refreshGroupConfTimer = FTLoopTimer(300, -1, self.refreshCategoryGroupConf)
            self._refreshGroupConfTimer.start()

    def clearTimer(self):
        """
        清理所有定时器
        """
        self.clearCategoryTimer()
        self.clearShoalTimer()
        if self._refreshGroupConfTimer:
            self._refreshGroupConfTimer.cancel()
            self._refreshGroupConfTimer = None
        if ftlog.is_debug():
            ftlog.debug("AutofillFishGroup clearTimer", self.table.tableId)

    def clearCategoryTimer(self):
        """
        清理鱼种类别定时器
        """
        for _timer in self._checkCategoryTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        self._checkCategoryTimerList = []

    def clearShoalTimer(self):
        """
        清理鱼种类别下的鱼群定时器
        """
        for _timer in self._checkShoalTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        self._checkShoalTimerList = []

    def startDefaultAutofillFish(self):
        """
        默认状态下的自动填充鱼
        """
        self.defaultConf = config.getAutofillFishConf_m("default", self.table.runConfig.fishPool)
        if self.defaultConf:
            self._generalCategoryGroupConf(self.defaultConf)
            self._generalCategoryTimer()
            self._generalShoalTimer()

    def startSuperBossAutofillFish(self):
        """
        超级Boss期间的自动填充鱼
        """
        self.superBossConf = config.getAutofillFishConf_m("superBoss", self.table.runConfig.fishPool)
        if self.superBossConf:
            self._generalCategoryGroupConf(self.superBossConf)
            self._generalCategoryTimer()
            self._generalShoalTimer()

    def refreshCategoryGroupConf(self):
        """
        刷新各类鱼的分组数据（重新随机分组）
        """
        self._generalCategoryGroupConf()

    def _generalCategoryGroupConf(self, autofillFishConf=None):
        """
        生成并记录各类鱼的分组数据
        """
        self.autofillFishConf = autofillFishConf or self.autofillFishConf
        for categoryId, categoryConf in self.autofillFishConf.iteritems():
            self._categoryGroupConf[categoryId] = random.choice(categoryConf["groups"])
        if ftlog.is_debug():
            ftlog.debug("_generalCategoryGroupConf", self.table.tableId, self._categoryGroupConf)

    def _generalCategoryTimer(self):
        """
        生成并存储各类鱼的定时器
        """
        self.clearCategoryTimer()
        for categoryId, categoryConf in self.autofillFishConf.iteritems():
            interval = categoryConf["cSupplyInterval"]
            checkTimer = FTLoopTimer(interval, -1, self._checkCategoryAutoFillFish, categoryId)
            checkTimer.start()
            self._checkCategoryTimerList.append(checkTimer)

    def _checkCategoryAutoFillFish(self, categoryId):
        """
        检测该类鱼是否需要填充鱼
        """
        if self.table.hasTideFishGroup():  # 当前渔场存在鱼潮
            return
        group = self._categoryGroupConf[categoryId]
        groupType = group["groupType"]
        if groupType == 1:
            for fishConf in group["fishes"]:
                fillCount, totalCount = self._getAutoFillCount([fishConf])
                self._addAutoFillFishGroup(categoryId, fishConf, fillCount, totalCount)
        elif groupType == 2:
            fillCount, totalCount = self._getAutoFillCount(group["fishes"])
            for _ in xrange(fillCount):
                fishConf = util.getOneResultByWeight(group["fishes"])
                self._addAutoFillFishGroup(categoryId, fishConf, 1, totalCount)

    def _getAutoFillCount(self, fishConfList):
        """
        统计某类鱼的存活数量，再计算某条鱼所需填充数量
        @return: 需要填充数量, 该类鱼存活数量
        """
        aliveCount = 0
        fishConf = None
        for fishConf in fishConfList:
            aliveCount += self.table.fishCountMap.get(fishConf["fishType"], 0)
        if aliveCount <= fishConf["minCount"]:
            randInt = random.randint(fishConf["minCount"], fishConf["maxCount"])
            return int(math.ceil(float(randInt - aliveCount) / max(fishConf["fishCount"], 1))), aliveCount
        return 0, aliveCount

    def _addAutoFillFishGroup(self, categoryId, fishConf, fillCount, aliveCount):
        """
        添加填充鱼
        """
        if fillCount > 0:
            if fishConf["fishType"] not in self.table.runConfig.allAutofillGroupIds:
                ftlog.error("_addAutoFillFishGroup error", self.table.tableId, fishConf["fishType"])
                return
            if ftlog.is_debug():
                ftlog.debug("_addAutoFillFishGroup tableId =", self.table.tableId,
                            "categoryId =", categoryId,
                            "fishType =", fishConf["fishType"],
                            "aliveCount =", aliveCount,
                            "fillCount =", fillCount,
                            "maxCount =", fishConf["maxCount"])
            autofillGroupIds = self.table.runConfig.allAutofillGroupIds[fishConf["fishType"]]
            if autofillGroupIds:
                groupNames = random.sample(autofillGroupIds, min(len(autofillGroupIds), fillCount))
                groupNames and self.table.insertFishGroup(groupNames)

    def _generalShoalTimer(self):
        """
        生成并存储各类鱼的鱼群定时器
        """
        self.clearShoalTimer()
        for categoryId, categoryConf in self.autofillFishConf.iteritems():
            interval = categoryConf["sSupplyInterval"]
            if interval > 0:
                checkTimer = FTLoopTimer(interval, -1, self._checkAutoFillFishShoal, categoryId)
                checkTimer.start()
                self._checkShoalTimerList.append(checkTimer)

    def _checkAutoFillFishShoal(self, categoryId):
        """
        检测该类鱼的鱼群是否需要填充
        """
        if self.table.hasTideFishGroup():  # 当前渔场存在鱼潮
            return
        group = self._categoryGroupConf[categoryId]
        fishConf = random.choice(group["fishes"])
        self._addAutoFillFishShoal(fishConf)

    def _addAutoFillFishShoal(self, fishConf):
        """
        添加填充鱼群
        """
        autofillGroupIds = self.table.runConfig.allAutofillShoalGroupIds[fishConf["fishType"]]
        if autofillGroupIds:
            groupNames = random.sample(autofillGroupIds, 1)
            groupNames and self.table.insertFishGroup(groupNames)

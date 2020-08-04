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
        self.startDefaultAutofillFish()

    def clearTimer(self):
        """
        清理所有定时器
        """
        self.clearCategoryTimer()
        self.clearShoalTimer()
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

    def _generalCategoryGroupConf(self, autofillFishConf):
        """
        生成并记录各类鱼的分组index
        """
        self.autofillFishConf = autofillFishConf
        for categoryId, categoryConf in autofillFishConf.iteritems():
            self._categoryGroupConf[categoryId] = random.choice(categoryConf["groups"])

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
        group = self._categoryGroupConf[categoryId]
        groupType = group["groupType"]
        if groupType == 1:
            for fishConf in group["fishes"]:
                fillCount = self._getAutoFillCount(fishConf)
                self._addAutoFillFishGroup(fishConf, fillCount)
        elif groupType == 2:
            fishConf = util.getOneResultByWeight(group["fishes"])
            if fishConf:
                fillCount = self._getAutoFillCount(fishConf)
                self._addAutoFillFishGroup(fishConf, fillCount)
                ftlog.debug("_checkCategoryAutoFillFish", fillCount, self.table.tableId)

    def _getAutoFillCount(self, fishConf):
        """
        获取某条鱼所需填充数量
        """
        totalCount = self.table.fishCountMap.get(fishConf["fishType"], 0)
        if totalCount <= fishConf["minCount"]:
            randInt = random.randint(fishConf["minCount"], fishConf["maxCount"])
            return int(math.ceil(float(randInt - totalCount) / max(fishConf["fishCount"], 1)))
        return 0

    def _addAutoFillFishGroup(self, fishConf, fillCount):
        """
        添加填充鱼
        """
        if fillCount > 0:
            if fishConf["fishType"] not in self.table.runConfig.allAutofillGroupIds:
                return
            if ftlog.is_debug():
                ftlog.debug("_addAutoFillFishGroup tableId =", self.table.tableId,
                            "fishType =", fishConf["fishType"],
                            "currentCount =", self.table.fishCountMap.get(fishConf["fishType"], 0),
                            "maxCount =", fishConf["maxCount"],
                            "fillCount =", fillCount)
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

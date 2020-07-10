#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/10

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
        # 各鱼种类别下鱼组index
        self._categoryGroupConf = {}
        # 各鱼种类别定时器
        self._checkCategoryTimerList = []
        self.startDefaultAutofillFishTimer()

    def clearTimer(self):
        """清理定时器"""
        for _timer in self._checkCategoryTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        self._checkCategoryTimerList = []
        ftlog.debug("AutofillFishGroup clearTimer", self.table.tableId)

    def startDefaultAutofillFishTimer(self):
        """
        启动默认填充鱼定时器
        """
        self.clearTimer()
        self.defaultConf = config.getAutofillFishConf_m("default", self.table.runConfig.fishPool)
        if self.defaultConf:
            self._generalCategoryGroupConf(self.defaultConf)
            self._generalCategoryTimer(self.defaultConf)

    def startSuperBossAutofillFishTimer(self):
        """
        启动超级Boss填充鱼定时器
        """
        self.clearTimer()
        self.superBossConf = config.getAutofillFishConf_m("superBoss", self.table.runConfig.fishPool)
        if self.superBossConf:
            self._generalCategoryGroupConf(self.superBossConf)
            self._generalCategoryTimer(self.superBossConf)

    def _generalCategoryGroupConf(self, autofillFishConf):
        """
        生成并记录各鱼种类别的组index
        """
        for categoryId, categoryConf in autofillFishConf.iteritems():
            groupIndex = random.choice(xrange(len(categoryConf["groups"])))
            self._categoryGroupConf[categoryId] = groupIndex

    def _generalCategoryTimer(self, autofillFishConf):
        """
        生成并存储各鱼种类别定时器
        """
        for categoryId, categoryConf in autofillFishConf.iteritems():
            interval = categoryConf["supplyInterval"]
            checkTimer = FTLoopTimer(interval, -1, self._checkCategoryAutoFillFish, categoryConf)
            checkTimer.start()
            self._checkCategoryTimerList.append(checkTimer)

    def _checkCategoryAutoFillFish(self, categoryConf):
        """
        检测该鱼种类别是否需要填充鱼
        """
        grounIndex = self._categoryGroupConf[categoryConf["categoryId"]]
        group = categoryConf["groups"][grounIndex]
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
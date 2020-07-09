#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/9


import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class AutofillFishGroup(object):
    """
    autofill鱼群
    """

    def __init__(self, table):
        self.table = table
        self.autofillFishConf = config.getAutofillFishConf(self.table.runConfig.fishPool)
        self.fishTypeList = []
        self._nextTimerList = []                # 正常出鱼定时器
        self._checkCountTimerList = []          # 补鱼定时器
        self._setAutofillFishTimer()            # 启动自动填充鱼的定时器
    
    def clearTimer(self):
        """清理定时器"""
        for _timer in self._nextTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        for _timer in self._checkCountTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        self._nextTimerList = []
        self._checkCountTimerList = []
    
    def _setAutofillFishTimer(self):
        """
        设置自动填充鱼的定时器
        """
        for idx, fishConf in enumerate(self.autofillFishConf):
            self.fishTypeList.append([fish["fishType"] for fish in fishConf["fish"]])
            interval = random.randint(fishConf["minInterval"], fishConf["maxInterval"])     # 自动添加鱼的时间间隔
            fishTimer = FTLoopTimer(interval, 0, self._addAutofillFishGroup, idx)
            fishTimer.start()
            self._nextTimerList.append(fishTimer)
            supplyInterval = fishConf["supplyInterval"]                                     # 补充鱼时间间隔
            checkTimer = FTLoopTimer(max(3, supplyInterval), -1, self._checkFishTypeCount, idx)
            checkTimer.start()
            self._checkCountTimerList.append(checkTimer)
        if ftlog.is_debug():
            ftlog.debug("_setAutofillFishTimer", "tableId =", self.table.tableId, self.fishTypeList)

    def _addAutofillFishGroup(self, idx):
        """添加填充鱼群"""
        fishConf = self.autofillFishConf[idx]
        fishType, interval = self._randomFishTypeAndInterval(fishConf)
        if fishType not in self.table.runConfig.allAutofillGroupIds or interval == 0:
            if ftlog.is_debug():
                ftlog.debug("_addAutofillFishGroup, error", self.table.tableId, fishType, interval)
            return
        maxCount = fishConf["maxCount"]
        totalCount = self._getFishCountByType(idx)
        if totalCount < maxCount and not self._hasTideFish() and not self.table.hasSuperBossFishGroup():
            autofillFishGroupIds = self.table.runConfig.allAutofillGroupIds[fishType]
            if autofillFishGroupIds:
                autofillGroupId = random.choice(autofillFishGroupIds)
                if ftlog.is_debug():
                    ftlog.debug("_addAutofillFishGroup, insert !", "tableId =", self.table.tableId, "idx =", idx,
                                "totalCount = ", totalCount, "fishType =", fishType, "autofillGroupId =", autofillGroupId)
                self.table.insertFishGroup(autofillGroupId)
        else:
            if ftlog.is_debug():
                ftlog.debug("_addAutofillFishGroup, too many fish !", "tableId =", self.table.tableId,
                            "totalCount =", totalCount, "fishType =", fishType, "idx =", idx)
        # totalCount = self._getFishCountByType(idx)
        try:
            self._nextTimerList[idx] = None
            self._nextTimerList[idx] = FTLoopTimer(interval, 0, self._addAutofillFishGroup, idx)
            self._nextTimerList[idx].start()
        except:
            ftlog.error("_addAutofillFishGroup", "tableId =", self.table.tableId, "idx =", idx, "totalCount =",
                        totalCount, "fishType =", fishType, "interval =", interval, len(self._nextTimerList))
        if ftlog.is_debug():
            totalCount = self._getFishCountByType(idx)
            ftlog.debug("_addAutofillFishGroup", "tableId =", self.table.tableId, "idx =", idx, "totalCount =", totalCount,
                        "fishType =", fishType, "interval =", interval)

    def _randomFishTypeAndInterval(self, fishConf):
        """
        随机fishType和时间间隔，用以添加autofill鱼阵
        """
        fishType = 0
        fishSize = len(fishConf["fish"])
        interval = random.randint(fishConf["minInterval"], fishConf["maxInterval"])
        if fishSize > 0:
            if fishSize == 1:
                fishType = int(fishConf["fish"][0]["fishType"])
            else:
                randomNum = random.randint(1, fishConf["fish"][-1]["probb"][-1])
                ret = [int(val["fishType"]) for val in fishConf["fish"] if val["probb"][0] <= randomNum <= val["probb"][-1]]
                fishType = ret[0] if ret else 0
        if ftlog.is_debug():
            ftlog.debug("_randomFishTypeAndInterval", self.table.tableId, fishType, interval, fishConf["fish"][-1]["probb"][-1])
        return fishType, interval


    def _getFishCountByType(self, idx):
        """
        获取鱼阵中鱼的数量
        """
        # totalCount = 0
        # nowTableTime = time.time() - self.table.startTime
        # for fId, v in self.table.fishMap.items():
        #     fishType = v.get("fishType", 0)
        #     if fishType in self.fishTypeList[idx]:
        #         if v["alive"] and v["group"] and v["group"].isAlive(nowTableTime):
        #             totalCount += 1
        #     # if v["group"] and v["group"].isAlive(nowTableTime) is True and v["alive"] is True:
        #     #     fishType = v.get("conf", {}).get("fishType", 0)
        #     #     if fishType in self.fishTypeList[idx]:
        #     #
        tc = 0
        for ft in self.fishTypeList[idx]:
            if ft in self.table.fishCountMap:
                tc += self.table.fishCountMap[ft]
        totalCount = tc
        if tc != totalCount:
            ftlog.debug("_getFishCountByType, tableId =", self.table.tableId, ", countDiff =", totalCount - tc)
        return totalCount

    def _hasTideFish(self):
        """
        是否存在鱼潮
        """
        enterTime = time.time()
        exitTime = 0
        for group in self.table.normalFishGroups.itervalues():
            # 普通鱼潮,活动鱼潮1,活动鱼潮2
            if group.id in self.table.runConfig.allTideGroupIds \
                    or group.id in self.table.runConfig.allActTideGroupIds \
                    or group.id in self.table.runConfig.allActTide2GroupIds:
                enterTime = min(enterTime, self.table.startTime + group.enterTime)
                exitTime = max(exitTime, self.table.startTime + group.exitTime + group.addTime)
        ret = int(enterTime) <= int(time.time()) <= int(exitTime)
        if ftlog.is_debug():
            ftlog.debug("_hasTideFish, ret :", ret, self.table.tableId)
        return ret

    def _checkFishTypeCount(self, idx):
        """
        检测是否应该补充某种类型鱼的数量
        """
        totalCount = self._getFishCountByType(idx)
        fishConf = self.autofillFishConf[idx]
        if totalCount < fishConf["minCount"] and not self._hasTideFish():
            isSupplyNow = True
            if self._nextTimerList[idx]:
                if self._nextTimerList[idx].getTimeOut() > 1:
                    self._nextTimerList[idx].cancel()
                else:
                    isSupplyNow = False
            if isSupplyNow:
                self._addAutofillFishGroup(idx)
            if ftlog.is_debug():
                ftlog.debug("_checkFishTypeCount, supply !!", "tableId =", self.table.tableId, "idx =", idx,
                            isSupplyNow)
        if ftlog.is_debug():
            ftlog.debug("_checkFishTypeCount", "tableId =", self.table.tableId, "idx =", idx, "totalCount =", totalCount)
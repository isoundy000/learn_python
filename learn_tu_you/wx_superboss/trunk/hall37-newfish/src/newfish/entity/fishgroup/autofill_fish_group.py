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
            interval = random.randint(fishConf["minInterval"], fishConf["maxInterval"])
            fishTimer = FTLoopTimer(interval, 0, self._addAutofillFishGroup, idx)
            fishTimer.start()
            self._nextTimerList.append(fishTimer)
            supplyInterval = fishConf["supplyInterval"]
            checkTimer = FTLoopTimer(max(3, supplyInterval), -1, self._checkFishTypeCount, idx)


    def _addAutofillFishGroup(self, idx):
        pass

    def _randomFishTypeAndInterval(self, fishConf):
        pass

    def _getFishCountByType(self, idx):
        """
        获取鱼阵中鱼的数量
        """
        pass

    def _hasTideFish(self):
        """
        是否存在鱼潮
        """
        pass

    def _checkFishTypeCount(self, idx):
        """
        检测是否应该补充某种类型鱼的数量
        """
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.fishactivity.fish_activity import ActivityType


class ActivityFishGroup(object):
    """
    活动鱼(幸运海螺)及河马
    """

    def __init__(self, table):
        self.table = table
        self._nextActivityGroup()
        self._nextHippoTimer = None
        self._nextHippoGroup()

    def clearTimer(self):
        if self.checkTimer:                     # 活动鱼鱼阵
            self.checkTimer.cancel()
            self.checkTimer = None
        if self._nextHippoTimer:                # 海马鱼阵
            self._nextHippoTimer.cancel()
            self._nextHippoTimer = None

    def _nextActivityGroup(self):
        self._lastAppearTime = 0
        self.checkTimer = FTLoopTimer(60, -1, self._checkAcCondition)
        self.checkTimer.start()

    def _nextHippoGroup(self):
        '''下一波河马鱼阵'''
        hippoFishConf = config.getHippoFishConf(self.table.runConfig.fishPool)
        if self._nextHippoTimer:
            self._nextHippoTimer.cancel()
            self._nextHippoTimer = None
        if hippoFishConf:
            minTime = hippoFishConf["minTime"]
            maxTime = hippoFishConf["maxTime"]
            randomTime = random.randint(minTime, maxTime)
            ftlog.debug("HippoFishGroup->_nextHippoGroup->", self.table.runConfig.fishPool, minTime, maxTime,
                        randomTime)
            self._nextHippoTimer = FTLoopTimer(randomTime, 0, self._checkHippoCondition)
            self._nextHippoTimer.start()

    def _checkHippoCondition(self):
        """
        检测是否添加河马鱼阵
        """
        pass

    def _checkAcCondition(self):
        """
        检测是否应该添加活动鱼鱼阵
        """
        pass
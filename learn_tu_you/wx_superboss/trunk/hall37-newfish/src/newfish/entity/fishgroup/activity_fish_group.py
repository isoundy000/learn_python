# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/9/21.
"""

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
        """下一次活动的鱼群"""
        self._lastAppearTime = 0                # 最后一次出现鱼群的时间
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
            self._nextHippoTimer = FTLoopTimer(randomTime, 0, self._checkHippoCondition)
            self._nextHippoTimer.start()

    def _checkHippoCondition(self):
        """
        检测是否添加河马鱼阵
        """
        hippoFishConf = config.getHippoFishConf(self.table.runConfig.fishPool)
        isOpen = fish_activity_system.isActivityOpen(ActivityType.ExchangeBonusTask)
        if hippoFishConf and isOpen:
            fishType = hippoFishConf["fishType"]
            allActivityGroupIds = self.table.runConfig.allActivityGroupIds
            groupId = random.choice(allActivityGroupIds[fishType])
            ftlog.debug("HippoFishGroup->_checkHippoCondition->", groupId)
            self._addActivityFishGroup(groupId)
        self._nextHippoGroup()

    def _checkAcCondition(self):
        """
        检测是否应该添加活动鱼鱼阵
        """
        activityFishConf = config.getActivityFishConf(self.table.runConfig.fishPool)
        isOpen = fish_activity_system.isActivityOpen(ActivityType.CatchItemExchange)
        if activityFishConf and isOpen:
            totalBullet = sum([player.activityConsumeClip for player in self.table.players if player and player.userId > 0])
            ftlog.debug("ActivityFishGroup->_checkCondition->totalBullet =", totalBullet, self.table.bigRoomId)
            interval = time.time() - self._lastAppearTime
            if (totalBullet >= activityFishConf["totalBullet"] and interval >= activityFishConf["minSecond"]) or \
                    interval >= activityFishConf["maxSecond"]:  # 子弹大于配置表中的子弹数且时间间隔大于等于最小配置间隔 或者间隔大于等于最大时间，添加活动鱼阵
                randInt = random.randint(1, 10000)
                for fish in activityFishConf["fishes"]:
                    probb = fish["probb"]
                    if probb[0] <= randInt <= probb[1]:
                        fishType = fish["fishType"]
                        allActivityGroupIds = self.table.runConfig.allActivityGroupIds
                        groupId = random.choice(allActivityGroupIds[fishType])
                        self._addActivityFishGroup(groupId)
                        break

    def _addActivityFishGroup(self, groupId):
        """
        添加活动鱼鱼阵,修改鱼阵最后出现时间并重置玩家在活动中消耗的金币数
        """
        ftlog.debug("_addActivityFishGroup", groupId, self.table.tableId)
        self.table.insertFishGroup(groupId)
        self._lastAppearTime = time.time()
        for player in self.table.players:
            if player and player.userId > 0:
                player.resetActivityConsumeClip()       # 重置活动消耗的子弹数

    def _isAppear(self, name):
        """
        是否出现鱼阵
        """
        atideAppearConf = config.getPublic(name)
        if atideAppearConf:
            startTime = util.getTimestampFromStr(atideAppearConf[0])
            endTime = util.getTimestampFromStr(atideAppearConf[1])
            if startTime <= int(time.time()) <= endTime:
                return True
        return False
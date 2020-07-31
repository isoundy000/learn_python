# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/4/12.
"""

import random
import time
import datetime
from itertools import islice

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util


class NormalFishGroup(object):
    """
    普通鱼群
    """
    def __init__(self, table):
        self.table = table
        self._initData()
        self._generateNumOnce = 5                                       # 生成几个鱼群
        self._nextGroupTimer = None
        self._appearIndex = datetime.datetime.now().minute / 15 + 1     # 1、2、3、4
        self._appearTideMinute = [range(9, 15), range(24, 30), range(39, 45), range(54, 60)]     # 鱼潮 [9, 10, 11, 12, 13, 14]
        if self.table.typeName == config.FISH_ROBBERY:                  # 招财模式渔场
            self._generateNumOnce = 10
            self._appearIndex = random.choice(range(len(self.fishes)))
        self._nextGroup()                                               # 添加鱼群

    def clearTimer(self):
        """清理定时器"""
        if self._nextGroupTimer:
            self._nextGroupTimer.cancel()
            self._nextGroupTimer = None

    def _initData(self):
        """初始化数据"""
        self.fishes = {}
        if self.table.typeName == config.FISH_ROBBERY:                  # 招财模式boss鱼潮
            for bossFishMap in config.getBossFishConf(self.table.runConfig.fishPool, self.table.runConfig.gameMode):
                fishType = bossFishMap["fishType"]
                self.fishes.setdefault(fishType, [])
                for groupId in self.table.runConfig.allRobberyBossGroupIds:
                    if fishType and str(fishType) in groupId:
                        self.fishes[fishType].append(groupId)

    def _addNormalFishGroups(self):
        """
        add_group消息默认是下一个鱼阵开始前60s左右发送，每次调用add_group方法耗费时间一般为0.5s以内(包含对象创建和定时器延迟)
        长此以往会导致add_group消息在当前鱼阵结束后没有及时发送，需要修正时间
        """
        selectGroupIds = []
        if self.table.typeName == config.FISH_ROBBERY:                  # 招财模式boss鱼潮
            if len(self.table.runConfig.allRobberyBossGroupIds):
                allRobberyBossGroupIds = self.fishes[self.fishes.keys()[self._appearIndex]]
                tideGroupIds = random.sample(allRobberyBossGroupIds, 1)
                selectGroupIds.extend(tideGroupIds)
                self._appearIndex += 1
                if self._appearIndex >= len(self.fishes):
                    self._appearIndex = 0
        else:
            if self._appearIndex >= len(self._appearTideMinute):        # 4
                self._appearIndex = 0
            currMinute = datetime.datetime.now().minute
            if currMinute in self._appearTideMinute[self._appearIndex] and not self.table.hasSuperBossFishGroup():
                tideGroupIds = []
                if len(self.table.runConfig.allTideGroupIds):       # 普通鱼潮
                    tideGroupIds = random.sample(self.table.runConfig.allTideGroupIds, 1)
                if len(self.table.runConfig.allActTideGroupIds):    # 活动鱼潮1
                    if self._isActivityTideAppear("atideAppearConf"):
                        tideGroupIds = random.sample(self.table.runConfig.allActTideGroupIds, 1)
                if len(self.table.runConfig.allActTide2GroupIds):   # 活动鱼潮2
                    if self._isActivityTideAppear("atide2AppearConf"):
                        tideGroupIds = random.sample(self.table.runConfig.allActTide2GroupIds, 1)
                selectGroupIds.extend(tideGroupIds)
                self._appearIndex += 1
                if ftlog.is_debug():
                    ftlog.debug("_addNormalFishGroups->addTideGroupId = ", tideGroupIds, self._appearIndex, self.table.tableId)
        if ftlog.is_debug():
            ftlog.debug("_addNormalFishGroups->selectGroupIds =", selectGroupIds, self._appearIndex, self.table.tableId)

        selectGroupIds.extend(random.sample(self.table.runConfig.allNormalGroupIds, self._generateNumOnce - len(selectGroupIds)))
        if ftlog.is_debug():
            ftlog.debug("self.table.normalFishGroups =", self.table.tableId, self.table.normalFishGroups)
        enterTime = self.table.getNextGroupEnterTime()
        correctValue = 0
        if enterTime > 0 > self.table.startTime + enterTime - time.time():
            correctValue = abs(self.table.startTime + enterTime - time.time()) + 30
        self.table.addNormalFishGroups(selectGroupIds)
        nextAddGroupInterval = round(self._getNextAddGroupInterval() - correctValue, 2)
        nextAddGroupInterval = max(nextAddGroupInterval, 1)         # 如果当前时间已经过了本该出鱼的时间，则指定下一秒立即出鱼
        self.clearTimer()
        self._nextGroupTimer = FTLoopTimer(nextAddGroupInterval, 0, self._nextGroup)
        self._nextGroupTimer.start()
        if ftlog.is_debug():
            ftlog.debug(
                "_addNormalFishGroups nextAddGroupInterval =", nextAddGroupInterval,
                "nextGroupEnterTimeInterval =", self.table.startTime + enterTime - time.time(),
                "tableId =", self.table.tableId,
                "nowTime =", time.time(),
                "correctValue =", correctValue,
                "selectGroupIds =", selectGroupIds
            )

    def _nextGroup(self):
        """添加普通鱼群"""
        self._addNormalFishGroups()

    def _getNextAddGroupInterval(self):
        """获取下一次添加鱼群的间隔"""
        interval = 0
        start = max(len(self.table.normalFishGroups) - self._generateNumOnce, 0)
        for group in islice(self.table.normalFishGroups.itervalues(), start, None):     # 跳过前start个鱼群
            interval += group.maxEnterTime
        return interval

    def _getActivityTideAppearConf(self, confName):
        """获取活动配置"""
        atideAppearConf = config.getPublic(confName)                # atideAppearConf
        if atideAppearConf:
            startTime = util.getTimestampFromStr(atideAppearConf[0][0])
            endTime = util.getTimestampFromStr(atideAppearConf[0][1])
            if startTime <= int(time.time()) <= endTime:
                return atideAppearConf[1], atideAppearConf[2]       # 出现的整点、索引
        return [], []

    def _isActivityTideAppear(self, confName):
        """活动鱼潮是否出现"""
        try:
            currHour = datetime.datetime.now().hour
            appearHour, appearIndex = self._getActivityTideAppearConf(confName)
            if currHour in appearHour and self._appearIndex in appearIndex:
                return True
        except:
            ftlog.error("_isActivityTideAppear error", confName, self.table.roomId)
        return False
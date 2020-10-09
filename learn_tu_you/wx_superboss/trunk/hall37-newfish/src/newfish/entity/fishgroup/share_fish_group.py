# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/8/7.
"""

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, share_system
from newfish.entity.share_system import RandomChest


class ShareFishGroup(object):
    """
    分享宝箱鱼群
    """
    def __init__(self, table):
        self.table = table
        self._interval = 60         # 间隔
        self._totalTime = 0
        self.checkTimer = FTLoopTimer(self._interval, -1, self._checkCondition)
        self.checkTimer.start()

    def clearTimer(self):
        if self.checkTimer:
            self.checkTimer.cancel()
            self.checkTimer = None

    def _checkCondition(self):
        """检查条件"""
        self._totalTime += self._interval
        # 所有人可见的宝箱出现时间600s
        if self._totalTime % 600 == 0:
            groupId = self._getFishGroupId()
            if groupId:
                self._addShareFishGroup(groupId)
        else:
            # 玩家个人宝箱出现时间
            for player in self.table.players:
                if player:
                    appearCount, playTime, expiresTime, state = self._getShareData(player.userId)
                    if ftlog.is_debug():
                        ftlog.debug("ShareFishGroup_checkCondition", player.userId, appearCount, playTime, expiresTime)
                    appearMinTime = 180 + 120 * appearCount
                    appearMaxTime = 240 + 120 * appearCount
                    groupId = self._getFishGroupId()
                    if (appearMinTime <= playTime * 60 <= appearMaxTime and time.time() > expiresTime and
                       state == share_system.ShareRewardState.Unavailable and groupId):
                        self._addShareFishGroup(groupId, player.userId)

    def _getShareData(self, userId):
        """获取分享宝箱鱼的数据"""
        shareClass = RandomChest(userId)
        return shareClass.shareData[share_system.INDEX_OTHER_DATA].get("appearCount", 0), \
               shareClass.shareData[share_system.INDEX_OTHER_DATA].get("playTime", 0), \
               shareClass.shareData[share_system.INDEX_OTHER_DATA].get("expiresTime", 0), \
               shareClass.shareData[share_system.INDEX_OTHER_DATA].get("state", 0)

    def addAppearCount(self, userId=None):
        """添加分享鱼出现的次数"""
        if userId:
            shareClass = RandomChest(userId)                # 随机分享宝箱
            appearCount = shareClass.shareData[share_system.INDEX_OTHER_DATA].get("appearCount", 0) + 1
            shareClass.shareData[share_system.INDEX_OTHER_DATA]["appearCount"] = appearCount
            shareClass.shareData[share_system.INDEX_OTHER_DATA]["playTime"] = 0
            shareClass.saveData()

    def _getFishGroupId(self):
        """获取鱼群Id"""
        shareFishConf = config.getShareFishConf(self.table.runConfig.fishPool)      # 获取分享宝箱鱼配置
        randInt = random.randint(1, 10000)
        for fish in shareFishConf["fishes"]:
            probb = fish["probb"]
            if probb[0] <= randInt <= probb[1]:
                fishType = fish["fishType"]
                allShareGroupIds = self.table.runConfig.allShareGroupIds
                groupId = random.choice(allShareGroupIds[fishType])
                return groupId
        return None

    def _addShareFishGroup(self, groupId, userId=None):
        """添加分享宝箱鱼群"""
        if ftlog.is_debug():
            ftlog.debug("_addShareFishGroup", groupId, userId)
        self.table.insertFishGroup(groupId, userId=userId, sendUserId=userId)
        self.addAppearCount(userId)
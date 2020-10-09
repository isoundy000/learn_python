# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/4/12.
"""

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import gamedata
from hall.entity import hallvip
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.event import EnterTableEvent, LeaveTableEvent


class CouponFishGroup(object):
    """
    奖券鱼鱼群
    """
    def __init__(self, table):
        self.table = table
        self._lastUtilAppearTime = int(time.time())     # 上一次添加所有人可见红包奖券出现的事件
        self.checkTimer = FTLoopTimer(10, -1, self._checkCondition)     # 检查条件
        self.checkTimer.start()
        self._clearUserCouponFishData()                 # 清理用户奖券数据
        self._registerEvent()                           # 注册事件

    def clearTimer(self):
        """清理定时器"""
        if self.checkTimer:
            self.checkTimer.cancel()
            self.checkTimer = None
        for player in self.table.players:
            if player and player.userId:
                self._clearPlayerTimer(player.userId)   # 清理玩家定时器

    def _clearUserCouponFishData(self):
        """
        初始化个人可见奖券鱼相关数据
        """
        self._playerCouponTimerDict = {}                # 玩家奖券定时器
        for player in self.table.players:
            if player and player.userId:
                self._clearPlayerTimer(player.userId)

    def _clearPlayerTimer(self, userId):
        """
        清除与player相关的定时器和鱼阵
        """
        timer = self._playerCouponTimerDict.get(userId)
        if timer:
            timer.cancel()
            self._playerCouponTimerDict.pop(userId)

    def _checkCondition(self):
        """
        定时器条件检查
        """
        self._checkUtilConditionNew()

    def _checkUtilConditionNew(self):
        """
        检查定时的奖券鱼
        """
        couponFishConf = config.getCouponFishConf(self.table.runConfig.fishPool)
        if not couponFishConf:
            return
        interval = time.time() - self._lastUtilAppearTime
        couponRange = couponFishConf.get("couponRange")
        if interval >= couponFishConf["maxSecond"]:
            if ftlog.is_debug():
                ftlog.debug("_checkUtilConditionNew, interval =", interval, couponRange, self.table.tableId)
            randInt = random.randint(1, 10000)
            for fish in couponFishConf["fishes"]:
                probb = fish["probb"]
                if probb[0] <= randInt <= probb[1]:
                    fishType = fish["fishType"]
                    allCouponGroupIds = self.table.runConfig.allCouponGroupIds
                    groupId = random.choice(allCouponGroupIds[fishType])
                    self._addUtilCouponFishGroupNew(groupId, couponRange)
                    break

    def _addUtilCouponFishGroupNew(self, groupId, couponRange):
        """
        添加定时出生的奖券鱼
        """
        self._lastUtilAppearTime = time.time()
        if not couponRange:
            if ftlog.is_debug():
                ftlog.debug("_addUtilCouponFishGroupNew, groupId =", groupId, "tableId =", self.table.tableId)
            self.table.insertFishGroup(groupId)
            return
        sendUserList = []
        for player in self.table.players:
            if player and player.userId > 0:
                totalEntityAmount = gamedata.getGameAttr(player.userId, FISH_GAMEID, GameData.totalEntityAmount)
                totalEntityAmount = float(totalEntityAmount) if totalEntityAmount else 0
                if couponRange[0] <= totalEntityAmount < couponRange[1]:
                    sendUserList.append(player.userId)
        if ftlog.is_debug():
            ftlog.debug("_addUtilCouponFishGroupNew, groupId =", groupId, "couponRange =", couponRange,
                    "sendUserList =", sendUserList, "tableId =", self.table.tableId)
        if sendUserList:
            self.table.insertFishGroup(groupId, sendUserId=sendUserList)

    def _checkUserConditionNew(self, userId):
        """
        检查个人可见奖券鱼出现条件是否满足
        """
        userCouponFishConf = config.getUserCouponFishConf(self.table.runConfig.fishPool)
        groupId, interval, totalBullet = self._isAppearUserCouponFishNew(userId, userCouponFishConf)
        if groupId:
            timer = FTLoopTimer(interval, 0, self._addUserCouponFishGroupNew, groupId, userId, totalBullet)
            timer.start()
            self._playerCouponTimerDict[userId] = timer
            if ftlog.is_debug():
                ftlog.debug("_checkUserConditionNew->userId =", userId, "groupId =", groupId, "interval =", interval,
                        "totalBullet =", totalBullet, "tableId =", self.table.tableId)

    def _isAppearUserCouponFishNew(self, userId, userCouponFishConf):
        """
        个人奖券鱼是否出现
        """
        groupId = None
        interval = 0
        totalBullet = 0
        if not userCouponFishConf:
            return groupId, interval, totalBullet
        catchCountDict = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.catchUserCouponFishCount, {})
        catchCount = catchCountDict.get(str(self.table.runConfig.fishPool), 0)
        rechargeAmount = hallvip.userVipSystem.getUserVip(userId).vipExp // 10
        totalEntityAmount = gamedata.getGameAttr(userId, FISH_GAMEID, GameData.totalEntityAmount)
        totalEntityAmount = float(totalEntityAmount) if totalEntityAmount else 0
        for conf in userCouponFishConf:
            if catchCount >= conf["limitCount"]:
                continue
            section = conf["sections"]
            if ftlog.is_debug():
                ftlog.debug("_isAppearUserCouponFishNew->tabId=", self.table.tableId, "userId =", userId,
                        "groupId =", groupId, "section =", section)
            # 充值金额大于等于指定值，获得金额小于指定值
            if len(section) == 3 and rechargeAmount >= section[0] and section[1] <= totalEntityAmount < section[2]:
                randInt = random.randint(1, 10000)
                for fish in conf["fishes"]:
                    probb = fish["probb"]
                    if probb[0] <= randInt <= probb[1]:
                        fishType = fish["fishType"]
                        allCouponGroupIds = self.table.runConfig.allCouponGroupIds
                        groupId = random.choice(allCouponGroupIds[fishType])
                        interval = random.randint(conf["minSecond"], conf["maxSecond"])
                        totalBullet = conf["totalBullet"]
                break
        if ftlog.is_debug():
            ftlog.debug("_isAppearUserCouponFishNew->tabId=", self.table.tableId, "userId =", userId, "groupId =", groupId,
                    "catchCountDict =", catchCountDict, "rechargeAmount =", rechargeAmount,
                    "totalEntityAmount =", totalEntityAmount, "interval =", interval, "totalBullet =", totalBullet)
        return groupId, interval, totalBullet

    def _addUserCouponFishGroupNew(self, groupId, userId, totalBullet):
        """
        添加个人可见的奖券鱼
        """
        player = self.table.getPlayer(userId)
        self._clearPlayerTimer(userId)
        if player:
            playerBullet = player.couponConsumeClip
            if playerBullet < totalBullet:
                timer = FTLoopTimer(10, 0, self._addUserCouponFishGroupNew, groupId, userId, totalBullet)
                timer.start()
                self._playerCouponTimerDict[userId] = timer
                if ftlog.is_debug():
                    ftlog.debug("_addUserCouponFishGroupNew, check later, tableId =", self.table.tableId, "userId =", userId,
                            "playerBullet =", playerBullet, "totalBullet =", totalBullet)
            else:
                player.resetCouponConsumeClip()
                if ftlog.is_debug():
                    ftlog.debug("_addUserCouponFishGroupNew, tabId =", self.table.tableId, "userId =", userId, "groupId =", groupId)
                self.table.insertFishGroup(groupId, userId=userId, sendUserId=userId)
                self._checkUserConditionNew(userId)

    def _dealEnterTable(self, event):
        """
        处理进入事件
        """
        if event.tableId == self.table.tableId and not event.reconnect:
            self._checkUserConditionNew(event.userId)

    def _dealLeaveTable(self, event):
        """
        处理离开事件
        """
        if event.tableId == self.table.tableId:
            self._clearPlayerTimer(event.userId)

    def _registerEvent(self):
        """
        注册监听事件
        """
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EnterTableEvent, self._dealEnterTable)
        TGFish.getEventBus().subscribe(LeaveTableEvent, self._dealLeaveTable)
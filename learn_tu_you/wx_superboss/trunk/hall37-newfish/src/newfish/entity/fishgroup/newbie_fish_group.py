# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/5/17.
"""

import random
import time
from itertools import islice

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import gamedata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.task.task_base import TaskType
from newfish.entity.event import EnterTableEvent, LeaveTableEvent, TableTaskStartEvent


class NewbieFishGroup(object):
    """
    新手任务鱼群
    """
    def __init__(self, table):
        self.table = table
        self._generateNumOnce = 1               # 一次生成多少条
        self._normalFishGroupTimer = None       # 普通鱼群的定时器
        self._multipleGroupTimer = None         # 倍率定时器
        self._bombGroupTimer = None             # 炸弹鱼
        self._rainbowGroupTimer = None          # 彩虹鱼
        self._bossGroupTimer = None             # boss鱼
        self._playerCouponTimerDict = {}        # 奖券鱼
        self._playerBossTimerDict = {}          # boss鱼
        self._playerTerrorTimerDict = {}        # 特殊鱼
        self._playerTuitionTimerDict = {}       # 教学鱼
        self._playerSharkTimerDict = {}         # 大白鲨

        self._registerEvent()
        self._clear()
        self._nextNormalFishGroup()

    def _clear(self):
        self._taskId = 0                        # 当前任务Id
        self.table.clearFishGroup()             # 清除鱼阵
        self._allNormalGroupIds = self.table.runConfig.allGroupIds[:10]     # 该场次可使用的所有鱼阵
        self._allMultipleGroupIds = []
        self._allBombGroupIds = []
        self._allRainbowGroupIds = []
        self._appearedNormalGroupIds = []       # 出现普通的鱼群Id
        self._appearedMultipleGroupIds = []     # 出现倍率鱼的鱼群Id
        self._appearedBombGroupIds = []
        self._appearedRainbowGroupIds = []
        for player in self.table.players:
            if player and player.userId:
                self._clearPlayerTimer(player.userId)
        self._playerCouponTimerDict = {}
        self._playerBossTimerDict = {}
        self._playerTerrorTimerDict = {}
        self._playerTuitionTimerDict = {}
        self._playerSharkTimerDict = {}
        if self._multipleGroupTimer:
            self._multipleGroupTimer.cancel()
            self._multipleGroupTimer = None
        if self._bombGroupTimer:
            self._bombGroupTimer.cancel()
            self._bombGroupTimer = None
        if self._rainbowGroupTimer:
            self._rainbowGroupTimer.cancel()
            self._rainbowGroupTimer = None
        if self._bossGroupTimer:
            self._bossGroupTimer.cancel()
            self._bossGroupTimer = None

    def _clearPlayerTimer(self, userId):
        """清理玩家定时器"""
        data = self._playerCouponTimerDict.get(userId)
        if data:
            group, timer = data[0], data[1]
            self.table.deleteFishGroup(group)
            timer.cancel()
            self._playerCouponTimerDict.pop(userId)
        data = self._playerBossTimerDict.get(userId)
        if data:
            group, timer = data[0], data[1]
            self.table.deleteFishGroup(group)
            timer.cancel()
            self._playerBossTimerDict.pop(userId)
        data = self._playerTerrorTimerDict.get(userId)
        if data:
            group, timer = data[0], data[1]
            self.table.deleteFishGroup(group)
            timer.cancel()
            self._playerTerrorTimerDict.pop(userId)
        data = self._playerTuitionTimerDict.get(userId)
        if data:
            group, timer = data[0], data[1]
            self.table.deleteFishGroup(group)
            timer.cancel()
            self._playerTuitionTimerDict.pop(userId)
        data = self._playerSharkTimerDict.get(userId)
        if data:
            group, timer = data[0], data[1]
            self.table.deleteFishGroup(group)
            timer.cancel()
            self._playerSharkTimerDict.pop(userId)

    def _addNormalFishGroup(self):
        """
        add_group消息默认是下一个鱼阵开始前60s左右发送，每次调用add_group方法耗费时间一般为0.5s以内(包含对象创建和定时器延迟)
        长此以往会导致add_group消息在当前鱼阵结束后没有及时发送，需要修正时间
        """
        taskIds = []
        newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
        for player in self.table.players:
            if player and player.taskSystemUser:
                taskIds.append(str(player.taskSystemUser.getCurMainTaskId()))       # 获取当前主线任务Id
        taskIds.sort()
        if taskIds:
            taskId = taskIds[-1]
            if taskId in newbieFishGroupConf and int(taskId) > self._taskId:
                self._taskId = int(taskId)
                self._allNormalGroupIds = newbieFishGroupConf[str(taskId)].get("normalFishGroups", [])
                self._allMultipleGroupIds = newbieFishGroupConf[str(taskId)].get("multipleFishGroups", [])
                self._allBombGroupIds = newbieFishGroupConf[str(taskId)].get("bombFishGroups", [])
                self._allRainbowGroupIds = newbieFishGroupConf[str(taskId)].get("rainbowFishGroups", [])
        ftlog.debug("_addNormalFishGroup->", taskIds, self._taskId, self._allNormalGroupIds)
        randomGroupIds = list(set(self._allNormalGroupIds) - set(self._appearedNormalGroupIds))
        if not randomGroupIds:
            randomGroupIds = self._allNormalGroupIds
            self._appearedNormalGroupIds = []
        selectGroupIds = random.sample(randomGroupIds, self._generateNumOnce)
        self._appearedNormalGroupIds.extend(selectGroupIds)
        enterTime = self.table.getNextGroupEnterTime()
        correctValue = 0
        if enterTime > 0 > self.table.startTime + enterTime - time.time():
            correctValue = abs(self.table.startTime + enterTime - time.time())
        self.table.addNormalFishGroups(selectGroupIds)
        nextAddGroupInterval = round(self._getNextAddGroupInterval() - correctValue, 2)
        if nextAddGroupInterval < 1:
            nextAddGroupInterval = 1
        if self._normalFishGroupTimer:
            self._normalFishGroupTimer.cancel()
        self._normalFishGroupTimer = FTLoopTimer(nextAddGroupInterval, 0, self._nextNormalFishGroup)
        self._normalFishGroupTimer.start()
        self._nextMultipleFishGroup()
        self._nextBombFishGroup()
        self._nextRainbowFishGroup()
        ftlog.debug("_addNormalFishGroup->nextAddGroupInterval =", nextAddGroupInterval,
                    "nextGroupEnterTimeInterval =", self.table.startTime + enterTime - time.time(),
                    "tableId =", self.table.tableId,
                    "self.table.startTime =", self.table.startTime,
                    "enterTime =", enterTime,
                    "nowTime =", time.time(),
                    "correctValue =", correctValue)

    def _addMultipleFishGroup(self):
        """
        添加倍率鱼
        """
        randomGroupIds = list(set(self._allMultipleGroupIds) - set(self._appearedMultipleGroupIds))
        if not randomGroupIds:
            randomGroupIds = self._allMultipleGroupIds
            self._appearedMultipleGroupIds = []
        if not randomGroupIds:
            if self._multipleGroupTimer:
                self._multipleGroupTimer.cancel()
            return
        multipleFishGroupId = random.choice(randomGroupIds)
        self._appearedMultipleGroupIds.append(multipleFishGroupId)
        group = self.table.insertFishGroup(multipleFishGroupId)
        self._multipleGroupTimer = FTLoopTimer(group.totalTime, 0, self._addMultipleFishGroup)
        self._multipleGroupTimer.start()

    def _addBombFishGroup(self):
        """
        添加炸弹鱼
        """
        randomGroupIds = list(set(self._allBombGroupIds) - set(self._appearedBombGroupIds))
        if not randomGroupIds:
            randomGroupIds = self._allBombGroupIds
            self._appearedBombGroupIds = []
        if not randomGroupIds:
            if self._bombGroupTimer:
                self._bombGroupTimer.cancel()
            return
        bombFishGroupId = random.choice(randomGroupIds)
        self._appearedBombGroupIds.append(bombFishGroupId)
        group = self.table.insertFishGroup(bombFishGroupId)
        # self._bombGroupTimer = FTLoopTimer(group.totalTime, 0, self._addBombFishGroup)
        self._bombGroupTimer = FTLoopTimer(60, 0, self._addBombFishGroup)
        self._bombGroupTimer.start()

    def _addRainbowFishGroup(self):
        """
        添加彩虹鱼
        """
        randomGroupIds = list(set(self._allRainbowGroupIds) - set(self._appearedRainbowGroupIds))
        if not randomGroupIds:
            randomGroupIds = self._allRainbowGroupIds
            self._appearedRainbowGroupIds = []
        if not randomGroupIds:
            if self._rainbowGroupTimer:
                self._rainbowGroupTimer.cancel()
            return
        rainbowFishGroupId = random.choice(randomGroupIds)
        self._appearedRainbowGroupIds.append(rainbowFishGroupId)
        group = self.table.insertFishGroup(rainbowFishGroupId)
        self._rainbowGroupTimer = FTLoopTimer(group.totalTime, 0, self._addRainbowFishGroup)
        self._rainbowGroupTimer.start()

    def _addCouponFishGroup(self, userId):
        """
        添加红包券鱼
        """
        ftlog.debug("_addCouponFishGroup", userId, self.table.tableId)
        player = self.table.getPlayer(userId)
        catchCouponFishCount = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.catchCouponFishCount)
        if player and player.taskSystemUser and player.taskSystemUser.curTask:
            if catchCouponFishCount < 10 or player.taskSystemUser.curTask.taskConfig["type"] == TaskType.CatchRedPacketFishNum:
                taskId = player.taskSystemUser.getCurMainTaskId()
                newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
                couponFishGroups = newbieFishGroupConf.get(str(taskId), {}).get("couponFishGroups", [])
                data = self._playerCouponTimerDict.get(userId)
                if couponFishGroups and (not data or data[1].getTimeOut() <= 0):
                    group = self.table.insertFishGroup(random.choice(couponFishGroups), userId=userId, sendUserId=userId)
                    timer = FTLoopTimer(group.totalTime, 0, self._addCouponFishGroup, userId)
                    timer.start()
                    self._playerCouponTimerDict[userId] = [group, timer]

    def _addBossFishGroup(self, userId):
        """
        添加Boss鱼
        """
        ftlog.debug("_addBossFishGroup", userId, self.table.tableId)
        player = self.table.getPlayer(userId)
        if player and player.taskSystemUser:
            taskId = player.taskSystemUser.getCurMainTaskId()
            newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
            bossFishGroups = newbieFishGroupConf.get(str(taskId), {}).get("bossFishGroups", [])
            data = self._playerBossTimerDict.get(userId)
            if bossFishGroups and (not data or data[1].getTimeOut() <= 0):
                group = self.table.insertFishGroup(random.choice(bossFishGroups), userId=userId, sendUserId=userId)
                timer = FTLoopTimer(120, 0, self._addBossFishGroup, userId)
                timer.start()
                self._playerBossTimerDict[userId] = [group, timer]
                player.bossAppearCount += 1

    def _addTerrorFishGroup(self, userId):
        """
        添加Terror鱼
        """
        ftlog.debug("_addTerrorFishGroup", userId, self.table.tableId)
        player = self.table.getPlayer(userId)
        if player and player.taskSystemUser:
            taskId = player.taskSystemUser.getCurMainTaskId()
            newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
            terrorFishGroups = newbieFishGroupConf.get(str(taskId), {}).get("terrorFishGroups", [])
            data = self._playerTerrorTimerDict.get(userId)
            if terrorFishGroups and (not data or data[1].getTimeOut() <= 0):
                group = self.table.insertFishGroup(random.choice(terrorFishGroups), userId=userId, sendUserId=userId)
                timer = FTLoopTimer(120, 0, self._addTerrorFishGroup, userId)
                timer.start()
                self._playerTerrorTimerDict[userId] = [group, timer]
                #player.bossAppearCount += 1

    def _addTuitionFishGroup(self, userId):
        """
        添加教学鱼
        """
        player = self.table.getPlayer(userId)
        if player and player.taskSystemUser:
            taskId = player.taskSystemUser.getCurMainTaskId()
            ftlog.debug("_addTuitionFishGroup", userId, self.table.tableId, taskId)
            newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
            tuitionFishGroups = newbieFishGroupConf.get(str(taskId), {}).get("tuitionFishGroups", [])
            data = self._playerTuitionTimerDict.get(userId)
            if tuitionFishGroups and (not data or data[1].getTimeOut() <= 0):
                group = self.table.insertFishGroup(random.choice(tuitionFishGroups), userId=userId, sendUserId=userId)
                timer = FTLoopTimer(group.totalTime + 1, 0, self._addTuitionFishGroup, userId)
                timer.start()
                self._playerTuitionTimerDict[userId] = [group, timer]
                # player.bossAppearCount += 1

    def _addSharkFishGroup(self, userId):
        """
        添加大白鲨
        """
        player = self.table.getPlayer(userId)
        if player and player.taskSystemUser:
            taskId = player.taskSystemUser.getCurMainTaskId()
            ftlog.debug("_addSharkFishGroup", userId, self.table.tableId, taskId)
            newbieFishGroupConf = config.getPublic("newbieFishGroupConf", {})
            sharkFishGroups = newbieFishGroupConf.get(str(taskId), {}).get("sharkFishGroups", [])
            data = self._playerSharkTimerDict.get(userId)
            if sharkFishGroups and (not data or data[1].getTimeOut() <= 0):
                group = self.table.insertFishGroup(random.choice(sharkFishGroups), userId=userId, sendUserId=userId)
                timer = FTLoopTimer(group.totalTime + 1, 0, self._addSharkFishGroup, userId)
                timer.start()
                self._playerSharkTimerDict[userId] = [group, timer]
                # player.bossAppearCount += 1

    def _nextNormalFishGroup(self):
        """添加下一个鱼群"""
        self._addNormalFishGroup()

    def _nextMultipleFishGroup(self):
        """添加倍率鱼群"""
        if self._multipleGroupTimer:
            return
        self._addMultipleFishGroup()

    def _nextBombFishGroup(self):
        """添加炸弹鱼"""
        if self._bombGroupTimer:
            return
        self._addBombFishGroup()

    def _nextRainbowFishGroup(self):
        """添加彩虹鱼"""
        if self._rainbowGroupTimer:
            return
        self._addRainbowFishGroup()

    def _nextCouponFishGroups(self, userId):
        self._addCouponFishGroup(userId)

    def _nextBossFishGroups(self, userId):
        FTLoopTimer(10, 0, self._addBossFishGroup, userId).start()

    def _nextTerrorFishGroups(self, userId):
        FTLoopTimer(10, 0, self._addTerrorFishGroup, userId).start()

    def _nextTuitionFishGroups(self, userId):
        FTLoopTimer(1, 0, self._addTuitionFishGroup, userId).start()

    def _nextSharkFishGroups(self, userId):
        FTLoopTimer(1, 0, self._addSharkFishGroup, userId).start()

    def _getNextAddGroupInterval(self):
        """获取下一个添加鱼群的间隔"""
        interval = 0
        start = max(len(self.table.normalFishGroups) - self._generateNumOnce, 0)
        for group in islice(self.table.normalFishGroups.itervalues(), start, None):
            interval += group.maxEnterTime
        return interval

    def _dealEnterTable(self, event):
        """
        处理进入事件
        """
        if event.tableId == self.table.tableId and not event.reconnect:
            self._nextCouponFishGroups(event.userId)
            self._nextBossFishGroups(event.userId)
            self._nextTerrorFishGroups(event.userId)
            self._nextTuitionFishGroups(event.userId)
            self._nextSharkFishGroups(event.userId)

    def _dealLeaveTable(self, event):
        """
        处理离开事件
        """
        if event.tableId == self.table.tableId:
            self._clearPlayerTimer(event.userId)
            if self.table.playersNum == 0:
                self._clear()
                self._nextNormalFishGroup()

    def _dealTableTaskStart(self, event):
        """
        处理渔场任务开始事件
        """
        if event.tableId == self.table.tableId:
            if event.taskId == 10003:
                self._nextCouponFishGroups(event.userId)
                self._nextSharkFishGroups(event.userId)
            elif event.taskId == 10006:
                self._nextBossFishGroups(event.userId)
                self._nextSharkFishGroups(event.userId)
            elif event.taskId == 10004:
                self._nextCouponFishGroups(event.userId)
                self._nextTuitionFishGroups(event.userId)
                self._nextSharkFishGroups(event.userId)

    def _registerEvent(self):
        """
        注册监听事件
        """
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EnterTableEvent, self._dealEnterTable)
        TGFish.getEventBus().subscribe(LeaveTableEvent, self._dealLeaveTable)
        TGFish.getEventBus().subscribe(TableTaskStartEvent, self._dealTableTaskStart)
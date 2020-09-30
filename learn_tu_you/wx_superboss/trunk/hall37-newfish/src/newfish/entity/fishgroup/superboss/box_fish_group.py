# -*- coding=utf-8 -*-
"""
宝箱怪
"""
# @Author  : Kangxiaopeng
# @Time    : 2020/5/25


import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.cron import FTCron
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup


class BoxFishGroup(SuperBossFishGroup):
    """
    宝箱怪鱼阵
    """
    def __init__(self, table):
        super(BoxFishGroup, self).__init__(table)
        self._interval = 300            # 宝箱怪出生间隔. 600 5分钟
        self._bBossFishType = 71201     # 宝箱儿子
        self._mBossFishType = 71202     # 宝箱妈妈
        self._fBossFishType = 71203     # 宝箱爸爸
        self._startTS = 0               # 宝箱怪出现的时间戳.
        self._fBossAppearTS = 0         # 宝箱爸爸出现的最晚时间戳.
        self._isBossShowTimeStage = 0   # showtime是boss出现前30秒(stage=0x1000), bBoss(0x1), mBoss(0x10), fBoss(0x100). 暂停状态(-0x1)
        self._hasBorned = []            # 已经出生的宝箱boss
        self._initConfTimer = None      # 初始化配置定时器
        self._nextTimer = None          # 下次填充鱼的时间戳
        self._autofillTimer = {}        # 自动填充的时间
        self._clearTimer = None         # 清理宝箱的定时器.
        self._group = {}                # 渔群信息
        self._initConf()

    def _initConf(self):
        if self._initConfTimer:
            self._initConfTimer.cancel()
            self._initConfTimer = None
        self.boxConf = self.table.room.roomConf.get("boxConf")
        self._cron = FTCron(self.boxConf["cronTime"])
        self._interval = self._cron.getNextLater()
        if self._interval >= 0:
            self._setTimer()                # 启动定时器
            self._initConfTimer = FTLoopTimer(self._interval + 1, 0, self._initConf)
            self._initConfTimer.start()
        else:
            ftlog.error("BoxFishGroup initConf error", self._cron.getTimeList())

    def _addBossShowTimeStage(self, val):
        """添加boss展示的阶段"""
        self._isBossShowTimeStage |= val

    def _removeBossShowTimeStage(self, val):
        """移除boss展示阶段"""
        self._isBossShowTimeStage &= ~val
        if ftlog.is_debug():
            ftlog.debug("BoxFishGroup._removeBossShowTimeStage =", self.table.tableId, self._isBossShowTimeStage)

    def _clearData(self, isSendMsg=True, fishType=0, isEnd=0.0):
        """
        boss出生前清理相关数据
        """
        self._isBossShowTimeStage = 0
        self._hasBorned = []
        for _timer in self._autofillTimer.values():
            if _timer:
                _timer.cancel()
                _timer = None
        self._autofillTimer = {}
        if self._clearTimer:
            self._clearTimer.cancel()
            self._clearTimer = None
        # 清理鱼阵.
        for _group in self._group.values():
            if _group and self.table.fishGroupSystem:
                self.table.deleteFishGroup(_group)
        self._group = {}
        if isEnd:
            self.addTideFishGroup(isEnd)
        if isSendMsg:
            msg = MsgPack()
            msg.setCmd("superboss_end")
            msg.setResult("gameId", config.FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("type", "box")                            # 宝箱
            msg.setResult("fishType", fishType)                     # 鱼Id
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def isAppear(self):
        """
        boss即将出现或已经出现
        """
        if ftlog.is_debug():
            ftlog.debug("BoxFishGroup", self.table.tableId, self._isBossShowTimeStage)
        return self._isBossShowTimeStage & 0x1000 > 0 or self._isBossShowTimeStage & 0x111 > 0

    def _setTimer(self):
        """
        设置boss出现时的计时器
        """
        if self._nextTimer:
            self._nextTimer.cancel()
            self._nextTimer = None
        if self._interval >= 0:
            self._nextTimer = FTLoopTimer(self._interval, 0, self._addFishGroup)
            self._nextTimer.start()
            self.appear()
            FTLoopTimer(max(self._interval - self.boxConf["tipTime"], 0), 0, self._addBossShowTimeStage, 0x1000).start()        # 提示的时间

    def _addFishGroup(self):
        """
        添加boss鱼阵
        """
        self._clearData(False)
        # 渔场内人数不满足时不出生宝箱怪.
        if self.table.playersNum < self.table.room.roomConf["superBossMinSeatN"]:
            return
        self._startTS = int(time.time())                            # 宝箱怪出现的时间
        self._fBossAppearTS = self._startTS + 90                    # 宝箱爸爸出现的时间
        for fishType in [self._bBossFishType, self._mBossFishType]:
            self._addBoss(fishType)                                 # 宝箱儿子 宝箱妈妈
        # 超出boss存活时间后清理boss.
        if self.boxConf["maxAliveTime"] > 0:                                  # 最大的存活时长
            self._clearTimer = FTLoopTimer(self.boxConf["maxAliveTime"] + 2, 0, self._clearData, True, 0, 0.1)
            self._clearTimer.start()

    def _addBoss(self, fishType, isSysTimerCall=True):
        """
        添加宝箱boss
        """
        if self._isBossShowTimeStage == -0x1:
            self._isBossShowTimeStage = 0
        if self._autofillTimer.get(fishType):
            self._autofillTimer[fishType].cancel()
            self._autofillTimer[fishType] = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group.get(fishType) and not isSysTimerCall and self._group[fishType].extendGroupTime > 0:
                self._autofillTimer[fishType] = FTLoopTimer(self._group[fishType].extendGroupTime, 0, self._addBoss, fishType, False)
                self._autofillTimer[fishType].start()
                self._group[fishType].extendGroupTime = 0
                return
        # boss超出最大存在时间后不再出现.
        if int(time.time()) >= self._startTS + self.boxConf["maxAliveTime"]:
            if fishType == self._bBossFishType:
                self._removeBossShowTimeStage(0x1)
            elif fishType == self._mBossFishType:
                self._removeBossShowTimeStage(0x10)
            else:
                self._removeBossShowTimeStage(0x100)
            return
        self._group[fishType] = None
        # 使用出生路径.
        if fishType not in self._hasBorned:
            self._hasBorned.append(fishType)
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
        elif self._isBossShowTimeStage & 0x11 != 0x11:                      # bBoss或mBoss只有一个存在,则使用加速鱼阵.
            _bossGroupIds = self.table.runConfig.allSuperBossFastMoveGroupIds.get(fishType)
            if not _bossGroupIds:
                _bossGroupIds = self.table.runConfig.allSuperBossGroupIds[fishType]
        else:
            _bossGroupIds = self.table.runConfig.allSuperBossGroupIds[fishType]
        if _bossGroupIds:
            _bossGroupId = random.choice(_bossGroupIds)
            self._group[fishType] = self.table.insertFishGroup(_bossGroupId)
            if self._group[fishType]:
                self._autofillTimer[fishType] = FTLoopTimer(self._group[fishType].totalTime + 1, 0, self._addBoss, fishType, False)
                self._autofillTimer[fishType].start()
                if fishType == self._bBossFishType:
                    self._addBossShowTimeStage(0x1)
                elif fishType == self._mBossFishType:
                    self._addBossShowTimeStage(0x10)
                else:
                    self._addBossShowTimeStage(0x100)
                return self._group[fishType]
        ftlog.error("superboss_fish_group.BoxFishGroup, error, tableId =", self.table.tableId, fishType, self._hasBorned)
        return

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        _fishType = 0
        isBoxBossCatched = False
        if self._bBossFishType in event.fishTypes and self._group.get(self._bBossFishType):
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "ft =", self._bBossFishType, self._isBossShowTimeStage)
            isBoxBossCatched = True
            _fishType = self._bBossFishType
            self._group[self._bBossFishType] = None
            self._removeBossShowTimeStage(0x1)

        if self._mBossFishType in event.fishTypes and self._group.get(self._mBossFishType):
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "ft =", self._mBossFishType, self._isBossShowTimeStage)
            isBoxBossCatched = True
            _fishType = self._mBossFishType
            self._group[self._mBossFishType] = None
            self._removeBossShowTimeStage(0x10)

        if isBoxBossCatched:
            if self._autofillTimer.get(_fishType):
                self._autofillTimer[_fishType].cancel()
                self._autofillTimer[_fishType] = None

        if isBoxBossCatched and self._isBossShowTimeStage == 0:         # 捕获宝箱宝宝和宝箱妈妈后，如果时间充裕就出生宝箱爸爸.
            if int(time.time()) < self._fBossAppearTS:
                self._isBossShowTimeStage = -0x1
                FTLoopTimer(self.boxConf["fDelayTime"], 0, self._addBoss, self._fBossFishType).start()  # 宝箱爸爸
            else:                                                       # 时间不够则结束boss状态.
                self._clearData(isSendMsg=True, fishType=_fishType, isEnd=0.1)

        if self._fBossFishType in event.fishTypes:
            if not self._group.get(self._fBossFishType):                # 宝箱爸爸被捕获时可能刚好超时,所以此时就不要再爆炸了.
                return
            stageCount = 0
            for catchMap in event.catch:
                fishInfo = self.table.fishMap[catchMap["fId"]]
                fishType = fishInfo["fishType"]
                if catchMap["reason"] == 0 and fishType == self._fBossFishType:
                    stageCount = catchMap.get("stageCount")
                    break
            self._group[self._fBossFishType] = None
            self._removeBossShowTimeStage(0x100)
            if self._autofillTimer.get(self._fBossFishType):
                self._autofillTimer[self._fBossFishType].cancel()
                self._autofillTimer[self._fBossFishType] = None
            if self._clearTimer:
                self._clearTimer.cancel()
                self._clearTimer = None
            if stageCount > 1:
                msg = MsgPack()
                msg.setCmd("superboss_explosion_info")                  # 爆炸信息
                msg.setResult("gameId", config.FISH_GAMEID)
                msg.setResult("roomId", self.table.roomId)
                msg.setResult("tableId", self.table.tableId)
                explosionPos = range(1, 5)                              # 选择狂暴落点索引. [1,2,3,4]
                random.shuffle(explosionPos)
                explosionPos.insert(0, 0)
                explosionPos.extend(random.sample(explosionPos[:-1], 1))
                msg.setResult("explosionPos", explosionPos[:stageCount])
                GameMsg.sendMsg(msg, self.table.getBroadcastUids())
                FTLoopTimer(stageCount * self.boxConf["stageTime"] + self.boxConf["endDelayTime"], 0, self._clearData, True, self._fBossFishType, self.boxConf["tideDelayTime"]).start()

    def addTideFishGroup(self, delayTime=0.1):
        """添加鱼潮"""
        if delayTime > 0:
            FTLoopTimer(delayTime, 0, self.leave).start()        # 鱼潮延迟出来的时间

    def dealEnterTable(self, userId):
        """
        玩家进入渔场时发送
        """
        # 当前阶段boss开始出现的时间戳.
        startTS = 0
        if self._isBossShowTimeStage & 0x111 != 0:
            startTS = self._startTS
        msg = MsgPack()
        msg.setCmd("box_info")
        msg.setResult("gameId", config.FISH_GAMEID)
        msg.setResult("roomId", self.table.roomId)
        msg.setResult("tableId", self.table.tableId)
        msg.setResult("startTS", startTS)
        GameMsg.sendMsg(msg, userId)
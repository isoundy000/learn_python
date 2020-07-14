#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/12
"""
宝箱怪
"""

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity.fishgroup.superboss_fish_group import SuperBossFishGroup


class BoxFishGroup(SuperBossFishGroup):
    """
    宝箱怪鱼阵
    """
    def __init__(self, table):
        super(BoxFishGroup, self).__init__()
        self.table = table
        self._interval = 300            # 宝箱怪出生间隔. 600 5分钟
        self._maxAliveTime = 150        # 宝箱怪的存在时间.
        self._bBossFishType = 71201     # 宝箱儿子
        self._mBossFishType = 71202     # 宝箱妈妈
        self._fBossFishType = 71203     # 宝箱爸爸
        self._startTS = 0               # 宝箱怪出现的时间戳.
        self._fBossAppearTS = 0         # 宝箱爸爸出现的最晚时间戳.
        self._nextTimer = None          # 下次填充鱼的时间戳
        self._isBossShowTimeStage = 0   # showtime是boss出现前30秒(stage=0x1000), bBoss(0x1), mBoss(0x10), fBoss(0x100).
        self._hasBorned = []
        self._autofillTimer = {}        # 自动填充的时间
        self._clearTimer = None         # 清理宝箱的定时器.
        self._group = {}                # 渔群信息
        self._setTimer()

    def addTestSuperBoss(self):
        """添加测试boss"""
        self._addFishGroup()

    def _addBossShowTimeStage(self, val):
        """添加boss展示的阶段"""
        self._isBossShowTimeStage |= val
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId,
                        hex(self._isBossShowTimeStage), hex(val))

    def _removeBossShowTimeStage(self, val):
        """移除boss展示阶段"""
        self._isBossShowTimeStage &= ~val
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId,
                        hex(self._isBossShowTimeStage), hex(val))

    def _clearData(self, isSendMsg=True, fishType=0):
        """
        boss出生前清理相关数据
        """
        self._stageCount = 0
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
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId,
                        ", isSendMsg =", isSendMsg, "fishType =", fishType)
        if isSendMsg:
            msg = MsgPack()
            msg.setCmd("superboss_end")
            msg.setResult("gameId", config.FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("type", "box")                    # 宝箱
            msg.setResult("fishType", fishType)             # 鱼Id
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def isAppear(self):
        """
        boss即将出现或已经出现
        """
        return self._isBossShowTimeStage & 0x1000 > 0 or self._isBossShowTimeStage & 0x111 > 0

    def _setTimer(self):
        """
        设置boss出现时的计时器
        """
        if self._nextTimer:
            self._nextTimer.cancel()
            self._nextTimer = None
        if self._interval > 0:
            self._nextTimer = FTLoopTimer(self._interval, -1, self._addFishGroup)
            self._nextTimer.start()
        if self._interval - 30 > 0:         # 往前推30s中
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x1000).start()

    def _addBoss(self, fishType, isSysTimerCall=True):
        """
        添加宝箱boss
        """
        if self._autofillTimer.get(fishType):
            self._autofillTimer[fishType].cancel()
            self._autofillTimer[fishType] = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group.get(fishType) and not isSysTimerCall and self._group[fishType].extendGroupTime > 0:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, delay !", self.table.tableId, fishType,
                                self._group[fishType].extendGroupTime)
                self._autofillTimer[fishType] = FTLoopTimer(self._group[fishType].extendGroupTime, 0, self._addBoss, fishType, False)
                self._autofillTimer[fishType].start()
                self._group[fishType].extendGroupTime = 0
                return
        # boss超出最大存在时间后不再出现.
        if int(time.time()) >= self._startTS + self._maxAliveTime:
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
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
        if _bossGroupIds:
            _bossGroupId = random.choice(_bossGroupIds)
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId,
                            "groupId =", _bossGroupId, "ft =", fishType, hex(self._isBossShowTimeStage), isSysTimerCall)
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
        ftlog.error("superboss_fish_group.BoxFishGroup, error, tableId =", self.table.tableId)
        return None

    def _addFishGroup(self):
        """
        添加boss鱼阵
        """
        self._clearData(False)
        self._isBossShowTimeStage = 0
        if self._interval - 30 > 0:
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x1000).start()
        # 渔场内人数不满足时不出生宝箱怪.
        if self.table.playersNum < self.table.room.roomConf["superBossMinSeatN"]:
            return
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId)

        self._startTS = int(time.time())
        self._fBossAppearTS = self._startTS + 90
        for _ft in [self._bBossFishType, self._mBossFishType]:      # 宝箱爸爸、宝箱妈妈
            self._addBoss(_ft)
        # 超出boss存活时间后清理boss.
        if self._maxAliveTime > 0:
            self._clearTimer = FTLoopTimer(self._maxAliveTime + 2, 0, self._clearData)
            self._clearTimer.start()

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        _fishType = 0
        isBoxBossCatched = False
        if self._bBossFishType in event.fishTypes:
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "ft =", self._bBossFishType)
            if self._group.get(self._bBossFishType):
                isBoxBossCatched = True
                _fishType = self._bBossFishType
                self._group[self._bBossFishType] = None
                self._removeBossShowTimeStage(0x1)
                if self._autofillTimer.get(self._bBossFishType):
                    self._autofillTimer[self._bBossFishType].cancel()
                    self._autofillTimer[self._bBossFishType] = None
            else:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, over time, tableId =", self.table.tableId, "ft =",
                                self._bBossFishType)

        if self._mBossFishType in event.fishTypes:
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "ft =", self._mBossFishType)
            if self._group.get(self._mBossFishType):
                isBoxBossCatched = True
                _fishType = self._mBossFishType
                self._group[self._mBossFishType] = None
                self._removeBossShowTimeStage(0x10)
                if self._autofillTimer.get(self._mBossFishType):
                    self._autofillTimer[self._mBossFishType].cancel()
                    self._autofillTimer[self._mBossFishType] = None
            else:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, over time, tableId =", self.table.tableId, "ft =",
                                self._bBossFishType)
        if self._fBossFishType in event.fishTypes:
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "ft =", self._fBossFishType)
            if not self._group.get(self._fBossFishType):                # 宝箱爸爸被捕获时可能刚好超时,所以此时就不要再爆炸了.
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, over time, tableId =", self.table.tableId, "ft =",
                                self._fBossFishType)
                return
            self._group[self._fBossFishType] = None
            self._removeBossShowTimeStage(0x100)
            if self._autofillTimer.get(self._fBossFishType):
                self._autofillTimer[self._fBossFishType].cancel()
                self._autofillTimer[self._fBossFishType] = None
            if self._clearTimer:
                self._clearTimer.cancel()
                self._clearTimer = None
            powerConf = config.getSuperbossPowerConf()
            countPctList = powerConf.get("power", {}).get(str(self._fBossFishType), {}).get("countPct", [])
            if countPctList and len(countPctList) >= self._stageCount > 1:
                msg = MsgPack()
                msg.setCmd("superboss_explosion_info")          # 爆炸信息
                msg.setResult("gameId", config.FISH_GAMEID)
                msg.setResult("roomId", self.table.roomId)
                msg.setResult("tableId", self.table.tableId)
                explosionPos = range(1, len(countPctList))      # 选择狂暴落点. [1,2,3,4]
                random.shuffle(explosionPos)
                explosionPos.insert(0, 0)
                tmp = range(len(countPctList))                  # [0,1,2,3,4]
                tmp.remove(explosionPos[-1])
                random.shuffle(tmp)
                explosionPos.append(tmp[0])
                msg.setResult("explosionPos", explosionPos[:self._stageCount])
                GameMsg.sendMsg(msg, self.table.getBroadcastUids())
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId, "msg =", msg, self._stageCount)

        if isBoxBossCatched:
            if self._isBossShowTimeStage == 0:                  # 捕获宝箱宝宝和宝箱妈妈后，如果时间充裕就出生宝箱爸爸.
                if int(time.time()) < self._fBossAppearTS:
                    self._addBoss(self._fBossFishType)
                else:                                           # 时间不够则结束boss状态.
                    self._clearData(fishType=_fishType)
            else:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.BoxFishGroup, tableId =", self.table.tableId,
                                max(self._fBossAppearTS - int(time.time()), 0), hex(self._isBossShowTimeStage))

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
# -*- coding=utf-8 -*-
"""
龙女王鱼阵
"""
# @Author  : Kangxiaopeng
# @Time    : 2020/5/25

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup


class QueenFishGroup(SuperBossFishGroup):
    """
    龙女王鱼阵
    """
    def __init__(self, table):
        super(QueenFishGroup, self).__init__()
        self.table = table
        # boss出生间隔.
        self._interval = 90             # 600
        # boss的存在时间.
        self._maxAliveTime = 150        # 总时长
        # 龙女王
        self._fishType = 74207
        # 女王保护罩.
        self._maskFishType = 74215
        # boss出现的时间戳.
        self._startTS = 0
        self._nextTimer = None
        # showtime是boss出现前30秒(stage=0x1000), 有保护罩(0x1), 没有保护罩(0x10).
        self._isBossShowTimeStage = 0
        self._autofillTimer = None
        # 清理鱼阵的定时器.
        self._clearTimer = None
        self._group = None
        self._setTimer()

    def addTestSuperBoss(self):
        self._addFishGroup()

    def _addBossShowTimeStage(self, val):
        """展示boss的状态"""
        self._isBossShowTimeStage |= val
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId, hex(self._isBossShowTimeStage), hex(val))

    def _removeBossShowTimeStage(self, val):
        """删除boss状态"""
        self._isBossShowTimeStage &= ~val
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId, hex(self._isBossShowTimeStage), hex(val))

    def _clearData(self, isSendMsg=True, fishType=0):
        """
        boss出生前清理相关数据
        """
        self._stageCount = 0
        if self._autofillTimer:
            self._autofillTimer.cancel()
        self._autofillTimer = None
        if self._clearTimer:
            self._clearTimer.cancel()
        self._clearTimer = None
        # 清理鱼阵.
        if self._group and self.table.fishGroupSystem:
            self.table.deleteFishGroup(self._group)
        self._group = None
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId, ", isSendMsg =", isSendMsg, "fishType =", fishType)
        if isSendMsg:
            msg = MsgPack()
            msg.setCmd("superboss_end")
            msg.setResult("gameId", config.FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("type", "queen")
            msg.setResult("fishType", fishType)
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def isAppear(self):
        """
        boss即将出现或已经出现
        """
        return self._isBossShowTimeStage & 0x1000 > 0 or self._isBossShowTimeStage & 0x11 > 0

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
        if self._interval - 30 > 0:
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x1000).start()

    def _addBoss(self, fishType, isSysTimerCall=True):
        """
        添加宝箱boss
        """
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group and not isSysTimerCall and self._group.extendGroupTime > 0:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.QueenFishGroup, delay !", self.table.tableId, fishType,
                                self._group.extendGroupTime)
                self._autofillTimer = FTLoopTimer(self._group.extendGroupTime, 0, self._addBoss, fishType, False)
                self._autofillTimer.start()
                self._group.extendGroupTime = 0
                return
        # boss超出最大存在时间后不再出现.
        if int(time.time()) >= self._startTS + self._maxAliveTime:
            self._removeBossShowTimeStage(0x1)
            return
        self._group = None
        # if self._isBossShowTimeStage & 0x1:# 有保护罩.
        _bossGroupIds = self.table.runConfig.allSuperBossGroupIds[fishType]
        # else:# 无保护罩.
        #     _bossGroupIds = self.table.runConfig.allSuperBossFastMoveGroupIds[fishType]
        if _bossGroupIds:
            _bossGroupId = random.choice(_bossGroupIds)
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId,
                            "groupId =", _bossGroupId, "ft =", fishType, hex(self._isBossShowTimeStage), isSysTimerCall)
            self._group = self.table.insertFishGroup(_bossGroupId)
            if self._group:
                self._autofillTimer = FTLoopTimer(self._group.totalTime + 1, 0, self._addBoss, fishType, False)
                self._autofillTimer.start()
                if self._isBossShowTimeStage == 0:
                    self._addBossShowTimeStage(0x1)
                return self._group
        ftlog.error("superboss_fish_group.QueenFishGroup, error, tableId =", self.table.tableId)
        return None

    def _addFishGroup(self):
        """
        添加boss鱼阵
        """
        self._clearData(False)
        self._isBossShowTimeStage = 0
        if self._interval - 7 > 0:
            FTLoopTimer(self._interval - 7, 0, self._addBossShowTimeStage, 0x1000).start()
        # 渔场内人数不满足时不出生boss.
        # if self.table.playersNum < self.table.room.roomConf["superBossMinSeatN"]:
        #     return
        if ftlog.is_debug():
            ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId)
        self._startTS = int(time.time())
        self._addBoss(self._fishType)
        # 超出boss存活时间后清理boss.
        if self._maxAliveTime > 0:
            self._clearTimer = FTLoopTimer(self._maxAliveTime + 2, 0, self._clearData, True, self._fishType)
            self._clearTimer.start()

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        _fishType = 0
        if self._maskFishType in event.fishTypes:           # 女王保护罩
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.ChestFishGroup, tableId =", self.table.tableId, "ft =", self._maskFishType)
            if self._group:
                self._removeBossShowTimeStage(0x1)
                self._addBossShowTimeStage(0x10)
            else:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.QueenFishGroup, over time, tableId =", self.table.tableId, "ft =", self._maskFishType)

        if self._fishType in event.fishTypes:               # 龙女王
            if ftlog.is_debug():
                ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId, "ft =", self._fishType)
            # boss被捕获时可能刚好超时,所以此时就不要再爆炸了.
            if not self._group:
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.QueenFishGroup, over time, tableId =", self.table.tableId, "ft =", self._maskFishType)
                return
            self._clearData(False, self._fishType)

            powerConf = config.getSuperbossPowerConf()      # 获取超级boss威力配置
            countPctList = powerConf.get("power", {}).get(str(self._fishType), {}).get("countPct", [])
            if countPctList and len(countPctList) >= self._stageCount > 1:
                msg = MsgPack()
                msg.setCmd("superboss_explosion_info")
                msg.setResult("gameId", config.FISH_GAMEID)
                msg.setResult("roomId", self.table.roomId)
                msg.setResult("tableId", self.table.tableId)
                # 选择狂暴落点.
                explosionPos = range(1, len(countPctList))  # [1,2,3,4]
                random.shuffle(explosionPos)
                explosionPos.insert(0, 0)
                tmp = range(len(countPctList))              # [0,1,2,3,4]
                tmp.remove(explosionPos[-1])
                random.shuffle(tmp)
                explosionPos.append(tmp[0])
                msg.setResult("explosionPos", explosionPos[:self._stageCount])
                GameMsg.sendMsg(msg, self.table.getBroadcastUids())
                if ftlog.is_debug():
                    ftlog.debug("superboss_fish_group.QueenFishGroup, tableId =", self.table.tableId, "msg =", msg, self._stageCount)

    def dealEnterTable(self, userId):
        """
        玩家进入渔场时发送
        """
        # 当前阶段boss开始出现的时间戳.
        startTS = 0
        if self._isBossShowTimeStage & 0x011 != 0:
            startTS = self._startTS
        msg = MsgPack()
        msg.setCmd("queen_info")
        msg.setResult("gameId", config.FISH_GAMEID)
        msg.setResult("roomId", self.table.roomId)
        msg.setResult("tableId", self.table.tableId)
        msg.setResult("startTS", startTS)
        GameMsg.sendMsg(msg, userId)
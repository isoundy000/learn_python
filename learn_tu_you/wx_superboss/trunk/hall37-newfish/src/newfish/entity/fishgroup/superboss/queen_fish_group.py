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
from newfish.entity.cron import FTCron
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup


class QueenFishGroup(SuperBossFishGroup):
    """
    龙女王鱼阵
    """
    def __init__(self, table):
        super(QueenFishGroup, self).__init__(table)
        self._interval = 300            # boss出生间隔
        self._maskFishType = 74215      # 女王保护罩
        self._fishType = 74207          # 龙女王
        self._idx = 0                   # 阶段boss的索引          3、4、5、1、2
        self._startTS = 0               # boss出现的时间戳
        self._nextTimer = None          # 下一个boss出生的定时器
        self._isBossShowTimeStage = 0   # showtime是boss出现前30秒 有保护罩(stage=0x1000) 第一阶段(0x1), 受伤阶段(0x10), 没有保护罩(0x100)
        self._initConfTimer = None      # 初始化配置定时器
        self._autofillTimer = None      # boss被捕获后是否自动填充
        self._clearTimer = None         # 清理鱼阵的定时器.
        self._modQuitTimer = None       # 120s内没有打掉保护罩、龙女王退场
        self._group = None              # 鱼群对象
        self._initConf()

    def _initConf(self):
        if self._initConfTimer:
            self._initConfTimer.cancel()
            self._initConfTimer = None
        self.queenConf = self.table.room.roomConf.get("queenConf")
        self._cron = FTCron(self.queenConf["cronTime"])
        self._interval = self._cron.getNextLater()
        if self._interval > 0:
            self._setTimer()                # 启动定时器
            self._initConfTimer = FTLoopTimer(self._interval + 1, 0, self._initConf)
            self._initConfTimer.start()
        else:
            ftlog.error("QueenFishGroup initConf error", self._cron.getTimeList())

    def _addBossShowTimeStage(self, val):
        """展示boss的状态"""
        self._isBossShowTimeStage |= val

    def _removeBossShowTimeStage(self, val):
        """删除boss状态"""
        self._isBossShowTimeStage &= ~val

    def _clearData(self, isSendMsg=True, fishType=0, isEnd=0.0):
        """
        boss出生前清理相关数据
        """
        self._isBossShowTimeStage = 0
        if self._autofillTimer:
            self._autofillTimer.cancel()
        self._autofillTimer = None
        if self._clearTimer:
            self._clearTimer.cancel()
        self._clearTimer = None
        if self._modQuitTimer:
            self._modQuitTimer.cancel()
        self._modQuitTimer = None
        # 清理鱼阵.
        if self._group and self.table.fishGroupSystem:
            self.table.deleteFishGroup(self._group)
        self._group = None
        if isEnd:
            self.addTideFishGroup(isEnd)
        if isSendMsg:
            msg = MsgPack()
            msg.setCmd("queen_end")
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
        return self._isBossShowTimeStage & 0x1000 > 0 or self._isBossShowTimeStage & 0x111 > 0

    def _setTimer(self):
        """
        设置boss出现时的计时器
        """
        if self._nextTimer:
            self._nextTimer.cancel()
        self._nextTimer = None
        if self._interval >= 0:
            self._nextTimer = FTLoopTimer(self._interval, 0, self._addFishGroup)               # 添加初始化鱼群
            self._nextTimer.start()
            self.appear()
            FTLoopTimer(max(self._interval - self.queenConf["tipTime"], 0), 0, self._addBossShowTimeStage, 0x1000).start()  # boss即将出现 1次

    def _addFishGroup(self):
        """
        添加boss鱼阵
        """
        self._clearData(False)                                                                  # 清理数据
        self._startTS = int(time.time())                                                        # boss出现的时间戳
        self._addBoss()                                                                         # 添加boss
        if self.queenConf["addHurtTime"] > 0:
            self._modQuitTimer = FTLoopTimer(self.queenConf["addHurtTime"], 0, self._clearData, True, self._maskFishType, 0.1)  # 2分钟后没有打掉保护罩，自动退场
            self._modQuitTimer.start()
        # 超出boss存活时间后清理boss.
        if self.queenConf["maxAliveTime"] > 0:
            self._clearTimer = FTLoopTimer(self.queenConf["maxAliveTime"], 0, self._clearData, True, self._fishType, 0.1)
            self._clearTimer.start()

    def _addBoss(self, isSysTimerCall=True, nextStage=0x1000):
        """
        添加宝箱boss
        """
        if nextStage != self._isBossShowTimeStage:
            self._removeBossShowTimeStage(self._isBossShowTimeStage)
            self._addBossShowTimeStage(nextStage)
        stage = 0x1000
        if self._isBossShowTimeStage == 0x1000:                                                 # 出生鱼阵  有保护罩.
            fishType = self._maskFishType
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
            stage = 0x1
        elif self._isBossShowTimeStage == 0x1:                                                  # 第一阶段  有保护罩.
            fishType = self._maskFishType
            _bossGroupIds = self.random_boss_groupid(fishType)
            if not isSysTimerCall:
                stage = 0x1
            else:
                stage = 0x10
        elif self._isBossShowTimeStage == 0x10:                                                 # 受伤鱼阵  无保护罩.
            fishType = self._fishType
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
            stage = 0x100
        elif self._isBossShowTimeStage == 0x100:                                                # 第二阶段  无保护罩.
            fishType = self._fishType
            _bossGroupIds = self.random_boss_groupid(fishType)
            stage = 0x100
        else:
            return
        # nowTime = int(time.time())
        # boss超出最大存在时间后不再出现.
        # if nowTime >= self._startTS + self.queenConf["maxAliveTime"]:
        #     self._removeBossShowTimeStage(self._isBossShowTimeStage)
        #     return
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group and not isSysTimerCall and self._group.extendGroupTime > 0:          # 该鱼群冰冻延长的时间
                self._autofillTimer = FTLoopTimer(self._group.extendGroupTime, 0, self._addBoss, False, stage)
                self._autofillTimer.start()
                self._group.extendGroupTime = 0
                return
        _bossGroupId = random.choice(_bossGroupIds)
        if not _bossGroupId:
            return
        self._group = self.table.insertFishGroup(_bossGroupId)
        if self._group:
            # 龙女王的离场时间
            interval = self._group.getFishExitTime(fishType)
            self._autofillTimer = FTLoopTimer(interval, 0, self._addBoss, False, stage)  # 自动填充下一阶段的鱼阵
            self._autofillTimer.start()
            if ftlog.is_debug():
                ftlog.debug("QueenFishGroup _addBoss", self.table.tableId, _bossGroupId, stage, interval)
        else:
            ftlog.error("QueenFishGroup _addBoss error", _bossGroupId)

    def random_boss_groupid(self, fishType):
        """
        第一阶段和第二阶段随机一类鱼群  在再该类鱼群中随机一个鱼群
        统计一类鱼1、2、3、4、5
        出现顺序为3、4、5、1、2
                4、5、1、2、3
        """
        groupMap = {}
        _bossGroupIds = self.table.runConfig.allSuperBossGroupIds[fishType]
        for group_name in _bossGroupIds:
            group = int(group_name.rsplit("_")[-2])
            if group not in groupMap:
                groupMap[group] = [group_name]
            else:
                groupMap[group].append(group_name)
        if not self._idx:
            num = random.randint(1, len(groupMap.keys()))
            self._idx = num
        else:
            if self._idx + 1 in groupMap.keys():
                self._idx += 1
            else:
                self._idx = min(groupMap.keys())
        _bossGroupIds = groupMap[self._idx]
        return _bossGroupIds

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        if self._maskFishType in event.fishTypes and self._isBossShowTimeStage in [0x1000, 0x1] and self._group:
            if self._autofillTimer:                                                            # 女王保护罩 出生鱼阵 第一鱼阵
                self._autofillTimer.cancel()
            self._autofillTimer = None
            if self._modQuitTimer:
                self._modQuitTimer.cancel()
            self._modQuitTimer = None
            self._addBoss(False, 0x10)
            return

        # boss被捕获时可能刚好超时, 所以此时就不要再爆炸了.
        if self._fishType in event.fishTypes and self._isBossShowTimeStage in [0x10, 0x100] and self._group:    # 龙女王不带保护罩 第二阶段
            if self._autofillTimer:                                                            # 女王保护罩 出生鱼阵 第一鱼阵
                self._autofillTimer.cancel()
            self._autofillTimer = None
            if self._clearTimer:
                self._clearTimer.cancel()
            self._clearTimer = None
            stageCount = 0
            for catchMap in event.catch:
                fishInfo = self.table.fishMap[catchMap["fId"]]
                fishType = fishInfo["fishType"]
                if catchMap["reason"] == 0 and fishType == self._fishType:
                    stageCount = catchMap.get("stageCount")
                    break
            FTLoopTimer(stageCount * self.queenConf["stageTime"] + self.queenConf["endDelayTime"], 0, self._clearData, True, self._fishType, self.queenConf["tideDelayTime"]).start()

    def addTideFishGroup(self, delayTime=0.1):
        """
        添加鱼潮
        """
        if delayTime > 0:
            FTLoopTimer(delayTime, 0, self.leave).start()

    def dealEnterTable(self, userId):
        """
        玩家进入渔场时发送
        """
        # 当前阶段boss开始出现的时间戳.
        startTS = 0
        if self._isBossShowTimeStage & 0x111 != 0:
            startTS = self._startTS
        msg = MsgPack()
        msg.setCmd("queen_info")
        msg.setResult("gameId", config.FISH_GAMEID)
        msg.setResult("roomId", self.table.roomId)
        msg.setResult("tableId", self.table.tableId)
        msg.setResult("startTS", startTS)
        GameMsg.sendMsg(msg, userId)

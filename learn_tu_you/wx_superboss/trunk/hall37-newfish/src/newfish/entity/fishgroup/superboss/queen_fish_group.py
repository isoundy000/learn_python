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
        self._interval = 300            # boss出生间隔.
        self._maxAliveTime = 150        # boss的存在时间. 总时长
        self._addHurtTime = 120         # 添加受伤鱼群            2分钟后没有打掉保护罩，自动退场
        self._fishType = 74207          # 龙女王
        self._maskFishType = 74215      # 女王保护罩.
        self._idx = 0                   # 阶段boss的索引          3、4、5、1、2
        self._startTS = 0               # boss出现的时间戳.
        self._nextTimer = None          # 下一个boss出生的定时器
        # showtime是boss出现前30秒(stage=0x10000) 有保护罩(0x1), 第一阶段(0x10), 受伤阶段(0x100)，没有保护罩(0x1000)
        self._isBossShowTimeStage = 0
        self._autofillTimer = None      # boss被捕获后是否自动填充
        self._clearTimer = None         # 清理鱼阵的定时器.
        self._group = None              # 鱼群对象
        self._setTimer()                # 设置定时器

    def addTestSuperBoss(self):
        self._addFishGroup()

    def _addBossShowTimeStage(self, val):
        """展示boss的状态"""
        self._isBossShowTimeStage |= val

    def _removeBossShowTimeStage(self, val):
        """删除boss状态"""
        self._isBossShowTimeStage &= ~val

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
        return self._isBossShowTimeStage & 0x10000 > 0 or self._isBossShowTimeStage & 0x1111 > 0

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
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x10000).start()     # boss即将出现

    def _addBoss(self, isSysTimerCall=True):
        """
        添加宝箱boss
        """
        if self._isBossShowTimeStage == 0x10000:                                                # 出生鱼阵  有保护罩.
            fishType = self._maskFishType
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
        elif self._isBossShowTimeStage == 0x1:                                                  # 第一阶段  有保护罩.
            fishType = self._maskFishType
            _bossGroupIds = self.random_boss_groupid(fishType)
        elif self._isBossShowTimeStage == 0x10:                                                 # 受伤鱼阵  无保护罩.
            fishType = self._fishType
            _bossGroupIds = self.table.runConfig.allSuperBossBornGroupIds[fishType]
        elif self._isBossShowTimeStage == 0x100:                                                # 第二阶段  无保护罩.
            fishType = self._fishType
            _bossGroupIds = self.random_boss_groupid(fishType)
        else:
            return
        nowTime = int(time.time())
        if nowTime >= self._startTS + self._addHurtTime:                                        # 2分钟后没有打掉保护罩，自动退场
            if self._isBossShowTimeStage in [0x1, 0x10]:
                if self._clearTimer:
                    self._clearTimer.cancel()
                    self._clearTimer = None
                self._clearTimer = FTLoopTimer(0.1, 0, self._clearData, True, self._maskFishType)
                self._clearTimer.start()
                return
        # boss超出最大存在时间后不再出现.
        if nowTime >= self._startTS + self._maxAliveTime:
            self._removeBossShowTimeStage(self._isBossShowTimeStage)
            return
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None
            # 处理冰冻自动填充时机延后逻辑.
            if self._group and not isSysTimerCall and self._group.extendGroupTime > 0:
                self._autofillTimer = FTLoopTimer(self._group.extendGroupTime, 0, self._addBoss, fishType, False)
                self._autofillTimer.start()
                self._group.extendGroupTime = 0
                return
        self._group = None
        _bossGroupId = random.choice(_bossGroupIds)
        if _bossGroupId:
            self._group = self.table.insertFishGroup(_bossGroupId)
            if self._group:
                self._autofillTimer = FTLoopTimer(self._group.totalTime + 1, 0, self._addBoss, fishType, False)
                self._autofillTimer.start()
                if self._isBossShowTimeStage == 0x10000:
                    self._removeBossShowTimeStage(self._isBossShowTimeStage)
                    self._addBossShowTimeStage(0x1)                                             # 出生鱼阵的状态
                elif self._isBossShowTimeStage == 0x1:
                    self._removeBossShowTimeStage(self._isBossShowTimeStage)
                    self._addBossShowTimeStage(0x10)                                            # 第一阶段的状态
                elif self._isBossShowTimeStage == 0x10:
                    self._removeBossShowTimeStage(self._isBossShowTimeStage)
                    self._addBossShowTimeStage(0x100)                                           # 受伤鱼阵的状态
                elif self._isBossShowTimeStage == 0x100:
                    self._removeBossShowTimeStage(self._isBossShowTimeStage)
                    self._addBossShowTimeStage(0x1000)                                          # 第二阶段的状态
                return self._group

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

        group_number = len(groupMap.keys()) / 3
        if not self._idx:
            num = random.randint(1, group_number)
            self._idx = num
        else:
            if self._idx + 1 in groupMap.keys():
                self._idx += 1
            else:
                self._idx = min(groupMap.keys())
        _bossGroupIds = groupMap[self._idx]
        return _bossGroupIds

    def _addFishGroup(self):
        """
        添加boss鱼阵
        """
        self._clearData(False)
        self._isBossShowTimeStage = 0
        if self._interval - 30 > 0:
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x10000).start()    # boss即将出现
        self._startTS = int(time.time())                                                        # boss出现的时间戳
        self._addBoss()                                                                         # 添加boss
        # 超出boss存活时间后清理boss.
        if self._maxAliveTime > 0:
            self._clearTimer = FTLoopTimer(self._maxAliveTime + 2, 0, self._clearData, True, self._fishType)
            self._clearTimer.start()

    def triggerCatchFishEvent(self, event):
        """
        处理捕获事件
        """
        _fishType = 0
        if self._maskFishType in event.fishTypes and self._isBossShowTimeStage == 0x1:           # 女王保护罩 出生鱼阵
            if self._group:
                self._removeBossShowTimeStage(0x1)
                self._addBossShowTimeStage(0x100)

        if self._maskFishType in event.fishTypes and self._isBossShowTimeStage == 0x10:          # 女王保护罩 第一鱼阵
            if self._group:
                self._removeBossShowTimeStage(0x1)
                self._addBossShowTimeStage(0x100)

        if self._fishType in event.fishTypes and self._isBossShowTimeStage == 0x100:            # 龙女王不带保护罩 受伤鱼阵
            if self._group:
                self._removeBossShowTimeStage(0x10)
                self._addBossShowTimeStage(0x100)

        if self._fishType in event.fishTypes and self._isBossShowTimeStage == 0x1000:           # 龙女王不带保护罩 第二阶段
            # boss被捕获时可能刚好超时,所以此时就不要再爆炸了.
            if not self._group:
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
                explosionPos = range(1, len(countPctList))  # [1, 2, 3, 4]
                random.shuffle(explosionPos)
                explosionPos.insert(0, 0)
                tmp = range(len(countPctList))              # [0, 1, 2, 3, 4]
                tmp.remove(explosionPos[-1])
                random.shuffle(tmp)
                explosionPos.append(tmp[0])
                msg.setResult("explosionPos", explosionPos[:self._stageCount])
                GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def dealEnterTable(self, userId):
        """
        玩家进入渔场时发送
        """
        # 当前阶段boss开始出现的时间戳.
        startTS = 0
        if self._isBossShowTimeStage & 0x1111 != 0:
            startTS = self._startTS
        msg = MsgPack()
        msg.setCmd("queen_info")
        msg.setResult("gameId", config.FISH_GAMEID)
        msg.setResult("roomId", self.table.roomId)
        msg.setResult("tableId", self.table.tableId)
        msg.setResult("startTS", startTS)
        GameMsg.sendMsg(msg, userId)
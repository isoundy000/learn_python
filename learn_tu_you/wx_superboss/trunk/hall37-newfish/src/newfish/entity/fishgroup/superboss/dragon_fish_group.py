# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/6/12.
"""

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
import poker.util.timestamp as pktimestamp
from newfish.entity.config import FISH_GAMEID
from newfish.entity.heartbeat import HeartbeatAble
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup
from newfish.entity.msg import GameMsg


class OctopusFishGroup(SuperBossFishGroup):
    """
    远古寒龙Boss鱼群
    """
    def __init__(self, table):
        super(OctopusFishGroup, self).__init__()
        self.table = table
        self.dragon = None
        if self.table.room.roomConf.get("dragonConf"):
            self.dragon = Dragon(table)
            self.dragon.startHeart()

    def isAppear(self):
        return self.dragon and self.dragon.state > Dragon.ST_IDLE

    def triggerCatchFishEvent(self, event):
        catch = event.catch
        fIds = [catchMap["fId"] for catchMap in catch if catchMap["reason"] == 0]

    def dealEnterTable(self, userId):
        pass

    def frozen(self, fishId, fishType, frozenTime):
        pass


class Dragon(HeartbeatAble):
    """
    远古寒龙
    """
    # 冰龙状态
    ST_IDLE = 0
    ST_PREPARE = 1
    ST_APPEARING = 2
    ST_APPEARED = 3
    ST_LEAVE = 4
    ST_FINAL = 5

    def __init__(self, table):
        super(Dragon, self).__init__(1)
        self.table = table
        # 冰龙状态
        self._state = None

    @property
    def state(self):
        return self._state

    def _doHeartbeat(self):
        timestamp = pktimestamp.getCurrentTimestamp() + 1
        if self._state is None:
            self.postCall(self._doIdle)
        elif self._state == Dragon.ST_IDLE:
            if timestamp >= self.prepareTime:
                self.postCall(self._doPrepare)
        elif self._state == Dragon.ST_PREPARE:
            if timestamp >= self.appearingTime:
                self.postCall(self._doAppearing)
        elif self._state == Dragon.ST_APPEARING:
            if timestamp >= self.appearedTime:
                self.postCall(self._doAppeared)
        elif self._state == Dragon.ST_APPEARED:
            if timestamp >= self.leaveTime:
                self.postCall(self._doLeave)
        elif self._state == Dragon.ST_LEAVE:
            if timestamp >= self.finalTime:
                self.postCall(self._doFinal)
        elif self._state == Dragon.ST_FINAL:
            if timestamp >= self.nextTime:
                self.postCall(self._doNext)
        return 1

    def _doIdle(self):
        """
        空闲状态
        """
        self.dragonConf = self.table.room.roomConf["dragonConf"]
        self._state = Dragon.ST_IDLE
        # 空闲状态开始时间戳
        self.idleTime = self.calcIdleTime()
        # 出场前状态开始时间戳
        self.prepareTime = self.calcPrepareTime()
        # 出场中状态开始时间戳
        self.appearingTime = self.calcAppearingTime()
        # 已出现状态开始时间戳
        self.appearedTime = self.calcAppearedTime()
        # 退场中状态开始时间戳
        self.leaveTime = self.calcLeaveTime()
        # 结束状态开始时间戳
        self.finalTime = self.calcFinalTime()
        # 下一只冰龙空闲状态开始时间戳
        self.nextTime = self.finalTime
        if ftlog.is_debug():
            ftlog.debug("Dragon._doIdle->", self.idleTime, self.prepareTime, self.appearingTime,
                        self.appearedTime, self.leaveTime, self.finalTime)

    def _doPrepare(self):
        """
        出场前状态
        """
        self._state = Dragon.ST_PREPARE
        self.syncDragonState()

    def _doAppearing(self):
        """
        出场中状态
        """
        self._state = Dragon.ST_APPEARING
        self.syncDragonState()

    def _doAppeared(self):
        """
        已出现状态
        """
        self._state = Dragon.ST_APPEARED
        self.syncDragonState()

    def _doLeave(self, isNow=False):
        """
        退场中状态
        """
        self._state = Dragon.ST_LEAVE
        if isNow:
            self.leaveTime = pktimestamp.getCurrentTimestamp()
            self.finalTime = self.calcFinalTime()
        self.syncDragonState()

    def _doFinal(self):
        """
        结束状态
        """
        self._state = Dragon.ST_FINAL

    def _doNext(self):
        """
        下一只巨型章鱼空闲状态
        """
        self._doIdle()

    def calcIdleTime(self):
        """
        计算空闲状态开始时间戳
        """
        return pktimestamp.getCurrentTimestamp() + 1

    def calcPrepareTime(self):
        """
        计算出场前状态开始时间戳
        """
        return self.idleTime + self.dragonConf["idle.times"]

    def calcAppearingTime(self):
        """
        计算出场中状态开始时间戳
        """
        return self.prepareTime + self.dragonConf["prepare.times"]

    def calcAppearedTime(self):
        """
        计算已出现状态开始时间戳
        """
        return self.appearingTime + self.dragonConf["appearing.times"]

    def calcLeaveTime(self):
        """
        计算退场中状态开始时间戳
        """
        return self.appearedTime + self.dragonConf["appeared.times"]

    def calcFinalTime(self):
        """
        计算结束状态开始时间戳
        """
        return self.leaveTime + self.dragonConf["leave.times"]

    def getCurrentStateStageTime(self):
        """
        获取当前状态开始结束时间
        """
        stateTime = {
            Dragon.ST_IDLE: self.idleTime,
            Dragon.ST_PREPARE: self.prepareTime,
            Dragon.ST_APPEARING: self.appearingTime,
            Dragon.ST_APPEARED: self.appearedTime,
            Dragon.ST_LEAVE: self.leaveTime,
            Dragon.ST_FINAL: self.finalTime
        }
        return stateTime[self._state], stateTime[self._state + 1]

    def syncDragonState(self, userId=0):
        """
        向玩家同步冰龙状态
        """
        if Dragon.ST_IDLE < self._state < Dragon.ST_FINAL:
            msg = MsgPack()
            msg.setCmd("dragon_info")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("state", self.state)
            startTime, endTime = self.getCurrentStateStageTime()
            ftlog.debug("syncDragonState", self.table.tableId, msg)
            if startTime and endTime:
                msg.setResult("progress", [startTime, endTime])
                GameMsg.sendMsg(msg, userId or self.table.getBroadcastUids())
            else:
                ftlog.error("syncDragonState error", self.table.tableId, msg)

# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/4/11.
"""

import random

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
import poker.util.timestamp as pktimestamp
from newfish.entity import util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.heartbeat import HeartbeatAble
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup
from newfish.entity.msg import GameMsg


class OctopusFishGroup(SuperBossFishGroup):
    """
    巨型章鱼Boss鱼群
    """
    def __init__(self, table):
        super(OctopusFishGroup, self).__init__()
        self.table = table
        self.octopus = None
        if self.table.room.roomConf.get("octopusConf") and self.table.room.roomConf.get("tentacleConf"):
            self.octopus = Octopus(table)
            self.octopus.startHeart()

    def isAppear(self):
        return self.octopus and self.octopus.state > Octopus.ST_IDLE

    def triggerCatchFishEvent(self, event):
        """触发捕鱼事件"""
        catch = event.catch
        fIds = [catchMap["fId"] for catchMap in catch if catchMap["reason"] == 0]
        self.octopus.catchTentacles(fIds)

    def dealEnterTable(self, userId):
        """进入桌子"""
        if self.octopus:
            self.octopus.syncOctopusState(userId=userId)
            self.octopus.syncTentacleState(userId=userId)

    def frozen(self, fishId, fishType, frozenTime):
        """冰冻"""
        self.octopus.frozenTentacles(fishId, fishType, frozenTime)


class Octopus(HeartbeatAble):
    """
    巨型章鱼
    """
    # 章鱼状态
    ST_IDLE = 0
    ST_PREPARE = 1
    ST_APPEARING = 2
    ST_APPEARED = 3
    ST_LEAVE = 4
    ST_FINAL = 5

    # 表情状态
    FACE_LAUGH = 1
    FACE_PAIN = 2

    def __init__(self, table):
        super(Octopus, self).__init__(1)
        self.table = table
        # 章鱼状态
        self._state = None
        # 章鱼表情定时器
        self._faceTimer = None
        # 所有触手对象
        self._tentacles = []
        # 已死亡触手
        self.diedTentaclesCount = {}
        # 剩余可出现触手
        self.surplusTentaclesCount = {}

    @property
    def state(self):
        return self._state

    def _doHeartbeat(self):
        timestamp = pktimestamp.getCurrentTimestamp() + 1
        if self._state is None:
            self.postCall(self._doIdle)
        elif self._state == Octopus.ST_IDLE:
            if timestamp >= self.prepareTime:
                self.postCall(self._doPrepare)
        elif self._state == Octopus.ST_PREPARE:
            if timestamp >= self.appearingTime:
                self.postCall(self._doAppearing)
        elif self._state == Octopus.ST_APPEARING:
            if timestamp >= self.appearedTime:
                self.postCall(self._doAppeared)
        elif self._state == Octopus.ST_APPEARED:
            if timestamp >= self.leaveTime:
                self.postCall(self._doLeave)
        elif self._state == Octopus.ST_LEAVE:
            if timestamp >= self.finalTime:
                self.postCall(self._doFinal)
        elif self._state == Octopus.ST_FINAL:
            if timestamp >= self.nextTime:
                self.postCall(self._doNext)
        return 1

    def _doIdle(self):
        """
        空闲状态
        """
        self.octopusConf = self.table.room.roomConf["octopusConf"]
        self.tentacleConf = self.table.room.roomConf["tentacleConf"]
        self._state = Octopus.ST_IDLE
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
        # 下一只巨型章鱼空闲状态开始时间戳
        self.nextTime = self.finalTime
        # 已死亡触手
        self.diedTentaclesCount = {}
        # 剩余可出现触手
        self.surplusTentaclesCount = {}
        for fishType, count in self.tentacleConf["totalTentacleCount"].iteritems():
            self.diedTentaclesCount[str(fishType)] = 0
            self.surplusTentaclesCount[str(fishType)] = count
        if ftlog.is_debug():
            ftlog.debug("Octopus._doIdle->", self.idleTime, self.prepareTime, self.appearingTime,
                        self.appearedTime, self.leaveTime, self.finalTime)

    def _doPrepare(self):
        """
        出场前状态
        """
        self._state = Octopus.ST_PREPARE
        self.syncOctopusState()

    def _doAppearing(self):
        """
        出场中状态
        """
        self._state = Octopus.ST_APPEARING
        self.syncOctopusState()
        self.createTentacles()

    def _doAppeared(self):
        """
        已出现状态
        """
        self._state = Octopus.ST_APPEARED
        self.syncOctopusState()
        self.initOctopusFace()

    def _doLeave(self, isNow=False):
        """
        退场中状态
        """
        self._state = Octopus.ST_LEAVE
        if isNow:
            self.leaveTime = pktimestamp.getCurrentTimestamp()
            self.finalTime = self.calcFinalTime()
        self.syncOctopusState()

    def _doFinal(self):
        """
        结束状态
        """
        self._state = Octopus.ST_FINAL
        self.clearTentacles()

    def _doNext(self):
        """
        下一只巨型章鱼空闲状态
        """
        self._doIdle()

    def createTentacles(self):
        """
        初始化所有触手
        """
        if self.table.playersNum >= self.table.room.roomConf["superBossMinSeatN"]:
            for initTentacle in self.tentacleConf["initTentacles"]:
                tentacle = Tentacle(self.table, self)
                tentacle.init(initTentacle["posId"], initTentacle["fishType"], initTentacle["delayTime"])
                self._tentacles.append(tentacle)
            self.syncTentacleState()

    def clearTentacles(self):
        """
        清除所有触手
        """
        for _tentacle in self._tentacles:
            _tentacle.clear()
        self._tentacles = []

    def catchTentacles(self, fIds):
        """
        捕获触手
        """
        if self._state == Octopus.ST_APPEARED:
            isCatch = False
            for _tentacle in self._tentacles:
                if _tentacle.state == Tentacle.ST_SWING and _tentacle.fishId in fIds:
                    isCatch = True
                    self.diedTentaclesCount[str(_tentacle.fishType)] += 1
                    _tentacle.catch()
            if ftlog.is_debug():
                ftlog.debug("catchTentacles", fIds, self.diedTentaclesCount)
            if self.diedTentaclesCount == self.tentacleConf["totalTentacleCount"]:
                self._doLeave(isNow=True)
            elif isCatch:
                self.playingOctopusPainFace()

    def frozenTentacles(self, fishId, fishType, frozenTime):
        """
        触手被冻住
        """
        if self._state == Octopus.ST_APPEARED:
            if str(fishType) in self.tentacleConf["totalTentacleCount"]:
                ftlog.debug("frozenTentacles", fishId, fishType, frozenTime)
                for _tentacle in self._tentacles:
                    if _tentacle.state == Tentacle.ST_SWING and _tentacle.fishId == fishId:
                        _tentacle.frozenTentacleFish(frozenTime)
                        break

    def getAliveTentacles(self):
        """
        获得当前存活触手数量
        """
        aliveCount = 0
        for _tentacle in self._tentacles:
            if _tentacle.state == Tentacle.ST_SWING:
                aliveCount += 1
        return aliveCount

    def initOctopusFace(self):
        """
        初始化章鱼表情
        """
        self._faceTimer and self._faceTimer.cancel()
        if self._state == Octopus.ST_APPEARED:
            laughTime = random.randint(*self.octopusConf["laughTimeRange"])
            self._faceTimer = FTLoopTimer(laughTime, 0, self.playingOctopusLaughFace)
            self._faceTimer.start()

    def playingOctopusLaughFace(self):
        """
        循环间隔一段时间播放嗤笑表情
        """
        self.sendOctopusFaceInfo(Octopus.FACE_LAUGH)
        self.initOctopusFace()

    def playingOctopusPainFace(self):
        """
        播放疼痛表情
        """
        self.sendOctopusFaceInfo(Octopus.FACE_PAIN)

    def sendOctopusFaceInfo(self, state):
        """
        发送章鱼表情信息
        """
        if self._state == Octopus.ST_APPEARED:
            msg = MsgPack()
            msg.setCmd("octopus_face")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("state", state)
            GameMsg.sendMsg(msg, self.table.getBroadcastUids())
            ftlog.debug("sendOctopusFaceInfo", self.table.tableId, msg)

    # def refreshTentacles(self, timestamp):
    #     """
    #     刷新所有触手状态
    #     """
    #     isRefresh = False
    #     for tentacle in self._tentacles:
    #         if tentacle.refreshState(timestamp):
    #             isRefresh = True
    #     if isRefresh:
    #         self.syncTentacleState()

    def calcIdleTime(self):
        """
        计算空闲状态开始时间戳
        """
        return pktimestamp.getCurrentTimestamp() + 1

    def calcPrepareTime(self):
        """
        计算出场前状态开始时间戳
        """
        return self.idleTime + self.octopusConf["idle.time"]

    def calcAppearingTime(self):
        """
        计算出场中状态开始时间戳
        """
        return self.prepareTime + self.octopusConf["prepare.time"]

    def calcAppearedTime(self):
        """
        计算已出现状态开始时间戳
        """
        return self.appearingTime + self.octopusConf["appearing.time"]

    def calcLeaveTime(self):
        """
        计算退场中状态开始时间戳
        """
        return self.appearedTime + self.octopusConf["appeared.time"]

    def calcFinalTime(self):
        """
        计算结束状态开始时间戳
        """
        return self.leaveTime + self.octopusConf["leave.time"]

    def getCurrentStateStageTime(self):
        """
        获取当前状态开始结束时间
        """
        stateTime = {
            Octopus.ST_IDLE: self.idleTime,
            Octopus.ST_PREPARE: self.prepareTime,
            Octopus.ST_APPEARING: self.appearingTime,
            Octopus.ST_APPEARED: self.appearedTime,
            Octopus.ST_LEAVE: self.leaveTime,
            Octopus.ST_FINAL: self.finalTime
        }
        return stateTime[self._state], stateTime[self._state + 1]

    def generateNewTentacleConf(self, oldPosId):
        """
        生成新触手配置
        """
        if self.diedTentaclesCount != self.tentacleConf["totalTentacleCount"]:
            probability = []
            for fishType, count in self.surplusTentaclesCount.iteritems():
                if count > 0:
                    probb = {
                        "fishType": int(fishType),
                        "count": count
                    }
                    probability.append(probb)
            ftlog.debug("generateNewTentacleConf", probability)
            if probability:
                idx = util.selectIdxByWeight([probb["count"] for probb in probability])
                fishType = probability[idx]["fishType"]
                posId = self.generateNewPosId(oldPosId)
                delayTimeRange = self.tentacleConf["delayTimeRange"][0] if self.getAliveTentacles() < 2 else \
                    self.tentacleConf["delayTimeRange"][1]
                delayTime = random.randint(*delayTimeRange)
                ftlog.debug("generateNewTentacleConf", fishType, posId, delayTime)
                return posId, fishType, delayTime
        return 0, 0, 0

    def generateNewPosId(self, oldPosId):
        """
        生成新posId
        """
        defaultGroups = [(1, 4), (2, 3), (5, 6)]
        usableGroups = filter(lambda group: oldPosId in group, defaultGroups)
        if usableGroups:
            return random.choice(random.choice(list(usableGroups)))
        return 0

    def syncOctopusState(self, userId=0):
        """
        向玩家同步巨型章鱼状态
        """
        if Octopus.ST_IDLE < self._state < Octopus.ST_FINAL:
            msg = MsgPack()
            msg.setCmd("octopus_info")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("state", self.state)
            startTime, endTime = self.getCurrentStateStageTime()
            ftlog.debug("syncOctopusState", self.table.tableId, msg)
            if startTime and endTime:
                msg.setResult("progress", [startTime, endTime])
                GameMsg.sendMsg(msg, userId or self.table.getBroadcastUids())
            else:
                ftlog.error("syncOctopusState error", self.table.tableId, msg)

    def syncTentacleState(self, tentacle=None, userId=0):
        """
        向玩家同步触手状态
        """
        if Octopus.ST_PREPARE < self._state < Octopus.ST_LEAVE:
            tentacles = [tentacle] if tentacle else self._tentacles
            tentacleList = []
            for _tentacle in tentacles:
                if Tentacle.ST_IDLE < _tentacle.state < Tentacle.ST_FINAL:
                    tentacleList.append(_tentacle.toDict())
            ftlog.debug("syncTentacleState", userId, self.table.tableId, tentacleList, self._tentacles, self.state)
            if tentacleList:
                msg = MsgPack()
                msg.setCmd("tentacle_info")
                msg.setResult("gameId", FISH_GAMEID)
                msg.setResult("roomId", self.table.roomId)
                msg.setResult("tableId", self.table.tableId)
                msg.setResult("tentacles", tentacleList)
                GameMsg.sendMsg(msg, userId or self.table.getBroadcastUids())
                ftlog.debug("syncTentacleState", self.table.tableId, msg)


class Tentacle(object):
    """
    触手
    """
    ST_IDLE = -1
    ST_SWING = 0
    ST_RETRACT = 1
    ST_FINAL = 2

    def __init__(self, table, octopus):
        self.table = table
        self.octopus = octopus
        self._state = None
        self._idleTimer = None
        self._swingTimer = None
        self._retractTimer = None
        self.clear()

    @property
    def state(self):
        return self._state

    def clear(self):
        self._idleTimer and self._idleTimer.cancel()
        self._swingTimer and self._swingTimer.cancel()
        self._retractTimer and self._retractTimer.cancel()
        self._state = None
        self.posId = 0
        self.fishId = 0
        self.fishType = 0
        self.delayTime = 0
        self.frozenTime = 0

    def init(self, posId, fishType, delayTime):
        """初始化章鱼boss的触手"""
        self.tentacleConf = self.table.room.roomConf["tentacleConf"]
        self.posId = posId
        self.fishType = fishType
        self.delayTime = delayTime
        self.idleTime = self.calcIdleTime()
        self.swingTime = self.calcSwingTime()
        self.retractTime = self.calcRetractTime()
        self.finalTime = self.calcFinalTime()
        self.createTentacleFish()
        if self.fishId > 0:
            if self.delayTime > 0:
                self._doIdle()
            else:
                self._doSwing()

    def _doIdle(self):
        """
        空闲等待
        """
        self._state = Tentacle.ST_IDLE
        stageTime = self.getCurrentStateStageTime()
        interval = stageTime[1] - stageTime[0]
        self._idleTimer = FTLoopTimer(interval, 0, self._doSwing)
        self._idleTimer.start()

    def _doSwing(self):
        """
        摆动触手
        """
        self._state = Tentacle.ST_SWING
        if self.delayTime > 0:
            self.octopus.syncTentacleState(self)
        stageTime = self.getCurrentStateStageTime()
        interval = stageTime[1] - stageTime[0]
        self._swingTimer = FTLoopTimer(interval, 0, self._doRetract)
        self._swingTimer.start()

    def _doRetract(self):
        """
        触手开始收回
        """
        if self._state == Tentacle.ST_SWING:
            self._state = Tentacle.ST_RETRACT
            self.octopus.syncTentacleState(self)
            stageTime = self.getCurrentStateStageTime()
            interval = stageTime[1] - stageTime[0]
            self._retractTimer = FTLoopTimer(interval, 0, self._doFinal)
            self._retractTimer.start()

    def _doFinal(self):
        """
        触手已收回
        """
        if self.octopus.state == Octopus.ST_APPEARED and self._state == Tentacle.ST_RETRACT:
            self.octopus.surplusTentaclesCount[str(self.fishType)] += 1
        self.disappear()

    def disappear(self):
        """
        触手消失
        """
        self._state = Tentacle.ST_FINAL
        posId, fishType, delayTime = self.octopus.generateNewTentacleConf(self.posId)
        self.clear()
        if self.octopus.state == Octopus.ST_APPEARED:
            if fishType and posId:
                ftlog.debug("disappear init", self.table.tableId, posId, fishType, delayTime)
                self.init(posId, fishType, delayTime)

    def catch(self):
        """
        触手被捕获
        """
        self._swingTimer and self._swingTimer.cancel()
        self._retractTimer = FTLoopTimer(self.tentacleConf["retractTime"], 0, self._doFinal)
        self._retractTimer.start()

    def calcIdleTime(self):
        """
        计算空闲状态开始时间戳
        """
        return pktimestamp.getCurrentTimestamp() + 1

    def calcSwingTime(self):
        """
        计算摆动状态开始时间戳
        """
        return self.idleTime + self.delayTime

    def calcRetractTime(self):
        """
        计算收回状态开始时间戳
        """
        return self.swingTime + random.randint(*self.tentacleConf["swingTimeRange"]) + self.frozenTime

    def calcFinalTime(self):
        """
        计算结束状态开始时间戳
        """
        return self.retractTime + self.tentacleConf["retractTime"]

    def getCurrentStateStageTime(self):
        """
        获取当前状态开始结束时间
        """
        stateTime = {
            Tentacle.ST_IDLE: self.idleTime,
            Tentacle.ST_SWING: self.swingTime,
            Tentacle.ST_RETRACT: self.retractTime,
            Tentacle.ST_FINAL: self.finalTime
        }
        return stateTime[self._state], stateTime[self._state + 1]

    def createTentacleFish(self):
        """
        创建触手对应的鱼阵
        """
        groupIds = self.table.runConfig.allSuperBossGroupIds[self.fishType]
        if groupIds:
            groupIds = random.choice(groupIds)
            group = self.table.insertFishGroup(groupIds)
            self.fishId = group.startFishId
            self.octopus.surplusTentaclesCount[str(self.fishType)] -= 1

    def frozenTentacleFish(self, frozenTime):
        """
        触手被冻住
        """
        self.frozenTime += frozenTime
        # 刷新触手收回动画开始和结束时间
        self.retractTime = self.calcRetractTime()
        self.finalTime = self.calcFinalTime()
        stageTime = self.getCurrentStateStageTime()
        interval = stageTime[1] - pktimestamp.getCurrentTimestamp()
        ftlog.debug("frozenTentacleFish", self.frozenTime, self.retractTime, interval)
        self._swingTimer and self._swingTimer.cancel()
        self._swingTimer = FTLoopTimer(interval, 0, self._doRetract)
        self._swingTimer.start()

    def toDict(self):
        if Tentacle.ST_IDLE < self._state < Tentacle.ST_FINAL:
            return {
                "posId": self.posId,
                "fishId": self.fishId,
                "fishType": self.fishType,
                "state": self.state,
                "progress": list(self.getCurrentStateStageTime())
            }
        return {}
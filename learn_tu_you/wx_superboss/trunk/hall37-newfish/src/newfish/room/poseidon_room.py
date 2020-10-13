# -*- coding=utf-8 -*-
"""
Created by lichen on 2019-10-22.
"""

import functools
import time
from datetime import datetime
from random import choice, randint
from collections import OrderedDict

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from freetime.util.log import getMethodName
import poker.util.timestamp as pktimestamp
from poker.protocol import router
from poker.entity.biz import bireport
from poker.entity.dao import daobase
from poker.entity.configure import gdata
from poker.entity.game.rooms.normal_room import TYNormalRoom
from hall.entity import hallvip
from newfish.entity import config, util
from newfish.entity.cron import FTCron
from newfish.entity.lotterypool import poseidon_lottery_pool
from newfish.entity.redis_keys import MixData
from newfish.entity.config import FISH_GAMEID, ELEC_TOWERID, TOWERIDS
from newfish.servers.table.rpc import table_remote
from newfish.servers.util.rpc import user_rpc
from newfish.entity.quick_start import FishQuickStart


class FishPoseidonRoom(TYNormalRoom):
    """
    捕鱼海皇来袭房间
    """
    def __init__(self, roomDefine):
        super(FishPoseidonRoom, self).__init__(roomDefine)
        self.poseidon = None
        self.lastTowerTotalBets = [0, 0, 0]                     # 最后充能的电能倍率
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:
            self.allTableDict = {}                              # {roomId: {tableId: table, tableId1, table}}
            self.initialized = False                            # 初始化所有的影子房间
            self.initializedRoomIds = set()                     # roomId
            self.initPoseidon()
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:
            self._allTableDict = {}
            self._allPlayerDict = {}
            self._usableTableList = []
            from newfish.game import TGFish
            from newfish.entity.event import EnterTableEvent, LeaveTableEvent
            TGFish.getEventBus().subscribe(EnterTableEvent, self._triggerEnterTableEvent)
            TGFish.getEventBus().subscribe(LeaveTableEvent, self._triggerLeaveTableEvent)
            self.towerTotalBetsTimer = None

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.poseidon_table import FishPoseidonTable
        table = FishPoseidonTable(self, tableId)
        self._addTable(table)
        return table

    def _addTable(self, table):
        self._allTableDict[table.tableId] = table
        self._usableTableList.append(table)
        if ftlog.is_debug():
            ftlog.debug("_addTable->", self._allTableDict, self._usableTableList)

    def initializedGT(self, shadowRoomId, tableCount):
        """
        GT初始化完成
        """
        if ftlog.is_debug():
            ftlog.debug("initializedGT->", shadowRoomId, tableCount)
        for i in xrange(tableCount):
            tableId = shadowRoomId * 10000 + i + 1
            table = Table(self.gameId, shadowRoomId, tableId)
            self.allTableDict.setdefault(shadowRoomId, {})
            self.allTableDict[shadowRoomId][table.tableId] = table
        self.initializedRoomIds.add(shadowRoomId)
        if len(self.initializedRoomIds) == len(self.roomDefine.shadowRoomIds):
            self.initialized = True
        if ftlog.is_debug():
            ftlog.debug("initializedGT->", self.initialized, self.allTableDict)

    def initPoseidon(self):
        """
        初始化海皇
        """
        self.poseidon = Poseidon(self)
        self.poseidon.startHeart()

    def startTowerTotalBetsTimer(self):
        """
        启动魔塔累计充能金币刷新定时器
        """
        if not self.towerTotalBetsTimer:
            self.towerTotalBetsTimer = FTLoopTimer(1, -1, self.getTowerTotalBets)
            self.towerTotalBetsTimer.start()
            self.lastTowerTotalBets = [0, 0, 0]

    def stopTowerTotalBetsTimer(self):
        """
        停止魔塔累计充能金币刷新定时器
        """
        if self.towerTotalBetsTimer:
            self.towerTotalBetsTimer.cancel()
            self.towerTotalBetsTimer = None

    def incrTowerTotalBets(self, towerId, count):
        """
        增加魔塔累计充能金币
        """
        assert (towerId in TOWERIDS)
        finalCount = daobase.executeMixCmd("HINCRBY", MixData.towerTotalBets, towerId, count)
        self.lastTowerTotalBets[TOWERIDS.index(towerId)] = finalCount

    def getTowerTotalBets(self):
        """
        获取魔塔累计充能金币
        """
        totalBets = daobase.executeMixCmd("HMGET", MixData.towerTotalBets, *TOWERIDS)
        self.lastTowerTotalBets = map(lambda bet: bet or 0, totalBets)
        return self.lastTowerTotalBets

    def delTowerTotalBets(self):
        """
        删除魔塔累计充能金币
        """
        daobase.executeMixCmd("DEL", MixData.towerTotalBets)

    def doQuickStart(self, msg):
        """
        Note:
            1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
            2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。
            3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
        """
        assert self.roomId == msg.getParam("roomId")

        userId = msg.getParam("userId")
        shadowRoomId = msg.getParam("shadowRoomId")
        tableId = msg.getParam("tableId")
        clientId = msg.getParam("clientId")
        ftlog.hinfo(getMethodName(), "->|userId, clientId, roomId, shadowRoomId, tableId:", userId, clientId, self.roomId, shadowRoomId, tableId)

        if self.runStatus != self.ROOM_STATUS_RUN:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE, userId, clientId, self.roomId)
            return
        if tableId == 0:  # 服务器为玩家选择桌子并坐下
            details = bireport.getRoomOnLineUserCount(FISH_GAMEID, True)[2]
            complete = False
            roomIds = self.roomDefine.shadowRoomIds
            # 按VIP等级分桌
            vipRoomConf = OrderedDict({6: -3, 3: -6, 1: -8, 0: -10})
            vipLevel = hallvip.userVipSystem.getVipInfo(userId).get("level", 0)
            index = 0
            for level in vipRoomConf:
                if vipLevel >= level:
                    index = vipRoomConf[level]
                    break
            for roomId in roomIds[index:]:
                tableCount = self.roomDefine.configure["gameTableCount"]
                maxSeatN = self.tableConf["maxSeatN"]
                if details.get(str(roomId)) < int(tableCount * maxSeatN * self.roomConf.get("occupyMax", 0.9)):
                    shadowRoomId = roomId
                    complete = True
                    break
            if not complete:
                shadowRoomId = choice(self.roomDefine.shadowRoomIds)
            tableId = self.getBestTableId(userId, shadowRoomId)
        else:  # 玩家自选桌子坐下
            assert isinstance(shadowRoomId, int) and gdata.roomIdDefineMap()[shadowRoomId].bigRoomId == self.roomDefine.bigRoomId
            tableId = self.enterOneTable(userId, shadowRoomId, tableId)

        if not tableId:
            ftlog.error(getMethodName(), "getFreeTableId timeout", "|userId, roomId, tableId:", userId, self.roomId, tableId)
            return

        if ftlog.is_debug():
            ftlog.info(getMethodName(), "after choose table", "|userId, shadowRoomId, tableId:", userId, shadowRoomId, tableId)
        extParams = msg.getKey("params")
        self.querySitReq(userId, shadowRoomId, tableId, clientId, extParams)

    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量
        """
        pass

    def _updateUsableTableList(self):
        pass

    def _triggerEnterTableEvent(self, event):
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            self._allPlayerDict[userId] = tableId
            if ftlog.is_debug():
                ftlog.debug("_triggerEnterTableEvent", self._allPlayerDict)

    def _triggerLeaveTableEvent(self, event):
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            if userId in self._allPlayerDict:
                self._allPlayerDict.pop(userId)
            if ftlog.is_debug():
                ftlog.debug("_triggerLeaveTableEvent", self._allPlayerDict)


class Heartbeat(object):
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, target, interval):
        self._target = target                           # 目标
        self._state = Heartbeat.ST_IDLE                 # 状态
        self._count = 0                                 # 次数
        self._postTaskList = []
        self._timer = None
        self._interval = interval
        self._init = False

    def start(self):
        assert (self._state == Heartbeat.ST_IDLE)
        self._state = Heartbeat.ST_START
        self._timer = FTLoopTimer(0, 0, self._onInit)
        self._timer.start()

    def stop(self):
        if self._state != Heartbeat.ST_STOP:
            self._state = Heartbeat.ST_STOP
            if self._timer:
                self._timer.cancel()
            self._timer = None

    @property
    def count(self):
        return self._count

    def postCall(self, func, *args, **kwargs):
        self.postTask(functools.partial(func, *args, **kwargs))

    def postTask(self, task):
        if self._state != Heartbeat.ST_STOP:
            self._postTaskList.append(task)
            if self._init and self._timer:
                self._timer.cancel()
                self._timer = FTLoopTimer(0, 0, self._onTimeout)
                self._timer.start()

    def _onInit(self):
        try:
            self._timer = None
            interval = self._target.onInit()
            if interval:
                self._interval = interval
            self._scheduleTimer()
        except:
            ftlog.error("Heartbeat._onInit")

    def _onTimeout(self):
        try:
            self._timer = None
            self._count += 1
            self._processPostTaskList()
            interval = self._target.onHeartbeat()
            if interval is not None:
                self._interval = interval
        except:
            self._interval = 1
            ftlog.error("Heartbeat._onTimeout")
        self._scheduleTimer()

    def _scheduleTimer(self):
        if self._state == Heartbeat.ST_START:
            interval = 0 if self._postTaskList else self._interval
            self._timer = FTLoopTimer(interval, 0, self._onTimeout)
            self._timer.start()

    def _processPostTaskList(self):
        taskList = self._postTaskList
        self._postTaskList = []
        for task in taskList:
            try:
                task()
            except:
                ftlog.error("task=", task)


class HeartbeatAble(object):

    def __init__(self, interval):
        self._heart = Heartbeat(self, interval)

    def startHeart(self):
        self._heart.start()

    def stopHeart(self):
        self._heart.stop()

    def onInit(self):
        return self._doInit()

    def onHeartbeat(self):
        return self._doHeartbeat()

    def postCall(self, func, *args, **kwargs):
        self._heart.postCall(func, *args, **kwargs)

    def _doInit(self):
        return 1

    def _doHeartbeat(self):
        return 1


class Table(object):
    def __init__(self, gameId, roomId, tableId):
        self._gameId = gameId
        self._roomId = roomId
        self._tableId = tableId

    @property
    def gameId(self):
        return self._gameId

    @property
    def roomId(self):
        return self._roomId

    @property
    def tableId(self):
        return self._tableId


class Poseidon(HeartbeatAble):
    """
    海皇
    """
    ST_IDLE = 0
    ST_PREPARE = 1
    ST_APPEAR = 2
    ST_LEAVE = 3
    ST_FINAL = 4

    def __init__(self, room):
        super(Poseidon, self).__init__(1)
        self.room = room
        self._state = None
        self.tower = None

    @property
    def state(self):
        return self._state

    def _doHeartbeat(self):
        ftlog.is_debug() and ftlog.debug("Poseidon._doHeartbeat", "state=", self._state)
        timestamp = pktimestamp.getCurrentTimestamp() + 1
        if self._state is None and self.room.initialized:
            self.postCall(self._doIdle)
        elif self._state == Poseidon.ST_IDLE:
            self._sendLed(timestamp, self.prepareTime)
            if timestamp >= self.prepareTime:
                self.postCall(self._doPrepare)
        elif self._state == Poseidon.ST_PREPARE:
            if timestamp >= self.appearTime:
                self.postCall(self._doAppear)
        elif self._state == Poseidon.ST_APPEAR:
            if timestamp >= self.leaveTime:
                self.postCall(self._doLeave)
        elif self._state == Poseidon.ST_LEAVE:
            if timestamp >= self.finalTime:
                self.postCall(self._doFinal)
        return 1

    def _doIdle(self):
        """
        海皇空闲状态
        """
        self.poseidonConf = self.room.roomConf["poseidonConf"]
        self._state = Poseidon.ST_IDLE
        self._cron = FTCron(self.poseidonConf["cronTime"])
        self.appearTimeStrList = [time_.strftime("%R") for time_ in self._cron.getTimeList()]
        # 海皇空闲状态开始时间戳
        self.idleTime = self.calcIdleTime()
        # 海皇出现状态开始时间戳
        self.appearTime = self.calcAppearTime()
        if not self.appearTime:
            ftlog.error("Poseidon._doIdle->error", self.idleTime, self.room.roomConf["poseidonConf"])
            return
        # 海皇准备出现状态开始时间戳
        self.prepareTime = self.calcPrepareTime(self.appearTime)
        # 海皇撤离状态开始时间戳
        self.leaveTime = self.calcLeaveTime(self.appearTime)
        # 海皇撤离完成时间戳（下一只海皇空闲状态开始时间戳）
        self.finalTime = self.calcFinalTime(self.appearTime)
        if ftlog.is_debug():
            ftlog.debug("Poseidon._doIdle->", self.appearTimeStrList, self.appearTime, self.idleTime,
                        self.prepareTime, self.leaveTime, self.finalTime)
        self.syncPoseidonState()
        self.startTower()
        # 每轮开始前处理上一轮盈亏数据（重启后立即处理）
        poseidon_lottery_pool.dealPoseidonProfitAndLoss()

    def _doPrepare(self):
        """
        海皇准备出现状态
        """
        self._state = Poseidon.ST_PREPARE
        self.syncPoseidonState()

    def _doAppear(self):
        """
        海皇出现状态
        """
        self._state = Poseidon.ST_APPEAR
        self.syncPoseidonState()
        self.tower.doCharge()

    def _doLeave(self):
        """
        海皇撤离状态
        """
        self._state = Poseidon.ST_LEAVE
        self.syncPoseidonState()

    def _doFinal(self):
        """
        海皇结束状态
        """
        self.stopTower()
        self._doIdle()

    def startTower(self):
        """
        启动魔塔
        """
        self.tower = Tower(self.room, self)
        self.tower.startHeart()
        self.tower.doIdle()

    def stopTower(self):
        """
        停止魔塔
        """
        self.tower.stopHeart()
        self.tower = None

    def calcIdleTime(self):
        """
        计算空闲时间戳
        """
        return pktimestamp.getCurrentTimestamp() + 1

    def calcPrepareTime(self, appearTime):
        """
        计算准备出现时间戳
        """
        return appearTime - self.poseidonConf["prepare.time"]

    def calcAppearTime(self, timestamp=None):
        """
        计算出现时间戳
        """
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        ntime = datetime.fromtimestamp(int(timestamp))
        nexttime = None
        if self._cron:
            nexttime = self._cron.getNextTime(ntime)
        if nexttime:
            return int(time.mktime(nexttime.timetuple()))
        return None

    def calcLeaveTime(self, appearTime):
        """
        计算撤离时间戳
        """
        return appearTime + self.poseidonConf["appear.time"]

    def calcFinalTime(self, appearTime):
        """
        计算结束时间戳
        """
        return self.calcLeaveTime(appearTime) + self.poseidonConf["leave.time"]

    def getCurrentStateStageTime(self):
        """
        获取当前状态开始结束时间
        """
        stateTime = {
            Poseidon.ST_IDLE: self.idleTime,
            Poseidon.ST_PREPARE: self.prepareTime,
            Poseidon.ST_APPEAR: self.appearTime,
            Poseidon.ST_LEAVE: self.leaveTime,
            Poseidon.ST_FINAL: self.finalTime
        }
        return stateTime[self._state], stateTime[self._state + 1]

    def syncPoseidonState(self):
        """
        向渔场同步海皇状态
        """
        for _, tableDict in self.room.allTableDict.iteritems():
            # 异步处理防止阻塞
            FTLoopTimer(0, 0, self._syncPoseidonState, tableDict).start()
            if ftlog.is_debug():
                ftlog.debug("syncPoseidonState->", tableDict)

    def _syncPoseidonState(self, tableDict):
        """
        向渔场同步海皇状态
        """
        for table in tableDict.values():
            self.sendPoseidonStateMessage(table)

    def sendPoseidonStateMessage(self, table):
        """
        发送海皇状态消息
        """
        msg = MsgPack()
        msg.setCmd("table_manage")
        msg.setParam("action", "poseidon_state")
        msg.setParam("gameId", table.gameId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("state", self._state)
        startTime, endTime = self.getCurrentStateStageTime()
        if startTime and endTime:
            msg.setParam("stageTime", [startTime, endTime])
            router.sendTableServer(msg, table.roomId)
        else:
            ftlog.error("sendPoseidonStateMessage->error", table.tableId, startTime, endTime)

    def _sendLed(self, timestamp, prepareTime):
        """
        发送LED提示
        """
        leftTime = prepareTime - timestamp
        if leftTime == 120 or leftTime == 30:
            for lang in util.getAllLanguage():
                mid = "ID_LED_POSEIDON_1"
                msg = config.getMultiLangTextConf(mid, lang=lang) % (time.strftime("%H:%M", time.localtime(prepareTime)))
                user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, id=mid, lang=lang)


class Tower(HeartbeatAble):
    """
    魔塔
    """
    ST_IDLE = -1
    ST_CHARGE = 0
    ST_ATTACK = 1
    ST_AWARD = 2
    ST_FINAL = 3

    def __init__(self, room, poseidon):
        super(Tower, self).__init__(1)
        self.room = room
        self.poseidon = poseidon
        self._state = None
        self._multiples = None

    def _doHeartbeat(self):
        timestamp = pktimestamp.getCurrentTimestamp() + 1
        if self._state == Tower.ST_CHARGE:
            if timestamp >= self.attackTime:
                self.postCall(self._doAttack)
        elif self._state == Tower.ST_ATTACK:
            if timestamp >= self.awardTime:
                self.postCall(self._doAward)
        elif self._state == Tower.ST_AWARD:
            if timestamp >= self.finalTime:
                self.postCall(self._doFinal)
        return 1

    def _doIdle(self):
        """
        空闲状态
        """
        self.towerConf = self.room.roomConf["towerConf"]
        self._state = Tower.ST_IDLE
        self._multiples = None
        self.chargeTimeList = []
        self.firstChargeTime = self.poseidon.appearTime
        self.calcAllTime()
        if ftlog.is_debug():
            ftlog.debug("Tower._doIdle->", self.chargeTime, self.attackTime, self.awardTime, self.finalTime)

    def _doCharge(self):
        """
        充能状态
        """
        self._state = Tower.ST_CHARGE
        self.room.delTowerTotalBets()
        self.syncTowerState()
        self.startTowerTotalBetsTimer()

    def _doAttack(self):
        """
        攻击状态
        """
        self._state = Tower.ST_ATTACK
        self.calcAttackResult()
        self.syncTowerState()
        self.stopTowerTotalBetsTimer()

    def _doAward(self):
        """
        发奖状态
        """
        self._state = Tower.ST_AWARD
        self.syncTowerState()
        self.reportServerProfitAndLoss()

    def _doFinal(self):
        """
        结束状态
        """
        self.updateTowerHistory()
        self.calcAllTime()
        if self.chargeTime:
            self._doCharge()
        else:
            self._state = Tower.ST_FINAL

    def doIdle(self):
        """
        由海皇调用，保证消息顺序
        """
        self._doIdle()

    def doCharge(self):
        """
        由海皇调用，保证消息顺序
        """
        self._doCharge()

    def calcAllTime(self):
        """
        计算出所有所需时间
        """
        self.chargeTime = self.calcChargeTime()
        if self.chargeTime:
            self.attackTime = self.calcAttackTime(self.chargeTime)
            self.awardTime = self.calcAwardTime(self.chargeTime)
            self.finalTime = self.calcFinalTime(self.chargeTime)

    def calcChargeTime(self, timestamp=None):
        """
        魔塔开始充能时间
        """
        if not self.chargeTimeList:
            # 每轮开始充能时间戳
            eachChargeTime = self.firstChargeTime
            # 每轮总时间
            towerRoundTime = self.towerConf["charge.time"] + self.towerConf["attack.time"] + self.towerConf["award.time"]
            while eachChargeTime < self.poseidon.leaveTime:
                self.chargeTimeList.append(eachChargeTime)
                eachChargeTime += towerRoundTime
            if ftlog.is_debug():
                ftlog.debug("Tower.calcChargeTime->",
                            [time.strftime("%H:%M:%S",time.localtime(time_)) for time_ in self.chargeTimeList])
        timestamp = timestamp or pktimestamp.getCurrentTimestamp()
        for _, chargeTime in enumerate(self.chargeTimeList):
            if timestamp <= chargeTime:
                return chargeTime
        return None

    def calcAttackTime(self, chargeTime):
        """
        魔塔开始攻击时间
        """
        return chargeTime + self.towerConf["charge.time"]

    def calcAwardTime(self, chargeTime):
        """
        魔塔开始发奖时间
        """
        return self.calcAttackTime(chargeTime) + self.towerConf["attack.time"]

    def calcFinalTime(self, chargeTime):
        """
        魔塔结束时间
        """
        return self.calcAwardTime(chargeTime) + self.towerConf["award.time"]

    def calcAttackResult(self):
        """
        魔塔攻击结果
        """
        self._multiples = []
        towerMultipleConf = config.getPoseidonConf("towerMultiple")
        randInt = randint(1, 10000)
        for towerId in config.TOWERIDS:
            if towerId == ELEC_TOWERID:
                randInt = randint(1, 10000)
                multiple = self._getMultiple(randInt, towerMultipleConf[str(towerId)])
                multiple = self._getElecTowerMultiple(multiple, towerMultipleConf[str(towerId)])
            else:
                multiple = self._getMultiple(randInt, towerMultipleConf[str(towerId)])

            self._multiples.append(multiple)

    def _getMultiple(self, randInt, multipleList):
        """
        获得魔塔倍率
        """
        for multipleMap in multipleList:
            probb = multipleMap["probb"]
            if probb[0] <= randInt <= probb[-1]:
                return multipleMap["multiple"]
        return 0

    def _getElecTowerMultiple(self, originMultiple, multipleList):
        """
        获得电塔最终倍率
        """
        multiples = sorted([multipleMap["multiple"] for multipleMap in multipleList])
        nextIndex = min(multiples.index(originMultiple) + 1, len(multiples) - 1)
        nextMultiple = multiples[nextIndex]
        if originMultiple > 0 and nextMultiple - originMultiple > 0:
            # 当前轮次玩家对电塔充能总额
            elecTowerTotalBet = self.room.getTowerTotalBets()[TOWERIDS.index(ELEC_TOWERID)]
            # 提升电塔倍率的充能金币基数
            elecTowerBetRadix = config.getPoseidonConf("elecTowerBetRadix") or 0
            # 电塔奖池
            lotteryCoin = poseidon_lottery_pool.getElecTowerPool()
            # 电塔差额倍率金币
            multipleCoin = (nextMultiple - originMultiple) * elecTowerTotalBet
            ftlog.info("_getElecTowerMultiple", originMultiple, nextMultiple, elecTowerTotalBet,
                       elecTowerBetRadix, lotteryCoin, multipleCoin)
            if elecTowerTotalBet >= elecTowerBetRadix and lotteryCoin >= multipleCoin:
                poseidon_lottery_pool.incrElecTowerPool(-multipleCoin)
                return nextMultiple
        return originMultiple


    def updateTowerHistory(self):
        """
        更新魔塔记录
        """
        poseidon_lottery_pool.updateTowerHistory(self._multiples)

    def getCurrentStateStageTime(self):
        """
        获取当前状态开始结束时间
        """
        stateTime = {
            Tower.ST_CHARGE: self.chargeTime,
            Tower.ST_ATTACK: self.attackTime,
            Tower.ST_AWARD: self.awardTime,
            Tower.ST_FINAL: self.finalTime
        }
        return stateTime[self._state], stateTime[self._state + 1]

    def syncTowerState(self):
        """
        向渔场同步魔塔状态
        """
        for _, tableDict in self.room.allTableDict.iteritems():
            FTLoopTimer(0, 0, self._syncTowerState, tableDict).start()
            if ftlog.is_debug():
                ftlog.debug("syncTowerState->", tableDict)

    def _syncTowerState(self, tableDict):
        """
        向渔场同步魔塔状态
        """
        for table in tableDict.values():
            self.sendTowerStateMessage(table)

    def sendTowerStateMessage(self, table):
        """
        发送魔塔状态消息
        """
        msg = MsgPack()
        msg.setCmd("table_manage")
        msg.setParam("action", "tower_state")
        msg.setParam("gameId", table.gameId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("state", self._state)
        if self._state >= Tower.ST_ATTACK:
            msg.setParam("multiples", self._multiples)
        startTime, endTime = self.getCurrentStateStageTime()
        if startTime and endTime:
            msg.setParam("stageTime", [startTime, endTime])
            router.sendTableServer(msg, table.roomId)
        else:
            ftlog.error("sendTowerStateMessage->error", table.tableId, startTime, endTime)

    def startTowerTotalBetsTimer(self):
        """
        通知GT启动魔塔累计充能金币刷新定时器
        """
        for shadowRoomId, _ in self.room.allTableDict.iteritems():
            FTLoopTimer(0, 0, table_remote.startTowerTotalBetsTimer, shadowRoomId).start()

    def stopTowerTotalBetsTimer(self):
        """
        通知GT停止魔塔累计充能金币刷新定时器
        """
        for shadowRoomId, _ in self.room.allTableDict.iteritems():
            FTLoopTimer(0, 0, table_remote.stopTowerTotalBetsTimer, shadowRoomId).start()

    def reportServerProfitAndLoss(self):
        """
        上报服务器每轮魔塔盈亏
        """
        try:
            towerBets = self.room.getTowerTotalBets()
            towerRewards = [bet * multiple for bet, multiple in zip(towerBets, self._multiples)]
            towerNetIncome = sum(towerBets) - sum(towerRewards)
            data = towerBets + self._multiples + towerRewards
            bireport.reportGameEvent("BI_NFISH_GE_TOWER_SERVER", config.ROBOT_MAX_USER_ID, FISH_GAMEID, self.room.roomId,
                                     0, self.chargeTime, 0, 0, 0, data, config.CLIENTID_ROBOT, towerNetIncome)
        except:
            ftlog.error("reportServerProfitAndLoss error")
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import functools
import time
from datetime import datetime
from random import choice, randint
from collections import OrderedDict

import freetime.util.log as ftlog
from freetime.util.cron import FTCron
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
            self.allTableDict = {}
            self.initialized = False
            self.initializedRoomIds = set()
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
        """添加桌子"""
        self._allTableDict[table.tableId] = table
        self._usableTableList.append(table)
        ftlog.debug("_addTable->", self._allTableDict, self._usableTableList)

    def initializedGT(self, shadowRoomId, tableCount):
        """
        GT初始化完成
        """
        pass

    def initPoseidon(self):
        """
        初始化海皇
        """
        self.poseidon = Poseidon(self)
        self.poseidon.startHeart()

    def doQuickStart(self, msg):
        """
        Note:
            1> 由于不同游戏评分机制不同，例如德州会根据游戏阶段评分，所以把桌子评分存到redis里，方便各游戏服务器自由刷新。
            2> 为了防止同一张桌子同时被选出来分配座位，选桌时会把tableScore里选出的桌子删除，玩家坐下成功后再添加回去，添回去之前无需刷新该桌子的评分。
            3> 玩家自选桌时，可能选中一张正在分配座位的桌子，此时需要休眠后重试，只到该桌子完成分配或者等待超时。
        """
        pass

    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量
        """
        pass

    def _updateUsableTableList(self):
        pass

    def _triggerEnterTableEvent(self, event):
        """触发进入桌子事件"""
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            self._allPlayerDict[userId] = tableId
            ftlog.debug("_triggerEnterTableEvent", self._allPlayerDict)

    def _triggerLeaveTableEvent(self, event):
        """触发离开桌子事件"""
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            if userId in self._allPlayerDict:
                self._allPlayerDict.pop(userId)
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

    def stop(self):
        if self._state != Heartbeat.ST_STOP:
            self._state = Heartbeat.ST_STOP
            if self._timer:
                self._timer.cancel()
            self._timer = None

    @property
    def count(self):
        """执行队列函数的次数"""
        return self._count

    def postCall(self, func, *args, **kwargs):
        """添加处理函数"""
        self.postTask(functools.partial(func, *args, **kwargs))

    def postTask(self, task):
        """
        添加任务
        :param task: 任务
        """
        if self._state != Heartbeat.ST_STOP:
            self._postTaskList.append(task)
            if self._init and self._timer:
                self._timer.cancel()
                self._timer = FTLoopTimer(0, 0, self._onTimeout)
                self._timer.start()

    def _onInit(self):
        """初始化"""
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
        """定时计时器"""
        if self._state == Heartbeat.ST_START:
            interval = 0 if self._postTaskList else self._interval
            self._timer = FTLoopTimer(interval, 0, self._onTimeout)
            self._timer.start()

    def _processPostTaskList(self):
        """处理任务队列"""
        taskList = self._postTaskList
        self._postTaskList = []
        for task in taskList:
            try:
                task()
            except:
                ftlog.error("task=", task)


class HeartbeatAble(object):
    """心跳执行函数"""
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
        """多少秒数之后执行函数"""
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
        # FTLoopTimer(10, -1, self.syncPoseidonState).start()

    @property
    def state(self):
        return self._state


class Tower(HeartbeatAble):
    pass


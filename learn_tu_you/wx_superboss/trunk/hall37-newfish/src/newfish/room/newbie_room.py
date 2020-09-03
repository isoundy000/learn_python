#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

import traceback
from random import choice

from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util.keylock import KeyLock
from poker.entity.game.rooms.normal_room import TYNormalRoom
from newfish.entity import util
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote


class FishNewbieRoom(TYNormalRoom):
    """
    捕鱼新手房间
    """
    tableTaskIdDict = {
        0: [10001, 10002, 10003, 0],
        10001: [10001, 10002, 10003, 0],
        10002: [10001, 10002, 10003, 0],
        10003: [10001, 10002, 10003, 0],
        10004: [10004, 10005, 10006, 0],
        10005: [10004, 10005, 10006, 0],
        10006: [10004, 10005, 10006, 0],
        10007: [10004, 10005, 10006, 10007, 10008, 10009, 10010, 0],
        10008: [10005, 10006, 10007, 10008, 10009, 10010, 0],
        10009: [10006, 10007, 10008, 10009, 10010, 0],
        10010: [10007, 10008, 10009, 10010, 0]
    }

    def __init__(self, roomDefine):
        super(FishNewbieRoom, self).__init__(roomDefine)
        ftlog.debug("FishNewbieRoom->", gdata.serverType(), self.roomDefine.shadowRoomIds)
        self._keyLock = KeyLock()
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:    # GR进程
            self.shadowRoomIdOccupyList = [[shadowRoomId, 0, []] for shadowRoomId in self.roomDefine.shadowRoomIds]
            self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
            self.tableSeatDetails = {}
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:  # GT进程
            self._allTableDict = {}                     # tableId: table
            self._allPlayerDict = {}                    # userId: tableId
            self._allTableSeatDict = {}                 # tableId: set()
            self._usableTableDict = {}                  # taskId: [tableId, tableId1]
            FTLoopTimer(self.roomConf.get("occupyIntervalSeconds", 3), -1, self._reportRoomUserOccupy).start()
            from newfish.game import TGFish
            from newfish.entity.event import EnterTableEvent, LeaveTableEvent
            TGFish.getEventBus().subscribe(EnterTableEvent, self._triggerEnterTableEvent)
            TGFish.getEventBus().subscribe(LeaveTableEvent, self._triggerLeaveTableEvent)

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        ftlog.debug("newTable->", tableId)
        from newfish.table.newbie_table import FishNewbieTable
        table = FishNewbieTable(self, tableId)
        self._addTable(table)
        return table

    def _addTable(self, table):
        """添加桌子"""
        self._allTableDict[table.tableId] = table
        self._allTableSeatDict[table.tableId] = set()
        ftlog.debug("_addTable->", self._allTableDict, self._allTableSeatDict)

    def initializedGT(self, shadowRoomId, tableCount):
        pass

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
        extParams = msg.getKey("params")
        ftlog.hinfo("doQuickStart->", "userId =", userId, "clientId =", clientId, "roomId =", self.roomId,
                    "shadowRoomId =", shadowRoomId, "tableId =", tableId, "extParams =", extParams)

        if self.runStatus != self.ROOM_STATUS_RUN:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE, userId, clientId, self.roomId)
            return

        self.quickStartInGR(shadowRoomId, tableId, userId, clientId, extParams)

    def _choiceTableRoom(self, userId):
        """选择一个房间影子Id"""
        shadowRoomIdList = self.shadowRoomIdOccupyList
        ignoreShadowRoomList = self.roomConf.get("ignoreShadowRoomList", [])
        usebleShadowRoomIdList = [v[0] for v in shadowRoomIdList if v[0] not in ignoreShadowRoomList]
        choiceShadowRoomId = choice(usebleShadowRoomIdList[-2:])
        mainTaskId = util.getMainTaskId(userId, self.bigRoomId)                     # 获得用户主线任务ID
        occupyData = self.roomConf.get("occupyMax", [0.9])
        maxSeatN = self.roomConf.get("tableConf", {}).get("maxSeatN", 4)
        if not isinstance(occupyData, list):
            occupyData = [occupyData]
        occupy = occupyData[-1]
        for _oc in occupyData:
            isFind = True
            for index, shadowRoomOccupy in enumerate(shadowRoomIdList):
                if shadowRoomIdList[index][0] in ignoreShadowRoomList:
                    continue
                if shadowRoomOccupy[1] >= _oc:
                    continue
                if maxSeatN > 1 and shadowRoomOccupy[2]:
                    if mainTaskId not in shadowRoomOccupy[2]:
                        continue
                    # elif shadowRoomOccupy[2].count(mainTaskId) <= 1:
                    #     continue
                choiceShadowRoomId = shadowRoomIdList[index][0]
                break
            else:
                isFind = False
            if isFind:
                occupy = _oc
                break
        ftlog.info("FishNewbieRoom._choiceTableRoom",
                   "roomId=", self.roomId,
                   "userId=", userId,
                   "choiceShadowRoomId=", choiceShadowRoomId,
                   "shadowRoomIdList=", shadowRoomIdList,
                   "shadowRoomIdOccupyList=", self.shadowRoomIdOccupyList,
                   "occupyData =", occupyData,
                   "occupy =", occupy,
                   "usebleShadowRoomIdList =", usebleShadowRoomIdList,
                   "ignoreShadowRoomList =", ignoreShadowRoomList)
        return choiceShadowRoomId

    def quickStartInGR(self, shadowRoomId, tableId, userId, clientId, extParams):
        """快速进入房间"""
        try:
            if shadowRoomId is None:
                shadowRoomId = self._choiceTableRoom(userId)
            table_remote.quickStart(shadowRoomId, tableId, userId, clientId, extParams)                 # 快速进入桌子
        except Exception, e:
            ftlog.error("quickStartInGR error", userId, extParams, traceback.format_exc())
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def quickStartInGT(self, shadowRoomId, tableId, userId, clientId, extParams):
        """快速进入桌子"""
        isSitDown = self._trySitDown(shadowRoomId, tableId, userId, clientId, extParams)
        if not isSitDown:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def _trySitDown(self, shadowRoomId, tableId, userId, clientId, extParams):
        """尝试落座"""
        with self._keyLock.lock(userId):
            table = None
            for _ in xrange(3):
                try:
                    if userId in self._allPlayerDict:
                        tableId = self._allPlayerDict[userId]
                        table = self._allTableDict[tableId]
                    else:
                        if tableId == 0:
                            table = self.getBestTable(userId)
                            if not table:
                                mainTaskId = util.getMainTaskId(userId, self.bigRoomId)
                                ftlog.error("_trySitDown table not enough", shadowRoomId, tableId, userId, clientId,
                                            extParams, mainTaskId, self.tableTaskIdDict.get(mainTaskId),
                                            "useableTable =",
                                            dict([(taskId, [table.tableId for table in tables]) for taskId, tables in self._usableTableDict.iteritems()]),
                                            "tableScore =", {k: v.getTableScore() for k, v in self._allTableDict.iteritems()})
                        else:
                            assert isinstance(shadowRoomId, int) and gdata.roomIdDefineMap()[shadowRoomId].bigRoomId == self.bigRoomId
                            table = self._allTableDict[tableId]
                    if not table or table.processing:
                        continue
                    table.processing = True
                    msg = self.makeSitMsg(userId, shadowRoomId, tableId, clientId, extParams)
                    isOK = table.doSit(msg, userId, msg.getParam("seatId", 0), clientId)
                    if not isOK:
                        continue
                    return isOK
                except Exception, e:
                    ftlog.error("_trySitDown error", userId, shadowRoomId, tableId, clientId, extParams, traceback.format_exc())
                finally:
                    if table:
                        table.processing = False
                FTTasklet.getCurrentFTTasklet().sleepNb(0.2)
            return False

    def getBestTable(self, userId):
        """获取做好的桌子"""
        table = None
        self._updateUsableTableDict()
        if self._usableTableDict:
            maxSeatN = self.roomConf.get("tableConf", {}).get("maxSeatN", 4)
            if maxSeatN == 1:
                usableTableList = []
                for _, v in self._usableTableDict.iteritems():
                    usableTableList.extend(v)
                if usableTableList:
                    table = choice(usableTableList)
            else:
                mainTaskId = util.getMainTaskId(userId, self.bigRoomId)
                tableTaskIdRange = self.tableTaskIdDict[mainTaskId]
                for taskId in tableTaskIdRange:
                    usableTableList = self._usableTableDict.get(taskId)
                    if usableTableList:
                        table = choice(usableTableList)
                        break
        return table

    def makeSitMsg(self, userId, shadowRoomId, tableId, clientId, extParams):
        """生成坐下的消息"""
        mpSitReq = self.makeSitReq(userId, shadowRoomId, tableId, clientId)
        if extParams:
            moParams = mpSitReq.getKey("params")
            for k, v in extParams.items():
                if not k in moParams:
                    moParams[k] = v
        return mpSitReq

    def _updateUsableTableDict(self):
        """更新可用的桌子字典"""
        self._usableTableDict = {}
        for _, table in self._allTableDict.iteritems():
            # if 0 < table.getTableScore() < 100:
            # 使用单人房间.
            if 0 < table.getTableScore() <= 100:
                self._usableTableDict.setdefault(table.getTableMinMainTaskId(), []).append(table)   # {taskId: [tableId、tableId1]}
        if ftlog.is_debug():
            ftlog.debug("FishNewbieRoom._updateUsableTableDict", "_usableTableDict=",
                        dict([(taskId, [table.tableId for table in tables]) for taskId, tables in self._usableTableDict.iteritems()]))

    def roomUserOccupy(self, shadowRoomId, roomOccupy, extData=None):
        """房间玩家的容量"""
        for shadowRoomOccupy in self.shadowRoomIdOccupyList:
            if shadowRoomOccupy[0] == int(shadowRoomId):
                shadowRoomOccupy[1] = roomOccupy
                shadowRoomOccupy[2] = extData
        ftlog.debug("FishNewbieRoom.roomUserOccupy",
                    "roomId=", self.roomId,
                    "shadowRoomId=", shadowRoomId,
                    "roomOccupy=", roomOccupy,
                    "extData=", extData,
                    "shadowRoomIdOccupyList=", self.shadowRoomIdOccupyList)
        return True

    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量
        """
        if not self.roomConf.get("occupySwitch", 1) or self.runStatus != self.ROOM_STATUS_RUN:
            return
        playerCount = len(self._allPlayerDict)
        tableCount = len(self._allTableDict)
        tableSeatCount = self.tableConf["maxSeatN"]
        totalCount = tableSeatCount * tableCount
        occupy = round(playerCount * 1.0 / (totalCount or 1), 3)
        ftlog.debug("FishNewbieRoom._processRoomUserOccupy",
                    "roomId=", self.roomId,
                    "playerCount=", playerCount,
                    "tableCount=", tableCount,
                    "tableSeatCount=", tableSeatCount,
                    "totalCount=", totalCount,
                    "roomUserOccupy=", occupy,
                    "usableTableDict=", self._usableTableDict,
                    "ctrlRoomId=", self.ctrlRoomId)
        room_remote.reportRoomUserOccupy(self.ctrlRoomId, self.roomId, occupy, self._usableTableDict.keys())

    def _triggerEnterTableEvent(self, event):
        """触发进入桌子事件"""
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            self._allPlayerDict[userId] = tableId
            self._allTableSeatDict[tableId].add(userId)
            ftlog.debug("_triggerEnterTableEvent", self._allPlayerDict)
        import time
        from poker.util import strutil
        from newfish.entity.task.task_system_user import RedState
        from newfish.entity.config import FISH_GAMEID
        from newfish.entity.redis_keys import GameData
        newbie7DayGiftData = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.newbie7DayGiftData)     # 新手7日礼包数据
        if isinstance(newbie7DayGiftData, list) and len(newbie7DayGiftData) == 2:
            return
        redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)                          # 新手任务状态
        if redState < RedState.Complete:
            gamedata.setGameAttr(userId, FISH_GAMEID, GameData.newbie7DayGiftData,
                                 strutil.dumps([util.getDayStartTimestamp(int(time.time())), []]))

    def _triggerLeaveTableEvent(self, event):
        """触发离开桌子的事件"""
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            if userId in self._allPlayerDict:
                self._allPlayerDict.pop(userId)
                self._allTableSeatDict[tableId].discard(userId)
            ftlog.debug("_triggerLeaveTableEvent", self._allPlayerDict)
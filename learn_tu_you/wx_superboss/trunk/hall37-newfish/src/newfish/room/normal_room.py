# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/6/21.
"""

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
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote


class FishNormalRoom(TYNormalRoom):
    """
    捕鱼普通房间
    """
    def __init__(self, roomDefine):
        super(FishNormalRoom, self).__init__(roomDefine)
        self._keyLock = KeyLock()
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:       # 当前进程的类型   'GR' # 服务类型: 游戏的房间服务
            self.shadowRoomIdOccupyList = [[shadowRoomId, 0] for shadowRoomId in self.roomDefine.shadowRoomIds]
            self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:      # GT进程
            self._allTableDict = {}                         # 所有桌子的字典 {桌子Id: 桌子对象}
            self._allPlayerDict = {}                        # {userId: tableId}
            self._usableTableList = []                      # 所有可用的桌子对象
            FTLoopTimer(self.roomConf.get("occupyIntervalSeconds", 3), -1, self._reportRoomUserOccupy).start()
            from newfish.game import TGFish
            from newfish.entity.event import EnterTableEvent, LeaveTableEvent
            TGFish.getEventBus().subscribe(EnterTableEvent, self._triggerEnterTableEvent)
            TGFish.getEventBus().subscribe(LeaveTableEvent, self._triggerLeaveTableEvent)

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.normal_table import FishNormalTable
        table = FishNormalTable(self, tableId)
        self._addTable(table)
        return table

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
        shadowRoomId = msg.getParam("shadowRoomId")     # 房间Id
        tableId = msg.getParam("tableId")               # 桌子Id
        clientId = msg.getParam("clientId")
        extParams = msg.getKey("params")
        ftlog.hinfo("doQuickStart->", "userId =", userId, "clientId =", clientId, "roomId =", self.roomId,
                    "shadowRoomId =", shadowRoomId, "tableId =", tableId, "extParams =", extParams)

        if self.runStatus != self.ROOM_STATUS_RUN:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE, userId, clientId, self.roomId)
            return
        self.quickStartInGR(shadowRoomId, tableId, userId, clientId, extParams)

    def _addTable(self, table):
        """添加桌子"""
        self._allTableDict[table.tableId] = table
        self._usableTableList.append(table)
        ftlog.debug("_addTable->", self._allTableDict, self._usableTableList)

    def _choiceTableRoom(self, userId):
        """选择一个房间ID"""
        level = util.getLevelByGunLevel(userId)
        shadowRoomIdList = self.shadowRoomIdOccupyList
        if level <= 5:
            shadowRoomIdList = self.shadowRoomIdOccupyList[::-1]
        choiceShadowRoomId = shadowRoomIdList[-1][0]
        for index, shadowRoomOccupy in enumerate(shadowRoomIdList):
            if shadowRoomOccupy[1] >= self.roomConf.get("occupyMax", 0.95):
                continue
            choiceShadowRoomId = shadowRoomIdList[index][0]
            break
        ftlog.debug("FishNormalRoom._choiceTableRoom", "roomId=", self.roomId, "userId=", userId,
                    "choiceShadowRoomId=", choiceShadowRoomId, "shadowRoomIdList=", shadowRoomIdList,
                    "shadowRoomIdOccupyList=", self.shadowRoomIdOccupyList)
        return choiceShadowRoomId

    def quickStartInGR(self, shadowRoomId, tableId, userId, clientId, extParams):
        """快速进入GR"""
        try:
            if shadowRoomId is None:
                shadowRoomId = self._choiceTableRoom(userId)
            table_remote.quickStart(shadowRoomId, tableId, userId, clientId, extParams)
        except Exception, e:
            ftlog.error("quickStartInGR error", userId, extParams, traceback.format_exc())
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def quickStartInGT(self, shadowRoomId, tableId, userId, clientId, extParams):
        """快速进入GT"""
        isSitDown = self._trySitDown(shadowRoomId, tableId, userId, clientId, extParams)
        if not isSitDown:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def _trySitDown(self, shadowRoomId, tableId, userId, clientId, extParams):
        """尝试坐下"""
        with self._keyLock.lock(userId):
            table = None
            for _ in xrange(3):
                try:
                    if userId in self._allPlayerDict:
                        tableId = self._allPlayerDict[userId]
                    if tableId == 0:
                        self._updateUsableTableList()
                        if not self._usableTableList:
                            continue
                        table = choice(self._usableTableList)
                    else:
                        assert isinstance(shadowRoomId, int) and gdata.roomIdDefineMap()[shadowRoomId].bigRoomId == self.bigRoomId
                        table = self._allTableDict[tableId]
                    if table.processing or table.getTableScore() == 0:
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

    def makeSitMsg(self, userId, shadowRoomId, tableId, clientId, extParams):
        """生成坐下请求的参数"""
        mpSitReq = self.makeSitReq(userId, shadowRoomId, tableId, clientId)
        if extParams:
            moParams = mpSitReq.getKey("params")
            for k, v in extParams.items():
                if not k in moParams:
                    moParams[k] = v
        return mpSitReq

    def roomUserOccupy(self, shadowRoomId, roomOccupy, extData=None):

        for shadowRoomOccupy in self.shadowRoomIdOccupyList:
            if shadowRoomOccupy[0] == int(shadowRoomId):
                shadowRoomOccupy[1] = roomOccupy
        ftlog.debug("FishNormalRoom.roomUserOccupy",
                    "roomId=", self.roomId,
                    "shadowRoomId=", shadowRoomId,
                    "roomOccupy=", roomOccupy,
                    "shadowRoomIdOccupyList=", self.shadowRoomIdOccupyList)
        return True

    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量 occupy空间、面积
        """
        if not self.roomConf.get("occupySwitch", 1) or self.runStatus != self.ROOM_STATUS_RUN:
            return
        playerCount = len(self._allPlayerDict)
        tableCount = len(self._allTableDict)
        tableSeatCount = self.tableConf["maxSeatN"]
        totalCount = tableSeatCount * tableCount
        occupy = round(playerCount * 1.0 / (totalCount or 1), 3)
        ftlog.debug("FishNormalRoom._processRoomUserOccupy",
                    "roomId=", self.roomId,
                    "playerCount=", playerCount,
                    "tableCount=", tableCount,
                    "tableSeatCount=", tableSeatCount,
                    "totalCount=", totalCount,
                    "roomUserOccupy=", occupy)
        room_remote.reportRoomUserOccupy(self.ctrlRoomId, self.roomId, occupy)

    def _updateUsableTableList(self):
        """更新可用桌子列表"""
        nobodyTableList = []        # 无玩家的桌子
        somebodyTableList = []      # 有人的桌子
        for _, table in self._allTableDict.iteritems():
            tableScore = table.getTableScore()
            defaultScore = 100 / table.maxSeatN
            if tableScore == defaultScore:
                nobodyTableList.append(table)
            elif tableScore > defaultScore:
                somebodyTableList.append(table)
        if nobodyTableList:
            somebodyTableList.append(choice(nobodyTableList))
        self._usableTableList = somebodyTableList
        if ftlog.is_debug():
            ftlog.debug("FishNormalRoom._updateUsableTableList",
                        "nobodyTableList=", [table.tableId for table in nobodyTableList],
                        "_usableTableList=", [table.tableId for table in self._usableTableList])

    def _triggerEnterTableEvent(self, event):
        """
        触发进入房间事件
        """
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            self._allPlayerDict[userId] = tableId
            ftlog.debug("_triggerEnterTableEvent", self._allPlayerDict)

    def _triggerLeaveTableEvent(self, event):
        """
        触发离开桌子的事件
        """
        tableId = event.tableId
        userId = event.userId
        if tableId in self._allTableDict:
            if userId in self._allPlayerDict:
                self._allPlayerDict.pop(userId)
            ftlog.debug("_triggerLeaveTableEvent", self._allPlayerDict)
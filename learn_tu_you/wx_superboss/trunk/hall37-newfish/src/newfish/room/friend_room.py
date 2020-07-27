# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/5/11.
"""

import time
import traceback
from random import choice

from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util.keylock import KeyLock
from poker.entity.game.rooms.normal_room import TYNormalRoom
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote


class FishFriendRoom(TYNormalRoom):
    """
    捕鱼好友模式房间
    """
    def __init__(self, roomDefine):
        super(FishFriendRoom, self).__init__(roomDefine)
        self._keyLock = KeyLock()
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:   # GR进程
            self.shadowRoomIdOccupyList = [[shadowRoomId, 0] for shadowRoomId in self.roomDefine.shadowRoomIds]
            self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:  # GT进程
            self._allTableDict = {}                     # tableId: table
            self._allPlayerDict = {}                    # uid: tableId
            self._usableTableList = []                  # 可用的桌子集合
            FTLoopTimer(self.roomConf.get("occupyIntervalSeconds", 3), -1, self._reportRoomUserOccupy).start()
            from newfish.game import TGFish
            from newfish.entity.event import EnterTableEvent, LeaveTableEvent
            TGFish.getEventBus().subscribe(EnterTableEvent, self._triggerEnterTableEvent)
            TGFish.getEventBus().subscribe(LeaveTableEvent, self._triggerLeaveTableEvent)

    def initializedGT(self, shadowRoomId, tableCount):
        pass

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.friend_table import FishFriendTable
        table = FishFriendTable(self, tableId)
        table.matchingTime = 0
        self._addTable(table)
        return table

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
        ftlog.hinfo("doQuickStart->",
                    "userId =", userId, "clientId =", clientId, "roomId =", self.roomId,
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
        """选择影子桌子房间Id"""
        shadowRoomIdList = self.shadowRoomIdOccupyList
        ignoreShadowRoomList = self.roomConf.get("ignoreShadowRoomList", [])
        usebleShadowRoomIdList = [v[0] for v in shadowRoomIdList if v[0] not in ignoreShadowRoomList]
        choiceShadowRoomId = usebleShadowRoomIdList[-1]
        occupyData = self.roomConf.get("occupyMax", [0.9])
        if not isinstance(occupyData, list):
            occupyData = [occupyData]
        occupy = occupyData[-1]
        for _oc in occupyData:
            isFind = True
            for index, shadowRoomOccupy in enumerate(shadowRoomIdList):     # 房间进程使用的空间
                if shadowRoomIdList[index][0] in ignoreShadowRoomList:
                    continue
                if shadowRoomOccupy[1] >= _oc:
                    continue
                choiceShadowRoomId = shadowRoomIdList[index][0]
                break
            else:
                isFind = False
            if isFind:
                occupy = _oc
                break
        ftlog.info("FishFriendRoom._choiceTableRoom",
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
        """
        快速进入房间进程
        :param shadowRoomId: 影子房间Id
        :param tableId: 桌子Id
        :param userId: 玩家Id
        :param clientId: 客户端
        :param extParams: 扩展参数
        """
        try:
            if shadowRoomId is None:
                shadowRoomId = self._choiceTableRoom(userId)
            table_remote.quickStart(shadowRoomId, tableId, userId, clientId, extParams)             # 访问桌子进程
        except Exception, e:
            ftlog.error("quickStartInGR error", userId, extParams, traceback.format_exc())
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def quickStartInGT(self, shadowRoomId, tableId, userId, clientId, extParams):
        """快速进入桌子GT进程"""
        isSitDown = self._trySitDown(shadowRoomId, tableId, userId, clientId, extParams)
        if not isSitDown:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_INNER_ERROR, userId, clientId, self.roomId)

    def _trySitDown(self, shadowRoomId, tableId, userId, clientId, extParams):
        """尝试坐下 桌子的位置"""
        with self._keyLock.lock(userId):
            table = None
            for _ in xrange(3):
                try:
                    if userId in self._allPlayerDict:
                        tableId = self._allPlayerDict[userId]
                    if tableId == 0:                                    # 系统帮忙选桌子
                        self._updateUsableTableList()
                        if not self._usableTableList:
                            continue
                        table = choice(self._usableTableList)           # 选择一个桌子
                    else:
                        assert isinstance(shadowRoomId, int) and gdata.roomIdDefineMap()[shadowRoomId].bigRoomId == self.bigRoomId
                        table = self._allTableDict[tableId]             # 自己进入固定的桌子 所有桌子
                    if table.getTableScore() == 0:                      # 桌子积分为0 系统重新选桌子
                        self._updateUsableTableList()
                        if not self._usableTableList:
                            continue
                        table = choice(self._usableTableList)
                    if table.processing:                                # 桌子处理中
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
        """生成落座的消息"""
        mpSitReq = self.makeSitReq(userId, shadowRoomId, tableId, clientId)         # 调用父类的方法
        if extParams:
            moParams = mpSitReq.getKey("params")
            for k, v in extParams.items():
                if not k in moParams:
                    moParams[k] = v
        return mpSitReq

    def roomUserOccupy(self, shadowRoomId, roomOccupy, extData=None):
        """房间占用空间"""
        for shadowRoomOccupy in self.shadowRoomIdOccupyList:
            if shadowRoomOccupy[0] == int(shadowRoomId):
                shadowRoomOccupy[1] = roomOccupy
        ftlog.debug("FishFriendRoom.roomUserOccupy",
                    "roomId=", self.roomId,
                    "shadowRoomId=", shadowRoomId,
                    "roomOccupy=", roomOccupy,
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
        ftlog.debug("FishFriendRoom._processRoomUserOccupy",
                    "roomId=", self.roomId,
                    "playerCount=", playerCount,
                    "tableCount=", tableCount,
                    "tableSeatCount=", tableSeatCount,
                    "totalCount=", totalCount,
                    "roomUserOccupy=", occupy)
        room_remote.reportRoomUserOccupy(self.ctrlRoomId, self.roomId, occupy)

    def _updateUsableTableList(self):
        """
        分桌匹配算法
        """
        nobodyTableList = []    # 无人桌
        somebodyTableList = []  # 空闲桌
        for _, table in self._allTableDict.iteritems():
            tableScore = table.getTableScore()
            defaultScore = 100 / table.maxSeatN
            if tableScore == defaultScore:
                nobodyTableList.append(table)
            elif (tableScore > defaultScore and time.time() - table.matchingTime > self.roomConf.get("matchingIntervalTime", 30)):  # 匹配间隔事件
                somebodyTableList.append(table)
        matchingType = self.roomConf.get("matchingType", 1)     # 匹配类型
        ftlog.debug("_updateUsableTableList->", matchingType)
        if matchingType == 1:       # 始终加入一个空桌
            if nobodyTableList:
                somebodyTableList.append(choice(nobodyTableList))
        elif matchingType == 2:     # 空闲桌数不足总人数一半(向上取整)时，加入一个空桌
            needTableCount = int((len(self._allPlayerDict) + 2) / 2)
            if len(somebodyTableList) < needTableCount and nobodyTableList:
                somebodyTableList.append(choice(nobodyTableList))
            ftlog.debug("_updateUsableTableList->", matchingType, needTableCount, len(somebodyTableList))
        # 通过分配算法依旧无空闲桌子时，加入一个空桌
        if not somebodyTableList and nobodyTableList:
            somebodyTableList.append(choice(nobodyTableList))
        self._usableTableList = somebodyTableList
        if ftlog.is_debug():
            ftlog.debug("FishNormalRoom._updateUsableTableList",
                        "nobodyTableList=", [table.tableId for table in nobodyTableList],
                        "_usableTableList=", [table.tableId for table in self._usableTableList])

    def _triggerEnterTableEvent(self, event):
        """进入桌子事件"""
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
            table = self._allTableDict[tableId]
            if table.playersNum == 3:
                table.matchingTime = time.time()
            elif table.playersNum < 3:
                table.matchingTime = 0
            ftlog.debug("_triggerLeaveTableEvent", self._allPlayerDict)
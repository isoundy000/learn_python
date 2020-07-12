#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11

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
        if gdata.serverType() == gdata.SRV_TYPE_ROOM:
            self.shadowRoomIdOccupyList = [[shadowRoomId, 0] for shadowRoomId in self.roomDefine.shadowRoomIds]
            self.shadowRoomIdOccupyList.sort(key=lambda x: x[0])
        if gdata.serverType() == gdata.SRV_TYPE_TABLE:  # GT进程
            self._allTableDict = {}
            self._allPlayerDict = {}
            self._usableTableList = []
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
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE, userId, clientId,
                                              self.roomId)
            return
        self.quickStartInGR(shadowRoomId, tableId, userId, clientId, extParams)

    def _addTable(self, table):
        self._allTableDict[table.tableId] = table
        self._usableTableList.append(table)
        ftlog.debug("_addTable->", self._allTableDict, self._usableTableList)
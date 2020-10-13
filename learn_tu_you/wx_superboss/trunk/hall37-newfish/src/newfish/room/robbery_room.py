# -*- coding=utf-8 -*-
"""
Created by lichen on 2018/1/9.
"""

from random import choice
from collections import OrderedDict

import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.game.rooms.normal_room import TYNormalRoom
from hall.entity import hallvip
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quick_start import FishQuickStart


class FishRobberyRoom(TYNormalRoom):
    """
    捕鱼招财模式房间
    """
    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.robbery_table import FishRobberyTable
        table = FishRobberyTable(self, tableId)
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
        shadowRoomId = msg.getParam("shadowRoomId")
        tableId = msg.getParam("tableId")
        clientId = msg.getParam("clientId")
        ftlog.hinfo(getMethodName(), "->|userId, clientId, roomId, shadowRoomId, tableId:", userId, clientId, self.roomId, shadowRoomId, tableId)

        if self.runStatus != self.ROOM_STATUS_RUN:
            FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_MAINTENANCE, userId, clientId, self.roomId)
            return
        if tableId == 0:  # 服务器为玩家选择桌子并坐下
            _, _, details = bireport.getRoomOnLineUserCount(FISH_GAMEID, True)
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
                if details.get(str(roomId)) < int(tableCount * maxSeatN * 0.9):
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

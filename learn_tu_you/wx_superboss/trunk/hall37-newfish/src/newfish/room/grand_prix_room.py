# -*- coding=utf-8 -*-
"""
大奖赛房间逻辑
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/10/08

import time
from random import choice

from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util.keylock import KeyLock
from poker.entity.game.rooms.normal_room import TYNormalRoom
from newfish.room.friend_room import FishFriendRoom
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote


class FishGrandPrixRoom(FishFriendRoom):
    """
    大奖赛模式房间
    """
    def __init__(self, roomDefine):
        super(FishGrandPrixRoom, self).__init__(roomDefine)

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.grand_prix_table import FishGrandPrixTable
        table = FishGrandPrixTable(self, tableId)
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
        super(FishGrandPrixRoom, self).doQuickStart(msg)

    def _addTable(self, table):
        super(FishGrandPrixRoom, self)._addTable(table)

    def _choiceTableRoom(self, userId):
        return super(FishGrandPrixRoom, self)._choiceTableRoom(userId)

    def quickStartInGR(self, shadowRoomId, tableId, userId, clientId, extParams):
        super(FishGrandPrixRoom, self).quickStartInGR(shadowRoomId, tableId, userId, clientId, extParams)

    def quickStartInGT(self, shadowRoomId, tableId, userId, clientId, extParams):
        super(FishGrandPrixRoom, self).quickStartInGT(shadowRoomId, tableId, userId, clientId, extParams)

    def _trySitDown(self, shadowRoomId, tableId, userId, clientId, extParams):
        return super(FishGrandPrixRoom, self)._trySitDown(shadowRoomId, tableId, userId, clientId, extParams)

    def makeSitMsg(self, userId, shadowRoomId, tableId, clientId, extParams):
        return super(FishGrandPrixRoom, self).makeSitMsg(userId, shadowRoomId, tableId, clientId, extParams)

    def roomUserOccupy(self, shadowRoomId, roomOccupy, extData=None):
        return super(FishGrandPrixRoom, self).roomUserOccupy(shadowRoomId, roomOccupy, extData)

    def _reportRoomUserOccupy(self):
        """
        向GR汇报当前GT容量
        """
        super(FishGrandPrixRoom, self)._reportRoomUserOccupy()

    def _updateUsableTableList(self):
        """
        分桌匹配算法
        """
        super(FishGrandPrixRoom, self)._updateUsableTableList()

    def _triggerEnterTableEvent(self, event):
        """
        玩家加入桌子
        """
        super(FishGrandPrixRoom, self)._triggerEnterTableEvent(event)

    def _triggerLeaveTableEvent(self, event):
        """
        玩家离开桌子
        """
        super(FishGrandPrixRoom, self)._triggerLeaveTableEvent(event)
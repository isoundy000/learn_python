#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

from poker.entity.dao import daoconst
from poker.servers.util.direct import dbuser, dbonline, dbgeo
from poker.entity.configure import gdata

OFFLINE = daoconst.OFFLINE  # 用户不在线
ONLINE = daoconst.ONLINE  # 用户在线


def addOnlineLoc(userId, roomId, tableId, seatId, checkConfict=True):
    '''
    添加一个用户的在线位置,
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    通常此方法在用户真实坐在某一个桌位后调用
    '''
    assert (isinstance(roomId, int) and roomId > 0)
    assert (roomId in gdata.roomIdDefineMap() or roomId in gdata.bigRoomidsMap())
    assert (isinstance(tableId, int) and tableId > roomId)
    assert (isinstance(seatId, int) and seatId > 0)
    return dbuser._addOnlineLoc(userId, roomId, tableId, seatId, checkConfict)


def getOnlineLocSeatId(userId, roomId, tableId):
    '''
    添加一个用户的在线位置,
    注意: 子键值为roomId+'.'+tableId, 因此不允许用户再同一个桌子的不同桌位坐下
    通常此方法在用户真实坐在某一个桌位后调用
    '''
    assert (isinstance(roomId, int) and roomId > 0)
    assert (isinstance(tableId, int) and tableId > 0)
    return dbuser._getOnlineLocSeatId(userId, roomId, tableId)


def getOnlineLocList(userId):
    '''
    取得当前用户的所有在线位置信息list
    返回loc的数组列表, 每一项为一个3项值, 分别为: roomId, tableId, seatId
    示例 :
        return [
                [roomId1, tableId1, seatId1],
                [roomId2, tableId2, seatId2],
                ]
    '''
    return dbuser._getOnlineLocList(userId)


def checkUserLoc(userId, clientId, matchGameId=0):
    '''Why：
           玩家断线重连时，loc的信息可能与table不一致，conn server需要与table server通讯检查一致性；
           导致不一致的原因：服务端重启（特别是roomId、tableId变更）
           如果玩家在队列房间或者比赛房间的等待队列中, 此处不做一致性检查，等玩家发起quick_start时由room server检查
       What：
           与table server通讯检查桌子对象里是否有这个玩家的数据
           如果不一致，则回收牌桌金币并清空loc；
       Return：
           如果玩家在房间队列里，返回gameId.roomId.roomId*10000.1
           如果玩家在座位上，返回gameId.roomId.tableId.seatId
           如果玩家在旁观，返回gameId.roomId.tableId.0
           玩家不在table对象里，返回0.0.0.0
    '''
    return dbuser._checkUserLoc(userId, clientId, matchGameId)


def removeOnlineLoc(userId, roomId, tableId):
    '''
    移除一个用户的在线位置
    通常此方法在用户真实离开某一个桌位后调用
    '''
    assert (isinstance(roomId, int) and roomId > 0)
    assert (isinstance(tableId, int) and tableId > 0)
    return dbuser._removeOnlineLoc(userId, roomId, tableId)



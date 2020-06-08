#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

from poker.entity.dao import daoconst
from poker.servers.util.direct import dbuser, dbonline, dbgeo
from poker.entity.configure import gdata

OFFLINE = daoconst.OFFLINE  # 用户不在线
ONLINE = daoconst.ONLINE  # 用户在线


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
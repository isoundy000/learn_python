#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

from poker.entity.dao import daobase, daoconst
from poker.entity.dao.daoconst import UserDataSchema, UserSessionSchema, UserLocationSchema



def _getOnlineLocList(userId):
    '''
    取得当前用户的所有在线位置信息list
    返回loc的数组列表, 每一项为一个3项值, 分别为: roomId, tableId, seatId
    示例 :
        return [
                [roomId1, tableId1, seatId1],
                [roomId2, tableId2, seatId2],
                ]
    '''
    loclist = []
    val = daobase.executeUserCmd(userId, 'HGETALL', UserLocationSchema.mkey(userId))


def _removeOnlineLoc(userId, roomId, tableId):
    '''
    移除一个用户的在线位置
    通常此方法在用户真实离开某一个桌位后调用
    '''
    # 游戏时长计算, 1天后自动过期
    subkey = 'R.' + str(roomId) + '.' + str(tableId)
    if ftlog.is_debug():
        ftlog.debug('dbuser._removeOnlineLoc userId=', userId,
                    'roomId=', roomId,
                    'tableId=', tableId)
    daobase.sendUserCmd(userId, 'HDEL', UserLocationSchema.mkey(userId), subkey)
    dbplaytime._setPlayTimeStop(userId, roomId, tableId)
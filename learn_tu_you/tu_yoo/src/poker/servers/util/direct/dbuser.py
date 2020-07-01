#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import json

import freetime.util.log as ftlog
from poker.entity.configure import pokerconf, gdata
from poker.entity.dao import daobase, daoconst
from poker.entity.dao.daoconst import UserDataSchema, UserSessionSchema, \
    UserLocationSchema, UserWeakSchema, UserOnlineGameSchema
from poker.servers.rpc import roommgr
from poker.servers.util.rpc._private import dataswap, user_scripts
from poker.util import strutil, timestamp
from poker.servers.util.direct import dbonline, dbplaytime


def _checkUserData(userId, clientId=None, appId=0, session={}):
    ret = dataswap.checkUserData(userId, clientId, appId)
    if ret and session:
        _setSessionDatas(userId, session)
    return ret


def _getWeakData(userId, gameId, weakname, cycleName, curCycle):
    """
    获取弱数据 每日、每周、每月、本月剩余时间
    :param userId: 玩家uid
    :param gameId: 游戏Id
    :param weakname: 获取数据key
    :param cycleName: day、     week、   mothon
    :param curCycle:  200630    2002    2006
    :return:
    """
    dataKey = UserWeakSchema.mkey(cycleName, weakname, gameId, userId)
    jsonstr = daobase.executeUserCmd(userId, 'GET', dataKey)
    data = strutil.loads(jsonstr, ignoreException=True, execptionValue={})
    if not isinstance(data, dict):
        data = {}
    oldCycle = data.get('_cycle_', 0)
    if oldCycle != curCycle:
        data = {'_cycle_': curCycle}
    return data


def _setWeakData(userId, gameId, weakname, datas, cycleName, curCycle, expire):
    """
    设置弱数据信息
    :param userId: 玩家Id
    :param gameId: 游戏Id
    :param weakname: 设置数据key
    :param datas: 数据
    :param cycleName: day、     week、   mothon
    :param curCycle: 200630    2002    2006
    :param expire: 游戏期时长
    :return:
    """
    dataKey = UserWeakSchema.mkey(cycleName, weakname, gameId, userId)
    if datas:
        datas['_cycle_'] = curCycle
    if datas:
        ret = daobase.sendUserCmd(userId, 'SETEX', dataKey, expire, strutil.dumps(datas))
    else:
        ret = daobase.sendUserCmd(userId, 'DEL', dataKey)
    return ret


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


def _checkUserLoc(userId, clientId, matchGameId=0):
    return '0.0.0.0'


def _getUserDatas(userId, fieldList):
    dataKey = UserDataSchema.mkey(userId)
    values = daobase.executeUserCmd(userId, 'HMGET', dataKey, *fieldList)
    values = UserDataSchema.checkDataList(fieldList, values, None)
    ftlog.debug('_getUserDatas->', userId, fieldList, values)
    return values


def _getSessionDatas(userId):
    """
    获取Session数据
    """
    dataKey = UserSessionSchema.mkey(userId)
    return _cacheSession(userId, dataKey)
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/5

from poker.entity.dao import daoconst, daobase
from poker.util import strutil
from poker.servers.util.rpc._private import user_scripts
from poker.servers.util.direct import dbplaytime


def getGameAttrs(uid, gameid, attrlist, filterKeywords=False):
    """
    获取用户游戏属性列表 多个域
    """
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    values = daobase.executeUserCmd(uid, 'HMGET', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), *attrlist)
    if values and filterKeywords:
        return daobase.filterValues(attrlist, values)
    return values


def setGameAttrs(uid, gameid, attrlist, valuelist):
    '''
    设置用户游戏属性列表
    '''
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    gdkv = []
    for k, v in zip(attrlist, valuelist):
        gdkv.append(k)
        gdkv.append(v)
        assert (k not in daoconst.FILTER_KEYWORD_FIELDS)
    return daobase.executeUserCmd(uid, 'HMSET', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), *gdkv)


def delGameAttr(uid, gameid, attrname):
    """删除一个域"""
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HDEL', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname)


def delGameAttrs(uid, gameid, attrlist):
    """删除一堆域"""
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HDEL', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), *attrlist)


def getGameAttr(uid, gameid, attrname, filterKeywords=False):
    '''
    获取用户单个域游戏属性
    '''
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = daobase.executeUserCmd(uid, 'HGET', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname)
    if value and filterKeywords:
        return daobase.filterValue(attrname, value)
    return value


def getAllAttrs(uid, gameid, key):
    """获取玩家游戏数据指定key和指定游戏和用户 所有域和值"""
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HGETALL', '%s:%s:%s' % (key, gameid, uid))


def getGameAttrJson(uid, gameid, attrname, defaultVal=None):
    """
    获取用户游戏属性
    """
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = getGameAttr(uid, gameid, attrname)
    value = strutil.loads(value, False, True, defaultVal)
    return value


def setGameAttr(uid, gameid, attrname, value):
    '''
    设置用户游戏属性 单个域和值 {}, json.dumps()
    '''
    assert (isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    assert (attrname not in daoconst.FILTER_MUST_FUNC_FIELDS)
    return daobase.executeUserCmd(uid, 'HSET', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname, value)


def getGameAttrInt(uid, gameid, attrname):
    """获取单个域的值 值是int类型"""
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    value = getGameAttr(uid, gameid, attrname)
    if not isinstance(value, (int, float)):
        return 0
    return int(value)


def setnxGameAttr(uid, gameid, attrname, value):
    """设置单个域的值，如果不存在这个key就保存成功，否则保存不上"""
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'HSETNX', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname, value)


def incrGameAttr(uid, gameid, attrname, value):
    '''
    INCR用户游戏属性
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    assert(attrname not in daoconst.FILTER_MUST_FUNC_FIELDS)
    return daobase.executeUserCmd(uid, 'HINCRBY', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname, value)


def incrGameAttrLimit(uid, gameid, attrname, deltaCount, lowLimit, highLimit, chipNotEnoughOpMode):
    '''
    INCR用户游戏属性 执行lua命令
    参考: incr_chip_limit
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    assert(attrname not in daoconst.FILTER_MUST_FUNC_FIELDS)
    trueDetal, finalCount, fixCount = daobase.executeUserLua(uid, user_scripts.MAIN_INCR_CHIP_LUA_SCRIPT,
                                            6, deltaCount, lowLimit, highLimit,
                                            chipNotEnoughOpMode,
                                            daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid), attrname)
    return trueDetal, finalCount, fixCount


def isGameExists(uid, gameid):
    '''
    判定当前的游戏数据是否存在
    '''
    assert(isinstance(gameid, int) and gameid > 0), 'gameid must be int'
    return daobase.executeUserCmd(uid, 'EXISTS', daoconst.HKEY_GAMEDATA + str(gameid) + ':' + str(uid))


def incrPlayTime(userId, detalTime, gameId, roomId=-1, tableId=-1):
    """增加玩家游戏时长"""
    dbplaytime._incrPlayTime(userId, detalTime, gameId, roomId, tableId)
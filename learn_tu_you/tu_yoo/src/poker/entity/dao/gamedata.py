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
    获取用户游戏属性列表
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
    pass
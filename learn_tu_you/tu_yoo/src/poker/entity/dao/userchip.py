#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import daoconst, daobase, userdata, gamedata
from poker.servers.util.direct import dbuser


def getChip(uid):
    """获取金币"""
    return userdata.getAttr(uid, daoconst.ATT_CHIP)


def getTableChip(uid, gameid, tableId):
    '''
    取得用户的table_chip
    返回:
        否则返回gamedata中的tablechip
    '''
    mkey = daoconst.HKEY_TABLECHIP + str(uid)
    mfield = str(tableId)
    value = daobase.executeUserCmd(uid, 'HGET', mkey, mfield)
    ftlog.debug('UserChip->get_table_chip', uid, gameid, tableId, 'result->', value)
    if not isinstance(value, (int, float)):
        return 0
    return int(value)


def delTableChips(uid, tableIdList):
    '''
    取得用户的table_chip
    返回:
        所有的tablechip
    '''
    value = 0
    pass
    return value


def moveAllTableChipToChip(uid, gameid, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    转移用户所有的tablechip至chip
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, 0, 0, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)


def setTableChipToN(uid, gameid, tablechip, eventId, intEventParam, clientId, tableId, extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    设置用户的tablechip至传入的值
    参考: set_tablechip_to_range
    '''
    return _setTableChipToRange(uid, gameid, tablechip, tablechip, eventId, intEventParam, clientId, tableId,
                                extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02)
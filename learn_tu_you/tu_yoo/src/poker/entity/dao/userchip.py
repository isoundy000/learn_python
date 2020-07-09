#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import daoconst, daobase, userdata, gamedata
from poker.servers.util.direct import dbuser


EVENT_NAME_SYSTEM_REPAIR = 'SYSTEM_REPAIR'


class ChipNotEnoughOpMode(object):

    def __call__(self, *args, **kwargs):
        return self

    def __init__(self):
        self.NOOP = 0
        self.CLEAR_ZERO = 1


ChipNotEnoughOpMode = ChipNotEnoughOpMode()


def getChip(uid):
    """金币"""
    return userdata.getAttr(uid, daoconst.ATT_CHIP)


def getCoin(uid):
    """获取金币"""
    return userdata.getAttr(uid, daoconst.ATT_COIN)


def getDiamond(uid):
    """钻石"""
    return userdata.getAttr(uid, daoconst.ATT_DIAMOND)


def getCoupon(uid):
    """奖券"""
    return userdata.getAttr(uid, daoconst.ATT_COUPON)


def getUserChipAll(uid):
    '''
        取得用户的所有金币, 包含被带入的金币
        '''
    uchip = userdata.getAttr(uid, daoconst.ATT_CHIP)
    gchip1 = gamedata.getGameAttrInt(uid, 1, daoconst.ATT_TABLE_CHIP)  # TODO 就代码数据兼容, 可删除
    gchip8 = gamedata.getGameAttrInt(uid, 8, daoconst.ATT_TABLE_CHIP)  # TODO 就代码数据兼容, 可删除
    tchips = daobase.executeUserCmd(uid, 'HVALS', daoconst.HKEY_TABLECHIP + str(uid))
    allchip = uchip + gchip1 + gchip8
    if tchips:
        for x in tchips:
            if isinstance(x, (int, float)):
                allchip += int(x)
    return allchip


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


def incrChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId,
             extentId=0, roomId=0, tableId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的金币进行INCR操作
    @param uid: userId
    @param gameid: 游戏ID
    @param deltaCount: 变化的值可以是负数
    @param chipNotEnoughOpMode: 当INCR动作会变成负数时的处理模式, 0表示不进行操作; 1会给金币清零
    @param eventId: 触发INCR的事件ID
    @param argdict: 需要根据事件传入intEventParam
    @return (trueDelta, final) trueDelta表示实际变化的值, final表示变化后的最终数量
    参考incr_chip_limit的调用，此方法相当于用lowLimit, highLimit都是-1去调用incr_chip_limit
    '''
    return _incrUserChipFiled()


def incrTableChip(uid, gameid, deltaCount, chipNotEnoughOpMode, eventId, intEventParam, clientId, tableId,
                  extentId=0, roomId=0, roundId=0, param01=0, param02=0):
    '''
    对用户的tablechip进行INCR操作
    否则设置gamedata中的tablechip
    参考: incr_chip
    '''
    return _incrUserChipFiled(uid, gameid, deltaCount, -1, -1,
                              chipNotEnoughOpMode, eventId, daoconst.CHIP_TYPE_TABLE_CHIP,
                              intEventParam, clientId, tableId,
                              extentId=extentId, roomId=roomId, roundId=roundId, param01=param01, param02=param02, )
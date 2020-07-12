#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import json
import traceback

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import daobase, userdata
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.biz.exceptions import TYBizException
from newfish.entity.config import FISH_GAMEID
from newfish.entity import util
from newfish.entity import config
from newfish.entity.msg import GameMsg
from newfish.servers.util.rpc import user_rpc


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def ftBind(roomId, tableId, ftTable):
    """
    :param roomId:
    :param tableId:
    :param ftTable:
    :return:
    """
    try:
        room = gdata.rooms()[roomId]
        table = room.maptable[tableId]
        return table.doFTBind(ftTable)
    except TYBizException, e:
        return {"errorCode": e.errorCode, "message": e.message}







@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def quickStart(roomId, tableId, userId, clientId, extParams):
    """快速进入GT进程"""
    ftlog.debug("quickStart", userId, roomId, tableId, clientId)
    try:
        room = gdata.rooms()[roomId]
        room.quickStartInGT(roomId, tableId, userId, clientId, extParams)
    except Exception, e:
        ftlog.error("quickStart error", roomId, tableId, userId, clientId, extParams, traceback.format_exc())
    return 0
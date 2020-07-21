#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.biz.exceptions import TYBizException
from newfish.room.fight_room import FTConf











@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def initializedGT(roomId, shadowRoomId, tableCount):
    """初始化GT房间"""
    ftlog.info("initializedGT", roomId, shadowRoomId, tableCount, gdata.rooms().keys())
    gdata.rooms()[roomId].initializedGT(shadowRoomId, tableCount)
    return 1
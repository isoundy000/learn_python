# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/7/5.
"""

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol.rpccore import markRpcCall
from poker.entity.biz.exceptions import TYBizException
from newfish.room.fight_room import FTConf


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def getUserMatchSignin(userId, roomId):
    """比赛报名信息"""
    return gdata.rooms()[roomId].getUserMatchSignin(userId)


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def getRankList(userId, roomId):
    """获取玩家自己和排行榜前50的分数和奖励等数据"""
    return gdata.rooms()[roomId].getRankList(userId)


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def createFT(userId, roomId, fee):
    """创建自建桌"""
    try:
        ftConf = FTConf(fee)
        code = gdata.rooms()[roomId].createFT(userId, ftConf)
        return code
    except TYBizException, e:
        return {"errorCode": e.errorCode, "message": e.message}


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def enterFT(userId, roomId, ftId):
    try:
        code = gdata.rooms()[roomId].enterFT(userId, ftId)
        return code
    except TYBizException, e:
        return {"errorCode": e.errorCode, "message": e.message}


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def userStandUp(roomId, ftId, userId):
    """离开桌子"""
    gdata.rooms()[roomId].userStandUp(ftId, userId)
    return userId


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def disbindFT(roomId, ftId, isReturnFee):
    """解散房间"""
    gdata.rooms()[roomId].disbindFT(ftId, isReturnFee)
    return ftId


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def ftExists(roomId, ftId):
    """是否存在"""
    ftTable = gdata.rooms()[roomId].findFT(ftId)
    if ftlog.is_debug():
        ftlog.debug("ft_room_remote.ftExists roomId=", roomId, "ftId=", ftId, "ftTable=", ftTable)
    return True if ftTable else False


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def reportRoomUserOccupy(roomId, shadowRoomId, roomOccupy, extData=None):
    """向GR汇报当前GT容量"""
    return gdata.rooms()[roomId].roomUserOccupy(shadowRoomId, roomOccupy, extData)


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def addPointMatchRobot(roomId, userId, name):
    """添加比赛机器人"""
    gdata.rooms()[roomId].addMatchRobotUser(userId, name)
    return 1


@markRpcCall(groupName="roomId", lockName="", syncCall=1)
def initializedGT(roomId, shadowRoomId, tableCount):
    """初始化GT房间"""
    ftlog.info("initializedGT", roomId, shadowRoomId, tableCount, gdata.rooms().keys())
    gdata.rooms()[roomId].initializedGT(shadowRoomId, tableCount)
    return 1
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/8


import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runcmd, router
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class RoomTcpHandler(BaseMsgPackChecker):

    def __init__(self):
        pass

    @markCmdActionMethod(cmd="room", action="des", clientIdVer=0, scope="game")
    def doRoomDes(self, roomId, userId):
        """获取比赛相关描述"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomDes->", msg)
        gdata.rooms()[roomId].doGetDescription(userId)

    @markCmdActionMethod(cmd="room", action="signin", clientIdVer=0, scope="game")
    def doRoomSignIn(self, roomId, userId):
        """比赛报名，扣费"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomSignIn->", msg)
        gdata.rooms()[roomId].doSignin(userId)

    @markCmdActionMethod(cmd="room", action="signout", clientIdVer=0, scope="game")
    def doRoomSignOut(self, roomId, userId):
        """取消报名"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomSignOut->", msg)
        gdata.rooms()[roomId].doSignout(userId)

    @markCmdActionMethod(cmd="room", action="enter", clientIdVer=0, scope="game")
    def doRoomEnter(self, roomId, userId):
        """进入房间"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomEnter->", msg)
        gdata.rooms()[roomId].doEnter(userId)

    @markCmdActionMethod(cmd="room", action="leave", clientIdVer=0, scope="game")
    def doRoomLeave(self, roomId, userId):
        """离开房间"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomLeave", msg)
        gdata.rooms()[roomId].doLeave(userId, msg)

    @markCmdActionMethod(cmd="room", action="giveup", clientIdVer=0, scope="game")
    def doRoomGiveup(self, roomId, userId):
        """放弃比赛"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomGiveup", msg)
        gdata.rooms()[roomId].doGiveup(userId)

    @markCmdActionMethod(cmd="room", action="update", clientIdVer=0, lockParamName="", scope="game")
    def doRoomUpdate(self, roomId):
        """更新"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomUpdate->", msg)
        gdata.rooms()[roomId].doUpdate(msg)

    @markCmdActionMethod(cmd="room", action="winlose", clientIdVer=0, lockParamName="", scope="game")
    def doRoomWinlose(self, roomId):
        """赢或者输"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomWinlose->", msg)
        gdata.rooms()[roomId].doWinlose(msg)

    @markCmdActionMethod(cmd="room", action="rank_list", clientIdVer=0, lockParamName="roomId", scope="game")
    def doRoomRankList(self, roomId, userId):
        """获取排名"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomRankList->", msg)
        gdata.rooms()[roomId].doGetRankList(userId)

    @markCmdActionMethod(cmd="room", action="news", clientIdVer=0, lockParamName="", scope="game")
    def doRoomNews(self, roomId, userId):
        """房间信息"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomNews->", msg)
        gdata.rooms()[roomId].doGetNews(userId)

    @markCmdActionMethod(cmd="room", action="return_fee", clientIdVer=0, lockParamName="", scope="game")
    def doRoomReturnFee(self, roomId):
        """返还报名费"""
        msg = runcmd.getMsgPack()
        ftlog.debug("doRoomReturnFee->", msg)
        gdata.rooms()[roomId].doReturnFee(msg)
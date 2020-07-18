#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import freetime.util.log as ftlog
from poker.entity.game.game import TYGame
from poker.protocol import runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from hall.servers.common.base_checker import BaseMsgPackChecker


@markCmdActionHandler
class FishRobotTcpHandler(BaseMsgPackChecker):

    @markCmdActionMethod(cmd="robotmgr", action="shutdown_uid", clientIdVer=0, lockParamName="tableId")
    def doSpecifyRobotShutDown(self, gameId, roomId0, tableId0, userId):
        ftlog.debug("doSpecifyRobotShutDown", roomId0, tableId0, userId)
        """
        关闭指定机器人
        """
        rmgr = TYGame(gameId).getRobotManager()
        if rmgr:
            msg = runcmd.getMsgPack()
            rmgr.shutDownSpecifyRobot(msg, roomId0, tableId0, userId)
# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import traceback

import freetime.util.log as ftlog
from poker.util import strutil
from poker.protocol import runcmd
from poker.protocol.decorator import markCmdActionHandler, markCmdActionMethod
from poker.entity.configure import gdata
from hall.servers.common.base_checker import BaseMsgPackChecker
from newfish.entity.config import FISH_GAMEID


@markCmdActionHandler
class TableTcpHandler(BaseMsgPackChecker):

    @markCmdActionMethod(cmd="fish_table_call", action="*", clientIdVer=0, scope="game", lockParamName="userId")
    def doTableCall2(self, userId, roomId, tableId, clientId):
        """渔场内的函数调用"""
        if strutil.getGameIdFromInstanceRoomId(roomId) == FISH_GAMEID:
            table = None
            msg = runcmd.getMsgPack()
            try:
                room = gdata.rooms()[roomId]
                table = room.maptable[tableId]
                action = msg.getParam("action")
                seatId = msg.getParam("seatId", -1) # 旁观时没有seatId参数
                assert isinstance(seatId, int)
                table.doTableCallOwn(msg, userId, seatId, action, clientId)
            except:
                ftlog.error("doTableCall2 error clear table", userId, msg, traceback.format_exc())
                table and table._clearTable()
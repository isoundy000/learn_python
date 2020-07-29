#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import traceback

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import userdata
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.table.normal_table import FishNormalTable
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.newbie_fish_group import NewbieFishGroup
from newfish.player.newbie_player import FishNewbiePlayer


class FishNewbieTable(FishNormalTable):

    def __init__(self, room, tableId):
        super(FishNormalTable, self).__init__(room, tableId)
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 200
        self.actionMap["task_expedite"] = self._task_expedite
        if "user" in self.runConfig.taskSystemType:
            self.actionMap["table_task_info"] = self._getTableTask
            self.actionMap["table_task_change"] = self._changeTableTask
            self.actionMap["red_task_list"] = self._getRedTaskList

    def _doTableCall(self, msg, userId, seatId, action, clientId):
        """渔场内的函数"""
        try:
            if not super(FishNormalTable, self)._doTableCall(msg, userId, seatId, action, clientId):
                if seatId == 0 and action not in ["task_ready", "task_start", "task_end"]:
                    ftlog.warn("invalid seatId")
                    return
        except:
            ftlog.error("_doTableCall error clear table", userId, msg, traceback.format_exc())
            self._clearTable()


#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8


import functools
import random
import time

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
from poker.entity.dao import userdata, onlinedata
from hall.entity import hallvip
from newfish.entity import util, config
from newfish.entity.quick_start import FishQuickStart
from newfish.room.timematchctrl.config import MatchConfig
from newfish.room.timematchctrl.exceptions import MatchException, SigninException, BadStateException
from newfish.room.timematchctrl.models import TableManager
from newfish.room.timematchctrl.utils import Logger
from newfish.room.timematchctrl.match import TimeMatch


class FishTimeMatchRoom(TYRoom):
    """
    捕鱼回馈赛房间
    """
    def __init__(self, roomdefine, plugin=None):
        super(FishTimeMatchRoom, self).__init__(roomdefine)
        self.bigmatchId = self.bigRoomId
        if plugin is None:
            self.matchPlugin = TimeMatch
        else:
            self.matchPlugin = plugin
        self.match = None
        self.matchMaster = None
        self._logger = Logger()
        self._logger.add("cls", self.__class__.__name__)
        self._logger.add("roomId", self.roomId)
        self._logger.add("bigmatchId", self.bigmatchId)
        serverType = gdata.serverType()
        if serverType == gdata.SRV_TYPE_ROOM:
            self.initMatch()                                                    # 此处会给self.match赋值

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.time_match_table import FishTimeMatchTable
        table = FishTimeMatchTable(self, tableId)
        return table

    def initializedGT(self, shadowRoomId, tableCount):
        pass


    def initMatch(self):
        """初始化比赛"""
        assert (self.matchPlugin.getMatch(self.roomId) is None)
        self._logger.info("initMatch ...")
        conf = MatchConfig.parse(self.gameId, self.roomId, self.bigmatchId, self.roomConf["name"], self.matchConf)



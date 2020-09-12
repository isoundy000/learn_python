#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

"""
定时积分赛
"""
import time
import random

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack

from poker.entity.configure import gdata
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
from poker.entity.dao import userdata, onlinedata
import poker.util.timestamp as pktimestamp
from newfish.room.timematchctrl.interfaceimpl import TimePointPlayer
from newfish.room.time_match_room import FishTimeMatchRoom
from newfish.entity import util, config, mail_system
from newfish.room.timematchctrl.exceptions import MatchException, SigninException, BadStateException, \
    NotSigninException, RunOutSigninChanceException, MaintenanceException
from newfish.room.timematchctrl.match import TimePointMatch


class FishTimePointMatchRoom(FishTimeMatchRoom):
    """
    定时积分赛房间
    """
    def __init__(self, roomdefine):
        self.rankRewardsMap = {}
        self.rankBuildRewardsMap = {}
        self.userInfoMap = {}
        self.userInfoCacheTime = {}
        self.userVipMap = {}
        self.userFee = {}
        super(FishTimePointMatchRoom, self).__init__(roomdefine, TimePointMatch)
        self._logger.info("serverType=", gdata.serverType())

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.time_point_match_table import FishTimePointMatchTable
        table = FishTimePointMatchTable(self, tableId)
        return table
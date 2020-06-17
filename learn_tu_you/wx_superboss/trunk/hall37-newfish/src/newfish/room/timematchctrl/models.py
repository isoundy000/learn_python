#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10

import random

from newfish.room.timematchctrl.const import SeatQueuingType, ScoreCalcType
from newfish.room.timematchctrl.utils import Logger



class TableManager(object):
    """桌子管理者"""
    def __init__(self, room, tableSeatCount):
        self._room = room
        self._tableSeatCount = tableSeatCount       # 桌子座位数
        self._idleTables = []
        self._allTableMap = {}
        self._roomIds = set()
        self._logger = Logger()
        self._logger.add("roomId", self._room.roomId)

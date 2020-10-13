# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/3/27.
"""

import time
import traceback
from random import choice

from freetime.core.tasklet import FTTasklet
from freetime.core.timer import FTLoopTimer
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.entity.dao import gamedata
from poker.util.keylock import KeyLock
from poker.entity.game.rooms.normal_room import TYNormalRoom
from newfish.room.friend_room import FishFriendRoom
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.quick_start import FishQuickStart
from newfish.servers.table.rpc import table_remote
from newfish.servers.room.rpc import room_remote


class FishMultipleRoom(FishFriendRoom):
    """
    捕鱼千炮模式房间
    """
    def __init__(self, roomDefine):
        super(FishMultipleRoom, self).__init__(roomDefine)

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.multiple_table import FishMultipleTable
        table = FishMultipleTable(self, tableId)
        table.matchingTime = 0
        self._addTable(table)
        return table
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
"""
海皇来袭渔场
"""

import time
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.biz import bireport
from newfish.entity import config, weakdata, mail_system
from newfish.entity.lotterypool import poseidon_lottery_pool
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.table.normal_table import FishNormalTable
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.terror_fish_group import TerrorFishGroup
from newfish.entity.fishgroup.autofill_fish_group_m import AutofillFishGroup
from newfish.player.poseidon_player import FishPoseidonPlayer
from newfish.room.poseidon_room import Poseidon, Tower
from newfish.entity.redis_keys import WeakData


class FishPoseidonTable(FishNormalTable):

    def __init__(self, room, tableId):
        super(FishPoseidonTable, self).__init__(room, tableId)
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 180
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 180
        self.actionMap2["bet_tower"] = self._bet_tower
        self.resetPoseidonState()
        self.resetTowerState()
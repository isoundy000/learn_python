#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/12
"""
宝箱怪
"""

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity.fishgroup.superboss_fish_group import SuperBossFishGroup


class BoxFishGroup(SuperBossFishGroup):
    """
    宝箱怪鱼阵
    """
    def __init__(self, table):
        super(BoxFishGroup, self).__init__()
        self.table = table
        self._interval = 300            # 宝箱怪出生间隔. 600 5分钟
        self._maxAliveTime = 150        # 宝箱怪的存在时间.
        self._bBossFishType = 71201     # 宝箱儿子
        self._mBossFishType = 71202     # 宝箱妈妈
        self._fBossFishType = 71203     # 宝箱爸爸
        self._startTS = 0               # 宝箱怪出现的时间戳.
        self._fBossAppearTS = 0         # 宝箱爸爸出现的最晚时间戳.
        self._nextTimer = None
        self._isBossShowTimeStage = 0   # showtime是boss出现前30秒(stage=0x1000),bBoss(0x1), mBoss(0x10), fBoss(0x100).
        self._hasBorned = []
        self._autofillTimer = {}
        self._clearTimer = None         # 清理宝箱的定时器.
        self._group = {}
        self._setTimer()









    def _setTimer(self):
        """
        设置boss出现时的计时器
        """
        if self._nextTimer:
            self._nextTimer.cancel()
            self._nextTimer = None
        if self._interval > 0:
            self._nextTimer = FTLoopTimer(self._interval, -1, self._addFishGroup)
            self._nextTimer.start()
        if self._interval - 30 > 0:
            FTLoopTimer(self._interval - 30, 0, self._addBossShowTimeStage, 0x1000).start()

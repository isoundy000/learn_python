#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

import random
import time
import datetime

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config, util


class NormalFishGroup(object):
    """
    普通鱼群
    """
    def __init__(self, table):
        self.table = table
        self._initData()
        self._generateNumOnce = 5
        self._nextGroupTimer = None
        self._appearIndex = datetime.datetime.now().minute / 15 + 1
        self._appearTideMinute = [range(9, 15),
                                  range(24, 30),
                                  range(39, 45),
                                  range(54, 60)]
        if self.table.typeName == config.FISH_ROBBERY:                  # 招财模式渔场
            self._generateNumOnce = 10
            self._appearIndex = random.choice(range(len(self.fishes)))
        self._nextGroup()

    def clearTimer(self):
        if self._nextGroupTimer:
            self._nextGroupTimer.cancel()
            self._nextGroupTimer = None

    def _initData(self):
        self.fishes = {}
        pass

    def _nextGroup(self):
        pass
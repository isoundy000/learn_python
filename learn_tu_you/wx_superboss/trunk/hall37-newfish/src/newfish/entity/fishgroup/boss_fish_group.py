#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/1

import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class BossFishGroup(object):
    """
    boss鱼群
    """
    def __init__(self, table):
        self.table = table
        self._interval = 300
        self._bossGroupId = None            # boss鱼群Id
        self._nextBossTimer = None
        self._setBossTimer()
        self._fishType = 0
        self._bossAppearTS = 0
        self._autofillTimer = None
        self._group = None

    def clearTimer(self):
        if self._nextBossTimer:
            self._nextBossTimer.cancel()
            self._nextBossTimer = None
        if self._autofillTimer:
            self._autofillTimer.cancel()
            self._autofillTimer = None

    def _setBossTimer(self):
        pass
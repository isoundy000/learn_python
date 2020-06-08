#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/9


import random
import time

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity import config


class AutofillFishGroup(object):
    """
    autofill鱼群
    """
    
    def __init__(self, table):
        self.table = table
        self.autofillFishConf = config.getAutofillFishConf(self.table.runConfig.fishPool)
        self.fishTypeList = []
        # 正常出鱼定时器
        self._nextTimerList = []
        # 补鱼定时器
        self._checkCountTimerList = []
        self._setAutofillFishTimer()
    
    def clearTimer(self):
        """清理定时器"""
        for _timer in self._nextTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        for _timer in self._checkCountTimerList:
            if _timer:
                _timer.cancel()
                _timer = None
        self._nextTimerList = []
        self._checkCountTimerList = []
    
    def _setAutofillFishTimer(self):
        pass
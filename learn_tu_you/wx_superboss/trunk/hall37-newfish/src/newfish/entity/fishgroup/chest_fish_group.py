#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/2


import random
import math

from freetime.util import log as ftlog
import poker.util.timestamp as pktimestamp
from newfish.entity import config


class ChestFishGroup(object):
    """
    金币宝箱鱼群
    """
    def __init__(self, table):
        self.table = table
        self.chestFishTime = 0

    def clearTimer(self):
        pass

    def checkCondition(self, player, fishConf):
        pass

    def _getChestScore(self, chestFishConf):
        """
        获得金币宝箱鱼阵分数
        """
        pass

    def _addChestFishGroup(self, userId, score):
        """
        添加金币宝箱鱼阵并扣除宝箱池彩池奖金
        """
        pass
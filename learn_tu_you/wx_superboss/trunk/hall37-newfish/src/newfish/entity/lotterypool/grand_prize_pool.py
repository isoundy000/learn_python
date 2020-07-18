#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
"""
巨奖奖池
"""

import random
import json
import time

import freetime.util.log as ftlog
from poker.entity.configure import gdata
from hall.entity import hallvip
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import daobase, userdata
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import MixData



class GrandPrizePool(object):
    pass


    def checkSendReward(self, tableId, roomId, fId, userId, fireCost, seatId, fpMultiple):
        """
        检测能否发奖
        """
        pass


_inited = False
grandPrizePoolInst = None


def initialize():
    """初始化"""
    global _inited, grandPrizePoolInst
    if not _inited:
        _inited = True
        serverId = gdata.serverId()
        if serverId == "CT9999000001":
            grandPrizePoolInst = GrandPrizePool()
            ftlog.debug("GrandPrizePool, init grandPrizePoolInst", serverId)
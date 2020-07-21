#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
"""
竞赛活动
"""
import math
import time
import json
import random
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.protocol import router
from poker.entity.configure import gdata
from poker.entity.dao import userchip, userdata, gamedata, daobase
from poker.entity.configure import pokerconf
from newfish.entity import util, config, store
from newfish.entity.msg import GameMsg
from newfish.entity.config import FISH_GAMEID, BT_DIRECT, BT_DIAMOND
from newfish.entity.redis_keys import MixData, GameData
from newfish.entity.fishactivity.fish_activity import ActivityType
from newfish.servers.table.rpc import table_remote



class CompActState:
    CAS_NOTOPEN = 0  # 未开启
    CAS_INPROGRESS = 1  # 进行中
    CAS_END = 2  # 已结束


class CompAct(object):
    """
    竞赛活动
    """
    def __init__(self, userId, seatId, clientId):
        self.userId = userId
        self.seatId = seatId
        self.clientId = clientId
        # 是否在竞赛时段
        self._isInCompTime = False
        self._teamId = -1
        self._endTS = 0
        self._lastUpdateTS = 0
        self.updateTimer()
    
    def updateTimer(self):
        """
        更新定时器
        """
        # 更新间隔不小于30秒
        curTime = int(time.time())







def isActEnable(userId=None):
    pass



def _getCompStateAndRemainTime():
    pass




def initialize(a):
    pass
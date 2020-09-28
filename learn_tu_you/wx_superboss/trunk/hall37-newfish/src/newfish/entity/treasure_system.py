# -*- coding=utf-8 -*-
"""
Created by lichen on 2019-06-10.
宝藏系统
"""

import json
import time
import math
import random

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
import poker.util.timestamp as pktimestamp
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import daobase, userchip
from poker.entity.configure import gdata
from hall.entity import hallitem, datachangenotify
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, item, util, module_tip, mail_system
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import UserData
from newfish.entity.event import TreasureLevelUp


def refreshTreasureState(userId, kindId):
    """
    刷新宝藏状态等数据
    """
    pass




def initialize():
    ftlog.debug("newfish treasure_system initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import EventUserLogin
        from newfish.game import TGFish
        from newfish.entity.event import MatchOverEvent, RankOverEvent, FinishGrandPrixEvent, \
            MatchRewardEvent, TreasureItemCountChangeEvent
        TGFish.getEventBus().subscribe(EventUserLogin, _triggerUserLoginEvent)
        TGFish.getEventBus().subscribe(MatchOverEvent, _triggerMatchOverEvent)
        TGFish.getEventBus().subscribe(FinishGrandPrixEvent, _triggerFinishGrandPrixEvent)
        TGFish.getEventBus().subscribe(MatchRewardEvent, _triggerMatchRewardEvent)
        TGFish.getEventBus().subscribe(RankOverEvent, _triggerRankOverEvent)
        TGFish.getEventBus().subscribe(TreasureItemCountChangeEvent, _triggerTreasureItemCountChangeEvent)
    ftlog.debug("newfish treasure_system initialize end")
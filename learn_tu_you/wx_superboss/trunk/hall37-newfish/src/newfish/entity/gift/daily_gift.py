#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21
"""
每日礼包
"""
import time
import json

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from poker.entity.configure import pokerconf
from hall.entity import hallvip
from newfish.entity import config, util, weakdata, vip_system, store
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID, VOUCHER_KINDID, BT_VOUCHER
from newfish.entity.msg import GameMsg
from newfish.entity.chest import chest_system
from newfish.entity import mail_system
from poker.entity.biz import bireport


def doSendGift(userId, clientId):
    """
    获取礼包数据
    """
    message = MsgPack()
    message.setCmd("fishDailyGift")
    message.setResult("gameId", FISH_GAMEID)
    message.setResult("userId", userId)



_inited = False


def initialize():
    ftlog.debug("newfish daily_gift initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from hall.game import TGHall
        from newfish.game import TGFish
        from newfish.entity.event import NFChargeNotifyEvent
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
    ftlog.debug("newfish daily_gift initialize end")
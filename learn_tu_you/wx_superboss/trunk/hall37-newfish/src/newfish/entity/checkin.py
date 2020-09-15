#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21
"""
新版签到，分为3个转盘，记录连续登陆天数解锁后2个转盘。
"""

import time
import random

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import gamedata
from hall.entity import hallvip
from poker.protocol import router
from newfish.entity import config, weakdata, module_tip, util
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.chest import chest_system










def _triggerNewbieTaskCompleteEvent(event):
    """
    新手任务完成
    """
    userId = event.userId
    checkinDay = getCheckinDay(userId)
    if checkinDay:
        module_tip.addModuleTipEvent(userId, "checkin", checkinDay)


_inited = False


def initialize():
    ftlog.info("newfish checkin initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from newfish.game import TGFish
        from newfish.entity.event import NewbieTaskCompleteEvent
        TGFish.getEventBus().subscribe(NewbieTaskCompleteEvent, _triggerNewbieTaskCompleteEvent)  # 新手任务完成事件
    ftlog.info("newfish checkin initialize end")
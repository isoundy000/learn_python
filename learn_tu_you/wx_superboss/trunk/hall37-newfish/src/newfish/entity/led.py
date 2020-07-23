#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/22
import json
from datetime import datetime

from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.dao import onlinedata, sessiondata
from poker.protocol import router
from poker.util import strutil
from hall.entity import hallconf
from hall.entity.hallconf import HALL_GAMEID
from newfish.entity import config

_LEDS = {}





def doSendLedToUser(userId):
    """
    发送LED消息玩家（由客户端心跳消息触发，平均30s一次）
    """
    from newfish.entity import util
    gameIdList = onlinedata.getGameEnterIds(userId)
    lastGameId = onlinedata.getLastGameId(userId)
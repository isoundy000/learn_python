#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21
import random
import json
from datetime import date, timedelta

from freetime.util import log as ftlog
from poker.entity.dao import daobase, gamedata
import poker.util.timestamp as pktimestamp
from poker.entity.events.tyevent import EventHeartBeat
from hall.entity import hallranking
from newfish.entity import util, config
from newfish.entity.config import FISH_GAMEID, BULLET_KINDIDS, BRONZE_BULLET_KINDID, \
    SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, TM_BRONZE_BULLET_KINDID, TM_SILVER_BULLET_KINDID, TM_GOLD_BULLET_KINDID
from newfish.entity.event import RobberyBulletChangeEvent
from newfish.entity.redis_keys import GameData, UserData


KINDIDS = [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]
TM_KINDIDS = [TM_BRONZE_BULLET_KINDID, TM_SILVER_BULLET_KINDID, TM_GOLD_BULLET_KINDID]
KEY_EXPIRE_TIME = 2 * 24 * 60 * 60
SEVEN_RANK_EXPIRE_TIME = 7 * 24 * 60 * 60


def getRobberyGainKey():
    """
    招财模式系统总盈亏
    """
    return "robberygain:%d" % FISH_GAMEID


def getRobberyWinMostKey(userId, dateTime=None):
    """
    赢家榜用户个人数据
    """
    dateTime = dateTime or date.today()
    return UserData.robberywinmost % (FISH_GAMEID, userId, dateTime)


def getRobberyWinMostData(userId, dateTime=None, trialMode=None):
    """
    获取赢家榜用户个人数据
    @return: 各招财珠对应数量的数组
    """
    if trialMode:
        infos = "[0, 0, 0]"
    else:
        infos = daobase.executeUserCmd(userId, "GET", getRobberyWinMostKey(userId, dateTime)) or "[0, 0, 0]"
    return json.loads(infos)


def initialize(a):
    pass
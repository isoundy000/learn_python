#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11
import time
import json
import random
import string

from freetime.util import log as ftlog
from hall.entity import hallvip
from poker.entity.configure import gdata
from poker.util import strutil
from poker.entity.dao import gamedata, userchip, userdata
from newfish.entity import config, util, gift_system, weakdata, mail_system
from newfish.entity.config import FISH_GAMEID, SERVER_VERSION
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.data import FishData


def getInitDataKeys():
    """
    gamedata的key
    """
    return FishData.getGameDataKeys()


def getInitDataValues():
    """
    gamedata的value
    """
    return FishData.getGameDataValues()


def getGameInfo(userId, clientId):
    """
    获取玩家的游戏数据
    """
    from newfish.entity import user_system
    ukeys = getInitDataKeys()
    uvals = gamedata.getAllAttrs(userId, FISH_GAMEID, ukeys)
    uvals = list(uvals)
    values = getInitDataValues()
    for x in xrange(len(uvals)):
        if uvals[x] is None:
            uvals[x] = values[x]
    gdata = dict(zip(ukeys, uvals))
    gdata["name"] = util.getNickname(userId)
    gdata["userGuideStep"] = gamedata.getGameAttrJson(userId, FISH_GAMEID, GameData.userGuideStep, [])
    redState = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.redState)
    gdata["redState"] = redState
    gdata["giftState"] = newbie_7days_gift.checkNewbie7DaysGiftState(userId, redState)
    pass

    return gdata


def createGameData(userId, gameId):
    pass


def loginGame(userId, gameId, clientId, iscreate, isdayfirst):
    pass



def getDaShiFen(userId, clientId):
    pass
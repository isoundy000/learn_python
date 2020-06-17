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
    pass
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
"""
存钱罐模块
"""
import time
import json

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.configure import pokerconf
from poker.protocol import router
from hall.entity import hallvip
from poker.entity.dao import userchip, daobase
from newfish.entity import config, util, store, vip_system
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData

FREE_PIGGY_BANK_COOLDOWN_INTERVAL = 60 * 60 * 20



def addMoneyToPiggyBank(userId, clientId, type, addCount, ts=None):
    """
    向存钱罐加钱
    """


def fireCostChip(userId, clientId, vipLevel, chip):
    """
    存入开火消耗
    """
    ftlog.debug("piggy_bank, userId =", userId, "vip =", vipLevel, "chip =", chip)
    conf = config.getPiggyBankConf(clientId, vipLevel)
    for k, v in conf.iteritems():
        addCount = chip * v.get("firePct", 0)
        if addCount > 0:
            addMoneyToPiggyBank(userId, clientId, k, addCount)


def initialize():
    pass
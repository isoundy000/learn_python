#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11
import time
import json
from operator import itemgetter

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.dao import gamedata, userchip
from poker.entity.configure import pokerconf
from hall.entity import hallitem, hallvip
from newfish.entity import config, util, weakdata, share_system, vip_system, store
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.entity.config import FISH_GAMEID, VOUCHER_KINDID, BT_VOUCHER
from newfish.entity.chest import chest_system
from newfish.entity.gun import gun_system
from newfish.entity.msg import GameMsg
from newfish.entity.honor import honor_system








def doSendFishGift(userId, clientId):
    """
    发送礼包消息
    """
    pass


def doBuyFishGift(userId, clientId, giftId, buyType=None, itemId=0):
    """
    购买礼包
    """
    ftlog.debug("doBuyFishGift===>", userId, clientId, giftId, buyType, itemId)


def doGetFishGiftReward(userId, clientId, giftId):
    """
    领取礼包
    """

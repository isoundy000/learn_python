#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import time
import json
import random
import math
import datetime
import re
from distutils.version import StrictVersion

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.util import keywords, strutil
from poker.protocol import router
from poker.entity.dao import gamedata, userdata, daobase, sessiondata
from poker.entity.biz import bireport
from poker.entity.configure import gdata, pokerconf
from hall.entity import hallvip, hall_share2, hallitem
from hall.entity.hall_share2 import ParsedClientId
from newfish.entity.config import FISH_GAMEID
from newfish.entity.honor import honor_system
from newfish.entity import config, util, weakdata, module_tip, returner_mission
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.servers.util.rpc import user_rpc



def updateLoginData(userId):
    """
    更新用户登录数据
    """
    curTime = int(time.time())
    lastLoginTime = gamedata.getGameAttrInt(userId, FISH_GAMEID, GameData.lastloginTime) or curTime
    returner_mission.refreshReturnerMissionData(userId, lastLoginTime)  # 刷新回归豪礼数据
    lastLoginTime = util.getDayStartTimestamp(lastLoginTime)
    todayStartTime = util.getDayStartTimestamp(curTime)
    gamedata.setGameAttr(userId, FISH_GAMEID, GameData.lastloginTime, curTime)
    # 过天
    if todayStartTime - lastLoginTime > 24 * 3600:
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.loginDays, 1)
        gamedata.setGameAttr(userId, FISH_GAMEID, GameData.continuousLogin, 1)
    elif todayStartTime - lastLoginTime == 24 * 3600:  # 正好一天
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.loginDays, 1)
        gamedata.incrGameAttr(userId, FISH_GAMEID, GameData.continuousLogin, 1)
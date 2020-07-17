#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import random
import json
import time
import math
from copy import deepcopy

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.util import strutil
from poker.entity.dao import userdata, gamedata, daobase
from poker.entity.configure import gdata
from poker.entity.events.tyevent import EventUserLogin
from hall.entity import hallvip
from newfish.entity import config, util, treasure_system
from newfish.entity.redis_keys import GameData, UserData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.event import TableTaskEndEvent, CatchEvent, \
    NewSkillEvent, RandomChestShareEvent, MatchOverEvent, GameTimeEvent, \
    ShareFinishEvent
from newfish.servers.util.rpc import user_rpc


INDEX_STATE = 0                     # 第0位:当前分享状态
INDEX_MODE = 1                      # 第1位:当前分享模式
INDEX_POP_COUNT = 2                 # 第2位:当前已弹出次数
INDEX_FINISH_COUNT = 3              # 第3位:当前已完成次数
INDEX_FINISH_TIME = 4               # 第4位:上一次完成时间
INDEX_OTHER_DATA = 5                # 第5位:记录奖励等其他数据
DEFAULT_VALUE = [0, 0, 0, 0, 0, {}] # 分享数据默认值



class ShareRewardState:
    """
    分享奖励状态
    """
    Unavailable = 0                 # 不可领取
    Available = 1                   # 可领取
    Obtained = 2                    # 已领取


class FishShare(object):


    def __init__(self, userId):
        self.userId = userId
        self.vipLevel = hallvip.userVipSystem.getVipInfo(self.userId).get("level", 0)
        self.level, self.clientVersion = gamedata.getGameAttrs(self.userId, FISH_GAMEID,
                                                               [GameData.level, GameData.clientVersion])
        self.shareConf = config.getShareConf(typeId=self.TYPEID)
        self.lang = util.getLanguage(self.userId)
        data = daobase.executeUserCmd(self.userId, "HGET", _getUserShareDataKey(self.userId), str(self.shareConf["shareId"]))
        self.shareData = strutil.loads(data, False, True, deepcopy(DEFAULT_VALUE))
        self.finishCountLimit = self.shareConf["finishCountLimit"]



class RandomChest(FishShare):
    """
    随机分享宝箱
    """
    pass
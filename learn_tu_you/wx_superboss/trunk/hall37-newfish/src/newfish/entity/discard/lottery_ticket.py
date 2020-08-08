#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
# 红包券抽奖
import json
import time
import random
import copy
import math
import json
from distutils.version import StrictVersion
from poker.entity.dao import daobase, userdata, gamedata
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity.redis_keys import GameData
from newfish.entity import config, util
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData, UserData, ABTestData
from newfish.entity.config import FISH_GAMEID

# 红包券抽奖状态
class LTState:

    NOT_DRAW = 0        # 不能抽奖
    CAN_DRAW = 1        # 可抽奖
    NOT_COUNT = 2       # 抽奖次数已经用完


# 红包券存档数据索引
class LTValueIdx:

    STATE = 0           # 红包券抽奖状态
    DRAWCOUNT = 1       # 已抽奖次数
    TAKEN = 2           # 已领取的奖励索引
    REWARD = 3          # 计算好的奖励索引


class LotteryTicket(object):

    default_val = [0, 0, [], []]
    # 红包券抽奖状态，已抽奖次数，已领取的奖励索引，计算好的奖励索引

    def __init__(self, player, fishPool, roomId):
        self.player = player
        self.userId = player.userId
        self.fishPool = fishPool
        self.roomId = roomId
        self.clientId = player.clientId
        self.lang = player.lang
        self.lotteryTicketKey = UserData.lotteryTicketData % (FISH_GAMEID, self.userId)
        self.ltData = {}
        self.lastSendTS = 0
        self.ltConf = config.getLotteryTicActConf(self.clientId)
        self.registeTime = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.registTime)
        self.clientVersion = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.clientVersion)
        self.startTs = util.getTimestampFromStr(self.ltConf.get("startTime", "2020-02-19 00:00:00"))
        self.expireTs = self.registeTime + self.ltConf.get("expire", 0) * 24 * 3600
        # 新手ABC测试.
        testMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, ABTestData.newbiewABCTestMode)
        enableNewbieLottery = config.getABTestConf("abcTest").get("enableNewbieLottery", {}).get(testMode, 1)
        if ftlog.is_debug():
            ftlog.debug("abc test, userId =", self.userId, "mode =", testMode, "enableNewbieLottery =", enableNewbieLottery)
        if enableNewbieLottery == 0:
            self.expireTs = 0
        self.lastTotalFireCount = -1
        self.lastHasFireCount = -1
        # 服务器主动推送时，cmd由版本号决定；前端请求时，传的cmd是啥就回啥
        if StrictVersion(str(self.clientVersion)) < StrictVersion("2.0.50"):
            self.progressCmd = "lottery_ticket_progress"
        else:
            self.progressCmd = "ticket_progress"
        self.updateCostChipTimer = None
        self.iosClientIds = config.getPublic("multipleLangClientIds", [])
        if self._getData(fishPool)[LTValueIdx.STATE] != LTState.NOT_COUNT and self.effective(str(fishPool)) == 0:
            self.updateCostChipTimer = FTLoopTimer(1, -1, self.sendProgress, 1, "", 0)
            self.updateCostChipTimer.start()

    def clearTimer(self):
        """
        清除定时器
        """
        if self.updateCostChipTimer:
            self.updateCostChipTimer.cancel()
            self.updateCostChipTimer = None
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/1


import json
import random
from copy import deepcopy

from poker.entity.dao import userchip, daobase
from poker.entity.configure import gdata
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData
from newfish.entity.config import FISH_GAMEID
from newfish.entity import config, util
from newfish.entity.event import PrizeWheelSpinEvent
from newfish.entity.prize_wheel import PrizeWheel, PWState, PWValueSlot


class GrandPrixPrizeWheel(PrizeWheel):

    # 能量值，转盘状态，抽奖结果索引(包含选择押注的结果)，已获得的奖励索引，十倍场首次双倍竞猜必中双倍标记，选中的竞猜倍数, 充能池, 可用抽奖次数
    # ENERGY, STATE, RET, TAKEN, BETCOUNT, BET, ENERGYPOOL, SPINTIMES
    gp_default_val = [0, 0, [], [], 0, 0, 0, 0]

    def __init__(self, userId, fishPool, roomId):
        super(GrandPrixPrizeWheel, self).__init__(userId, fishPool, roomId)
        self.pwConf = config.getGrandPrixPrizeWheelConf()
        self.fireRatio = self.pwConf.get("ratio", {}).get("fire", 0)
        self.lossRatio = self.pwConf.get("ratio", {}).get("loss", 0)
        self.maxSpinTimes = self.pwConf.get("maxSpinTimes", 1)
        self.isEnergyStorageMode = (self.maxSpinTimes > 1)

    def dumpData(self):
        if str(self.fishPool) in self.pwData and self.pwData[str(self.fishPool)].keys():
            self._setData(self.fishPool, self.pwData[str(self.fishPool)].keys()[0])









    def addEnergyPool(self, fpMultiple, val):
        """
        渔场倍率充能池
        """
        pwData = self._getData(self.fishPool, fpMultiple)
        pass

    def fireCoin(self, fpMultiple, val):
        """
        开火累计倍率充能池
        """
        if not self._enable(self.fishPool, fpMultiple):
            return
        _val = val * self.fireRatio
        if _val > 0:
            self.addEnergyPool(fpMultiple, _val)
        ftlog.debug("grand_prix_prize_wheel, userId =", self.userId,
                    "fpMultiple =", fpMultiple, val, self.fireRatio, _val, self._getData(self.fishPool, fpMultiple))
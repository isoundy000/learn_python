# -*- coding=utf-8 -*-
"""
Created by haohongxian on 2017/8/1.
"""

import random
import math

from freetime.util import log as ftlog
import poker.util.timestamp as pktimestamp
from newfish.entity import config


class ChestFishGroup(object):
    """
    金币宝箱鱼群
    """
    def __init__(self, table):
        self.table = table
        self.chestFishTime = 0

    def clearTimer(self):
        pass

    def checkCondition(self, player, fishConf):
        """检查条件"""
        userId = player.userId
        chestFishInterval = int(config.getCommonValueByKey("chestFishInterval", 120))
        chestPoolCoin = self.table.room.lotteryPool.getChestPoolCoin()
        chestFishConf = config.getChestFishConf(self.table.runConfig.fishPool)
        playerMaxCoin = chestFishConf["maxCoin"]
        profitForChest = player.profitForChest.get(str(self.table.runConfig.fishPool), 0)
        resultNum = (math.sqrt(fishConf["score"]) - 30 * math.pow(profitForChest / playerMaxCoin, 3)) / 500
        randomNum = random.randint(1, 10000)
        ftlog.debug("checkCondition======>", userId, fishConf["score"], chestPoolCoin, profitForChest, resultNum * 10000, randomNum)
        if chestPoolCoin > 0 and randomNum <= resultNum * 10000 and \
                pktimestamp.getCurrentTimestamp() - self.chestFishTime >= chestFishInterval:
            chestScore = self._getChestScore(chestFishConf)
            player.clearProfitChest()
            ftlog.debug("ChestFishGroup->checkCondition", userId, chestPoolCoin, chestScore)
            self._addChestFishGroup(userId, chestScore)
            self.chestFishTime = pktimestamp.getCurrentTimestamp()

    def _getChestScore(self, chestFishConf):
        """
        获得金币宝箱鱼阵分数
        """
        randInt = random.randint(1, 10000)
        chestFishConf = chestFishConf.get("probbs", [])
        score = 0
        for fish in chestFishConf:
            probb = fish["probb"]
            if probb[0] <= randInt <= probb[1]:
                score = fish["score"]
                break
        return score

    def _addChestFishGroup(self, userId, score):
        """
        添加金币宝箱鱼阵并扣除宝箱池彩池奖金
        """
        allChestGroupIds = self.table.runConfig.allChestGroupIds
        groupId = random.choice(allChestGroupIds)
        self.table.insertFishGroup(groupId, userId=userId, score=score)
        self.table.room.lotteryPool.deductionChestPoolCoin(score * self.table.runConfig.multiple)
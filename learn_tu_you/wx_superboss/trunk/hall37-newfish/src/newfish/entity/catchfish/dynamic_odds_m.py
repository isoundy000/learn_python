# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/7/9.
"""

import random
import json

from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from newfish.entity import config, util, weakdata
from newfish.entity.catchfish.dynamic_odds import DynamicOdds
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData


class DynamicOdds_m(DynamicOdds):
    """
    动态概率控制
    """
    def __init__(self, table, player):
        super(DynamicOdds_m, self).__init__(table, player)
        self.table = table
        self.player = player
        self.initConstData()
        self.initVarData()

    @property
    def chip(self):
        return self.player.holdCoin

    @property
    def currRechargeBonus(self):
        bonus = 0
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return bonus
        if not self.player or not self.player.userId:
            return bonus
        return self._currRechargeBonus

    def initConstData(self):
        """
        初始化常量数据
        """
        # 新手保护概率
        self.protectOdds = [1.0, 1.0, 1.3, 1.25, 1.1, 1.05, 1, 1]

        # 普通火炮概率系数((出现概率, 概率系数随机区间))
        self.gunOddsSection = ((0.7, (1, 1)), (0.15, (1.6, 1.6)), (0.15, (0, 0)))
        # 技能概率系数((出现概率, 概率系数随机区间))
        self.skillOddsSection = ((0.1, (1.1, 2.4)), (0.7, (0.9, 1.2)), (0.2, (0, 0.4)))

        # 黑名单概率
        self.banOddsList = config.getPublic("banOddsList", [])
        self.fireBanOdds = 0.5
        self.skillBanOdds = 0.5

    def initVarData(self):
        """
        初始化变量数据
        """
        # 原始充值奖池
        self._originRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.rechargeBonus)
        # 当前充值奖池
        self._currRechargeBonus = self._originRechargeBonus
        # 扣除的充值奖池
        self.decreasedRechargeBonus = 0
        # 初始额外奖池
        self._orginExtraRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.extraRechargePool)

    def isProtectMode(self):
        """
        是否在新手保护期间
        """
        protectLevel = len(self.protectOdds)
        if self.player.level <= protectLevel:
            return True
        return False

    def getOdds(self, skill=None, superBullet=None, aloofFish=False, gunConf=None):
        """
        获得概率
        :param skill: 是否技能
        :param superBullet: 是否超级子弹
        :param aloofFish: 是否高冷鱼
        :param gunConf: 当前装备火炮配置
        :return: 返回概率系数
        """
        if not self.player or not self.player.userId:
            return 1

        if skill:
            if self.player.userId in self.banOddsList:
                odds = self.skillBanOdds
            else:
                odds = self.getSkillOdds()
        else:
            if self.player.userId in self.banOddsList:
                odds = self.fireBanOdds
            else:
                odds = self.getGunOdds()
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->getOdds->",
                        "userId =", self.player.userId,
                        "odds =", odds,
                        "skill =", skill,
                        "superBullet =", superBullet,
                        "aloofFish =", aloofFish,
                        "gunConf =", gunConf)
        return odds

    def getGunOdds(self):
        """
        获得普通火炮概率系数
        """
        oddsSection = self.gunOddsSection
        randomNum = random.randint(1, 10000)
        probb = 0
        for oddsDetail in oddsSection:
            probb += oddsDetail[0] * 10000
            if randomNum <= probb:
                return random.uniform(oddsDetail[1][0], oddsDetail[1][1])
        return 1

    def getSkillOdds(self):
        """
        获得技能概率系数
        """
        oddsSection = self.skillOddsSection
        randomNum = random.randint(1, 10000)
        probb = 0
        for oddsDetail in oddsSection:
            probb += oddsDetail[0] * 10000
            if randomNum <= probb:
                return random.uniform(oddsDetail[1][0], oddsDetail[1][1])
        return 1

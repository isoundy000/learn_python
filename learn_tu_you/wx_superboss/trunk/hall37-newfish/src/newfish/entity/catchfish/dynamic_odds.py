# -*- coding=utf-8 -*-
"""
Created by lichen on 17/4/20.
"""

import random
import json

from freetime.util import log as ftlog
from poker.entity.dao import gamedata
from poker.entity.biz import bireport
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData


WAVE_ID = 0     # 波动曲线ID
WAVE_INDEX = 1  # 波动频点位置
WAVE_RADIX = 2  # 波动单元基数
WAVE_COIN = 3   # 波动金币


class DynamicOdds(object):
    """
    动态概率控制
    """
    def __init__(self, table, player):
        self.table = table
        self.player = player
        self.fishPool = player.matchingFishPool     # self.table.runConfig.fishPool
        # # 目前使用A模式.
        # dynamicOdds1050TestMode = config.getPublic("dynamicOdds1050TestMode") or gamedata.getGameAttr(self.player.userId, FISH_GAMEID, GameData.dynamicOdds1050TestMode)
        # # 非a模式玩家，10倍50倍场使用2倍场曲线.
        # if dynamicOdds1050TestMode not in ["a"] and self.table.runConfig.fishPool in [44002, 44003]:
        #     fishPool = 44001
        # else:
        #     fishPool = self.fishPool
        if self.player.fpMultipleTestMode in ["b"]:     # 倍率测试模式 AB测试
            self.minWaveRadix = self.table.runConfig.minWaveRadix_b     # 最小波动基数(渔场倍率b模式)
            self.maxWaveRadix = self.table.runConfig.maxWaveRadix_b
        else:
            self.minWaveRadix = self.table.runConfig.minWaveRadix
            self.maxWaveRadix = self.table.runConfig.maxWaveRadix
        self.dynamicOddsMap = config.getDynamicOddsConf(self.fishPool)
        self.initConstData()
        self.initVarData()
        self.refreshOdds()
        # ftlog.debug("DynamicOdds, userId =", self.player.userId, "testMode =", dynamicOdds1050TestMode,
        #             "tableFishPool =", self.table.runConfig.fishPool, "oddsFishPool =", fishPool)

    @property
    def chip(self):
        """持有金币（非实时数据库+内存金币）"""
        return self.player.holdCoin

    @property
    def currRechargeBonus(self):
        """
        当前充值奖池
        """
        bonus = 0
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return bonus
        if not self.player or not self.player.userId:
            return bonus
        # 新手期间使用奖池.
        # if self.isProtectMode():
        #     return bonus
        return self._currRechargeBonus          # 当前充值奖池

    def initConstData(self):
        """
        初始化常量数据
        """
        # 新手保护概率
        self.protectOdds = [1.0, 1.0, 1.3, 1.25, 1.1, 1.05, 1, 1]

        # 火炮-曲线低概率随机区间
        self.gunCurveLowSection = (0.25, 1.25)
        # 火炮-曲线高概率随机区间
        self.gunCurveHighSection = (0.3, 2.2)

        # 常规技能-曲线低概率随机区间
        self.norSkillCurveLowSection = (0.24, 1.5)
        # 常规技能-曲线高概率随机区间
        self.norSkillCurveHighSection = (0.5, 2.5)
        # 常规技能-非曲线概率随机区间
        self.norSkillNonCurveSection = (0.32, 1.55)

        # 汇能弹、激光炮、猎鱼机甲、格林机关枪
        self.spSkills = [5106, 5108, 5109, 5110]
        # 特殊技能-曲线低概率区间((概率系数, 出现概率))
        self.spSkillCurveLowSection = ((1.35, 0.05), (1.05, 0.65), (0.5, 0.3))
        # 特殊技能-曲线高概率区间((概率系数, 出现概率))
        self.spSkillCurveHighSection = ((3.9, 0.1), (1.5, 0.7), (0.8, 0.2))
        # 特殊技能-非曲线概率区间((概率系数, 出现概率))
        self.spSkillNonCurveSection = ((1.5, 0.1), (1.05, 0.7), (0.3, 0.2))

        # 黑名单概率
        self.banOddsList = config.getPublic("banOddsList", [])
        self.fireBanOdds = 0.5
        self.skillBanOdds = 0.5

    def initVarData(self):
        """
        初始化变量数据
        """
        # 波动曲线ID
        self.waveId = 0
        # 波动曲线位置
        self.waveIndex = 0
        # 波动单位基数
        self.waveRadix = 0
        # 波动金币
        self.waveCoin = 0
        # 曲线
        self.frequency = []
        # 曲线频点
        self.frequencyPoint = 0
        # 目标金币列表
        self.targetCoins = []
        # 当前目标金币
        self.targetCoin = 0
        # 原始充值奖池
        self._originRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.rechargeBonus)
        # 当前充值奖池
        self._currRechargeBonus = self._originRechargeBonus
        # 破产AB测试模式
        self._bankruptTestMode = gamedata.getGameAttr(self.player.userId, FISH_GAMEID, ABTestData.bankruptTestMode)
        # 扣除的充值奖池
        self.decreasedRechargeBonus = 0
        # 初始额外奖池
        self._orginExtraRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.extraRechargePool)

    def isProtectMode(self):
        """
        是否在新手保护期间
        """
        protectLevel = len(self.protectOdds)
        if self._bankruptTestMode == "b":
            protectLevel = min(7, protectLevel)
        if self.player.level <= protectLevel:       # len(self.protectOdds):
            return True
        return False

    def refreshOdds(self):
        """
        刷新动态概率数据
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        if self.isProtectMode():
            return
        data = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, GameData.dynamicOdds, {})
        oddsData = data.get(str(self.fishPool), [])
        if oddsData:
            self.loadDynamicOddsData(oddsData[WAVE_ID])
            self.waveIndex = oddsData[WAVE_INDEX]
            self.computeTargetCoins(oddsData[WAVE_RADIX])
            self.refreshTargetCoin()
            self.waveCoin = oddsData[WAVE_COIN]
            # # 该玩家重置波动金币值.
            # if self.player.userId == 100350041 and self.waveCoin < 0:
            #     tmp_reset_odds = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, "tmp_reset_odds", [])
            #     if int(self.table.runConfig.fishPool) not in tmp_reset_odds:
            #         self.waveCoin = 0
            #         tmp_reset_odds.append(int(self.table.runConfig.fishPool))
            #         gamedata.setGameAttr(self.player.userId, FISH_GAMEID, "tmp_reset_odds", json.dumps(tmp_reset_odds))
        else:
            waveId = 1
            pass

    def saveDynamicOddsData(self):
        pass


    def getOdds(self, skill=None, superBullet=None, aloofFish=False, gunConf=None):
        """
        获得概率
        :param skill: 是否技能
        :param superBullet: 是否超级子弹
        :param aloofFish: 是否高冷鱼
        :param gunConf: 当前装备火炮配置
        :return: 返回概率系数 1、1.3、1.25
        """
        # 2倍场使用低概率.
        # if self.table.bigRoomId == 44401:
        #     return 0.25
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            # 大奖赛使用高冷模式
            if self.table.typeName == config.FISH_GRAND_PRIX:
                aloofFish = True
            else:
                return 1
        if not self.player or not self.player.userId:
            return 1
        if self.isProtectMode():
            return self.protectOdds[self.player.level - 1]
        if self.table.typeName == config.FISH_NEWBIE and self.chip <= 50:
            return 10000

        if skill:
            if self.player.userId in self.banOddsList:      # 黑名单概率
                odds = self.skillBanOdds                    # 0.5
            else:
                if superBullet:                             # 超级子弹
                    odds = 1
                else:
                    if aloofFish:
                        odds = self.getNorSkillNonCurveOdds()
                    else:
                        odds = self.getNorSkillCurveOdds()
        else:
            if self.player.userId in self.banOddsList:
                odds = self.fireBanOdds
            else:
                if superBullet:
                    odds = 1
                else:
                    if aloofFish:
                        odds = self.getGunNonCurveOdds(gunConf)
                    else:
                        odds = self.getGunCurveOdds()
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->getOdds->",
                        "userId =", self.player.userId,
                        "odds =", odds,
                        "skill =", skill,
                        "superBullet =", superBullet,
                        "aloofFish =", aloofFish,
                        "gunConf =", gunConf)
        return odds

    def changeOdds(self):
        """
        切换曲线
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        fishPool = self.player.matchingFishPool
        if fishPool == self.fishPool:
            return
        ftlog.debug("changeOdds, userId =", self.player.userId, "lastFishPool =", self.fishPool, "curFishPool =", fishPool)
        pass
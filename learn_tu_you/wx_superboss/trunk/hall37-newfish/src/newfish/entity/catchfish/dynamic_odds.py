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
        self.fishPool = self.table.runConfig.fishPool
        self.minWaveRadix = self.table.runConfig.minWaveRadix
        self.maxWaveRadix = self.table.runConfig.maxWaveRadix
        self.dynamicOddsMap = config.getDynamicOddsConf(self.fishPool)
        self.initConstData()
        self.initVarData()
        self.refreshOdds()

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
        return self._currRechargeBonus

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
        else:
            waveId = 6
            self.resetOdds(waveId)
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->refreshOdds->",
                        "userId =", self.player.userId,
                        "chip =", self.chip,
                        "waveId =", self.waveId,
                        "waveIndex =", self.waveIndex,
                        "targetCoins =", self.targetCoins,
                        "waveCoin =", self.waveCoin)

    def getWaveList(self, type=None):
        """
        获取指定类型曲线的列表
        """
        if type == "high":
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems() if dynamicOdds["type"] > 0]
        elif type == "low":
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems() if dynamicOdds["type"] < 0]
        else:
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems()]
        return dynamicOddsList

    def getWaveId(self, type=None):
        """
        确定曲线ID
        :param type: 曲线类型(涨跌)
        """
        if type == "high":
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems() if dynamicOdds["type"] > 0]
        elif type == "low":
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems() if dynamicOdds["type"] < 0]
        else:
            dynamicOddsList = [dynamicOdds for _, dynamicOdds in self.dynamicOddsMap.iteritems()]

        totalWeight = sum([dynamicOdds["weight"] for dynamicOdds in dynamicOddsList])
        randomNum = random.randint(1, totalWeight)
        for dynamicOdds in dynamicOddsList:
            randomNum -= dynamicOdds["weight"]
            if randomNum <= 0:
                return dynamicOdds["waveId"]

    def getWaveRadix(self):
        """
        确定波动单位基数
        """
        allChip = self.player.allChip
        waveRadix = int(self.minWaveRadix + (allChip - self.minWaveRadix) * self.table.runConfig.waveRadixRate)
        waveRadix = min(max(waveRadix, self.minWaveRadix), self.maxWaveRadix)
        if ftlog.is_debug():
            ftlog.debug("getWaveRadix->",
                        "userId =", self.player.userId,
                        "waveRadix =", waveRadix,
                        "allChip =", allChip,
                        "minWaveRadix =", self.minWaveRadix,
                        "maxWaveRadix =", self.maxWaveRadix,
                        "waveRadixRate =", self.table.runConfig.waveRadixRate)
        return waveRadix

    def resetOdds(self, waveId=None):
        """
        重置动态概率数据
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        if self.isProtectMode():
            return
        recentWaveStateDict = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, GameData.recentWaveStateDict, {})
        recentWaveStateList = recentWaveStateDict.get(str(self.fishPool), [])
        if waveId is None:
            if recentWaveStateList.count("low") >= 3:
                waveId = self.getWaveId("high")
            elif recentWaveStateList.count("high") >= 3:
                waveId = self.getWaveId("low")
            else:
                waveId = self.getWaveId()
        dynamicOdds = self.dynamicOddsMap[str(waveId)]
        if dynamicOdds["type"] > 0:
            recentWaveStateList.append("high")
        elif dynamicOdds["type"] < 0:
            recentWaveStateList.append("low")
        else:
            recentWaveStateList.append("balance")
        recentWaveStateDict[str(self.fishPool)] = recentWaveStateList[-3:]
        gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.recentWaveStateDict, json.dumps(recentWaveStateDict))

        self.waveIndex = 0
        self.loadDynamicOddsData(waveId)
        self.computeTargetCoins(self.getWaveRadix())
        self.refreshTargetCoin()
        self.saveDynamicOddsData()
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->resetOdds->", "userId =", self.player.userId, "waveId =", waveId)

    def updateOdds(self, profitCoin):
        """
        更新概率
        :param profitCoin: 每次开火盈亏值
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        if self.isProtectMode():
            return
        if self.player.userId in self.banOddsList:
            return
        if not self.frequency or not self.targetCoins:  # 刚度过新手保护期后走高概率曲线
            self.refreshOdds()
        self.waveCoin += int(profitCoin)
        if self.getWaveState():
            if self.waveCoin >= self.targetCoin:
                self.waveCoin -= self.targetCoin
                self.moveOddsIndex()
        else:
            if self.waveCoin <= self.targetCoin:
                self.waveCoin -= self.targetCoin
                self.moveOddsIndex()
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->updateOdds->",
                        "userId =", self.player.userId,
                        "waveId", self.waveId,
                        "waveIndex", self.waveIndex,
                        "frequencyPoint =", self.frequencyPoint,
                        "profitCoin =", profitCoin,
                        "waveCoin =", self.waveCoin,
                        "targetCoin =", self.targetCoin,
                        "waveState =", self.getWaveState())

    def moveOddsIndex(self):
        """
        移动曲线节点
        """
        self.waveIndex += 1
        if self.waveIndex >= len(self.frequency):
            self.resetOdds()
        elif self.frequency[self.waveIndex] == 1:
            self.moveOddsIndex()
        else:
            self.refreshTargetCoin()
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->moveOddsIndex->",
                        "userId =", self.player.userId,
                        "waveIndex =", self.waveIndex)

    def getOdds(self, skill=None, superBullet=None, aloofFish=False, gunConf=None):
        """
        获得概率
        :param skill: 是否技能
        :param superBullet: 是否超级子弹
        :param aloofFish: 是否高冷鱼
        :param gunConf: 当前装备火炮配置
        :return: 返回概率系数 1、1.3、1.25
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return 1
        if not self.player or not self.player.userId:
            return 1
        if self.isProtectMode():
            return self.protectOdds[self.player.level - 1]
        if skill:
            if self.player.userId in self.banOddsList:      # 黑名单概率
                odds = self.skillBanOdds                    # 0.5
            else:
                if skill.skillId in self.spSkills:
                    if aloofFish:
                        odds = self.getSpSkillNonCurveOdds()
                    else:
                        odds = self.getSpSkillCurveOdds()
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

    def getWaveState(self):
        """
        获得波动状态（当前涨跌）
        """
        return self.targetCoin >= 0

    def getGunCurveOdds(self):
        """
        火炮-曲线概率系数
        """
        if self.getWaveState():
            return random.uniform(self.gunCurveHighSection[0], self.gunCurveHighSection[1])
        else:
            return random.uniform(self.gunCurveLowSection[0], self.gunCurveLowSection[1])

    def getGunNonCurveOdds(self, gunConf):
        """
        火炮-非曲线概率系数
        """
        gunConf = gunConf or {}
        gunId = gunConf.get("gunId", 0)
        gunLevel = gunConf.get("gunLevel", 1)
        aloofOdds = config.getGunConf(gunId, self.player.clientId, gunLevel, self.table.gameMode).get("aloofOdds", [])
        probb = 0
        randomNum = random.randint(1, 10000)
        for oddsMap in aloofOdds:
            probb += oddsMap["probb"] * 10000
            if randomNum <= probb:
                return oddsMap["odds"]

    def getNorSkillCurveOdds(self):
        """
        常规技能-曲线概率系数
        """
        if self.getWaveState():
            return random.uniform(self.norSkillCurveHighSection[0], self.norSkillCurveHighSection[1])
        else:
            return random.uniform(self.norSkillCurveLowSection[0], self.norSkillCurveLowSection[1])

    def getNorSkillNonCurveOdds(self):
        """
        常规技能-非曲线概率系数
        """
        return random.uniform(self.norSkillNonCurveSection[0], self.norSkillNonCurveSection[1])

    def getSpSkillCurveOdds(self):
        """
        特殊技能-曲线概率系数
        """
        if self.getWaveState():
            oddsSection = self.spSkillCurveHighSection
        else:
            oddsSection = self.spSkillCurveLowSection
        randomNum = random.randint(1, 10000)
        probb = 0
        for oddsDetail in oddsSection:
            probb += oddsDetail[1] * 10000
            if randomNum <= probb:
                return oddsDetail[0]

    def getSpSkillNonCurveOdds(self):
        """
        特殊技能-非曲线概率系数
        """
        oddsSection = self.spSkillNonCurveSection
        randomNum = random.randint(1, 10000)
        probb = 0
        for oddsDetail in oddsSection:
            probb += oddsDetail[1] * 10000
            if randomNum <= probb:
                return oddsDetail[0]

    def computeTargetCoins(self, waveRadix):
        """
        计算所有目标金币列表
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        self.waveRadix = waveRadix
        self.targetCoins = []
        for frequencyPoint in self.frequency:
            targetCoin = int(self.waveRadix * (frequencyPoint - 1.0))
            self.targetCoins.append(targetCoin)
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->computeTargetCoins->",
                        "userId =", self.player.userId,
                        "waveRadix =", self.waveRadix,
                        "targetCoins =", self.targetCoins)

    def refreshTargetCoin(self):
        """
        刷新当前目标金币
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        self.frequencyPoint = self.frequency[self.waveIndex]
        self.targetCoin = self.targetCoins[self.waveIndex]
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->refreshTargetCoin->",
                        "userId =", self.player.userId,
                        "frequencyPoint =", self.frequencyPoint,
                        "targetCoin =", self.targetCoin)

    def loadDynamicOddsData(self, waveId):
        """
        根据曲线ID读取动态概率配置数据
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        if str(waveId) not in self.dynamicOddsMap:
            ftlog.error("loadDynamicOddsData error", self.player.userId, waveId)
            self.resetOdds()
            return
        dynamicOddsConf = self.dynamicOddsMap[str(waveId)]
        self.waveId = dynamicOddsConf["waveId"]
        self.frequency = dynamicOddsConf["frequency"]
        if ftlog.is_debug():
            ftlog.debug("DynamicOdds->loadDynamicOddsData->",
                        "userId =", self.player.userId,
                        "waveId =", self.waveId,
                        "frequency =", self.frequency)

    def saveDynamicOddsData(self):
        """
        保存动态概率配置数据
        """
        if not self.player or not self.player.userId:
            return
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return
        gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.rechargeBonus, self._currRechargeBonus)
        util.decreaseExtraceRechargeBonus(self.player.userId, self.decreasedRechargeBonus)
        self.decreasedRechargeBonus = 0
        if self.isProtectMode():
            return
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        if self.waveId:
            oddsData = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, GameData.dynamicOdds, {})
            oddsData[str(self.fishPool)] = [self.waveId, self.waveIndex, self.waveRadix, self.waveCoin]
            gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.dynamicOdds, json.dumps(oddsData))
            ftlog.info("saveDynamicOddsData->",
                        "userId =", self.player.userId,
                        "_originRechargeBonus =", self._originRechargeBonus,
                        "_currRechargeBonus =", self._currRechargeBonus,
                        "oddsData =", oddsData[str(self.fishPool)])

    def refreshRechargeOdds(self):
        """
        刷新充值概率数据
        """
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        if self._originRechargeBonus <= 0:
            self._originRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.rechargeBonus)
            self._currRechargeBonus = self._originRechargeBonus
        else:
            newestBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.rechargeBonus)
            self._currRechargeBonus += newestBonus - self._originRechargeBonus
            self._originRechargeBonus = self._currRechargeBonus
            gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.rechargeBonus, self._currRechargeBonus)
            ftlog.info("refreshRechargeOdds->",
                        "userId =", self.player.userId,
                        "newestBonus =", newestBonus,
                        "_originRechargeBonus =", self._originRechargeBonus,
                        "_currRechargeBonus =", self._currRechargeBonus)
        # 更新额外充值奖池,先按照额外充值奖池增加前的数据结算当前的扣除额外奖池，然后更新额外奖池和扣除奖池的数据.
        _orginExtraRechargeBonus = self._orginExtraRechargeBonus
        util.decreaseExtraceRechargeBonus(self.player.userId, min(_orginExtraRechargeBonus, self.decreasedRechargeBonus))
        self.decreasedRechargeBonus = 0
        self._orginExtraRechargeBonus = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.extraRechargePool)

    def addRechargeBonus(self, coin):
        """
        增加充值奖池
        """
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        # if self.isProtectMode():
        #     return
        self._currRechargeBonus += int(coin)
        if ftlog.is_debug():
            ftlog.debug("addRechargeBonus->",
                        "userId =", self.player.userId,
                        "_originRechargeBonus =", self._originRechargeBonus,
                        "_currRechargeBonus =", self._currRechargeBonus)

    def deductionRechargeBonus(self, coin):
        """
        扣减充值奖池
        """
        if self.table.typeName not in config.RECHARGE_BONUS_ROOM_TYPE:
            return
        if not self.player or not self.player.userId:
            return
        self._currRechargeBonus -= int(coin)
        self.decreasedRechargeBonus += int(coin)
        if ftlog.is_debug():
            ftlog.debug("deductionRechargeBonus->",
                        "userId =", self.player.userId,
                        "_originRechargeBonus =", self._originRechargeBonus,
                        "_currRechargeBonus =", self._currRechargeBonus,
                        "decreasedRechargeBonus =", self.decreasedRechargeBonus)

    def changeOdds(self):
        """
        切换曲线
        """
        if self.table.typeName not in config.DYNAMIC_ODDS_ROOM_TYPE:
            return
        self.saveDynamicOddsData()
        self.dynamicOddsMap = config.getDynamicOddsConf(self.fishPool)
        self.initVarData()
        self.refreshOdds()

    def triggerBankruptEvent(self, bankruptCount):
        """
        玩家破产
        """
        if self.fishPool == 44003:
            if bankruptCount <= 1:
                self.resetOdds()
        bireport.reportGameEvent("BI_NFISH_GE_BANKRUPT", self.player.userId, FISH_GAMEID, self.table.roomId,
                                 self.table.tableId, bankruptCount, self.player.level, 0, 0, [], self.player.clientId)


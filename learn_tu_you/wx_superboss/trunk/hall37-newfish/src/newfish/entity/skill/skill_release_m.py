# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/7/13.
技能在渔场中释放（千炮模式）
"""

import time
import random
import math
import json

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import gamedata, daobase
from newfish.entity import config, util, weakdata
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData, WeakData
from newfish.entity.skill.skill_release import SkillBase


class SkillBase_m(SkillBase):

    def updateSkillEnergy(self):
        """
        更新技能能量（通过奖池转换而来）
        """
        currRechargeBonus = self.player.dynamicOdds.currRechargeBonus
        if currRechargeBonus > 0:
            totalPower = float(self.power * self.powerRate)
            self.energy = min(currRechargeBonus / self.gunX, 0.5 * totalPower)
            self.player.dynamicOdds.deductionRechargeBonus(self.energy * self.gunX)

        if ftlog.is_debug():
            ftlog.debug(
                "updateSkillEnergy->",
                "userId =", self.player.userId,
                "energy =", self.energy
            )

    def _getFishProbbRadix(self, fishInfo, fishConf):
        if fishInfo["HP"] > 0:
            return fishConf["probb2"]
        return fishConf["probb1"]

    def normalCatchFish(self, bulletId, wpId, fIds, extends):
        """
        普通捕获算法
        """
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        gunX = self.player.getFireGunX(bulletId)
        fishes, fishesHPDict = self._sortedFishes(fIds, extends)
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        odds = self.player.dynamicOdds.getOdds(skill=self)
        realPower = self.originRealPower * odds
        for fId, probbRadix in fishes:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId, wpId)
            if not isOK:
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix)
            catchMap["HP"] = fishInfo["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                multiple = self.gunSkinMultiple
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple,
                                                                              multiple, bufferCoinAdd, gunX=gunX)
                catchMap["reason"] = 0
                if catchUserId == self.player.userId:
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
            else:
                if fId in fishesHPDict:
                    catch.append(catchMap)
                fishGainChip, fishGain = self.table.dealHitBossGain(self.totalPower, fId, self.player)
                if catchUserId == self.player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
        if ftlog.is_debug():
            ftlog.debug(
                "normalCatchFish->",
                "userId =", self.player.userId,
                "catch =", catch,
                "gain =", gain,
                "gainChip =", gainChip,
                "onceCostCoin =", self.onceCostCoin,
                "consumePower =", self.consumePower,
                "originRealPower =", self.originRealPower
            )
        return catch, gain, gainChip, exp

    def getSkillCatchProbb(self, fId, fIdsCount, realPower, probbRadix, aloofOdds=None, nonAloofOdds=None):
        """
        技能捕获鱼的概率
        :param fId: 鱼的ID
        :param fIdsCount: 鱼的数量
        :param realPower: 真实威力
        :param probbRadix: 鱼被捕获的概率数
        :param aloofOdds: 高冷鱼概率
        :param nonAloofOdds: 非高冷鱼概率
        :return: 捕获概率、剩余能量
        """
        fishInfo = self.table.fishMap[fId]
        fishHP = fishInfo["HP"]
        ftType = fishInfo["type"]
        coefficient = self.table.getProbbCoefficient(self.player, fishInfo)
        lossPower = 0
        # 概率参数为0时，无HP必定被捕获，有HP无法被捕获
        if probbRadix == 0:
            probb = 10000 if fishHP <= 0 else 0
        else:
            if realPower <= 0:
                probb = 0
            else:
                probb = realPower / probbRadix * 10000
                realPower -= probbRadix
        probb *= coefficient
        # 新手任务期间
        if self.table.typeName == config.FISH_NEWBIE and self.player.taskSystemUser:
            if self.player.redState and self.skillId == 5101:  # 合金飞弹
                useMissileCount = gamedata.getGameAttrInt(self.player.userId, FISH_GAMEID, GameData.useMissileCount)
                if useMissileCount < 10:
                    gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.useMissileCount, useMissileCount + 1)
                    probb = 10000
            # elif self.skillId == 5105:  # 榴弹炮
            #     if self.newbieUseTimes == 0:
            #         probb = max(4000, probb)
            #     elif taskId == 10006 and ftType not in config.BOSS_FISH_TYPE:
            #         probb = max(2000, probb)
        if ftlog.is_debug():
            ftlog.debug(
                "getSkillCatchProbb->",
                "userId =", self.player.userId,
                "skillId =", self.skillId,
                "probb =", probb,
                "fId =", fId,
                "fIdsCount =", fIdsCount,
                "fishType =", fishInfo["fishType"],
                "fishHP =", fishHP,
                "realPower =", realPower,
                "probbRadix =", probbRadix,
                "aloofOdds =", aloofOdds,
                "nonAloofOdds =", nonAloofOdds,
                "lossPower =", lossPower,
                "consumePower =", self.consumePower,
                "coefficient =", coefficient
            )
        return probb, realPower


class SkillMissile_m(SkillBase_m):
    """
    合金飞弹(5101)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        useMissileCount = gamedata.getGameAttr(self.player.userId, FISH_GAMEID, GameData.useMissileCount)
        if not useMissileCount or useMissileCount < 5 and self.gunX < 300:  # 前5个合金飞弹且炮倍低于300
            self.powerRate = 3
            useMissileCount = 1 if not useMissileCount else useMissileCount + 1
            gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.useMissileCount, useMissileCount)
        return self.normalCatchFish(bulletId, wpId, fIds, extends)

    def _sortedFishes(self, fIds, extends=None):
        """
        按照鱼的捕获概率排序
        """
        fishesDict = {}
        fishesHPDict = {}
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            fishInfo = self.table.fishMap[fId]
            originHP = fishInfo["HP"]
            fishType = fishInfo["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP)
            fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
            if originHP != fishHP:
                fishesHPDict[fId] = originHP
        # 网中的鱼数量大于5时从小到大排序;反之从大到小.
        fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1], reverse=(len(fishesDict) <= 5))
        if ftlog.is_debug():
            ftlog.debug(self.skillId, ", _sortedFishes->", fishes, fishesHPDict, fIds)
        return fishes, fishesHPDict

class SkillCannon_m(SkillBase_m):
    """
    火蛇加农炮(5103)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        gunX = self.player.getFireGunX(bulletId)
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        odds = self.player.dynamicOdds.getOdds(skill=self)
        realPower = self.originRealPower * odds
        for fId in fIds:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId)
            if not isOK or self.impale <= 0:
                break
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            fishType = fishInfo["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            originHP = fishInfo["HP"]
            probbRadix = fishInfo["HP"] + fishConf["probb2"]
            if self.impale > probbRadix:  # 子弹能穿刺鱼
                self.impale -= probbRadix
                self.impale = max(self.impale, 0)
                randInt = random.randint(1, 10000)
                if randInt <= 9000 or self.impaleCatch:
                    catchMap["reason"] = 0
                if ftlog.is_debug():
                    ftlog.debug(
                        "SkillCannon_m->impale->",
                        "userId =", self.player.userId,
                        "randInt =", randInt,
                        "fId =", fId,
                        "fishType =", fishInfo["fishType"],
                        "probbRadix =", probbRadix,
                        "impale =", self.impale
                    )
            else:  # 子弹无法穿刺鱼
                realPower += self.impale
                self.impale = 0
                self.deductionHP = self.totalPower
                fishHP = int(originHP - self.deductionHP)
                self.table.dealFishHP(fId, fishHP)
                probbRadix = self._getFishProbbRadix(fishInfo, fishConf)
                probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix)
                randInt = random.randint(1, 10000)
                if randInt <= probb:
                    catchMap["reason"] = 0
            catchMap["HP"] = fishInfo["HP"]
            if catchMap["reason"] == 0:
                multiple = self.gunSkinMultiple
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple,
                                                                              multiple, bufferCoinAdd, gunX=gunX)
                if catchUserId == self.player.userId:
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain,
                                                                 catchMap, fishExp)
            else:
                if originHP != catchMap["HP"]:
                    catch.append(catchMap)
                fishGainChip, fishGain = self.table.dealHitBossGain(self.power + self.impale, fId, self.player)
                if catchUserId == self.player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain)
        if ftlog.is_debug():
            ftlog.debug("catchFish->",
                        "userId =", self.player.userId,
                        "catch =", catch,
                        "gain =", gain,
                        "onceCostCoin =", self.onceCostCoin)
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp


class SkillGrenade_m(SkillBase_m):
    """
    榴弹炮(5105)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        return self.normalCatchFish(bulletId, wpId, fIds, extends)

    def _sortedFishes(self, fIds, extends=None):
        fishesDict = {}
        fishesHPDict = {}
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            fishInfo = self.table.fishMap[fId]
            originHP = fishInfo["HP"]
            fishType = fishInfo["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            fatal = self.table.dealIceConeEffect(fId, fishConf)
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP, fatal)
            fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
            if originHP != fishHP:
                fishesHPDict[fId] = originHP
        # 从大到小排序.
        fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1], reverse=True)
        return fishes, fishesHPDict

    def returnClip(self):
        """
        打空返还技能子弹
        """
        if self.state == 2:
            if self.clip < self.originClip:
                self.clip += 1
                self.updateSkillData()


class SkillEnergy_m(SkillBase_m):
    """
    汇能弹(5106)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        gunX = self.player.getFireGunX(bulletId)
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        odds = self.player.dynamicOdds.getOdds(skill=self)
        realPower = self.originRealPower * odds
        for fId in fIds:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId)
            if not isOK or self.impale <= 0:
                break
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            fishType = fishInfo["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            originHP = fishInfo["HP"]
            probbRadix = fishInfo["HP"] + fishConf["probb2"]
            if self.impale > probbRadix:  # 子弹能穿刺鱼
                self.impale -= probbRadix
                self.impale = max(self.impale, 0)
                randInt = random.randint(1, 10000)
                if randInt <= 9000 or self.impaleCatch:
                    catchMap["reason"] = 0
                if ftlog.is_debug():
                    ftlog.debug(
                        "SkillEnergy_m->impale->",
                        "userId =", self.player.userId,
                        "randInt =", randInt,
                        "fId =", fId,
                        "fishType =", fishInfo["fishType"],
                        "probbRadix =", probbRadix,
                        "impale =", self.impale
                    )
            else:  # 子弹无法穿刺鱼
                realPower += self.impale
                self.impale = 0
                self.deductionHP = self.totalPower
                fishHP = int(originHP - self.deductionHP)
                self.table.dealFishHP(fId, fishHP)
                probbRadix = self._getFishProbbRadix(fishInfo, fishConf)
                probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix)
                randInt = random.randint(1, 10000)
                if randInt <= probb:
                    catchMap["reason"] = 0
            catchMap["HP"] = fishInfo["HP"]
            if catchMap["reason"] == 0:
                multiple = self.gunSkinMultiple
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple,
                                                                              multiple, bufferCoinAdd, gunX=gunX)
                if catchUserId == self.player.userId:
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain,
                                                                 catchMap, fishExp)
            else:
                if originHP != catchMap["HP"]:
                    catch.append(catchMap)
                fishGainChip, fishGain = self.table.dealHitBossGain(self.power + self.impale, fId, self.player)
                if catchUserId == self.player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain)
        if ftlog.is_debug():
            ftlog.debug("catchFish->",
                        "userId =", self.player.userId,
                        "catch =", catch,
                        "gain =", gain,
                        "onceCostCoin =", self.onceCostCoin)
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp


class SkillLaser_m(SkillBase_m):
    """
    激光炮(5108)
    """
    def costClip(self, bulletId, fPosx=0, fPosy=0):
        """
        消耗技能子弹
        """
        if self.clip > 0:
            for val in self.player.usingSkill:  # 当前技能使用中时，检测之前技能是否在使用中，如果是，结束之前技能
                skillId = val.get("skillId")
                if skillId != self.skillId:
                    skill = self.player.getSkill(skillId)
                    if skill.state == 2:
                        skill.end()
            self.state = 2
            self.clip -= 1
            self.position[bulletId] = [fPosx, fPosy]
            return True
        return False

    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        if not extends:
            return catch, gain, gainChip, exp
        self.consumePower = 0
        self.powerRate = self.getPowerRate(extends)
        self.updateSkillData()
        gunX = self.player.getFireGunX(bulletId)
        fishes, fishesHPDict = self._sortedFishes(fIds, extends)
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        odds = self.player.dynamicOdds.getOdds(skill=self)
        realPower = self.originRealPower * odds
        for fId, probbRadix in fishes:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId, wpId)
            if not isOK:
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix)
            catchMap["HP"] = fishInfo["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                multiple = self.gunSkinMultiple
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple,
                                                                              multiple, bufferCoinAdd, gunX=gunX)
                catchMap["reason"] = 0
                if catchUserId == self.player.userId:
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain,
                                                                 catchMap, fishExp)
            else:
                if fId in fishesHPDict:
                    catch.append(catchMap)
                count, fishGain, fishGainChip = extends[0], [], 0
                if count == 1:  # 只有第一次算捕获
                    fishGainChip, fishGain = self.table.dealHitBossGain(self.totalPower, fId, self.player)
                if catchUserId == self.player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain)
        if ftlog.is_debug():
            ftlog.debug("catchFish->",
                        "userId =", self.player.userId,
                        "catch =", catch,
                        "gain =", gain,
                        "onceCostCoin =", self.onceCostCoin * self.powerRate)
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp

    def _sortedFishes(self, fIds, extends=None):
        count = extends[0]
        fishesDict = {}
        fishesHPDict = {}
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            fishInfo = self.table.fishMap[fId]
            originHP = fishInfo["HP"]
            fishType = fishInfo["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP)
            fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
            if originHP != fishHP:
                fishesHPDict[fId] = originHP
        if count <= 2:
            fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1])
        else:
            fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1], reverse=True)
        if ftlog.is_debug():
            ftlog.debug("_sortedFishes->", fishes, fishesHPDict, fIds)
        return fishes, fishesHPDict

    def getPowerRate(self, extends):
        count = extends[0]
        if count == 1:
            powerRate = 0.2
        elif count == 2:
            powerRate = 0.3
        elif count == 3:
            powerRate = 0.5
        else:
            powerRate = 0.2
            ftlog.error("getPowerRate error", self.player.userId, extends)
        return powerRate


class SkillHunt_m(SkillBase_m):
    """
    猎鱼机甲(5109)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch, gain, gainChip, exp = [], [], 0, 0
        if wpId == 2209:  # 释放猎鱼机甲
            position = self.position.get(bulletId, [0, 0])
            endTime = time.time() + self.duration
            buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0]
            group = self.table.insertFishGroup("call_robot", position, self.HP, buffer,
                                               gameResolution=self.player.gameResolution)
            self.durationEndTime = endTime
            self.onceCostCoin /= int(self.duration / self.interval)
            if group:
                self.skillFishes.append(group.startFishId)
        elif wpId == 2301:  # 猎鱼机甲开火
            if self.originRealPower and time.time() <= self.durationEndTime:
                return self.normalCatchFish(bulletId, wpId, fIds, extends)
        return catch, gain, gainChip, exp


class SkillGatling_m(SkillBase_m):
    """
    格林机关枪(5110)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        return self.normalCatchFish(bulletId, wpId, fIds, extends)

    def returnClip(self):
        """
        打空返还技能子弹
        """
        if self.state == 2:
            if self.clip < self.originClip:
                self.clip += 1
                self.updateSkillData()


skillMap = {
    5101: SkillMissile_m,     # 合金飞弹
    # 5102: SkillMagic,       # 魔术炮
    5103: SkillCannon_m,      # 火蛇加农炮
    # 5104: SkillFrozen,      # 极冻炮
    5105: SkillGrenade_m,     # 榴弹炮
    5106: SkillEnergy_m,      # 汇能弹
    # 5107: SkillFraud,       # 欺诈水晶
    5108: SkillLaser_m,       # 激光炮
    5109: SkillHunt_m,        # 猎鱼机甲
    5110: SkillGatling_m      # 格林机关枪
}


def createSkill(table, player, skillId, skillState, skillStar, skillGrade, skillType=0):
    skillClass = skillMap.get(skillId)
    skill = None
    if skillClass:
        skill = skillClass(table, player, skillId, skillState, skillStar, skillGrade, skillType)
    return skill
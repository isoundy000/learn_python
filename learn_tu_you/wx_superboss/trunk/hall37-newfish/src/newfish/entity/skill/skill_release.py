# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
技能在渔场中释放
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
from hall.entity import hallranking


class SkillBase(object):

    def __init__(self, table, player, skillId, skillState, skillStar, skillGrade, skillType=0):
        self.table = table
        self.player = player
        self.skillId = skillId
        self.skillState = skillState                        # 技能状态
        self.skillStar = skillStar                          # 技能星级
        self.skillGrade = skillGrade                        # 技能等级
        self.skillGrade = self.getRealEffectSkillGrade()    # 玩家在欢乐竞技和王者争霸中夺冠，则下次比赛中使用该技能降级
        self.skillType = skillType                          # 技能类型（0:主技能 1:辅助技能）
        self.skillMode = self.table.gameMode                # 0:经典 1:千炮
        self.position = {}                                  # [bulletId] = [fPosx, fPosy]
        self.initData()                                     # 初始化技能数据
        self.initState()                                    # 初始化技能状态

    def initLevel(self):
        """
        初始化等级属性数据
        """
        skillGradeConf = config.getSkillGradeConf(self.skillId, self.skillGrade, self.skillMode)
        self.cost = skillGradeConf.get("cost", 0)
        self.power = skillGradeConf.get("power", 0)
        self.HP = skillGradeConf.get("HP", 0)
        self.impale = skillGradeConf.get("impale", 0)
        self.clip = skillGradeConf.get("clip", 0)
        self.interval = skillGradeConf.get("interval", 0)
        self.duration = skillGradeConf.get("duration", 0)
        self.coolDown = skillGradeConf.get("coolDown", 0)
        self.range = skillGradeConf.get("range", 0)
        self.weaponId = skillGradeConf.get("weaponId", 0)
        self.double = skillGradeConf.get("double", [])
        self.isReturn = skillGradeConf.get("isReturn", 0)

    def initStar(self):
        """
        初始化星级属性数据
        """
        self.fatal = 0
        self.distance = False
        self.impaleCatch = False
        self.gunSkinMultiple = 1
        self.dayFreeMaxMulti = 0
        for skillStar in xrange(1, self.skillStar + 1):
            skillStarConf = config.getSkillStarConf(self.skillId, skillStar, self.skillMode)
            for abilityConf in skillStarConf["abilities"]:
                ability = abilityConf.get("ability", 0)
                value = abilityConf.get("value", 0)
                if ability == 1:                                # 减少冷却时间
                    self.coolDown -= value
                elif ability == 2:                              # 提高威力
                    self.power += self.power * value / 100
                elif ability == 3:                              # 增加技能效果时间
                    self.duration += value
                elif ability == 6:                              # 增加子弹数
                    self.clip += value
                elif ability == 7:                              # 增加机器人HP
                    self.HP += self.HP * value / 100
                elif ability == 8:                              # 提高对远距离鱼的威力
                    self.distance = True
                elif ability == 9:                              # 冰锥HP在65%以上时无法一击致命
                    self.fatal += value / 100
                elif ability == 10:                             # 被贯穿的鱼必被捕获
                    self.impaleCatch = True
                elif ability == 13:                             # 提升火蛇加农炮喷射距离
                    self.range += self.range * value / 100
                elif ability == 25:                             # 每天可在最高[var]倍下免费使用1次
                    self.dayFreeMaxMulti = value
        if self.table.typeName in config.NORMAL_ROOM_TYPE:      # 新手/普通/好友渔场-皮肤炮特性，技能双倍消耗/收益
            self.gunSkinMultiple = 2 if self.player.gunId in self.double else 1
            if self.table.typeName == config.FISH_GRAND_PRIX and self.player.isGrandPrixMode():  # 大奖赛冷却减半
                self.coolDown //= 2
                if self.skillType == 1:
                    self.cost = 0
        elif self.table.typeName in [config.FISH_TIME_MATCH, config.FISH_TIME_POINT_MATCH]: # 回馈赛-弹药消耗为0，冷却减半
            self.cost = 0
        elif self.table.typeName == config.FISH_FIGHT:          # 渔友竞技-冷却减半
            self.coolDown //= 2
        self.coolDown = max(self.coolDown, 1)

    def initCommonData(self):
        """
        初始化公共数据
        """
        self.fpMultiple = self.player.fpMultiple
        self.skillMultiple = 1
        # 格林机关枪除回馈赛外收益翻倍
        if self.skillId == 5110 and self.table.typeName != config.FISH_TIME_POINT_MATCH:
            self.skillMultiple = 2
        self.gunSkinMultiple *= self.skillMultiple
        self.gunX = util.getGunX(self.player.nowGunLevel, self.skillMode)
        self.powerRate = 1                                  # 技能威力倍率
        self.durationEndTime = 0                            # 技能效果结束时间
        self.skillFishes = []                               # 技能召唤的鱼(捕鱼机器人)
        self.originClip = self.clip                         # 技能原始总子弹数
        self.originEnergy = 0                               # 技能单发原始能量
        self.energy = 0                                     # 技能单发扣减能量
        self.totalPower = 0                                 # 技能总威力（无加成）
        self.originRealPower = 0                            # 技能总威力（加能量）
        self.deductionHP = 0                                # 技能扣减HP
        self.consumePower = 0                               # 技能曲线消耗能量
        self.onceCostCoin = self.getCost / float(self.originClip) * self.fpMultiple  # 技能单发价值金币数
        # 新手期间技能使用次数
        _key = UserData.newbieUseSkillTimes % (FISH_GAMEID, self.player.userId)
        self.newbieUseTimes = daobase.executeUserCmd(self.player.userId, "HGET", _key, str(self.skillId)) or 0

    def initData(self):
        """
        初始化技能数据
        """
        self.initLevel()
        self.initStar()
        self.initCommonData()

    def initState(self):
        """
        初始化技能状态
        """
        self.state = 0                                      # 0:未使用 1:装备中 2:使用中
        self.cdStartTime = int(time.time())                 # 技能冷却开始时的时间
        self.usingDayFree = False                           # 是否每日免费装备中

    def use(self, select):
        """
        选中取消技能
        """
        eventId = None
        orgState = self.state
        if select:
            if self.state == 0:
                if self.player.gchgTimer:
                    self.player.gchgTimer.cancel()
                self.state = 1
                self.clear()
                self.initData()
                if self.checkIfDayFree():
                    # 每日免费使用
                    self.doDayFreeUse()
                    self.usingDayFree = True
                else:
                    self.player.costClip(self.getCost, "BI_NFISH_USE_SKILL_%d" % self.skillId)
                self.player.addUsingSkill(self.skillId, self.skillType)
                eventId = "BI_NFISH_GE_SKILL_USE"
        else:
            if self.state == 1:
                if self.usingDayFree:
                    self.cancelDayFreeUse()
                else:
                    self.player.addClip(self.getCost, 0, self.skillId)
                self.state = 0
                self.player.removeUsingSkill(self.skillId, self.skillType)
                eventId = "BI_NFISH_GE_SKILL_CANCEL"
        self.table.broadcastSkillUse(self, select, self.player.userId, orgState)
        if config.LOCK_KINDID in self.player.skill_item:
            self.player.skill_item[config.LOCK_KINDID].pause_and_continue_time(config.LOCK_KINDID)
        self.player.gunEffectState(2)
        if eventId:
            bireport.reportGameEvent(eventId, self.player.userId, FISH_GAMEID, self.table.roomId,  self.table.tableId,
                                     int(self.skillId), self.player.level, 1 if self.usingDayFree else 0, 0, [], self.player.clientId)
            ftlog.info(
                "skill_release->use",
                "userId =", self.player.userId,
                "eventId =", eventId,
                "skillId =", self.skillId,
                "skillStar =", self.skillStar,
                "skillGrade =", self.skillGrade,
                "skillType =", self.skillType,
                "gunId =", self.player.gunId,
                "nowGunLevel =", self.player.nowGunLevel,
                "isDayFree =", self.usingDayFree
            )

    def end(self):
        """
        结束技能
        """
        if ftlog.is_debug():
            ftlog.debug("skill end, userId =", self.player.userId, "skillId =", self.skillId, "useTimes =", self.newbieUseTimes)
        if self.table.typeName == config.FISH_NEWBIE and not self.player.redState:
            _key = UserData.newbieUseSkillTimes % (FISH_GAMEID, self.player.userId)
            daobase.executeUserCmd(self.player.userId, "HINCRBY", _key, str(self.skillId), 1)
        self.initState()
        self.player.removeUsingSkill(self.skillId, self.skillType)
        self.table.broadcastSkillEnd(self)
        if config.LOCK_KINDID in self.player.skill_item:        # 锁定继承开始时间计时
            self.player.skill_item[config.LOCK_KINDID].pause_and_continue_time(config.LOCK_KINDID)
        self.player.syncSkillItemSlots()
        self.player.gunEffectState(2)
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            # 使用技能事件
            from newfish.game import TGFish
            from newfish.entity.event import UseSkillEvent
            chip = int(self.getCost * self.fpMultiple)
            event = UseSkillEvent(self.player.userId, FISH_GAMEID, self.table.roomId, self.table.tableId, self.skillId, self.fpMultiple, chip)
            TGFish.getEventBus().publishEvent(event)
            self.player.triggerUseSkillEvent(event)

    def clear(self):
        """
        清除技能数据(广播捕鱼机器人因主人离开房间而死亡)
        """
        self.player.delFire(wpId=self.weaponId)
        if self.skillFishes:
            fishes = []
            for fishId in self.skillFishes:
                if fishId in self.table.fishMap and self.table.fishMap[fishId]["alive"]:
                    for buffer in self.table.fishMap[fishId]["buffer"]:
                        skillId = buffer[0]
                        skillEndTime = buffer[1]
                        if skillId == self.skillId and skillEndTime >= time.time():
                            if self.table.fishMap[fishId]["alive"]:
                                self.table.refreshFishTypeCount(self.table.fishMap[fishId])
                            self.table.fishMap[fishId]["alive"] = False
                            fishes.append(fishId)
            if fishes:
                self.table.broadcastSkillEffect(self.player, time.time(), fishes, self.skillId)

    def getSkillFishesAlive(self):
        """
        获取捕鱼机器人是否存活
        """
        if self.skillFishes:
            for fishId in self.skillFishes:
                if fishId in self.table.fishMap and self.table.fishMap[fishId]["alive"]:
                    for buffer in self.table.fishMap[fishId]["buffer"]:
                        skillId = buffer[0]
                        skillEndTime = buffer[1]
                        if skillId == self.skillId and skillEndTime >= time.time():
                            return True
        return False

    def costClip(self, bulletId, fPosx=0, fPosy=0):
        """
        消耗技能子弹
        """
        if self.clip > 0:
            lastCoin = self.player.holdCoin
            for val in self.player.usingSkill:      # 当前技能使用中时，检测之前技能是否在使用中，如果是，结束之前技能
                skillId = val.get("skillId")
                skillType = val.get("skillType")
                if skillId != self.skillId:
                    skill = self.player.getSkill(skillId)
                    if skill.state == 2:
                        skill.end()
            self.state = 2
            self.clip -= 1
            self.position[bulletId] = [fPosx, fPosy]
            self.updateSkillData()
            self.player.reportBIFeatureData("BI_NFISH_GE_FT_FIRE", self.weaponId, self.onceCostCoin)

            # TODO 该段代码有问题（lichen）
            if lastCoin > self.table.runConfig.coinShortage > self.player.holdCoin:
                coinShortageCount = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, GameData.coinShortageCount, {})
                coinShortageCount.setdefault(str(self.table.runConfig.fishPool), 0)
                coinShortageCount[str(self.table.runConfig.fishPool)] += 1
                gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.coinShortageCount, json.dumps(coinShortageCount))
            return True
        return False

    def returnClip(self):
        """
        返还技能打空子弹
        """
        pass

    def updateSkillData(self):
        """
        更新技能数据
        """
        self.updateSkillEnergy()
        skillGradeConf = config.getSkillGradeConf(self.skillId, self.skillGrade, self.skillMode)
        self.impale = skillGradeConf.get("impale", 0)
        powerAddtion = self.player.getPowerAddition(self.weaponId)
        self.totalPower = float(self.power * self.powerRate * powerAddtion)
        self.originRealPower = self.totalPower + self.energy
        self.deductionHP = self.totalPower
        if ftlog.is_debug():
            ftlog.debug(
                "updateSkillData->",
                "userId =", self.player.userId,
                "impale =", self.impale,
                "totalPower =", self.totalPower,
                "deductionHP =", self.deductionHP
            )

    def updateSkillEnergy(self):
        """
        更新技能能量（通过奖池转换而来）
        """
        bonus = 0
        if self.table.room.lotteryPool:
            bonus = self.table.room.lotteryPool.getSkillPoolCoin() // self.fpMultiple
        randomNum = random.uniform(0.5, 1.5)
        singleEnergy = math.ceil(self.power * self.powerRate * randomNum)
        self.originEnergy = min(self.player.energy, singleEnergy)
        self.energy = max(min(self.originEnergy, bonus), 0)
        self.player.energy -= self.energy
        if self.table.room.lotteryPool:
            self.table.room.lotteryPool.deductionSkillPoolCoin(int(self.energy * self.fpMultiple))
        if ftlog.is_debug():
            ftlog.debug(
                "updateSkillEnergy->",
                "userId =", self.player.userId,
                "bonus =", bonus,
                "randomNum =", randomNum,
                "singleEnergy =", singleEnergy,
                "originEnergy =", self.originEnergy,
                "energy =", self.energy,
                "player.energy =", self.player.energy
            )

    @property
    def getCost(self):
        """
        技能消耗子弹数
        """
        return self.cost * self.gunSkinMultiple / self.skillMultiple * self.gunX

    @property
    def cdTimeLeft(self):
        """
        技能剩余CD时间
        """
        timeLeft = self.cdStartTime + self.coolDown - int(time.time())
        return max(timeLeft, 0)

    def changeCDStartTime(self, coolDown=0):
        """
        改变技能CD的开始时间
        """
        cdAddition = self.player.getSkillCDAddition(self.weaponId)
        if coolDown:
            self.cdStartTime -= coolDown
        else:
            self.cdStartTime -= self.coolDown * cdAddition

    def catchFish(self, bulletId, wpId, fIds, extends):
        """
        技能捕获判定
        """
        raise NotImplementedError

    def normalCatchFish(self, bulletId, wpId, fIds, extends):
        """
        普通捕获算法
        """
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        isCatch = False
        self.consumePower = 0
        fishes, fishesHPDict = self._sortedFishes(fIds, extends)
        totalPowerRate = self.totalPower / self.originRealPower  # 技能总威力（无加成）的占比
        realPower = self.originRealPower
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        curveProfitCoin = 0
        aloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=True)
        nonAloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=False)
        for fId, probbRadix in fishes:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId, wpId)
            if not isOK:
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix, aloofOdds, nonAloofOdds)
            catchMap["HP"] = fishInfo["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                multiple = self.gunSkinMultiple
                # 欺诈只获得1倍收益.
                if catchUserId != self.player.userId:
                    multiple = 1
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple, multiple, bufferCoinAdd)
                catchMap["reason"] = 0
                if catchUserId == self.player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain, catchMap, fishExp)
            else:
                if fId in fishesHPDict:
                    catch.append(catchMap)
                fishGainChip, fishGain = self.table.dealHitBossGain(self.totalPower, fId, self.player)
                if catchUserId == self.player.userId:
                    gainChip += fishGainChip
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain)
            # 技能曲线
            if self.table.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
                fishType = fishInfo["fishType"]
                fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
                if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                    if catchMap["reason"] == 0:
                        curveProfitCoin += totalPowerRate * fishConf["value"] * self.gunSkinMultiple * self.fpMultiple
        self.consumePower = min(self.consumePower, self.originRealPower)
        curveLossCoin = self.onceCostCoin * self.consumePower / self.originRealPower
        if ftlog.is_debug():
            ftlog.debug(
                "normalCatchFish->",
                "userId =", self.player.userId,
                "catch =", catch,
                "gain =", gain,
                "gainChip =", gainChip,
                "onceCostCoin =", self.onceCostCoin,
                "consumePower =", self.consumePower,
                "originRealPower =", self.originRealPower,
                "totalPowerRate =", totalPowerRate,
                "curveLossCoin =", curveLossCoin,
                "curveProfitCoin =", curveProfitCoin
            )
        self.player.dynamicOdds.updateOdds(curveProfitCoin - curveLossCoin)
        if isCatch:
            self.player.addCombo()
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp

    def _getFishProbbRadix(self, fishInfo, fishConf):
        # 新手任务期间概率特殊处理
        if self.player and util.isNewbieRoom(self.player.table.typeName):
            curTaskId = self.player.taskSystemUser.curTask.getTaskId()
            isTaskOver = self.player.taskSystemUser.curTask.isTaskOver()
            probbRadix = config.getCommonValueByKey("newbieFishProbb").get(str(fishConf["type"]), {}).get(str(curTaskId))
            if not isTaskOver and probbRadix:
                if fishConf["type"] == 2:
                    if self.player.bossAppearCount > 1:
                        return probbRadix
                else:
                    return probbRadix
        if fishInfo["HP"] > 0:
            return fishConf["probb2"]
        elif fishConf["type"] in config.RAINBOW_BONUS_FISH_TYPE:
            value = fishConf["score"]
            gunMultiple = config.getGunConf(self.player.gunId, self.player.clientId, self.player.gunLv, self.table.gameMode).get("multiple", 1)
            rainbowPoolCoin = 0
            if self.table.room.lotteryPool:
                rainbowPoolCoin = self.table.room.lotteryPool.getRainbowPoolCoin()
            if fishConf["type"] in config.TERROR_FISH_TYPE:
                value = config.getWeaponConf(fishConf["weaponId"], False, self.table.gameMode)["power"]
            if self.player.dynamicOdds.currRechargeBonus >= value * gunMultiple * self.fpMultiple:
                # 存在充值奖池
                if ftlog.is_debug():
                    ftlog.debug("_getFishProbbRadix->currRechargeBonus =", self.player.dynamicOdds.currRechargeBonus, fishConf)
                return fishConf["probb1"]
            elif (min(3 * self.originEnergy * self.fpMultiple, rainbowPoolCoin) >= value * gunMultiple * self.fpMultiple):
                # 存在能量及彩虹鱼奖池
                if ftlog.is_debug():
                    ftlog.debug("_getFishProbbRadix->energy =", self.originEnergy, rainbowPoolCoin, fishConf)
                return fishConf["probb1"]
            return fishConf["probb2"]
        else:
            return fishConf["probb1"]

    def _sortedFishes(self, fIds, extends=None):
        """
        排序所有鱼
        :param fIds: 鱼的Ids
        :param extends: 扩展
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
            fatal = self.table.dealIceConeEffect(fId, fishConf)
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP, fatal)
            fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
            if originHP != fishHP:
                fishesHPDict[fId] = originHP
        fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1])
        if ftlog.is_debug():
            ftlog.debug("_sortedFishes->", fishes, fishesHPDict, fIds)
        return fishes, fishesHPDict

    def getSkillCatchProbb(self, fId, fIdsCount, realPower, probbRadix, aloofOdds, nonAloofOdds):
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
        odds = 0
        lossPower = 0
        # 概率参数为0时，无HP必定被捕获，有HP无法被捕获
        if probbRadix == 0:
            probb = 10000 if fishHP <= 0 else 0
        else:
            if realPower <= 0:
                probb = 0
            else:
                if ftType in config.NON_ALOOF_FISH_TYPE:
                    odds = nonAloofOdds
                else:
                    odds = aloofOdds
                if odds > 0:
                    lossPower = probbRadix / odds
                    if realPower >= lossPower:
                        probb = 10000
                    else:
                        probb = realPower / lossPower * 10000
                else:
                    lossPower = probbRadix * 2
                    probb = 0
                if ftType in config.NON_ALOOF_FISH_TYPE:
                    if realPower >= lossPower:
                        self.consumePower += lossPower
                    else:
                        self.consumePower += realPower
                realPower -= lossPower
        probb *= coefficient
        if ftType in config.RED_FISH_TYPE:
            probb *= self.player.catchRedFishProbbRatio
            if self.player.userId in config.getPublic("banRedFishList", []):
                probb *= 0.3
        if ftlog.is_debug():
            ftlog.debug(
                "getSkillCatchProbb->",
                "userId =", self.player.userId,
                "probb =", probb,
                "odds =", odds,
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

    def getRealEffectSkillGrade(self):
        """
        玩家在欢乐竞技和王者争霸中夺冠，则下次比赛中使用该技能降级
        """
        _skillGrade = self.skillGrade
        match_rank = None
        reductGrade = 0
        if self.table.runConfig.fishPool == 44102:
            reductGrade = 5
            match_rank = config.RANK_MATCH_HLJJ
        elif self.table.runConfig.fishPool == 44103:
            reductGrade = 8
            match_rank = config.RANK_MATCH_WZZB
        if match_rank and reductGrade:
            rankingList = hallranking.rankingSystem.getTopN(match_rank, 1, int(time.time()))
            if rankingList and len(rankingList.rankingUserList) > 0 and rankingList.rankingUserList[0].userId == self.player.userId:
                _skillGrade = max(1, _skillGrade - reductGrade)
        if ftlog.is_debug():
            ftlog.debug("getRealEffectSkillGrade, userId =", self.player.userId, "lastGrade =", self.skillGrade,
                    "curGrade =", _skillGrade, self.table.runConfig.fishPool, match_rank, reductGrade)
        return _skillGrade

    def checkIfDayFree(self):
        """检查技能是否免费"""
        if ftlog.is_debug():
            ftlog.debug("SkillBase.checkIfDayFree IN", "tableId=", self.table.tableId, "userId=", self.player.userId,
                        "dayFreeMaxMulti=", self.dayFreeMaxMulti, "gunX=", self.gunX)
        if self.table.typeName == config.FISH_TIME_MATCH or self.table.typeName == config.FISH_TIME_POINT_MATCH:
            return False
        self.gunX = util.getGunX(self.player.nowGunLevel, self.skillMode)
        if self.dayFreeMaxMulti >= self.gunX:
            data = weakdata.getDayFishData(self.player.userId, WeakData.skillFreeUseCount, {})
            if ftlog.is_debug():
                ftlog.debug("SkillBase.checkIfDayFree get data", "userId=", self.player.userId, "data=", data)
            if str(self.skillId) in data:
                # 目前固定每日免费1次，不走配置
                if data[str(self.skillId)] < 1:
                    return True
            else:
                return True
        return False

    def doDayFreeUse(self):
        """免费使用次数"""
        data = weakdata.getDayFishData(self.player.userId, WeakData.skillFreeUseCount, {})
        skillId = str(self.skillId)
        if skillId in data:
            data[skillId] += 1
        else:
            data[skillId] = 1
        weakdata.setDayFishData(self.player.userId, WeakData.skillFreeUseCount, data)
        return data[skillId]

    def cancelDayFreeUse(self):
        """取消免费使用的次数"""
        data = weakdata.getDayFishData(self.player.userId, WeakData.skillFreeUseCount, {})
        skillId = str(self.skillId)
        if skillId in data:
            data[skillId] -= 1
            weakdata.setDayFishData(self.player.userId, WeakData.skillFreeUseCount, data)
        return data.get(skillId, 0)


class SkillMissile(SkillBase):
    """
    合金飞弹(5101)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        """合金飞弹捕鱼"""
        useMissileCount = gamedata.getGameAttr(self.player.userId, FISH_GAMEID, GameData.useMissileCount)
        if not useMissileCount or useMissileCount < 5 and self.table.runConfig.fishPool == 44001:   # 普通渔场2倍爆炸威力增加5倍
            self.powerRate = 5
            useMissileCount = 1 if not useMissileCount else useMissileCount + 1
            gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.useMissileCount, useMissileCount)
        return self.normalCatchFish(bulletId, wpId, fIds, extends)

    def _sortedFishes(self, fIds, extends=None):
        """按照鱼的捕获概率排序"""
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
            fatal = self.table.dealIceConeEffect(fId, fishConf)         # 冰锥HP在65%以上时无法一击致命
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP, fatal)
            fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
            if originHP != fishHP:
                fishesHPDict[fId] = originHP
        # 网中的鱼数量大于5时从小到大排序;反之从大到小.
        fishes = sorted(fishesDict.iteritems(), key=lambda d: d[1], reverse=(len(fishesDict) <= 5))
        if ftlog.is_debug():
            ftlog.debug(self.skillId, ", _sortedFishes->", fishes, fishesHPDict, fIds)
        return fishes, fishesHPDict


class SkillMagic(SkillBase):
    """
    魔术炮(5102)
    """
    def initStar(self):
        super(SkillMagic, self).initStar()
        if self.table.typeName == config.FISH_TIME_MATCH:   # 回馈赛-召唤出的鱼永久无敌
            self.duration += 999
        elif self.table.typeName == config.FISH_TIME_POINT_MATCH:
            self.duration += 999

    def catchFish(self, bulletId, wpId, fIds, extends):
        catch, gain, gainChip, exp = [], [], 0, 0
        position = self.position.get(bulletId, [0, 0])
        buffer = None
        endTime = time.time() + self.duration
        fishType = 0
        if self.duration:
            buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0]
            fishes = self.player.getTargetFishs()
            if fishes:
                fishType = random.choice(fishes)
        _skillGrade = self.skillGrade                       # self.getRealEffectSkillGrade()
        commonRoom = config.NORMAL_ROOM_TYPE
        if (self.table.typeName in commonRoom and not fishType) or \
           (self.table.typeName not in commonRoom):         # 普通场无任务时或者非普通场召唤倍率鱼
            callFishList = config.getCallMultipleFishConf(_skillGrade, self.table.typeName, self.table.runConfig.fishPool)
            totalWeight = sum([dict(fishes)["weight"] for fishes in callFishList if fishes])
            fishType = 0                                    # callFishList[0]["fishType"]
            if totalWeight > 0:
                weight = random.randint(0, totalWeight)
                for callFish in callFishList:
                    if callFish["weight"] == 0:
                        continue
                    if callFish and weight - callFish["weight"] <= 0:
                        fishType = callFish["fishType"]
                        break
                    weight -= callFish["weight"]
        if fishType > 0:
            groupName = "call_%d_lv%d" % (fishType, _skillGrade)
            self.table.insertFishGroup(groupName, position, buffer=buffer, gameResolution=self.player.gameResolution)
            if ftlog.is_debug():
                ftlog.debug("SkillMagic, insertFishGroup, userId =", self.player.userId, groupName, self.skillGrade, _skillGrade)
        else:
            if ftlog.is_debug():
                ftlog.debug("catchFish, not find fishType !", self.player.userId)
        return catch, gain, gainChip, exp


class SkillCannon(SkillBase):
    """
    火蛇加农炮(5103)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        isCatch = False
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        realPower = self.originRealPower
        aloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=True)
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
                    ftlog.debug("SkillCannon->impale->",
                                "userId =", self.player.userId,
                                "randInt =", randInt,
                                "fId =", fId,
                                "fishType =", fishInfo["fishType"],
                                "probbRadix =", probbRadix,
                                "impale =", self.impale)
            else:  # 子弹无法穿刺鱼
                realPower += self.impale
                self.impale = 0
                fatal = self.table.dealIceConeEffect(fId, fishConf)
                self.deductionHP = self.totalPower
                fishHP = int(originHP - self.deductionHP)
                self.table.dealFishHP(fId, fishHP, fatal)
                probbRadix = self._getFishProbbRadix(fishInfo, fishConf)
                probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix, aloofOdds, aloofOdds)
                randInt = random.randint(1, 10000)
                if randInt <= probb:
                    catchMap["reason"] = 0
            catchMap["HP"] = fishInfo["HP"]
            if catchMap["reason"] == 0:
                multiple = self.gunSkinMultiple
                # 欺诈只获得1倍收益.
                if catchUserId != self.player.userId:
                    multiple = 1
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple, multiple, bufferCoinAdd)
                if catchUserId == self.player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain, catchMap, fishExp)
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
                        "onceCostCoin =", self.onceCostCoin,
                        "originRealPower =", self.originRealPower)
        if isCatch:
            self.player.addCombo()
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp


class SkillFrozen(SkillBase):
    """
    极冻炮(5104)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        position = self.position.get(bulletId, [0, 0])
        endTime = time.time() + self.duration
        invincibleEndTime = 0
        frozenBuffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0]
        self.table.insertFishGroup("call_piton_%d" % self.skillStar, position, self.HP, frozenBuffer,
                                   gameResolution=self.player.gameResolution)
        frozenFishes = []
        invincibleFishes = []
        addTimeGroups = []
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            ftType = self.table.fishMap[fId]["type"]
            if ftType in config.ICE_FISH_TYPE:    # 冰锥不会刷新冰冻时间
                continue
            isCoverInvincible = True
            buffers = self.table.fishMap[fId]["buffer"]
            # 计算能否冰冻
            isCoverFrozen, lastFrozenTime, frozenTime, _ = self.table.checkCoverFrozen(fId, self.duration, endTime)
            if isCoverFrozen:
                self.table.frozenFish(fId, frozenBuffer, lastFrozenTime, frozenTime, addTimeGroups)
                frozenFishes.append(fId)
            # 计算能否无敌
            for lastBuffer in buffers:
                if lastBuffer[0] == 5102 and lastBuffer[1] > time.time():
                    isCoverInvincible = False
                    break
            if isCoverInvincible and self.table.typeName not in config.NORMAL_ROOM_TYPE:  # 非普通场极冻炮附加无敌效果
                if ftType in [6, 7]:  # 冰锥、捕鱼机器人不会有无敌效果
                    continue
                invincibleDuration = round(self.duration / 3.0, 3)
                if self.player.gunId == 1165:
                    invincibleDuration += 2
                invincibleEndTime = time.time() + invincibleDuration
                invincibleBuffer = [5102, invincibleEndTime, self.player.userId, self.skillStar, self.skillGrade, invincibleDuration, 0, self.skillType]
                self.table.setFishBuffer(fId, invincibleBuffer)
                invincibleFishes.append(fId)
        if frozenFishes:    # 广播新处于冰冻状态的鱼
            self.table.broadcastSkillEffect(self.player, endTime, frozenFishes, self.skillId)
        if invincibleFishes:     # 广播新处于无敌状态的鱼
            self.table.broadcastSkillEffect(self.player, invincibleEndTime, invincibleFishes, 5102)
        return catch, gain, gainChip, exp


class SkillGrenade(SkillBase):
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
        if ftlog.is_debug():
            ftlog.debug(self.skillId, ", _sortedFishes->", fishes, fishesHPDict, fIds)
        return fishes, fishesHPDict

    def returnClip(self):
        """
        打空返还技能子弹
        """
        if self.state == 2:
            if self.clip < self.originClip:
                self.clip += 1
                self.updateSkillData()


class SkillEnergy(SkillBase):
    """
    汇能弹(5106)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        isCatch = False
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        realPower = self.originRealPower
        aloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=True)
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
            if self.impale > probbRadix:    # 子弹能穿刺鱼
                self.impale -= probbRadix
                self.impale = max(self.impale, 0)
                randInt = random.randint(1, 10000)
                if randInt <= 9000 or self.impaleCatch:
                    catchMap["reason"] = 0
                if ftlog.is_debug():
                    ftlog.debug("SkillEnergy->impale->",
                                "userId =", self.player.userId,
                                "randInt =", randInt,
                                "fId =", fId,
                                "fishType =", fishInfo["fishType"],
                                "probbRadix =", probbRadix,
                                "impale =", self.impale)
            else:                           # 子弹无法穿刺鱼
                realPower += self.impale
                self.impale = 0
                fatal = self.table.dealIceConeEffect(fId, fishConf)
                self.deductionHP = self.totalPower
                fishHP = int(originHP - self.deductionHP)
                self.table.dealFishHP(fId, fishHP, fatal)
                probbRadix = self._getFishProbbRadix(fishInfo, fishConf)
                probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix, aloofOdds, aloofOdds)
                randInt = random.randint(1, 10000)
                if randInt <= probb:
                    catchMap["reason"] = 0
            catchMap["HP"] = fishInfo["HP"]
            if catchMap["reason"] == 0:
                multiple = self.gunSkinMultiple
                # 欺诈只获得1倍收益.
                if catchUserId != self.player.userId:
                    multiple = 1
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple, multiple, bufferCoinAdd)
                if catchUserId == self.player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain, catchMap, fishExp)
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
                        "onceCostCoin =", self.onceCostCoin,
                        "originRealPower =", self.originRealPower)
        if isCatch:
            self.player.addCombo()
        for userId, catchInfo in otherCatch.iteritems():
            otherPlayer = self.table.getPlayer(userId)
            if otherPlayer:
                self.table.dealCatch(bulletId, wpId, otherPlayer, catchInfo["catch"], catchInfo["gain"],
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, self.gunSkinMultiple, self.gunX)
        return catch, gain, gainChip, exp


class SkillFraud(SkillBase):
    """
    欺诈水晶(5107)
    """
    def initStar(self):
        super(SkillFraud, self).initStar()
        if self.table.typeName in [config.FISH_TIME_MATCH, config.FISH_FIGHT]:  # [回馈赛, 渔友竞技]-欺诈水晶3倍时长
            self.duration *= 3
        elif self.table.typeName == config.FISH_TIME_POINT_MATCH:
            self.duration *= 3

    def catchFish(self, bulletId, wpId, fIds, extends):
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        fishes = []
        endTime = time.time() + self.duration
        for fId in fIds:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId)
            if not isOK:
                continue
            buffers = self.table.fishMap[fId]["buffer"]
            for lastBuffer in buffers:
                if lastBuffer[0] == 5102 and lastBuffer[1] > time.time():
                    isOK = False
                    break
            if not isOK:
                continue
            ftType = self.table.fishMap[fId]["type"]
            if ftType in config.ICE_FISH_TYPE + config.ROBOT_FISH_TYPE:  # 欺诈水晶对冰锥、机器人无效
                continue
            buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0, self.skillType]
            self.table.setFishBuffer(fId, buffer)
            fishes.append(fId)
        if fishes:
            self.table.broadcastSkillEffect(self.player, endTime, fishes, self.skillId)
        return catch, gain, gainChip, exp


class SkillLaser(SkillBase):
    """
    激光炮(5108)
    """
    def costClip(self, bulletId, fPosx=0, fPosy=0):
        """
        消耗技能子弹
        """
        if self.clip > 0:
            for val in self.player.usingSkill:      # 当前技能使用中时，检测之前技能是否在使用中，如果是，结束之前技能
                skillId = val.get("skillId")
                skillType = val.get("skillType")
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
        isCatch = False
        if not extends:
            return catch, gain, gainChip, exp
        self.consumePower = 0
        self.powerRate = self.getPowerRate(extends)
        self.updateSkillData()
        fishes, fishesHPDict = self._sortedFishes(fIds, extends)
        totalPowerRate = self.totalPower / self.originRealPower  # 技能总威力（无加成）的占比
        realPower = self.originRealPower
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        curveProfitCoin = 0
        aloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=True)
        nonAloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=False)
        for fId, probbRadix in fishes:
            isOK, catchUserId = self.table.verifyFish(self.player.userId, fId, wpId)
            if not isOK:
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix, aloofOdds, nonAloofOdds)
            catchMap["HP"] = fishInfo["HP"]
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                multiple = self.gunSkinMultiple
                # 欺诈只获得1倍收益.
                if catchUserId != self.player.userId:
                    multiple = 1
                fishGainChip, fishGain, fishExp = self.table.dealKillFishGain(fId, self.player, self.fpMultiple, multiple, bufferCoinAdd)
                catchMap["reason"] = 0
                if catchUserId == self.player.userId:
                    isCatch = True
                    catch.append(catchMap)
                    gainChip += fishGainChip
                    exp += fishExp
                    if fishGain:
                        gain.extend(fishGain)
                else:
                    otherCatch = self.table.extendOtherCatchGain(fId, catchUserId, otherCatch, fishGainChip, fishGain, catchMap, fishExp)
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
            # 技能曲线
            if self.table.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
                fishType = fishInfo["fishType"]
                fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
                if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                    if catchMap["reason"] == 0:
                        curveProfitCoin += totalPowerRate * fishConf["value"] * self.gunSkinMultiple * self.fpMultiple
        self.consumePower = min(self.consumePower, self.originRealPower)
        curveLossCoin = self.onceCostCoin * self.powerRate * self.consumePower / self.originRealPower
        if ftlog.is_debug():
            ftlog.debug("catchFish->",
                        "userId =", self.player.userId,
                        "catch =", catch,
                        "gain =", gain,
                        "onceCostCoin =", self.onceCostCoin * self.powerRate,
                        "consumePower =", self.consumePower,
                        "originRealPower =", self.originRealPower,
                        "totalPowerRate =", totalPowerRate,
                        "curveLossCoin =", curveLossCoin,
                        "curveProfitCoin =", curveProfitCoin)
        self.player.dynamicOdds.updateOdds(curveProfitCoin - curveLossCoin)
        if isCatch:
            self.player.addCombo()
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
            fatal = self.table.dealIceConeEffect(fId, fishConf)
            fishHP = int(originHP - self.deductionHP)
            fishHP = self.table.dealFishHP(fId, fishHP, fatal)
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


class SkillHunt(SkillBase):
    """
    猎鱼机甲(5109)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        catch, gain, gainChip, exp = [], [], 0, 0
        if wpId == 2209:        # 释放猎鱼机甲
            position = self.position.get(bulletId, [0, 0])
            endTime = time.time() + self.duration
            buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0]
            group = self.table.insertFishGroup("call_robot", position, self.HP, buffer,
                                               gameResolution=self.player.gameResolution)
            self.durationEndTime = endTime
            self.onceCostCoin /= int(self.duration / self.interval)
            if group:
                self.skillFishes.append(group.startFishId)
        elif wpId == 2301:      # 猎鱼机甲开火
            if self.originRealPower and time.time() <= self.durationEndTime:
                return self.normalCatchFish(bulletId, wpId, fIds, extends)
        elif wpId == 2302:      # 猎鱼机甲爆炸
            if self.originRealPower:
                aliveTime = self.durationEndTime - time.time()
                aliveTime = aliveTime if 0 < aliveTime < self.duration else self.duration
                self.powerRate = (self.duration - aliveTime) * (1 / self.interval)
                powerAddtion = self.player.getPowerAddition(self.weaponId)
                self.totalPower = self.power * self.powerRate * powerAddtion + self.impale
                self.energy *= self.powerRate
                self.onceCostCoin *= self.powerRate
                self.originRealPower = self.totalPower + self.energy
                self.deductionHP = self.totalPower
                self.skillFishes = []
                if ftlog.is_debug():
                    ftlog.debug("SkillHunt->catchFish powerRate =", self.powerRate)
                return self.normalCatchFish(bulletId, wpId, fIds, extends)
        return catch, gain, gainChip, exp


class SkillGatling(SkillBase):
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
    5101: SkillMissile,     # 合金飞弹
    5102: SkillMagic,       # 魔术炮
    5103: SkillCannon,      # 火蛇加农炮
    5104: SkillFrozen,      # 极冻炮
    5105: SkillGrenade,     # 榴弹炮
    5106: SkillEnergy,      # 汇能弹
    5107: SkillFraud,       # 欺诈水晶
    5108: SkillLaser,       # 激光炮
    5109: SkillHunt,        # 猎鱼机甲
    5110: SkillGatling      # 格林机关枪
}

# 技能ID-武器ID对应关系
skillWeaponMap = {
    5101: 2201,
    5102: 2202,
    5103: 2203,
    5104: 2204,
    5105: 2205,
    5106: 2206,
    5107: 2207,
    5108: 2208,
    5109: 2209,
    5110: 2210
}

# 武器ID-技能ID对应关系
weaponSkillMap = {
    2201: 5101,
    2202: 5102,
    2203: 5103,
    2204: 5104,
    2205: 5105,
    2206: 5106,
    2207: 5107,
    2208: 5108,
    2209: 5109,
    2210: 5110
}


def createSkill(table, player, skillId, skillState, skillStar, skillGrade, skillType):
    skillClass = skillMap.get(skillId)
    skill = None
    if skillClass:
        skill = skillClass(table, player, skillId, skillState, skillStar, skillGrade, skillType)
    return skill

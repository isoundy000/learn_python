#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

import time
import random
import math
import json

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import gamedata, daobase
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, UserData
from hall.entity import hallranking


class SkillBase(object):

    def __init__(self, table, player, skillId, skillState, skillStar, skillGrade, skillType=0):
        self.table = table
        self.player = player
        self.skillId = skillId
        self.skillState = skillState
        self.skillStar = skillStar
        self.skillGrade = skillGrade
        self.skillGrade = self.getRealEffectSkillGrade()    # 玩家在欢乐竞技和王者争霸中夺冠，则下次比赛中使用该技能降级
        # 技能类型（0:主技能;1:辅助技能）
        self.skillType = skillType
        self.skillMode = self.table.gameMode    # 0经典 1千炮
        self.position = {}                      # [bulletId] = [fPosx, fPosy]
        self.initData()                         # 初始化技能数据
        self.initState()                        # 初始化技能状态

    def initLevel(self):
        """
        初始化等级属性数据
        """
        skillGradeConf = config.getSkillGradeConf(self.skillId, self.skillGrade, self.skillMode)
        self.cost = skillGradeConf.get("cost", 0)               # 消耗子弹
        self.power = skillGradeConf.get("power", 0)             # 单发威力
        self.HP = skillGradeConf.get("HP", 0)                   # HP
        self.impale = skillGradeConf.get("impale", 0)           # 贯穿力
        self.clip = skillGradeConf.get("clip", 0)               # 技能子弹数
        self.interval = skillGradeConf.get("interval", 0)       # 每发间隔时间
        self.duration = skillGradeConf.get("duration", 0)       # 效果时间
        self.coolDown = skillGradeConf.get("coolDown", 0)       # 冷却时间
        self.range = skillGradeConf.get("range", 0)             # 提升火蛇加农炮喷射距离
        self.weaponId = skillGradeConf.get("weaponId", 0)       # 对应武器
        self.double = skillGradeConf.get("double", [])          # 双倍皮肤炮ID
        self.isReturn = skillGradeConf.get("isReturn", 0)       # 打空是否返还子弹
        self.gunSkinMultiple = 1                                # 炮皮肤倍率
        self.skillMultiple = 1                                  # 技能倍率

    def initStar(self):
        """
        初始化星级属性数据
        """
        self.fatal = 0                                          # 冰锥HP在65%以上时无法一击致命
        self.distance = False                                   # 提高对远距离鱼的威力
        self.impaleCatch = False                                # 被贯穿的鱼必被捕获
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
        if self.table.typeName in config.NORMAL_ROOM_TYPE:      # 新手/普通/好友渔场-皮肤炮特性，技能双倍消耗/收益
            self.gunSkinMultiple = 2 if self.player.gunId in self.double else 1
            if self.table.typeName == config.FISH_GRAND_PRIX and self.player.isGrandPrixMode():  # 大奖赛冷却减半
                self.coolDown //= 2
                if self.skillType == 1:
                    self.cost = 0
        elif self.table.typeName == config.FISH_TIME_MATCH:     # 回馈赛-弹药消耗为0，冷却减半
            self.cost = 0
            self.coolDown //= 2
        elif self.table.typeName == config.FISH_TIME_POINT_MATCH:   # 定时积分赛-弹药消耗为0，冷却减半
            self.cost = 0
            self.coolDown //= 2
        elif self.table.typeName == config.FISH_FIGHT:          # 渔友竞技-冷却减半
            self.coolDown //= 2
        self.coolDown = max(self.coolDown, 1)
        # 格林机关枪除回馈赛外收益翻倍
        if self.skillId == 5110 and self.table.typeName != config.FISH_TIME_POINT_MATCH:
            self.skillMultiple = 2
        else:
            self.skillMultiple = 1
        self.gunSkinMultiple *= self.skillMultiple

    def initCommonData(self):
        """
        初始化公共数据
        """
        self.fpMultiple = self.player.fpMultiple
        self.powerRate = 1                          # 技能威力倍率
        self.durationEndTime = 0                    # 技能效果结束时间
        self.skillFishes = []                       # 技能召唤的鱼(捕鱼机器人)
        self.originClip = self.clip                 # 技能原始总子弹数
        self.originEnergy = 0                       # 技能单发原始能量
        self.energy = 0                             # 技能单发扣减能量
        self.totalPower = 0                         # 技能总威力（无加成）
        self.originRealPower = 0                    # 技能总威力（加能量）
        self.deductionHP = 0                        # 技能扣减HP
        self.consumePower = 0                       # 技能曲线消耗能量
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
        self.state = 0                              # 0:未使用 1:装备中 2:使用中
        self.cdStartTime = int(time.time())         # 技能冷却开始时的时间

    def use(self, select):
        """
        选中取消技能 select使用
        """
        eventId = None
        orgState = self.state
        if select:
            if self.state == 0:                     # 状态是未选中
                if self.player.gchgTimer:
                    self.player.gchgTimer.cancel()
                self.state = 1                      # 选中技能
                self.clear()                        # 清除技能数据(广播捕鱼机器人因主人离开房间而死亡)
                self.initData()                     # 初始化技能数据
                self.player.costClip(self.getCost, "BI_NFISH_USE_SKILL_%d" % self.skillId)      # 扣金币
                self.player.addUsingSkill(self.skillId, self.skillType)                         # 加技能
                eventId = "BI_NFISH_GE_SKILL_USE"
        else:                                           # 未选中
            if self.state == 1:                         # 选中状态
                self.state = 0
                self.player.addClip(self.getCost, "BI_NFISH_USE_SKILL_%d" % self.skillId)       # 加金币
                self.player.removeUsingSkill(self.skillId, self.skillType)                      # 取消技能
                eventId = "BI_NFISH_GE_SKILL_CANCEL"
        self.table.broadcastSkillUse(self, select, self.player.userId, orgState)                # 使用技能
        if eventId:
            bireport.reportGameEvent(eventId, self.player.userId, FISH_GAMEID, self.table.roomId,
                                     self.table.tableId, int(self.skillId), self.player.level, 0, 0, [], self.player.clientId)
            ftlog.info("skill_release->use",
                       "userId =", self.player.userId,
                       "eventId =", eventId,
                       "skillId =", self.skillId,
                       "skillStar =", self.skillStar,
                       "skillGrade =", self.skillGrade,
                       "skillType =", self.skillType,
                       "gunId =", self.player.gunId,
                       "nowGunLevel =", self.player.nowGunLevel)

    def end(self):
        """
        结束技能
        """
        if ftlog.is_debug():
            ftlog.debug("skill end, userId =", self.player.userId, "skillId =", self.skillId, "useTimes =",
                        self.newbieUseTimes)
        if self.table.typeName == config.FISH_NEWBIE and not self.player.redState:
            _key = UserData.newbieUseSkillTimes % (FISH_GAMEID, self.player.userId)
            daobase.executeUserCmd(self.player.userId, "HINCRBY", _key, str(self.skillId), 1)
        self.initState()
        self.player.removeUsingSkill(self.skillId, self.skillType)
        self.table.broadcastSkillEnd(self)
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            # 使用技能事件
            from newfish.game import TGFish
            from newfish.entity.event import UseSkillEvent
            chip = int(self.getCost * self.fpMultiple)              # 消耗的金币
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
        if self.clip > 0:                       # 技能子弹数
            lastCoin = self.player.holdCoin     # 持有金币（非实时数据库+内存金币）
            for val in self.player.usingSkill:  # 使用的技能
                skillId = val.get("skillId")
                skillType = val.get("skillType")
                if skillId != self.skillId or skillType != self.skillType:
                    skill = self.player.getSkill(skillId, skillType)
                    if skill.state == 2:        # 使用中
                        skill.end()
            self.state = 2                      # 0:未使用 1:装备中 2:使用中
            self.clip -= 1
            self.position[bulletId] = [fPosx, fPosy]    # 子弹的位置
            self.updateSkillData()                      # 更新技能power
            self.player.reportBIFeatureData("BI_NFISH_GE_FT_FIRE", self.weaponId, self.onceCostCoin)    # 技能单发价值金币数

            if lastCoin > self.table.runConfig.coinShortage > self.player.holdCoin:
                coinShortageCount = gamedata.getGameAttrJson(self.player.userId, FISH_GAMEID, GameData.coinShortageCount, {})   # 金币不足次数
                coinShortageCount.setdefault(str(self.table.runConfig.fishPool), 0)
                coinShortageCount[str(self.table.runConfig.fishPool)] += 1
                gamedata.setGameAttr(self.player.userId, FISH_GAMEID, GameData.coinShortageCount, json.dumps(coinShortageCount))
                if ftlog.is_debug():
                    ftlog.debug("costClip, skill", self.player.userId, lastCoin, self.table.runConfig.coinShortage,
                                self.player.holdCoin,
                                coinShortageCount)
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
        self.updateSkillEnergy()            # 更新技能能量
        skillGradeConf = config.getSkillGradeConf(self.skillId, self.skillGrade, self.skillMode)    # 获取技能等级的配置
        self.impale = skillGradeConf.get("impale", 0)
        powerAddtion = self.player.getPowerAddition(self.weaponId)
        self.totalPower = float(self.power * self.powerRate * powerAddtion)
        self.originRealPower = self.totalPower + self.energy    # 总威力 + 能量
        self.deductionHP = self.totalPower
        if ftlog.is_debug():
            ftlog.debug("updateSkillData->",
                    "userId =", self.player.userId,
                    "impale =", self.impale,
                    "totalPower =", self.totalPower,
                    "deductionHP =", self.deductionHP)

    def updateSkillEnergy(self):
        """
        更新技能能量
        """
        bonus = self.table.room.lotteryPool.getSkillPoolCoin() // self.fpMultiple   # 获取技能池的彩池奖金数
        randomNum = random.uniform(0.5, 1.5)
        singleEnergy = math.ceil(self.power * self.powerRate * randomNum)
        self.originEnergy = min(self.player.energy, singleEnergy)           # 单发威力
        self.energy = max(min(self.originEnergy, bonus), 0)                 # 能量
        self.player.energy -= self.energy
        self.table.room.lotteryPool.deductionSkillPoolCoin(int(self.energy * self.fpMultiple))  # 扣除技能池的彩池奖金数
        if ftlog.is_debug():
            ftlog.debug("updateSkillEnergy->",
                    "userId =", self.player.userId,
                    "bonus =", bonus,
                    "randomNum =", randomNum,
                    "singleEnergy =", singleEnergy,
                    "originEnergy =", self.originEnergy,
                    "energy =", self.energy,
                    "player.energy =", self.player.energy)

    @property
    def getCost(self):
        """
        技能消耗子弹数
        """
        return self.cost * self.gunSkinMultiple / self.skillMultiple

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

    def reportFishCost(self, use_fish_value, fishType, realPower, fishValue, *args):
        """
        上报开火捕鱼成本.
        """
        cost = fishValue if use_fish_value else realPower
        cost *= (self.fpMultiple * self.gunSkinMultiple)
        if ftlog.is_debug():
            ftlog.debug("report, fish cost, skill", use_fish_value, fishType, cost, args)
        self.table.cb_reporter.add_cost(fishType, cost)

    def normalCatchFish(self, bulletId, wpId, fIds, extends):
        """
        普通捕获算法
        :param bulletId: 子弹Id
        :param wpId: 武器Id
        :param fIds: 鱼的Ids
        :param extends: 扩展参数
        """
        catch = []
        gain = []
        gainChip = 0
        exp = 0
        otherCatch = {}
        isCatch = False
        self.consumePower = 0
        fishes, fishesHPDict = self._sortedFishes(fIds, extends)
        totalPowerRate = self.totalPower / self.originRealPower     # 技能总威力（无加成）的占比
        realPower = self.originRealPower
        bufferCoinAdd = self.player.getCoinAddition(self.weaponId)
        curveProfitCoin = 0
        aloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=True)         # 返回概率系数
        nonAloofOdds = self.player.dynamicOdds.getOdds(skill=self, aloofFish=False)     # 返回概率系数
        for fId, probbRadix in fishes:
            isOK, catchUserId, _ = self.table.verifyFish(self.player.userId, fId, wpId)
            if not isOK:
                continue
            catchMap = {}
            catchMap["fId"] = fId
            catchMap["reason"] = 1
            fishInfo = self.table.fishMap[fId]
            last_real_power = max(realPower, 0)
            probb, realPower = self.getSkillCatchProbb(fId, len(fIds), realPower, probbRadix, aloofOdds, nonAloofOdds)
            catchMap["HP"] = fishInfo["HP"]
            randInt = random.randint(1, 10000)
            use_fish_value = True if 10000 == probb else False
            if randInt <= probb:
                multiple = self.gunSkinMultiple
                # 欺诈只获得1倍收益.
                if catchUserId != self.player.userId:
                    multiple = 1
                # 捕鱼获得的金币、获得的道具、获得的经验
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
                fishType = fishInfo["conf"]["fishType"]
                fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
                if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                    if catchMap["reason"] == 0:
                        curveProfitCoin += totalPowerRate * fishConf[
                            "value"] * self.gunSkinMultiple * self.fpMultiple
                # 记录开火捕鱼成本.
                if fishConf["type"] in config.NON_ALOOF_FISH_TYPE:
                    odds = nonAloofOdds
                else:
                    odds = aloofOdds
                if odds == 0:
                    odds = 1
                fishValue = fishConf["value"] / odds
                self.reportFishCost(use_fish_value, fishType, last_real_power, fishValue, self.originRealPower, aloofOdds, nonAloofOdds)
        self.consumePower = min(self.consumePower, self.originRealPower)
        curveLossCoin = self.onceCostCoin * self.consumePower / self.originRealPower
        if ftlog.is_debug():
            ftlog.debug("normalCatchFish->",
                        "userId =", self.player.userId,
                        "catch =", catch,
                        "gain =", gain,
                        "gainChip =", gainChip,
                        "onceCostCoin =", self.onceCostCoin,
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
                                     catchInfo["gainChip"], catchInfo["exp"], self.fpMultiple, isFraud=True)
        return catch, gain, gainChip, exp

    def _getFishProbbRadix(self, fishInfo, fishConf):
        # 10倍场在完成641002时，难度使用200.
        if hasattr(self.table, "isNeedAdjustFishProbbRadix") and self.table.isNeedAdjustFishProbbRadix(fishConf, self.player):
            return 200
        # 新手任务期间概率特殊处理
        if self.player and self.player.taskSystemUser and self.player.taskSystemUser.isRedRoom():
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
            if fishConf["type"] in config.TERROR_FISH_TYPE:
                value = config.getWeaponConf(fishConf["weaponId"], False, self.table.gameMode)["power"]
            if self.player.dynamicOdds.currRechargeBonus >= value * gunMultiple * self.fpMultiple:
                # 存在充值奖池
                if ftlog.is_debug():
                    ftlog.debug("_getFishProbbRadix->currRechargeBonus =", self.player.dynamicOdds.currRechargeBonus, fishConf)
                return fishConf["probb1"]
            elif (min(3 * self.originEnergy * self.fpMultiple, self.table.room.lotteryPool.getRainbowPoolCoin()) >=
                  value * gunMultiple * self.fpMultiple):
                # 存在能量及彩虹鱼奖池
                if ftlog.is_debug():
                    ftlog.debug("_getFishProbbRadix->energy =", self.originEnergy, self.table.room.lotteryPool.getRainbowPoolCoin(), fishConf)
                return fishConf["probb1"]
            return fishConf["probb2"]
        else:
            return fishConf["probb1"]

    def _sortedFishes(self, fIds, extends=None):
        """
        排序所有鱼
        :param fIds: 鱼的Ids
        :param extends: 扩展
        :return:
        """
        fishesDict = {}
        fishesHPDict = {}
        for fId in fIds:
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            fishInfo = self.table.fishMap[fId]
            originHP = fishInfo["HP"]                   # 鱼血
            fishType = fishInfo["conf"]["fishType"]     # 鱼ID
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
        fishConf = config.getFishConf(fishInfo["conf"]["fishType"], self.table.typeName, self.fpMultiple)
        coefficient = self.table.getProbbCoefficient(self.player, fishConf, fishInfo)
        odds = 0
        lossPower = 0
        _ft = fishConf["type"]
        # 概率参数为0时，无HP必定被捕获，有HP无法被捕获
        if probbRadix == 0:
            if fishHP <= 0:
                probb = 10000
            else:
                probb = 0
        else:
            if realPower <= 0:
                probb = 0
            else:
                if _ft in config.NON_ALOOF_FISH_TYPE:       # 不是高冷鱼
                    odds = nonAloofOdds
                else:
                    odds = aloofOdds                        # 是否高冷鱼 是
                if odds > 0:
                    lossPower = probbRadix / odds
                    if realPower >= lossPower:
                        probb = 10000
                    else:
                        probb = realPower / lossPower * 10000
                else:
                    lossPower = probbRadix * 2
                    probb = 0
                if _ft in config.NON_ALOOF_FISH_TYPE:
                    if realPower >= lossPower:
                        self.consumePower += lossPower
                    else:
                        self.consumePower += realPower
                realPower -= lossPower
        probb *= coefficient
        if _ft in config.RED_FISH_TYPE:
            probb *= self.player.catchRedFishProbbRatio
            if self.player.userId in config.getPublic("banRedFishList", []):
                probb *= 0.3
        # 新手任务6期间.
        if self.table.typeName == config.FISH_NEWBIE and not self.player.redState and self.player.taskSystemUser:
            taskId = self.player.taskSystemUser.getCurMainTaskId()
            if taskId == 10006 and self.skillId == 5101:    # 合金飞弹
                if _ft not in config.BOSS_FISH_TYPE:
                    probb = 10000
            elif self.skillId == 5105:# 榴弹炮
                if self.newbieUseTimes == 0:
                    probb = max(4000, probb)
                elif taskId == 10006 and _ft not in config.BOSS_FISH_TYPE:
                    probb = max(2000, probb)
        if ftlog.is_debug():
            ftlog.debug("getSkillCatchProbb->",
                "userId =", self.player.userId,
                "probb =", probb,
                "odds =", odds,
                "fId =", fId,
                "fIdsCount =", fIdsCount,
                "fishType =", fishInfo["conf"]["fishType"],
                "fishHP =", fishHP,
                "realPower =", realPower,
                "probbRadix =", probbRadix,
                "aloofOdds =", aloofOdds,
                "nonAloofOdds =", nonAloofOdds,
                "lossPower =", lossPower,
                "consumePower =", self.consumePower,
                "coefficient =", coefficient)
        return probb, realPower

    def getRealEffectSkillGrade(self):
        """
        玩家在欢乐竞技和王者争霸中夺冠，则下次比赛中使用该技能降级
        """
        _skillGrade = self.skillGrade
        match_rank = 0
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


class SkillMissile(SkillBase):
    """
    合金飞弹(5101)
    """

    def catchFish(self, bulletId, wpId, fIds, extends):
        pass

    def _sortedFishes(self, fIds, extends=None):
        pass


class SkillMagic(SkillBase):
    """
    魔术炮(5102)
    """

    def initStar(self):
        pass

    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


class SkillCannon(SkillBase):
    """
    火蛇加农炮(5103)
    """
    # def _sortedFishes(self, fIds, extends=None):
    #     if extends:
    #         fIds = sorted(zip(fIds, extends), key=lambda d: int(d[1]))
    #     else:
    #         ftlog.debug("_sortedFishes, missing extends param! userId =", self.player.userId, "skillId =", self.skillId)
    #     fishesDict = {}
    #     fishesHPDict = {}
    #     for fId, distance in fIds:
    #         isOK = self.table.findFish(fId)
    #         if not isOK:
    #             continue
    #         fishInfo = self.table.fishMap[fId]
    #         originHP = fishInfo["HP"]
    #         fishType = fishInfo["conf"]["fishType"]
    #         fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
    #         fatal = self.table.dealIceConeEffect(fId)
    #         powerRateHP = self.getPowerRateHP(distance)
    #         self.deductionHP = self.totalPower * powerRateHP
    #         fishHP = int(originHP - self.deductionHP)
    #         fishHP = self.table.dealFishHP(fId, fishHP, fatal)
    #         fishesDict[fId] = self._getFishProbbRadix(fishInfo, fishConf)
    #         if originHP != fishHP:
    #             fishesHPDict[fId] = originHP
    #     fishes = fishesDict.items()
    #     ftlog.debug("_sortedFishes->", fishes, fishesHPDict, fIds)
    #     return fishes, fishesHPDict
    #
    # def getPowerRateHP(self, distance):
    #     if distance > self.range * 0.75:
    #         powerRateHP = 2 if self.distance else 1.5
    #     elif distance > self.range * 0.5:
    #         powerRateHP = 2.5 if self.distance else 2
    #     else:
    #         powerRateHP = 3
    #     return powerRateHP
    #
    # def catchFish(self, bulletId, wpId, fIds, extends):
    #     catch = []
    #     gain = []
    #     gainChip = 0
    #     exp = 0
    #     if len(fIds) != len(extends):
    #         ftlog.error("SkillCannon->catchFish fIds != extends", self.player.userId)
    #         return catch, gain, gainChip, exp
    #     return self.normalCatchFish(bulletId, wpId, fIds, extends)

    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


class SkillFrozen(SkillBase):
    """
    极冻炮(5104)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        """
        捕获算法 捕鱼
        :param bulletId: 子弹ID
        :param wpId: 武器ID
        :param fIds: 鱼的ID
        :param extends: 扩展
        """
        catch = []
        gain = []
        gainChip = 0
        exp = 0                     # 生用户等级的经验  现在炮的等级就是用户等级 炮的等级用珍珠升级
        position = self.position.get(bulletId, [0, 0])
        endTime = time.time() + self.duration       # self.duration效果时间
        invincibleEndTime = 0
        # 技能ID、结束时间、释放者ID、技能星级、技能等级、持续时间、次数、类型
        buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0]
        self.table.insertFishGroup("call_piton_%d" % self.skillStar, position, self.HP, buffer,
                                   gameResolution=self.player.gameResolution)           # 增加鱼群 == 召唤鱼群
        frozenFishes = []           # 冻住的鱼
        invincibleFishes = []
        addTimeGroup = []           # 延长时间的鱼群
        for fId in fIds:            # 冻住鱼并刷新剩余冰冻时间
            isOK = self.table.findFish(fId)
            if not isOK:
                continue
            fishType = self.table.fishMap[fId]["conf"]["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            if fishConf["type"] in config.ICE_FISH_TYPE:  # 冰锥不会刷新冰冻时间
                continue
            lastFrozenTime = 0              # 上次冰冻的持续时间
            frozenTime = self.duration
            isCoverFrozen = True
            isCoverInvincible = True
            buffer = [self.skillId, endTime, self.player.userId, self.skillStar, self.skillGrade, self.duration, 0, self.skillType]  # 0冰冻次数
            buffers = self.table.fishMap[fId]["buffer"]
            if ftlog.is_debug():
                ftlog.debug("SkillFrozen->lastBuffer =", fId, self.table.fishMap[fId], buffers, endTime)
            for lastBuffer in buffers:
                if lastBuffer[0] == 5102 and lastBuffer[1] > time.time():
                    isCoverInvincible = False       # 不能覆盖魔术炮的无敌技能
                if lastBuffer[0] == self.skillId:   # 之前处于冰冻状态的鱼
                    lastFrozenTime = lastBuffer[5]
                    if endTime > lastBuffer[1]:     # 新冰冻到期时间大于旧冰冻到期时间，覆盖时间
                        # 如果上一个冰冻状态未到期且小于新冰冻到期时间，则鱼在冰冻状态下再次冰冻，实际冰冻时间为间隔时间
                        if time.time() < lastBuffer[1] < endTime:
                            frozenTime = round(endTime - lastBuffer[1], 3)
                    else:
                        isCoverFrozen = False       # 不能覆盖冰冻状态
            if isCoverFrozen:
                if ftlog.is_debug():
                    ftlog.debug("SkillFrozen->frozenTime =", fId, frozenTime)
                buffer[5] = round(lastFrozenTime + frozenTime, 3)
                self.table.setFishBuffer(fId, buffer)
                frozenFishes.append(fId)            # 冻住的鱼
                if ftlog.is_debug():
                    ftlog.debug("SkillFrozen->isCoverFrozen->buffer =", fId, self.table.fishMap[fId]["buffer"])
                group = self.table.fishMap[fId]["group"]
                if group.startFishId not in addTimeGroup:
                    addTimeGroup.append(group.startFishId)
                    group.adjust(frozenTime)
                    self.table.superBossFishGroup and self.table.superBossFishGroup.frozen(fId, self.table.fishMap[fId]["conf"]["fishType"], frozenTime)
            if isCoverInvincible and self.table.typeName not in config.NORMAL_ROOM_TYPE:  # 非普通场极冻炮附加无敌效果
                if fishConf["type"] in [6, 7]:      # 冰锥、捕鱼机器人不会有无敌效果
                    continue
                invincibleDuration = round(self.duration / 3.0, 3)
                if self.player.gunId == 1165:
                    invincibleDuration += 2
                invincibleEndTime = time.time() + invincibleDuration
                if ftlog.is_debug():
                    ftlog.debug("SkillFrozen->invincibleTime =", fId, invincibleDuration)
                invincibleBuffer = [5102, invincibleEndTime, self.player.userId, self.skillStar, self.skillGrade, invincibleDuration, 0, self.skillType]
                self.table.setFishBuffer(fId, invincibleBuffer)
                invincibleFishes.append(fId)
                if ftlog.is_debug():
                    ftlog.debug("SkillFrozen->isCoverInvincible->buffer =", fId, self.table.fishMap[fId]["buffer"])
        if frozenFishes:                            # 广播新处于冰冻状态的鱼
            self.table.broadcastSkillEffect(self.player, endTime, frozenFishes, self.skillId)
        if invincibleFishes:                        # 广播新处于无敌状态的鱼
            self.table.broadcastSkillEffect(self.player, invincibleEndTime, invincibleFishes, 5102)
        return catch, gain, gainChip, exp

class SkillGrenade(SkillBase):
    """
    榴弹炮(5105)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        pass

    def _sortedFishes(self, fIds, extends=None):
        pass

    def returnClip(self):
        pass


class SkillEnergy(SkillBase):
    """
    汇能弹(5106)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


class SkillFraud(SkillBase):
    """
    欺诈水晶(5107)
    """
    def initStar(self):
        pass

    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


class SkillLaser(SkillBase):
    """
    激光炮(5108)
    """
    def costClip(self, bulletId, fPosx=0, fPosy=0):
        pass

    def catchFish(self, bulletId, wpId, fIds, extends):
        pass

    def _sortedFishes(self, fIds, extends=None):
        pass

    def getPowerRate(self, extends):
        pass


class SkillHunt(SkillBase):
    """
    猎鱼机甲(5109)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


class SkillGatling(SkillBase):
    """
    格林机关枪(5110)
    """
    def catchFish(self, bulletId, wpId, fIds, extends):
        pass


skillMap = {
    5101: SkillMissile,
    5102: SkillMagic,
    5103: SkillCannon,
    5104: SkillFrozen,
    5105: SkillGrenade,
    5106: SkillEnergy,
    5107: SkillFraud,
    5108: SkillLaser,
    5109: SkillHunt,
    5110: SkillGatling
}


skillWeaponMap = {
    5101: 2201,         # 技能炮 武器
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


weaponSkillMap = {
    2201: 5101,         # 武器 技能炮
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


def createSkill(table, player, skillId, skillStar, skillGrade, skillType):
    """
    创建技能对象
    :return:
    """
    skillClass = skillMap.get(skillId)
    skill = None
    if skillClass:
        skill = skillClass(table, player, skillId, skillStar, skillGrade, skillType)
    return skill
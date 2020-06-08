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

    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        self.table = table
        self.player = player
        self.skillId = skillId
        self.skillStar = skillStar
        self.skillGrade = skillGrade
        self.skillGrade = self.getRealEffectSkillGrade()
        # 技能类型（0:主技能;1:辅助技能）
        self.skillType = skillType
        self.skillMode = self.table.gameMode    # 0经典 1千炮
        self.position = {}
        self.initData()
        self.initState()

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
        self.gunSkinMultiple = 1
        self.skillMultiple = 1

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
        self.state = 0
        self.cdStartTime = int(time.time())

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
        else:                                           # 未选中
            if self.state == 1:                         # 选中状态
                self.state = 0
                self.player.addClip(self.getCost, "BI_NFISH_USE_SKILL_%d" % self.skillId)
                self.player.removeUsingSkill(self.skillId, self.skillType)
        pass

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

    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillMissile, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)



class SkillMagic(SkillBase):
    """
    魔术炮(5102)
    """

    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillMagic, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillCannon(SkillBase):
    """
    火蛇加农炮(5103)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillCannon, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillFrozen(SkillBase):
    """
    极冻炮(5104)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillFrozen, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillGrenade(SkillBase):
    """
    榴弹炮(5105)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillGrenade, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillEnergy(SkillBase):
    """
    汇能弹(5106)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillEnergy, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillFraud(SkillBase):
    """
    欺诈水晶(5107)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillFraud, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillLaser(SkillBase):
    """
    激光炮(5108)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillLaser, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillHunt(SkillBase):
    """
    猎鱼机甲(5109)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillHunt, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


class SkillGatling(SkillBase):
    """
    格林机关枪(5110)
    """
    def __init__(self, table, player, skillId, skillStar, skillGrade, skillType=0):
        super(SkillGatling, self).__init__(table, player, skillId, skillStar, skillGrade, skillType)


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
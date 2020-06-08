#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6


import copy
import json
import time
import random
import traceback
from collections import OrderedDict

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.util import strutil
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import userchip, userdata, gamedata, daobase
from poker.entity.game.tables.table_player import TYPlayer
from hall.entity import hallvip, datachangenotify
from newfish.entity import change_notify, config, util, weakdata, user_system, piggy_bank, module_tip, mini_game
from newfish.entity.gun import gun_system
from newfish.entity.config import FISH_GAMEID, COUPON_KINDID, STARFISH_KINDID, \
    SILVER_BULLET_KINDID, GOLD_BULLET_KINDID, BRONZE_BULLET_KINDID, BULLET_KINDIDS, PEARL_KINDID
from newfish.entity.redis_keys import GameData, WeakData, ABTestData
from newfish.entity.dynamic_odds import DynamicOdds
from newfish.entity.event import GameTimeEvent, StarfishChangeEvent, BulletChangeEvent, FireEvent, \
    NetIncomeChangeEvent, ChangeGunLevelEvent
from newfish.entity.msg import GameMsg
from newfish.entity.skill import skill_system, skill_release
from newfish.entity.honor import honor_system
from newfish.table.economic_data import EconomicData                    # 渔场内资产缓存数据
from newfish.entity.achievement.achievement_table_system import AchievementTableSystem
from newfish.entity.prize_wheel import PrizeWheel
# from newfish.entity.grand_prize_pool import GrandPrizePool
from newfish.entity.fishactivity.competition_activity import CompAct    # 竞赛活动
from newfish.entity.lottery_ticket import LotteryTicket
from newfish.entity.level_prize_wheel import LevelPrizeWheel


class FishPlayer(TYPlayer):
    
    def __str__(self):
        return "FishPlayer(" + str(self.userId) + ")" + str(id(self))
    
    def __repr__(self):
        return "FishPlayer(" + str(self.userId) + ")" + str(id(self))

    def __init__(self, table, seatIndex, clientId):
        super(FishPlayer, self).__init__(table, seatIndex)
        # 千炮模式（金币/金环）
        self.multipleMode = config.GOLDEN_COIN
        self.killPearlFishCount = 0  # 记录新手任务期间未掉落珍珠时捕获珍珠鱼的数量
        self.hallCoin = 0
        self.ignorePresent = False
        # self.initCurve5017TestMode = "b"
        # 玩家子弹威力奖池.
        self.bulletPowerPool = 0
        # self.upgradeGunTestMode = None
        self.grandPrixStartTS = 0                           # 大奖赛
        self.grandPrixUseSkillTimes = []
        self.grandPrixProfitCoin = {}
        self.clip = 0
        self.fpMultipleTestMode = None
        self.fpMultiple = table.runConfig.multiple          # 倍率
        self.matchingFishPool = table.runConfig.fishPool    # 比赛渔场
        self.prizeWheel = None
        if self.table.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
            self.prizeWheel = PrizeWheel(self.userId, table.runConfig.fishPool, self.table.roomId)
        if self.table.gameMode == config.MULTIPLE_MODE:     # 千炮转盘
            self.prizeWheel = LevelPrizeWheel(self.userId, table.runConfig.fishPool, self.table.roomId)
        self.vipLevel = 0
        self.clientId = ""
        if clientId:
            self.clientId = clientId
        self.lang = util.getLanguage(self.userId, self.clientId)
        # 主技能
        self.skills = {}                                    # 主技能
        self.skillSlots = {}                                # 技能
        # 辅助技能
        self.auxiliarySkills = {}
        self.auxiliarySkillSlots = {}
        # 处于选中或使用中的技能([{skillId:xx, type:0/1}])
        self.usingSkill = []
        # 竞赛活动模块
        if table.runConfig.typeName != config.FISH_NEWBIE and table.runConfig.typeName in config.NORMAL_ROOM_TYPE:
            self.compAct = CompAct(self.userId, self.seatId, self.clientId)
        else:
            self.compAct = None
        self.fireCount = {}
        self.lotteryTicket = None
        if self.table.typeName in config.QUICK_START_ROOM_TYPE:
            self.lotteryTicket = LotteryTicket(self, table.runConfig.fishPool, self.table.roomId)
        self._onInit()
        self.robotScript = None
        
    def _onInit(self):
        """
        初始化
        """
        self._initVarData()
        self._loadUserData()
        self.loadAllSkillData()

    def _initVarData(self):
        """
        初始化变量
        """
        self.lastActionTime = int(time.time())
        self.lastCatchTime = int(time.time())       # 最后一次捕鱼事件
        self.isFinishRedTask = False
        self.isBankrupt = False                     # 是否破产
        self.resetTime = 0
        self._fires = {}                            # 子弹
        self._catchFishes = {}
        self._comboBudgetTime = 1.2
        self.clip = 0
        self.combo = 0
        self.invalidCatch = 0
        self.enterTime = 0
        self.offline = 0
        self.rank = 0
        self.couponConsumeClip = 0                 # 奖券消耗的金币
        self.activityConsumeClip = 0
        self.energy = 0
        self.maxEnergy = 0
        self.luckyNum = 0
        self.luckyCount = 0
        self.currentTask = None
        self.taskSystemUser = None
        self.taskSystemTable = self.table.taskSystemTable
        self.activitySystem = None
        self.mainQuestSystem = None                 # 主线任务
        self.totalGainChip = 0
        self.catchBonus = 0
        # 开火消耗的金币，用于红包券抽奖
        self.lotteryFireCostChip = {}
        self.gameTime = 0
        self.gameTimeTimer = FTLoopTimer(60, -1, self._incrGameTimer)
        self.gameTimeTimer.start()
        self.gchgTimer = None
        self.comboTimer = None
        self.checkLimitTimeGift = True
        self.catchRedFishProbbRatio = 1  # 捕获红包鱼概率系数

        self.attackBossInfo = {}
        self.usedBufferInfos = []       # 使用中的buffer
        self.dropPearlCount = 0
        self.incrPearlDropRatio = 0.    # 额外增加珍珠掉率
        self.incrCrystalDropRatio = 0.  # 额外增加水晶掉率

        self.fireCost = {}
        # 开火消耗的金币量.
        self.fireCostChip = 0
        # 每日盈亏金币数据.
        self.dailyKey = ""
        self.dailyProfitConin = {}
        # 每日渔场盈亏数据
        self.dailyTSKey = ""
        self.dailyFishPoolProfitCoin = {}
        # 本次净收益
        self.netIncome = 0
        
        if self.isRobotUser:
            self.createScriptTimer = FTLoopTimer(2, 0, self.createScript)
            self.createScriptTimer.start()
            
    def createScript(self):
        """
        创建机器人
        """
        from newfish.script.script_base import ScriptBase
        self.robotScript = ScriptBase.createScript(self)
    
    def clear(self):
        pass
    
    def clearTimer(self):
        pass

    def clearingClip(self):
        pass
    
    
    def clearData(self):
        pass
    
    @property
    def allChip(self):
        """
        所有金币（实时数据库+内存金币）
        """
        return self.chip + self.tableChip + self.bulletChip
    
    @property
    def chip(self):
        """
        渔场外金币
        """
        return userdata.getChip(self.userId) if self.userId > 0 else 0

    @property
    def tableChip(self):
        """
        渔场内金币  渔场内资产缓存数据
        """
        return self.economicData.tableChip

    @property
    def bulletChip(self):
        """
        渔场内子弹价值金币
        """
        return self.economicData.bulletChip

    @property
    def holdCoin(self):
        """
        持有金币（非实时数据库+内存金币）
        """
        return self.hallCoin + self.tableChip + self.bulletChip
    
    def _loadUserData(self):
        """
        读取玩家数据
        """
        self.dailyTSKey = str(util.getDayStartTimestamp(int(time.time())))


    def loadAllSkillData(self):
        """
        读取并初始化所有技能数据
        """
        # 处于选中或使用中的技能
        self.usingSkill = []

        self.skills = {}
        self._refreshSkillSlots(0)
        for skillId in self.skillSlots.keys():
            self._loadSkillData(skillId, 0)
    
    def _refreshSkillSlots(self, skillType):
        """
        刷新技能数据 {5101: [star_level, current_level]}
        """
        if skillType == 0:
            self.skillSlots = skill_system.getInstalledSkill(self.userId, self.table.gameMode)
        ftlog.info("_refreshSkillSlots, userId =", self.userId, "skillType =", skillType, "skillSlots =", self.skillSlots)

    def _loadSkillData(self, skillId, skillType):
        """
        读取单个技能数据
        """
        if skillType == 0:
            if skillId in self.skillSlots:
                if self.skillSlots[skillId][1] > self.table.runConfig.maxSkillLevel:    # 技能当前等级
                    self.skillSlots[skillId][1] = self.table.runConfig.maxSkillLevel
                skillStar = self.skillSlots[skillId][0]
                skillGrade = self.skillSlots[skillId][1]
                skill = skill_release.createSkill(self.table, self, skillId, skillStar, skillGrade, 0)
                self.skills[skillId] = skill
        else:
            if skillId in self.auxiliarySkillSlots:
                if self.auxiliarySkillSlots[skillId][1] > self.table.runConfig.maxSkillLevel:
                    self.auxiliarySkillSlots[skillId][1] = self.table.runConfig.maxSkillLevel
                skillStar = self.auxiliarySkillSlots[skillId][0]
                skillGrade = self.auxiliarySkillSlots[skillId][1]
                skill = skill_release.createSkill(self.table, self, skillId, skillStar, skillGrade, 1)
                self.auxiliarySkills[skillId] = skill

    def getSkillSlotsInfo(self, skillType):
        """
        获取技能槽数据
        """
        if skillType == 0:
            skillSlotsTmp = copy.deepcopy(self.skillSlots)
            skillSlots = OrderedDict(sorted(skillSlotsTmp.iteritems(), key=lambda d: d[0]))
            totalSkillGrade = 0
            for skillId in skillSlots.keys():
                skillGrade = skillSlots[skillId][1]
                if skillGrade > self.table.runConfig.maxSkillLevel:
                    skillGrade = self.table.runConfig.maxSkillLevel
                    skillSlots[skillId][1] = skillGrade
                cdTimeLeft = self.skills[skillId].cdTimeLeft
                coolDown = self.skills[skillId].coolDown
                skillSlots[skillId].extend([cdTimeLeft, coolDown])      # [1,2,3,4,5,50,60]
                totalSkillGrade += skillGrade
            self.maxEnergy = 50 + totalSkillGrade * 50
            return skillSlots
        else:                                                           # 辅助技能
            auxiliarySkillSlotsTmp = copy.deepcopy(self.auxiliarySkillSlots)
            auxiliarySkillSlots = OrderedDict(sorted(auxiliarySkillSlotsTmp.iteritems(), key=lambda d: d[0]))
            for skillId in auxiliarySkillSlots.keys():
                skillGrade = auxiliarySkillSlots[skillId][1]
                if skillGrade > self.table.runConfig.maxSkillLevel:
                    skillGrade = self.table.runConfig.maxSkillLevel
                    auxiliarySkillSlots[skillId][1] = skillGrade
                cdTimeLeft = self.auxiliarySkills[skillId].cdTimeLeft
                coolDown = self.auxiliarySkills[skillId].coolDown
                auxiliarySkillSlots[skillId].extend([cdTimeLeft, coolDown])
            return auxiliarySkillSlots
        
    def refreshSkillStartTime(self):
        """
        刷新技能CD开始时间
        """
        for skillId in self.skillSlots.keys():
            self.skills[skillId].changeCDStartTime()
        for skillId in self.auxiliarySkillSlots.keys():
            self.auxiliarySkills[skillId].changeCDStartTime()
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
        self.skillSlots = {}                                # 技能槽
        # 辅助技能
        self.auxiliarySkills = {}                           # 辅助技能
        self.auxiliarySkillSlots = {}                       # 辅助技能槽
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
        self._initVarData()                         # 初始化变量
        self._loadUserData()                        # 读取玩家数据
        self.loadAllSkillData()                     # 读取并初始化所有技能数据

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
        self.gameTime = 0                           # 玩的次数
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
        try:
            if self.prizeWheel:
                self.prizeWheel.dumpData()
                self.prizeWheel = None
            self.clearTimer()
            self.clearingClip()
            self.clearData()
            if self.robotScript:
                self.robotScript.clear()
                self.robotScript = None
            if self.compAct:
                self.compAct = None
            if self.lotteryTicket:
                self.lotteryTicket.clearTimer()
                self.lotteryTicket = None
        except Exception, e:
            ftlog.error(self.userId, traceback.format_exc())

    def clearTimer(self):
        """清理定时器"""
        self.gameTimeTimer.cancel()
        if self.gchgTimer:              # 切换火炮等级
            self.gchgTimer.cancel()
        if self.comboTimer:
            self.comboTimer.cancel()

    def clearingClip(self):
        """
        清理金币
        """
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            self.dumpEconomicData()
            self.dumpGameData()
            self.clip = 0
            pass
    
    
    def clearData(self):
        """更新玩家登录数据"""
        user_system.updateLoginData(self.userId)
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            self.dynamicOdds.saveDynamicOddsData()
            self.saveUserData()
            self.reportTableData()
        for bufferInfo in self.usedBufferInfos:
            bufferInfo.endBuffer()

    
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

    def costClip(self, bullet, eventId):
        pass

    def addClip(self, bullet=0, auto=0, skillId=0):
        pass

    def _incrGameTimer(self):
        """增加游戏时长"""
        if self.userId <= 0:
            return
        if not self.isFinishRedTask:    # 是否完成所有新手任务
            self.isFinishRedTask = util.isFinishAllRedTask(self.userId)
        curDayStartTs = util.getDayStartTimestamp(int(time.time()))     # 获取0点时间戳
        key = GameData.playGameTime % (FISH_GAMEID, self.userId, curDayStartTs)
        daobase.executeUserCmd(self.userId, "INCR", key)
        daobase.executeUserCmd(self.userId, "EXPIREAT", key, curDayStartTs + 3 * 86400)
        self.gameTime += 1
        self.checkLimitTimeGift = True  # 限时礼包
        weakdata.incrDayFishData(self.userId, "gameTime", 1)
        if util.getDayStartTimestamp(self.resetTime) != util.getDayStartTimestamp(int(time.time())):
            self.resetTime = weakdata.getDayFishData(self.userId, "resetTime", 0)
        from newfish.game import TGFish
        event = GameTimeEvent(self.userId, FISH_GAMEID, self.table.roomId, self.table.tableId,
                              self.table.runConfig.fishPool, 1, self.fpMultiple, self.isFinishRedTask)
        TGFish.getEventBus().publishEvent(event)
        if hasattr(self, "fireCostChip") and self.fireCostChip > 0:
            piggy_bank.fireCostChip(self.userId, self.clientId, self.vipLevel, self.fireCostChip)
            self.fireCostChip = 0
        if hasattr(self, "dailyKey"):
            piggybank = config.getPiggyBankConf(self.clientId, self.vipLevel).get("paid", {})
            resetTime = piggybank.get("resetTime", -1)
            self.dailyKey = piggy_bank._getDataKey(int(time.time()), resetTime)
        if self.compAct:
            self.compAct.updateTimer()
        self.dailyTSKey = str(util.getDayStartTimestamp(int(time.time())))


    def _loadUserData(self):
        """
        读取玩家数据
        """
        self.dailyTSKey = str(util.getDayStartTimestamp(int(time.time())))
        self.economicData = EconomicData(self, self.table)
        self.name = util.getNickname(self.userId)
        # 魅力、性别、用户头像URL
        self.charm, self.sex, self.purl = userdata.getAttrs(self.userId, ["charm", "sex", "purl"])



    def loadAllSkillData(self):
        """
        读取并初始化所有技能数据
        """
        # 处于选中或使用中的技能
        self.usingSkill = []                    # 处于选中和使用中的技能

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
        if skillType == 0:                              # 主动技能
            if skillId in self.skillSlots:
                if self.skillSlots[skillId][1] > self.table.runConfig.maxSkillLevel:    # 技能当前等级
                    self.skillSlots[skillId][1] = self.table.runConfig.maxSkillLevel
                skillStar = self.skillSlots[skillId][0]
                skillGrade = self.skillSlots[skillId][1]
                skill = skill_release.createSkill(self.table, self, skillId, skillStar, skillGrade, 0)      # 根据技能Id 创建技能类
                self.skills[skillId] = skill
        else:                                           # 辅助技能
            if skillId in self.auxiliarySkillSlots:
                if self.auxiliarySkillSlots[skillId][1] > self.table.runConfig.maxSkillLevel:
                    self.auxiliarySkillSlots[skillId][1] = self.table.runConfig.maxSkillLevel
                skillStar = self.auxiliarySkillSlots[skillId][0]
                skillGrade = self.auxiliarySkillSlots[skillId][1]
                skill = skill_release.createSkill(self.table, self, skillId, skillStar, skillGrade, 1)
                self.auxiliarySkills[skillId] = skill

    def getSkillSlotsInfo(self, skillType):
        """
        获取技能槽数据 skillType 0:主动 1:辅助
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

    def getCoinAddition(self, weaponId):
        """
        获取金币加成
        :param weaponId: 武器ID
        """
        percent = 1
        for bufferInfo in self.usedBufferInfos:
            percent += bufferInfo.getCoinNumPercent(weaponId)
        return percent

    def getPowerAddition(self, weaponId):
        """
        获取武器威力加成
        """
        percent = 1
        for bufferInfo in self.usedBufferInfos:
            percent += bufferInfo.getPowerPercent(weaponId)
        return percent

    def getSkill(self, skillId, skillType=0):
        """
        获取技能
        :param skillId: 技能Id
        :param skillType: 0主 1辅
        """
        if skillType == 0:
            return self.skills.get(skillId)
        else:
            return self.auxiliarySkills.get(skillId)

    def addUsingSkill(self, skillId, skillType):
        """
        添加使用的技能
        """
        # if skillId not in self.usingSkill:
        #     self.usingSkill.append(skillId)
        for val in self.usingSkill:
            if val.get("skillId") == skillId and val.get("skillType") == skillType:
                break
        else:
            self.usingSkill.append({"skillId": skillId, "skillType": skillType})
        if ftlog.is_debug():
            ftlog.debug("addUsingSkill, userId =", self.userId, skillId, skillType, self.usingSkill)

    def removeUsingSkill(self, skillId, skillType):
        # if skillId in self.usingSkill:
        #     self.usingSkill.remove(skillId)
        for val in self.usingSkill:
            if val.get("skillId") == skillId and val.get("skillType") == skillType:
                self.usingSkill.remove(val)
                break
        if ftlog.is_debug():
            ftlog.debug("removeUsingSkill, userId =", self.userId, skillId, skillType, self.usingSkill)

    def _checkSkillCondition(self, skillId, select, skillType):
        """
        检查技能条件
        """
        reason = 0
        skill = self.getSkill(skillId, skillType)
        if skill:
            if select:
                bullet = self.tableChip // self.fpMultiple

    def useSkill(self, skillId, select, skillType):
        """
        使用技能
        """
        reason = self._checkSkillCondition(skillId, select, skillType)
        if reason:
            currSkill = self.getSkill(skillId, skillType)
            if select:              # 选中技能(装备技能)
                currSkill.use(1)    # 无之前技能记录或者已经被取消了上一个技能，直接装备技能
            else:                   # 取消技能
                if len(self.usingSkill) == 1 and skillId == self.usingSkill[-1].get("skillId") \
                    and skillType == self.usingSkill[-1].get("skillType", 0):       # 只有当前技能
                    currSkill.use(0)
                    self.table.broadcastGunChange(self)
                elif len(self.usingSkill) > 1 and skillId == self.usingSkill[-1].get("skillId") \
                        and skillType == self.usingSkill[-1].get("skillType", 0):   # 存在技能使用记录
                    lastSkillId = self.usingSkill[-2].get("skillId")
                    lastSkillType = self.usingSkill[-2].get("skillType", 0)
                    lastSkill = self.getSkill(lastSkillId, lastSkillType)
                    currSkill.use(0)    # 取消当前技能， 并切换到上一个技能
                    if lastSkill:
                        lastSkill.use(1)
                else:                   # 无之前技能使用记录或技能顺序错误，技能取消失败
                    reason = 6
        if reason != 0:
            msg = MsgPack()
            msg.setCmd("skill_use")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("seatId", self.seatId)
            msg.setResult("skillId", skillId)
            msg.setResult("skillType", skillType)
            msg.setResult("reason", reason)
            GameMsg.sendMsg(msg, self.userId)
        return reason

    def installSkill(self, skillId, install, ignoreFailMsg=False, skillType=0):
        """
        初始化技能 install 0:卸下 1:装备
        """
        code = 0
        # 使用中的技能不可卸载.
        if len(self.usingSkill) >= 1 and skillId == self.usingSkill[-1].get("skillId") \
            and skillType == self.usingSkill[-1].get("skillType"):
            code = 1
        # 捕鱼机器人存活时不可卸载.
        elif self.getSkill(skillId, skillType) and self.getSkill(skillId, skillType).getSkillFishesAlive():
            code = 1
        elif len(self.usingSkill) > 1 and skillId == self.usingSkill[0].get("skillId") \
            and skillType == self.usingSkill[0].get("skillType"):
            self.removeUsingSkill(skillId, skillType)
        if code == 0:
            code = skill_system.installSkill(self.userId, skillId, self.table.gameMode, install)
        if code == 0 or not ignoreFailMsg:
            msg = MsgPack()
            msg.setCmd("skill_install")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("seatId", self.seatId)
            msg.setResult("skillId", skillId)
            msg.setResult("skillMode", self.table.gameMode)
            msg.setResult("skillType", skillType)
            msg.setResult("install", install)
            msg.setResult("code", code)
            GameMsg.sendMsg(msg, self.userId)
        if code == 0:
            self._refreshSkillSlots(skillType)                  # self.skillSlots = {}             # 技能槽
            if not install and self.getSkill(skillId, skillType):
                if skillType == 0:
                    del self.skills[skillId]                    # 删除技能对象
                else:
                    del self.auxiliarySkills[skillId]
            elif install:
                self._loadSkillData(skillId, skillType)         # 读取单个技能数据 技能对象
            ftlog.info("installSkill->skills =", skillType,
                       self.skills, self.skillSlots,
                       self.auxiliarySkills, self.auxiliarySkillSlots)
            self.syncSkillSlots()

    def replaceSkill(self, installSkillId, uninstallSkillId, skillType=0):
        """技能替换 uninstallSkillId 要卸下的技能ID"""
        code = 0
        # 使用中的技能不可替换.
        if len(self.usingSkill) >= 1 and \
            (installSkillId == self.usingSkill[-1].get("skillId") or
             uninstallSkillId == self.usingSkill[-1].get("skillId")):
            code = 1
        # 捕鱼机器人存活时不可替换.
        elif self.getSkill(uninstallSkillId, skillType) and self.getSkill(uninstallSkillId, skillType).getSkillFishesAlive():
            code = 1
        elif len(self.usingSkill) > 1 and installSkillId == self.usingSkill[0].get("skillId") \
                and skillType == self.usingSkill[0].get("skillType"):
            self.removeUsingSkill(installSkillId, skillType)
        elif len(self.usingSkill) > 1 and uninstallSkillId == self.usingSkill[0].get("skillId") \
                and skillType == self.usingSkill[0].get("skillType"):
            self.removeUsingSkill(uninstallSkillId, skillType)
        if code == 0:
            code = skill_system.replaceSkill(self.userId, self.table.gameMode, installSkillId, uninstallSkillId)
        msg = MsgPack()
        msg.setCmd("skill_replace")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("installSkillId", installSkillId)
        msg.setResult("uninstallSkillId", uninstallSkillId)
        msg.setResult("skillType", skillType)
        msg.setResult("code", code)
        GameMsg.sendMsg(msg, self.userId)
        if code == 0:
            if self.getSkill(uninstallSkillId, skillType):
                if skillType == 0:
                    del self.skills[uninstallSkillId]
                else:
                    del self.auxiliarySkills[uninstallSkillId]
            self._refreshSkillSlots(skillType)
            self._loadSkillData(installSkillId, skillType)
            self.syncSkillSlots()

    def clearSkills(self):
        """
        清理技能
        """
        for skillId in self.skills:
            skill = self.getSkill(skillId, 0)
            if skill.state == 1:                 # 选中但未使用
                self.useSkill(skill.skillId, 0, 0)
            skill.clear()
        for skillId in self.auxiliarySkills:
            skill = self.getSkill(skillId, 1)
            if skill.state == 1:                # 选中但未使用
                self.useSkill(skill.skillId, 0, 1)
            skill.clear()

    def syncSkillSlots(self):
        """
        同步技能槽消息
        """
        msg = MsgPack()
        msg.setCmd("skill_slots")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("skillSlots", self.getSkillSlotsInfo(0))
        msg.setResult("usingSkill", self.getUsingSkillInfo())
        msg.setResult("auxiliarySkillSlots", self.getSkillSlotsInfo(1))
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def checkCanFire(self, fPos, wpId, bulletId, skillId, skillType):
        """
        检测玩家是否可以开火
        """
        fPosx, fPosy = fPos
        wpConf = config.getWeaponConf(wpId, mode=self.table.gameMode)
        extends = []        # 扩展
        reason = 0
        canFire = True
        skill = None
        clip = self.clip
        wpType = util.getWeaponType(wpId)
        costBullet = 1      # 消耗一颗子弹
        if not wpId or not bulletId or not wpConf:
            canFire = False
            reason = 6
            ftlog.warn("_verifyFire param is error", self.userId, wpId, bulletId, wpConf)
        else:
            costBullet = self.table.getCostBullet(self.gunId, self.gunLv, wpConf, self.clientId)
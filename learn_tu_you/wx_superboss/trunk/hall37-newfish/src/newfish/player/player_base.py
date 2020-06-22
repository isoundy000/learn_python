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
from newfish.entity.fishactivity.activity_table_system import ActivityTableSystem
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
        self.fpMultipleTestMode = None                      # 倍率测试模式 AB测试
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
        self.lastActionTime = int(time.time())      # 最后一次请求时间
        self.lastCatchTime = int(time.time())       # 最后一次捕鱼时间
        self.isFinishRedTask = False
        self.isBankrupt = False                     # 是否破产
        self.resetTime = 0
        self._fires = {}                            # 子弹
        self._catchFishes = {}                      # 捕获的鱼ID: 条数
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
        清理子弹变成金币
        """
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            self.dumpEconomicData()
            self.dumpGameData()
            self.clip = 0
            userchip.moveAllTableChipToChip(self.userId,
                                            FISH_GAMEID,
                                            "BI_NFISH_TCHIP_TO_CHIP",
                                            self.table.roomId,
                                            self.clientId,
                                            self.table.tableId,
                                            roomId=self.table.roomId)
            userchip.delTableChips(self.userId, [self.table.tableId])
            self.hallCoin = self.chip
        return self.chip
    
    def clearData(self):
        """更新玩家登录数据"""
        user_system.updateLoginData(self.userId)
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            self.dynamicOdds.saveDynamicOddsData()
            self.saveUserData()
            self.reportTableData()
        for bufferInfo in self.usedBufferInfos:
            bufferInfo.endBuffer()
        self.usedBufferInfos = []
        pass

    def dumpEconomicData(self):
        """保存渔场的缓存数据到数据库在重新载入"""
        self.economicData.refreshAllData()

    def dumpGameData(self):
        """保存游戏数据到数据库"""
        nowGunLevelKey = GameData.nowGunLevel if self.table.gameMode == config.CLASSIC_MODE else GameData.nowGunLevel_m
        data = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, nowGunLevelKey, {})
        data[str(self.table.bigRoomId)] = self.nowGunLevel
        gamedata.setGameAttrs(self.userId, FISH_GAMEID, [GameData.exp, nowGunLevelKey], [self.exp, json.dumps(data)])
        self.dumpGunData()

    def dumpGunData(self):
        # 渔场中切换版本的断线重连可能会在玩家进入渔场前收到gunlist消息,此时需要更新clientId和皮肤数据.
        clientId = util.getClientId(self.userId)
        if clientId != self.clientId:
            ftlog.info("dumpGunData, ", self.userId, self.offline, self.gunId, self.skinId, self.clientId, clientId)
            self.clientId = clientId
            self.refreshGunSkin()
        gun_system.setGunData(self.userId, self.gunId, [self.gunLv, self.gunExp, self.skinId], self.table.gameMode)
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.gunSkinPool, json.dumps(self.gunPool))    # 皮肤炮奖池数据

    @property
    def allChip(self):
        """
        所有金币（实时数据库+内存金币）  self.tableChip渔场金币  self.bulletChip 渔场内子弹价值金币
        """
        return self.chip + self.tableChip + self.bulletChip
    
    @property
    def chip(self):
        """
        渔场外金币       # 实时数据库金币
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
        持有金币（非实时数据库+内存金币）  self.hallCoin渔场外大厅金币(内存金币) self.tableChip渔场金币  self.bulletChip子弹价值的金币
        """
        return self.hallCoin + self.tableChip + self.bulletChip

    def costClip(self, bullet, eventId):
        """
        消耗子弹
        :param bullet: 子弹
        :param eventId: 事件
        """
        lastCoin = self.hallCoin
        self.clip -= bullet
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            chip = int(bullet * self.fpMultiple)
            self.economicData.consumeItem("bulletChip", chip, eventId, self.table.roomId, 1)
            if eventId != "EMOTICON_CONSUME":
                self.addLossCoin(chip)
                self.changeConsumeClip(bullet)
                if eventId == "BI_NFISH_GUN_FIRE":
                    self.reportBIFeatureData("BI_NFISH_GE_FT_FIRE", self.nowGunLevel, chip)
                    if self.energy < self.maxEnergy:
                        gunConf = config.getGunConf(self.gunId, self.clientId, self.gunLv, self.table.gameMode)
                        self.energy += bullet * 0.3 / gunConf.get("multiple", 1)        # 积攒能量
                        if ftlog.is_debug():
                            ftlog.debug("costClip->energy =", self.energy, "bullet =", bullet, "maxEnergy =", self.maxEnergy)
            if self.taskSystemTable and self.taskSystemTable.openBonusPool:
                self.table.room.lotteryPool.countBonusConsumeCoin(self.table.tableId, chip)
            if self.taskSystemTable and self.taskSystemTable.openCmpttPool:
                self.table.room.lotteryPool.countCmpttConsumeCoin(self.table.tableId, chip)
        if lastCoin > self.table.runConfig.coinShortage > self.holdCoin:
            coinShortageCount = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.coinShortageCount, {})  # 金币不足次数
            coinShortageCount.setdefault(str(self.table.runConfig.fishPool), 0)
            coinShortageCount[str(self.table.runConfig.fishPool)] += 1
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.coinShortageCount, json.dumps(coinShortageCount))
            if ftlog.is_debug():
                ftlog.debug("costClip", self.userId, lastCoin, self.table.runConfig.coinShortage, self.holdCoin, coinShortageCount)
        return self.clip

    def addClip(self, bullet=0, auto=0, skillId=0):
        """
        添加子弹
        :param bullet: 子弹
        :param auto: 是否子弹购买弹药
        :param skillId: 技能ID
        """
        chip = int(bullet * self.fpMultiple)        # 金币
        if skillId:
            self.changeConsumeClip(-bullet)         # 改变消耗子弹的数量
            # 技能取消返还子弹
            self.economicData.addGain([{"name": "bulletChip", "count": chip}], "BI_NFISH_CANCEL_SKILL", self.table.roomId)
            self.clip += bullet
            self.addProfitCoin(chip)
            self.fireCost.setdefault(str(self.table.bigRoomId), 0)
            self.fireCost[str(self.table.bigRoomId)] -= chip
            # GrandPrizePool.incrGrandPrizePool(self.table.bigRoomId, -chip)
            return 0, [chip, bullet]    # 金币、子弹
        if auto:
            # 自动购买弹药(使用牌桌内金币购买)
            bullet = self.tableChip // self.fpMultiple
            chip = int(bullet * self.fpMultiple)
            if bullet > 0:
                self.economicData.chgTableChip(-chip)
                self.economicData.chgBulletChip(chip)
                self.clip += bullet
                return 0, [chip, bullet]
        else:
            # if self.clip >= 200000:
            #     return 2, []
            # 使用牌桌外金币购买弹药
            chip = userchip.getChip(self.userId)            # 1001
            bullet = chip // self.fpMultiple                # 1001//100
            bulletChip = int(bullet * self.fpMultiple)      # 10 * 100
            tableChip = userchip.getTableChip(self.userId, FISH_GAMEID, self.table.tableId) + chip
            tfinal, final, delta = userchip.setTableChipToN(
                self.userId,
                FISH_GAMEID,
                tableChip,
                "BI_NFISH_CHIP_TO_TCHIP",
                self.table.roomId,
                self.clientId,
                self.table.tableId,
                roomId=self.table.roomId)
            if delta == -chip:
                self.hallCoin = self.chip                   # 剩余的金币
                self.economicData.chgTableChip(chip - bulletChip)   # 改变桌子缓存金币
                self.economicData.chgBulletChip(bulletChip)         # 改变子弹缓存金币
                self.clip += bullet                                 # 增加子弹
                return 0, [chip, bullet]
        return 1, []

    def _incrGameTimer(self):
        """增加游戏时长"""
        if self.userId <= 0:
            return
        if not self.isFinishRedTask:    # 是否完成所有新手任务
            self.isFinishRedTask = util.isFinishAllRedTask(self.userId)
        curDayStartTs = util.getDayStartTimestamp(int(time.time()))     # 获取0点时间戳
        key = GameData.playGameTime % (FISH_GAMEID, self.userId, curDayStartTs)
        daobase.executeUserCmd(self.userId, "INCR", key)                # 每日游戏时长（有效期2天）,playGameTime:44:uid:当日零点时间戳
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

    def upGunLevel(self):
        """更新用户等和炮的等级"""
        self.pearlCount = util.balanceItem(self.userId, PEARL_KINDID)
        gunLevelKey = GameData.gunLevel if self.table.gameMode == config.CLASSIC_MODE else GameData.gunLevel_m
        self.level, self.gunLevel = gamedata.getGameAttrs(self.userId, FISH_GAMEID,
                                                          [GameData.level, gunLevelKey])

    def _loadUserData(self):
        """
        读取玩家数据
        """
        self.dailyTSKey = str(util.getDayStartTimestamp(int(time.time())))
        self.economicData = EconomicData(self, self.table)
        self.name = util.getNickname(self.userId)
        # 魅力、性别、用户头像URL
        self.charm, self.sex, self.purl = userdata.getAttrs(self.userId, ["charm", "sex", "purl"])
        # 读取玩家游戏数据
        gunLevelKey = GameData.gunLevel if self.table.gameMode == config.CLASSIC_MODE else GameData.gunLevel_m      # 用户最大火炮等级
        self.level, self.gunLevel, self.exp, self.redState, \
        self.registTime, self.newbieMode, self.profitForChest, \
        self.profitForCoin, self.bankruptCount, self.fireCost, \
        self.dropPearlCount, self.dailyProfitCoin, self.gameResolution, \
        self.grandPrixProfitCoin, self.clientVersion, self.platformOS, self.fireCount, \
        self.lotteryFireCostChip, self.realProfitCoin, self.dailyFishPoolProfitCoin = gamedata.getGameAttrs(
            self.userId,
            FISH_GAMEID,
            [GameData.level, gunLevelKey, GameData.exp, GameData.redState,      # redState 新手任务状态
             GameData.registTime, ABTestData.newbieMode, GameData.profitChest,  # newbieMode 新手概率模式 profitChest 玩家在各场次的金币宝箱奖池
             GameData.profitCoin, GameData.bankruptCount, GameData.fireCost,    # profitCoin 玩家在各场次的盈亏金币 bankruptCount 玩家各场次累计破产次数  fireCost 玩家各个渔场开火消耗
             GameData.dropPearlCount, GameData.dailyProfitCoin, GameData.gameResolution,    # dropPearlCount 获得掉落珍珠的数量  dailyProfitCoin每日盈亏金币量K  gameResolution玩家的游戏分辨率
             GameData.grandPrixProfitCoin, GameData.clientVersion, GameData.platformOS, # grandPrixProfitCoin大奖赛盈亏金币量 客户端当前版本号 clientVersion   platformOS 微信小游戏的客户端系统
             GameData.fireCount, GameData.lotteryFireCostChip, GameData.realProfitCoin, # fireCount 玩家各个渔场开火次数 lotteryFireCostChip 各个渔场开火消耗 realProfitCoin 各场次真实盈亏
             GameData.dailyFishPoolProfitCoin])         # dailyFishPoolProfitCoin 每日渔场盈亏金币量K
        self.level = max(1, self.level)
        # 游戏数据格式转换
        self.enterRedState = self.redState
        self.dropPearlCount = int(self.dropPearlCount) if isinstance(self.dropPearlCount, (int, float)) else 0
        self.profitForChest = strutil.loads(self.profitForChest, False, True, {})
        self.profitForCoin = strutil.loads(self.profitForCoin, False, True, {})
        self.bankruptCount = strutil.loads(self.bankruptCount, False, True, {})
        self.fireCost = strutil.loads(self.fireCost, False, True, {})
        self.fireCount = strutil.loads(self.fireCount, False, True, {})
        self.lotteryFireCostChip = strutil.loads(self.lotteryFireCostChip, False, True, {})
        self.dailyProfitCoin = strutil.loads(self.dailyProfitCoin, False, True, {})
        self.dailyFishPoolProfitCoin = strutil.loads(self.dailyFishPoolProfitCoin, False, True, {})
        self.gameResolution = strutil.loads(self.gameResolution, False, True, [])
        self.grandPrixProfitCoin = strutil.loads(self.grandPrixProfitCoin, False, True, {})
        self.realProfitCoin = strutil.loads(self.realProfitCoin, False, True, {})
        # 玩家每日数据
        dayFishData = weakdata.getDayFishDataAll(self.userId, FISH_GAMEID)
        self.resetTime = dayFishData.get(WeakData.resetTime, 0)
        self.starfish = dayFishData.get(WeakData.starfish, 0)
        # 玩家珍珠数（用于控制珍珠掉率）
        self.pearlCount = util.balanceItem(self.userId, PEARL_KINDID)
        self.isFinishRedTask = util.isFinishAllRedTask(self.userId)
        # self.initCurve5017TestMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.initCurve5017TestMode)
        # self.upgradeGunTestMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.upgradeGunTestMode)
        if self.isSupplyBulletPowerMode():
            self.bulletPowerPool = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, ABTestData.bulletPowerPool)    # 子弹威力奖池
        self._refreshGunLevel()
        self.fpMultipleTestMode = config.getPublic("fpMultipleTestMode") or \
                                  gamedata.getGameAttr(self.userId, FISH_GAMEID, ABTestData.fpMultipleTestMode)
        self._refreshFpMultiple()

        # 渔场倍率AB测试玩家需要设置此数据.
        if self.isFpMultipleMode():
            # 进入渔场时提示此渔场可以使用的倍率红点
            tipVal = module_tip.getTipValue(self.userId, module_tip.findModuleTip("fpmultiple"))
            unlockedFpMultiples = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.unlockedFpMultiples, [])
            if tipVal:
                unlockedFpMultiples.extend(tipVal)
                unlockedFpMultiples = list(set(unlockedFpMultiples))
            tipVal2 = []
            for idx in range(len(unlockedFpMultiples) - 1, -1, -1):
                if self.table.runConfig.minMultiple <= unlockedFpMultiples[idx] <= self.table.runConfig.maxMultiple:
                    tipVal2.append(unlockedFpMultiples[idx])
                    del unlockedFpMultiples[idx]
            if set(tipVal) != set(tipVal2):
                if tipVal:
                    module_tip.resetModuleTipEvent(self.userId, "fpmultiple")
                gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.unlockedFpMultiples, json.dumps(unlockedFpMultiples))
                if tipVal2:
                    module_tip.addModuleTipEvent(self.userId, "fpmultiple", tipVal2)

        if self.isRobotUser:                                                        # 是机器人
            _gunLevelKeys = config.getGunLevelKeysConf(self.table.gameMode)
            _gunLevelList = [lv for lv in _gunLevelKeys if self.table.runConfig.minGunLevel <= lv <= self.table.runConfig.maxGunLevel]
            if _gunLevelList:
                self.gunLevel = self.nowGunLevel = random.choice(_gunLevelList)     # 随机一个炮的等级

        self.matchingFishPool = self.getMatchingFishPool(self.fpMultiple)
        self.dynamicOdds = DynamicOdds(self.table, self)
        self.achieveSystem = AchievementTableSystem(self.table, self)               # 成就系统
        self.activitySystem = ActivityTableSystem(self.table, self)                 # 活动系统

        self.refreshVipLevel()
        self.refreshGunData()       # 刷新火炮数据
        self.refreshHonor()

        self.incrPearlDropRatio = config.getIncrPearlDropRatio(self.userId)         # 获取可以增加的珍珠额外掉率
        self.incrCrystalDropRatio = config.getIncrCrystalDropRatio(self.userId)     # 获取可以增加的水晶额外掉率

        piggybank = config.getPiggyBankConf(self.clientId, self.vipLevel).get("paid", {})   # 获取存钱罐配置
        resetTime = piggybank.get("resetTime", -1)
        self.dailyKey = piggy_bank._getDataKey(int(time.time()), resetTime)

        itemPresentTestMode = util.getItemPresentTestMode(self.userId)
        self.ignorePresent = itemPresentTestMode == "b"
        self.cardNum = mini_game.getCardNum(self.table.roomId, self.userId)         # 小游戏卡片数

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

    def loadAllSkillItemData(self):
        """
        加载所有道具技能的数据
        """
        if self.table.gameMode == config.MULTIPLE_MODE:
            for item_id in self.table.runConfig.skill_item.keys():
                if item_id in self.skill_item:
                    continue
                skillItem = SkillItem(self.table, self, item_id)
                self.skill_item[item_id] = skillItem

    def getSkillItemInfo(self):
        """
        获取技能道具信息
        """
        data = {}
        for k, v in self.skills_item_slots.items():
            val = copy.deepcopy(v)
            del val["start_time"], val["conf"]             # val["remainTimes"], val["maxTimes"]
            data[k] = val
        return data

    def syncSkillItemSlots(self):
        """同步技能道具的槽位信息"""
        msg = MsgPack()
        msg.setCmd("item_slots")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("itemSlots", self.getSkillItemInfo())
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def end_skill_item(self, kindId=0):
        """结束道具的效果"""
        if kindId:
            del self.skill_item[kindId]
        else:
            self.skill_item = {}
        self.loadAllSkillItemData()

    def _refreshSkillSlots(self, skillType):
        """
        刷新技能数据 {5101: [star_level, current_level]}
        """
        if skillType == 0:
            self.skillSlots = skill_system.getInstalledSkill(self.userId, self.table.gameMode)
        ftlog.info("_refreshSkillSlots, userId =", self.userId, "skillType =", skillType, "skillSlots =",
                   self.skillSlots)

    def _loadSkillData(self, skillId, skillType):
        """
        读取单个技能数据
        """
        if skillType == 0:  # 主动技能
            if skillId in self.skillSlots:
                if self.skillSlots[skillId][1] > self.table.runConfig.maxSkillLevel:  # 技能当前等级
                    self.skillSlots[skillId][1] = self.table.runConfig.maxSkillLevel
                skillStar = self.skillSlots[skillId][0]
                skillGrade = self.skillSlots[skillId][1]
                skill = skill_release.createSkill(self.table, self, skillId, skillStar, skillGrade, 0)  # 根据技能Id 创建技能类
                self.skills[skillId] = skill
        else:  # 辅助技能
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
                skillSlots[skillId].extend([cdTimeLeft, coolDown])  # [1,2,3,4,5,50,60]
                totalSkillGrade += skillGrade
            self.maxEnergy = 50 + totalSkillGrade * 50
            return skillSlots
        else:  # 辅助技能
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

    def getUsingSkillInfo(self):
        """
        获取使用中的技能数据
        """
        usingSkillInfo = {}
        if self.usingSkill:
            skillId = self.usingSkill[-1].get("skillId")
            skillType = self.usingSkill[-1].get("skillType")
            skill = self.getSkill(skillId, skillType)
            if skill:
                usingSkillInfo[skill.skillId] = [skill.clip, skillType]
        return usingSkillInfo

    def refreshGunData(self):
        """
        刷新火炮数据
        """
        gunSkinIdKey = GameData.gunSkinId if self.table.gameMode == config.CLASSIC_MODE else GameData.gunSkinId_m
        self.gunId = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, gunSkinIdKey)
        gunData = gun_system.getGunData(self.userId, self.gunId, self.table.gameMode)
        # 皮肤炮熟练等级.
        self.gunLv = gunData[gun_system.INDEX_LEVEL]
        self.gunExp = gunData[gun_system.INDEX_EXP]
        self.skinId = gunData[gun_system.INDEX_SKINID]
        self.refreshGunSkin()
        userGunIds = gun_system.getGunIds(self.userId, self.table.gameMode)
        if self.gunId not in userGunIds:  # 皮肤炮过期后，默认装备已拥有的最后一个皮肤炮
            self.chgGunData(userGunIds[-1])
        self.gunPool = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.gunSkinPool, {})

    def refreshGunSkin(self):
        """
        刷新火炮皮肤数据
        """
        skins = config.getGunConf(self.gunId, self.clientId, mode=self.table.gameMode).get("skins")
        if self.skinId not in skins:
            self.skinId = skins[0]
            if ftlog.is_debug():
                ftlog.debug("refreshGunSkin, gun_skin", self.userId, self.gunId, self.gunLv, self.gunExp, self.skinId, self.clientId)



    def _refreshGunLevel(self):
        """
        刷新使用火炮的等级
        """
        # 注意:self.nowGunLevel需要和weaponId一致!
        nowGunLevelKey = GameData.nowGunLevel if self.table.gameMode == config.CLASSIC_MODE else GameData.nowGunLevel_m     # 当前玩家在经典渔场中的火炮等级
        data = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, nowGunLevelKey, {})
        self.nowGunLevel = data.get(str(self.table.bigRoomId), 0)
        if not data or not self.nowGunLevel:
            self.nowGunLevel = self.gunLevel            # nowGunLevel渔场内现在火炮的等级 gunLevel渔场外火炮达到的最大等级
        else:
            if self.nowGunLevel > self.gunLevel:        # 25 > 10
                self.nowGunLevel = self.gunLevel
        self.nowGunLevel = min(self.nowGunLevel, self.table.runConfig.maxGunLevel)      # 10 10
        if self.gunLevel >= self.table.runConfig.minGunLevel:
            self.nowGunLevel = max(self.nowGunLevel, self.table.runConfig.minGunLevel)

    def refreshVipLevel(self):
        """
        刷新用户VIP等级
        """
        self.vipLevel = hallvip.userVipSystem.getUserVip(self.userId).vipLevel.level

    def getMatchingFishPool(self, fpMultiple):
        """
        获取玩家渔场倍率对应的fishPool
        """
        fishPool = self.table.runConfig.fishPool
        if self.table.typeName not in config.NORMAL_ROOM_TYPE or not self.isFpMultipleMode():
            return fishPool
        fishPoolMultipleDict = {}
        for v in gdata.roomIdDefineMap().values():
            roomConf = v.configure
            if roomConf.get("typeName") not in [config.FISH_FRIEND]:
                continue
            fishPoolMultipleDict[str(roomConf.get("fishPool"))] = roomConf.get("multiple", 1)
        tmpList = sorted(fishPoolMultipleDict.items(), key=lambda x: x[1])
        for v in tmpList:
            if fpMultiple >= v[1]:
                fishPool = int(v[0])
        if ftlog.is_debug():
            ftlog.debug("getFishPool, userId =", self.userId, "fishPool-multiple =", tmpList, "fpMultiple =",
                        fpMultiple,
                        "tableFishPool =", self.table.runConfig.fishPool, "matchingFishPool =", fishPool)
        return fishPool

    def isSupplyBulletPowerMode(self):
        """
        是否为补足子弹威力的模式
        """
        return self.table.typeName == config.FISH_GRAND_PRIX
        # if self.table.typeName not in config.NORMAL_ROOM_TYPE:
        #     return False
        # else:
        #     return int(self.table.runConfig.fishPool) in config.getPublic("suppleBulletPowerFishPool", [])

    def addBulletPowerPool(self, val, fpMultiple, gunMultiple, gunX):
        """
        增加子弹威力奖池
        :param val: 炮的威力
        :param fpMultiple: 渔场倍率
        :param gunMultiple: 单倍|双倍炮
        :param gunX: 千炮 炮的倍率 | 经典为1
        :return:
        """
        if not self.isSupplyBulletPowerMode():
            return
        val = val * fpMultiple * gunMultiple * gunX
        self.bulletPowerPool += val                     # 增加子弹威力奖池
        if ftlog.is_debug():
            ftlog.debug("bulletPower, userId =", self.userId, "bulletPowerPool =", self.bulletPowerPool, "changed =", val,
                    "fpMultiple =", fpMultiple, "gunMultiple =", gunMultiple, "gunX =", gunX)

    def reduceBulletPowerPool(self, val, fpMultiple, gunMultiple, gunX):
        """
        扣除子弹威力奖池
        """
        if not self.isSupplyBulletPowerMode():          # 是否为补足子弹威力的模式
            return
        val = val * fpMultiple * gunMultiple * gunX
        self.bulletPowerPool -= val
        if ftlog.is_debug():
            ftlog.debug("bulletPower, userId =", self.userId, "bulletPowerPool =", self.bulletPowerPool, "changed =", val,
                    "fpMultiple =", fpMultiple, "gunMultiple =", gunMultiple, "gunX =", gunX)

    def processBulletPower(self, curPower, totalFishScore, fpMultiple, gunMultiple, cnt, bulletPowerPool, gunX):
        """
        处理子弹威力
        :param curPower: 当前子弹的威力
        :param totalFishScore: 鱼的总积分
        :param fpMultiple: 渔场倍率
        :param gunMultiple: 炮的倍率 单倍炮|双倍炮
        :param cnt: 一网打的鱼
        :param bulletPowerPool: 子弹能量池
        :param gunX: 炮的倍数
        """
        finalPower = curPower
        if self.isSupplyBulletPowerMode():      # 是否为补足子弹威力的模式
            if ftlog.is_debug():
                ftlog.debug("1 bulletPower, process =", self.isSupplyBulletPowerMode(), "userId =", self.userId,
                        "curPower =", curPower, "totalFishScore =", totalFishScore, "fpMultiple =", fpMultiple,
                        "gunMultiple =", gunMultiple, "cnt =", cnt, "bulletPowerPool =", bulletPowerPool, "gunX =", gunX)
            if curPower > totalFishScore:
                self.addBulletPowerPool((curPower - totalFishScore) / cnt, fpMultiple, gunMultiple, gunX)
            elif curPower == totalFishScore:
                pass
            else:
                poolPower = bulletPowerPool // (fpMultiple * gunMultiple)
                maxPower = min(2 * curPower, totalFishScore)
                _power = poolPower if maxPower - curPower > poolPower else maxPower - curPower
                self.reduceBulletPowerPool(_power / cnt, fpMultiple, gunMultiple, gunX)
                finalPower += _power
                if ftlog.is_debug():
                    ftlog.debug("bulletPower, process =", self.isSupplyBulletPowerMode(), "userId =", self.userId,
                            "curPower =", curPower, "maxPower =", maxPower, "totalFishScore =", totalFishScore,
                            "fpMultiple =", fpMultiple, "gunMultiple =", gunMultiple, "finalPower =", finalPower, "gunX =", gunX)
        return finalPower

    def _refreshFpMultiple(self):
        """
        刷新使用的渔场倍率
        """
        if not self.isFpMultipleMode():
            return
        data = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.nowFpMultiple, {})
        fpMultiple = data.get(str(self.table.bigRoomId))
        if fpMultiple is None:
            fpMultiple = config.getGunLevelConf(self.gunLevel, self.table.gameMode).get("unlockMultiple", 1)
        fpMultiple = max(self.table.runConfig.minMultiple, min(fpMultiple, self.table.runConfig.maxMultiple))
        self.fpMultiple = fpMultiple

    def isFpMultipleMode(self):
        """
        是否为渔场倍率模式
        """
        if self.table.typeName not in config.NORMAL_ROOM_TYPE:
            return False
        return self.fpMultipleTestMode in ["b"]


    


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

    def addProfitCoin(self, coin):
        """
        玩家金币增加
        """
        self.addLotteryPoolCoin(-coin)
        self.addProfitChest(coin)
        self.recordProfitCoin(coin)

    def addLossCoin(self, coin):
        """
        玩家金币减少
        """
        self.addLotteryPoolCoin(coin)
        self.addProfitChest(-coin)
        self.recordProfitCoin(-coin)
        self.fireCost.setdefault(str(self.table.bigRoomId), 0)
        self.fireCost[str(self.table.bigRoomId)] += coin
        # GrandPrizePool.incrGrandPrizePool(self.table.bigRoomId, coin)

    def addProfitRing(self, ring):
        """
        玩家金环增加
        """
        self.addLotteryPoolRing(-ring)

    def addLossRing(self, ring):
        """
        玩家金环减少
        """
        self.addLotteryPoolRing(ring)
        self.fireCost.setdefault(str(self.table.bigRoomId), 0)
        self.fireCost[str(self.table.bigRoomId)] += ring
        # GrandPrizePool.incrGrandPrizePool(self.table.bigRoomId, coin)

    def addLotteryPoolCoin(self, coin):
        """
        增加房间金币总奖池
        """
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            if ftlog.is_debug():
                ftlog.debug("addLotteryPoolCoin->", self.userId, coin)
            self.table.room.lotteryPool.addCoin(coin)

    def addLotteryPoolRing(self, ring):
        """
        增加房间金环总奖池
        """
        if self.table.typeName in config.NORMAL_ROOM_TYPE:
            if ftlog.is_debug():
                ftlog.debug("addLotteryPoolRing->", self.userId, ring)
            self.table.room.RingLotteryPool.addRing(ring)

    def addProfitChest(self, coin):
        pass

    def clearProfitChest(self):
        pass

    def recordProfitCoin(self, coin):
        """
        记录玩家在该房间的盈亏
        :param coin: 增减的金币
        """
        pass

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


    def useBullet(self, bulletKindId):
        pas

    def addCatchFishes(self, fishTypes):
        """
        添加捕获的鱼
        :param fishTypes: 鱼ID
        """
        self.lastCatchTime = int(time.time())           # 最后捕鱼时间
        for fishType in fishTypes:
            if fishType not in self._catchFishes:
                self._catchFishes[fishType] = 0
            self._catchFishes[fishType] += 1

    def getTargetFishs(self):
        """
        获取任务目标鱼
        """
        fishes = []
        if self.currentTask and self.currentTask[2] == 1 and self.currentTask[3]:
            if ftlog.is_debug():
                ftlog.debug("player.currentTask =", self.currentTask)
            if self.currentTask[3].has_key("target1"):
                fishes.append(self.currentTask[3]["target1"])
            if self.currentTask[3].has_key("target2"):
                fishes.append(self.currentTask[3]["target2"])
        if self.taskSystemUser:
            fishes.extend(self.taskSystemUser.getTaskTargets())
        return fishes

    def changeConsumeClip(self, clip):
        """
        统计触发奖券鱼阵和活动鱼阵的子弹数量(使用渔场基础倍率转换子弹数量)
        clip是子弹数
        """
        _clip = clip * self.fpMultiple // self.table.runConfig.multiple     # 子弹 * 10 / 10
        self.couponConsumeClip += _clip
        self.activityConsumeClip += _clip

    def resetCouponConsumeClip(self):
        """重置奖券消耗的子弹数"""
        self.couponConsumeClip = 0

    def resetActivityConsumeClip(self):
        """重置活动消耗的子弹数"""
        self.activityConsumeClip = 0

    def addFire(self, bulletId, wpId, sendTimestamp, fpMultiple, skill=None, power=None, multiple=None, clientFire=True, targetPos=None, fishType=None, costChip=0):
        """
        添加开火信息
        :param bulletId: 子弹Id
        :param wpId: 武器Id
        :param sendTimestamp: 时间
        :param fpMultiple: 渔场倍率
        :param skill: 技能对象
        :param power: 威力
        :param multiple: 单倍|双倍炮
        :param clientFire:
        :param targetPos: 目标位置
        :param fishType:
        :param costChip: 消耗的金币
        """
        if ftlog.is_debug():
            ftlog.debug("getFireWpId->add", self.userId, bulletId, wpId, sendTimestamp, power, self.gunId, self.gunLv, fpMultiple)
        nowTimestamp = int(time.time())
        if bulletId in self._fires:
            del self._fires[bulletId]
            if ftlog.is_debug():
                ftlog.debug("getFireWpId->add, delete repeat bullet, userId =", self.userId, "bulletId =", bulletId)
        self._fires[bulletId] = {
            "wpId": wpId,
            "skill": skill,
            "gunId": self.gunId,
            "gunLevel": self.gunLv,
            "sendTimestamp": sendTimestamp,
            "receiveTimestamp": nowTimestamp,
            "power": power,
            "initPower": power,
            "multiple": multiple,
            "targetPos": targetPos,
            "fishType": fishType,
            "fpMultiple": fpMultiple,
            "maxStage": len(power) - 1 if isinstance(power, list) and len(power) > 0 else 0
        }
        self._fires[bulletId].update({"superBullet": self.isSuperBullet(bulletId)})     # 超级子弹 获取炮的配置
        if clientFire:
            from newfish.game import TGFish
            event = FireEvent(self.userId, FISH_GAMEID, self.table.roomId, self.table.tableId, wpId, fpMultiple, costChip, self.holdCoin)
            TGFish.getEventBus().publishEvent(event)
            if hasattr(self, "fireCostChip"):
                self.fireCostChip += costChip       # 开火消耗的总金币
            wpType = util.getWeaponType(wpId)
            if wpType == config.GUN_WEAPON_TYPE:
                self.fireCount.setdefault(str(self.table.runConfig.fishPool), 0)        # 开火次数
                self.fireCount[str(self.table.runConfig.fishPool)] += 1
                if self.table.typeName in config.QUICK_START_ROOM_TYPE:
                    self.lotteryFireCostChip.setdefault(str(self.table.runConfig.fishPool), 0)
                    self.lotteryFireCostChip[str(self.table.runConfig.fishPool)] += costChip    # 开火消耗金币奖池

    def delFire(self, bulletId=0, extendId=0, wpId=0):
        """删除子弹"""
        if ftlog.is_debug():
            ftlog.debug("delFire, userId =", self.userId, "bulletId =", bulletId, "extendId =", extendId, "wpId =", wpId)
        if bulletId in self._fires:
            del self._fires[bulletId]
        if extendId in self._fires:
            del self._fires[extendId]
        if wpId > 0:
            delBulletId = []
            for bulletId, fire in self._fires.iteritems():
                if fire["wpId"] == wpId:
                    delBulletId.append(bulletId)
            for bulletId in delBulletId:
                if bulletId in self._fires:
                    del self._fires[bulletId]

    def getFire(self, bulletId):
        """获取一颗子弹的信息"""
        return self._fires.get(bulletId, {})

    def getFireWpId(self, bulletId):
        """获取子弹的武器 有效期35s"""
        wpId = None
        fire = self._fires.get(bulletId)
        if ftlog.is_debug():
            ftlog.debug("getFireWpId->fire =", self.userId, bulletId, self._fires)
        if fire:
            nowTimestamp = int(time.time())
            if nowTimestamp - fire["receiveTimestamp"] <= 35:
                wpId = fire["wpId"]
            else:
                if ftlog.is_debug():
                    ftlog.debug("getFireWpId->del", self.userId, bulletId, fire)
                self.delFire(bulletId)
        return wpId

    def getFireSkill(self, bulletId):
        """获取子弹的技能对象"""
        return self._fires.get(bulletId, {}).get("skill")

    def getFirePower(self, bulletId, stageId=0, wpId=0):
        """获取子弹的威力 第几阶段"""
        # power = self._fires.get(bulletId, {}).get("power") or [0]
        # power = power[stageId] if 0 <= stageId < len(power) else power[0]
        try:
            power = self._fires.get(bulletId, {}).get("power")
            power = power[stageId]
        except Exception, e:
            ftlog.error("getFirePower", "userId =", self.userId, "wpId =", wpId, "bulletId =", bulletId
                        , "stageId =", stageId, "e =", e)
            power = 0
        return power

    def getFireInitPower(self, bulletId, stageId=0):
        """获取子弹初始化威力 第几阶段"""
        power = self._fires.get(bulletId, {}).get("initPower") or [0]
        power = power[stageId] if stageId < len(power) else power[0]
        return power

    def getFireMultiple(self, bulletId, extendId):
        """
        获取开火时的倍率
        """
        if extendId:
            _fire = self._fires.get(extendId, {})
        else:
            _fire = self._fires.get(bulletId, {})
        return _fire.get("multiple")

    def getFireFpMultiple(self, bulletId, extendId):
        """
        获取开火时的渔场倍率
        """
        if extendId:
            _fire = self._fires.get(extendId, {})
        else:
            _fire = self._fires.get(bulletId, {})
        return _fire.get("fpMultiple", self.table.runConfig.multiple)

    def decreaseFirePower(self, bulletId, val, stageId=0):
        """减少子弹威力"""
        if self._fires.get(bulletId, {}).get("power") and stageId < len(self._fires[bulletId]["power"]):
            self._fires[bulletId]["power"][stageId] -= val
            self._fires[bulletId]["power"][stageId] = max(0, self._fires[bulletId]["power"][stageId])
            if ftlog.is_debug():
                ftlog.debug("decreaseFirePower", self.userId, bulletId, val, self._fires[bulletId]["power"][stageId])

    def getFireMaxStage(self, bulletId, extendId):
        """
        获取字段的最大阶段数值
        """
        if extendId:
            _fire = self._fires.get(extendId, {})
        else:
            _fire = self._fires.get(bulletId, {})
        return _fire.get("maxStage", 0)

    def isSuperBullet(self, bulletId):
        """子弹有几率变成超级子弹、提升威力"""
        fire = self._fires.get(bulletId)
        ftlog.debug("isSuperBullet->fire =", self.userId, bulletId, self._fires)
        try:
            if fire:
                wpId = fire["wpId"]
                gunId = fire["gunId"]
                gunLv = fire["gunLevel"]
                sendTimestamp = fire["sendTimestamp"]
                if util.getWeaponType(wpId) != config.GUN_WEAPON_TYPE:  # 火炮/千炮
                    return {}
                gunConf = config.getGunConf(gunId, self.clientId, gunLv, self.table.gameMode)
                if gunConf["effectType"] != 2:
                    return {}
                randInt = util.getSeedRandom(sendTimestamp)
                if ftlog.is_debug():
                    ftlog.debug("isSuperBullet->", randInt)
                if sendTimestamp > 0 and randInt <= gunConf["effectProbb"]:
                    if ftlog.is_debug():
                        ftlog.debug("isSuperBullet True", bulletId)
                    return gunConf
        except Exception, e:
            ftlog.error("isSuperBullet error", self.userId, fire, traceback.format_exc())
        return {}

    def getGunConf(self, bulletId, extendId=0):
        """获取开火子弹 炮的配置"""
        if extendId:
            fire = self._fires.get(extendId)
        else:
            fire = self._fires.get(bulletId)
        if not fire:
            ftlog.info("getGunConf error", self.userId, self.gunId, bulletId, extendId)
        try:
            if fire:
                wpId = fire["wpId"]
                gunId = fire["gunId"]
                gunLv = fire["gunLevel"]
                if util.getWeaponType(wpId) != 1:
                    if ftlog.is_debug():
                        ftlog.debug("getGunConf->", self.userId, fire)
                    return {}
                return config.getGunConf(gunId, self.clientId, gunLv, self.table.gameMode)
        except Exception, e:
            ftlog.error("getGunConf error", self.userId, fire, traceback.format_exc())
        return {}

    def getBulletDisappearSeconds(self):
        """
        获取子弹消失的剩余秒数
        """
        interval = 0
        maxTstmp = 0
        for k, v in self._fires.iteritems():
            if v["receiveTimestamp"] > maxTstmp:
                maxTstmp = v["receiveTimestamp"]
        if maxTstmp > 0:
            interval = 35 - (time.time() - maxTstmp)
            if interval < 0:
                interval = 0
        return interval

    def addTableChip(self, chip, eventId):
        """添加桌子的金币"""
        if chip > 0:
            changed = self.economicData.addGain([{"name": "tableChip", "count": int(chip)}],
                                                eventId, self.table.roomId)
            if changed:
                change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.table.getBroadcastUids())

    def catchBudget(self, gainChip, gainCoupon, items, nowExp=0, wpId=0):
        """
        捕获添加奖励
        :param gainChip:
        :param gainCoupon:
        :param items:
        :param nowExp:
        :param wpId:
        :return:
        """
        self.reportBIFeatureData("BI_NFISH_GE_FT_CATCH", wpId, gainChip)


    def getFinalWpPower(self, bulletId):
        """
        获取子弹加成后的威力
        """
        _fire = self.getFire(bulletId)
        wpId = _fire.get("wpId", 0)
        wpType = util.getWeaponType(wpId)
        # 威力加成
        effectAddition = _fire.get("superBullet", {}).get("effectAddition", 1)
        honorAddition = honor_system.getWeaponPowerAddition(self.ownedHonors, wpId)
        bufferAddition = self.getPowerAddition(wpId)
        wpPower = 0
        if wpType == config.GUN_WEAPON_TYPE:  # 火炮
            wpPower = _fire.get("power", 0) * effectAddition * honorAddition * bufferAddition
        return wpPower

    def refreshHonor(self):
        """刷新称号 称号"""
        self.ownedHonors = honor_system.getOwnedHonors(self.userId)
        honorId, _ = honor_system.getInstalledHonor(self.userId, self.ownedHonors)
        self.honorId = honorId if honorId >= 0 else 0

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
            costBullet = self.table.getCostBullet(self.gunId, self.gunLv, wpConf, self.clientId)    # 消耗的子弹数量
            if skillId:
                skill = self.getSkill(skillId, skillType)
                if skill and skillId == skill_release.weaponSkillMap.get(wpId):                     # 根据武器ID获取 技能炮
                    usingSkill = [val.get("skillId") for val in self.usingSkill]
                    if skill in usingSkill:
                        if ftlog.is_debug():
                            ftlog.debug("player.usingSkill, userId =", self.userId, self.usingSkill, skillId, skillType)
                        isOK = skill.costClip(bulletId, fPosx, fPosy)
                        clip = skill.clip
                        if isOK:
                            if self.getTargetFishs():
                                extends.append(1)
                        else:
                            canFire = False
                            reason = 5
                    else:
                        canFire = False
                        reason = 4
                        ftlog.warn("_verifyFire usingSkill error", self.userId, self.usingSkill, skillId)
                elif not skill or wpType not in [config.RB_FIRE_WEAPON_TYPE, config.RB_BOMB_WEAPON_TYPE]:
                    canFire = False
                    reason = 3
                    ftlog.warn("_verifyFire skill error", self.userId, skillId)
            elif wpType == config.GUN_WEAPON_TYPE and (wpId > self.gunLevel or self.getUsingSkillInfo()):   # 获取使用中的技能数据
                canFire = False
                reason = 2
                ftlog.warn("_verifyFire weapon error", self.userId, wpId, self.gunLevel)
            elif self.clip < costBullet:
                canFire = False
                reason = 1
                if ftlog.is_debug():
                    ftlog.debug("_verifyFire clip not enough")
        if ftlog.is_debug():
            ftlog.debug("_verifyFire succ, ", self.userId, canFire, reason)
        return canFire, reason, clip, costBullet, extends, skill

    def sendFireMsg(self, userId, seatId, extends, params):
        """
        发送开火确认消息
        """
        fPos = params.get("fPos")
        wpId = params.get("wpId")
        bulletId = params.get("bulletId")
        skillId = params.get("skillId")
        timestamp = params.get("timestamp")
        canFire = params.get("canFire")
        reason = params.get("reason")
        clip = params.get("clip")                   # 消耗的金币
        skillType = params.get("skillType", 0)
        lockFId = params.get("lockFId", 0)          # 锁鱼
        fPosx, fPosy = fPos
        retMsg = MsgPack()
        retMsg.setCmd("fire")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("wpId", wpId)
        retMsg.setResult("bulletId", bulletId)
        retMsg.setResult("skillId", skillId)
        retMsg.setResult("skillType", skillType)
        retMsg.setResult("extends", extends)        # 扩展字段
        retMsg.setResult("timestamp", timestamp)
        retMsg.setResult("reason", reason)
        retMsg.setResult("grandPrixFireCount", 0)   # 大奖赛开火次数
        retMsg.setResult("clip", clip)
        retMsg.setResult("lockFId", lockFId)
        superBullet = self.getFire(bulletId).get("superBullet", {})  # self.isSuperBullet(bulletId)
        retMsg.setResult("superBullet", 1 if superBullet else 0)  # 测试代码
        GameMsg.sendMsg(retMsg, userId)
        if canFire:
            retMsg.setResult("fPosx", fPosx)
            retMsg.setResult("fPosy", fPosy)
            retMsg.setResult("seatId", seatId)
            GameMsg.sendMsg(retMsg, self.table.getBroadcastUids(userId))
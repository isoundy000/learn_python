# -*- coding=utf-8 -*-
"""
Created by lichen on 16/12/13.
"""

import copy
import json
import time
import random
import traceback

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
from newfish.entity.catchfish.dynamic_odds import DynamicOdds
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
from newfish.entity.level_prize_wheel import LevelPrizeWheel
from newfish.entity.skill.skill_item import SkillItem, State


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
        self.bulletPowerPool = 0                            # 玩家子弹威力奖池.
        # self.upgradeGunTestMode = None
        self.grandPrixStartTS = 0                           # 大奖赛
        self.grandPrixUseSkillTimes = []
        self.grandPrixProfitCoin = {}                       # 大奖赛盈亏金币量
        self.clip = 0
        self.fpMultipleTestMode = None                      # 倍率测试模式 AB测试
        self.fpMultiple = table.runConfig.multiple          # 倍率
        self.matchingFishPool = table.runConfig.fishPool    # 比赛渔场
        self.prizeWheel = None
        if self.table.typeName in config.DYNAMIC_ODDS_ROOM_TYPE:
            self.prizeWheel = PrizeWheel(self.userId, table.runConfig.fishPool, self.table.roomId)
        if self.table.gameMode == config.MULTIPLE_MODE and self.table.typeName not in [config.FISH_TIME_MATCH, config.FISH_TIME_POINT_MATCH]:   # 千炮转盘
            self.prizeWheel = LevelPrizeWheel(self.userId, table.runConfig.fishPool, self.table.roomId)
        self.vipLevel = 0
        self.clientId = ""
        if clientId:
            self.clientId = clientId                        # 此client是字符串
        self.lang = util.getLanguage(self.userId, self.clientId)
        # 主技能
        self.skills = {}                                            # 技能ID: 对象
        self.skillSlots = {}                                        # 技能槽 [skill_Id: [0, 0, 0, 0, 0]]
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
        self.fireCount = {}                                 # {fishPool: times}
        self.skill_item = {}                        # 道具技能对象 item_id: skill_item
        self.skills_item_slots = {}                 # 道具技能槽item_id: {"cost": xxx, "progress": [0, 10], "state": 0}
        self._onInit()
        self.robotScript = None

    def _onInit(self):
        """
        初始化
        """
        self._initVarData()
        self._loadUserData()
        self.loadAllSkillData()
        self.loadAllSkillItemData()

    def _initVarData(self):
        """
        初始化变量
        """
        self.lastActionTime = int(time.time())      # 最后一次请求时间
        self.lastCatchTime = int(time.time())       # 最后一次捕鱼时间
        self.isFinishRedTask = False                # 是否完成新手任务
        self.isBankrupt = False                     # 是否破产
        self.resetTime = 0
        self._fires = {}                            # 子弹信息
        self._catchFishes = {}                      # 捕获的鱼ID: 条数
        self._comboBudgetTime = 1.2                 # 连击奖励的定时器时间间隔
        self.clip = 0
        self.combo = 0
        self.invalidCatch = 0
        self.enterTime = 0
        self.offline = 0
        self.rank = 0
        self.couponConsumeClip = 0                  # 奖券消耗的金币
        self.activityConsumeClip = 0
        self.energy = 0
        self.maxEnergy = 0
        self.luckyNum = 0
        self.luckyCount = 0
        self.currentTask = None                     # 玩家当前任务[任务名、任务Id、类型、条数]
        self.taskSystemUser = None
        self.taskSystemTable = self.table.taskSystemTable
        self.activitySystem = None
        self.mainQuestSystem = None                 # 主线任务
        self.totalGainChip = 0
        self.catchBonus = 0                         # 捕获收益
        # 开火消耗的金币，用于红包券抽奖
        self.lotteryFireCostChip = {}               # 开火消耗的金币，用于红包券抽奖
        self.gameTime = 0                           # 玩的分钟数
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

        self.fireCost = {}              # {bigRoomId: coin, bigRoomId1: coin}
        # 开火消耗的金币量.
        self.fireCostChip = 0
        # 每日盈亏金币数据.
        self.dailyKey = ""
        self.dailyProfitConin = {}
        # 每日渔场盈亏数据
        self.dailyTSKey = ""
        self.dailyFishPoolProfitCoin = {}   # 每日渔场盈亏金币量K
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
            self.gunEffectState(4)                                  # 清理定时器
            self.clearTimer()
            self.clearingClip()
            self.clearData()
            if self.robotScript:
                self.robotScript.clear()
                self.robotScript = None
            if self.compAct:
                self.compAct = None
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
            userchip.moveAllTableChipToChip(self.userId, FISH_GAMEID, "BI_NFISH_TCHIP_TO_CHIP",  self.table.roomId,
                self.clientId, self.table.tableId, roomId=self.table.roomId)
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
        self.achieveSystem and self.achieveSystem.dealLeaveTable()      # 成就系统
        self.achieveSystem = None
        self.taskSystemUser and self.taskSystemUser.dealLeaveTable()    # 任务系统
        self.taskSystemUser = None
        self.activitySystem and self.activitySystem.leaveRoom()         # 活动系统
        self.activitySystem = None
        self.mainQuestSystem and self.mainQuestSystem.dealLeaveTable()  # 主线任务
        self.mainQuestSystem = None

    @property
    def allChip(self):
        """
        所有金币（实时数据库+内存金币）  self.tableChip渔场金币  self.bulletChip 渔场内子弹价值金币
        """
        return self.chip + self.tableChip + self.bulletChip

    @property
    def holdCoin(self):
        """
        持有金币（非实时数据库+内存金币）  self.hallCoin渔场外大厅金币(内存金币) self.tableChip渔场金币  self.bulletChip子弹价值的金币
        """
        return self.hallCoin + self.tableChip + self.bulletChip

    @property
    def chip(self):
        """
        渔场外金币       # 实时数据库金币
        """
        return userchip.getChip(self.userId) if self.userId > 0 else 0

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

    def costClip(self, bullet, eventId):
        """
        消耗渔场内的子弹
        :param bullet: 子弹数量
        :param eventId: 事件
        """
        lastCoin = self.holdCoin
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
        :param bullet: 子弹数量
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
        self.gameTime += 1                                          # 时间、分钟数
        self.checkLimitTimeGift = True  # 限时礼包
        weakdata.incrDayFishData(self.userId, "gameTime", 1)
        if util.getDayStartTimestamp(self.resetTime) != util.getDayStartTimestamp(int(time.time())):
            self.resetTime = weakdata.getDayFishData(self.userId, "resetTime", 0)
        self.activitySystem and self.activitySystem.incrGameTime()
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
        self.level, self.gunLevel = gamedata.getGameAttrs(self.userId, FISH_GAMEID, [GameData.level, gunLevelKey])

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
        self.starfish = dayFishData.get(WeakData.starfish, 0)                   # 海星数量
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

        if self.isRobotUser:                                                        # 是机器人
            _gunLevelKeys = config.getGunLevelKeysConf(self.table.gameMode)
            _gunLevelList = [lv for lv in _gunLevelKeys if self.table.runConfig.minGunLevel <= lv <= self.table.runConfig.maxGunLevel]
            if _gunLevelList:
                self.gunLevel = self.nowGunLevel = random.choice(_gunLevelList)     # gunLevel炮的最大等级 self.nowGunLevel现在渔场中使用的火炮等级

        self.matchingFishPool = 44005                           # self.getMatchingFishPool(self.fpMultiple)
        self.dynamicOdds = DynamicOdds(self.table, self)
        self.achieveSystem = AchievementTableSystem(self.table, self)               # 成就系统
        self.activitySystem = ActivityTableSystem(self.table, self)                 # 活动系统

        self.refreshVipLevel()                                                      # 刷新用户VIP等级
        self.refreshGunData()                                                       # 刷新火炮数据
        self.refreshHonor()                                                         # 刷新称号 称号

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
        for skillId in self.skillSlots:
            self._loadSkillData(skillId, 0)


    def loadAllSkillItemData(self):
        """
        加载所有道具技能的数据
        """
        if self.table.gameMode != config.MULTIPLE_MODE:
            return
        for item_id in self.table.runConfig.skill_item.keys():
            if item_id in self.skill_item:
                continue
            skillItem = SkillItem(self.table, self, item_id)
            self.skill_item[item_id] = skillItem

    def getSkillItemInfo(self, kindId=0):
        """
        获取技能道具信息
        """
        data = {}
        for k, v in self.skills_item_slots.items():
            val = copy.deepcopy(v)
            if val["state"] == State.USING:
                val["progress"][0] += float('%.2f' % time.time()) - val["start_time"]
                val["progress"][0] = min(val["progress"][0], val["progress"][1])
            del val["start_time"], val["conf"]  # val["remainTimes"], val["maxTimes"]
            if kindId == 0:
                data[k] = val
            elif k == kindId:
                data[k] = val
        return data

    def syncSkillItemSlots(self, kindId=0):
        """同步技能道具的槽位信息"""
        msg = MsgPack()
        msg.setCmd("item_slots")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("itemSlots", self.getSkillItemInfo(kindId))
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
            if self.table.typeName == config.FISH_NEWBIE:
                self.skillSlots = skill_system.getNewbieSkill(self.userId)
            else:
                self.skillSlots = skill_system.getInstalledSkill(self.userId, self.table.gameMode)
        ftlog.info("_refreshSkillSlots, userId =", self.userId, "skillType =", skillType, "skillSlots =", self.skillSlots)

    def _loadSkillData(self, skillId, skillType=0):
        """
        读取单个技能数据
        """
        if skillId in self.skillSlots:
            self.skillSlots[skillId][2] = min(self.skillSlots[skillId][2], self.table.runConfig.maxSkillLevel)
            skillState = self.skillSlots[skillId][0]
            skillStar = self.skillSlots[skillId][1]
            skillGrade = self.skillSlots[skillId][2]
            skill = skill_release.createSkill(self.table, self, skillId, skillState, skillStar, skillGrade, 0)
            self.skills[skillId] = skill

    def getSkillSlotsInfo(self, skillType):
        """
        获取技能槽数据 skillType 0:主动 1:辅助
        """
        if skillType == 0:
            skillSlots = copy.deepcopy(self.skillSlots)
            totalSkillGrade = 0
            for skillId in skillSlots:
                skillGrade = skillSlots[skillId][2]
                cdTimeLeft = self.skills[skillId].cdTimeLeft
                coolDown = self.skills[skillId].coolDown
                dayFreeUse = 1 if self.skills[skillId].checkIfDayFree() else 0
                skillSlots[skillId].extend([cdTimeLeft, coolDown, dayFreeUse])
                totalSkillGrade += skillGrade
            self.maxEnergy = 50 + totalSkillGrade * 50
            return skillSlots
        else:
            auxiliarySkillSlots = copy.deepcopy(self.auxiliarySkillSlots)
            # for skillId in auxiliarySkillSlots:
            #     skillGrade = auxiliarySkillSlots[skillId][1]
            #     if skillGrade > self.table.runConfig.maxSkillLevel:
            #         skillGrade = self.table.runConfig.maxSkillLevel
            #         auxiliarySkillSlots[skillId][1] = skillGrade
            #     cdTimeLeft = self.auxiliarySkills[skillId].cdTimeLeft
            #     coolDown = self.auxiliarySkills[skillId].coolDown
            #     auxiliarySkillSlots[skillId].extend([cdTimeLeft, coolDown])
            return auxiliarySkillSlots

    def refreshSkillStartTime(self):
        """
        刷新技能CD开始时间
        """
        for skillId in self.skillSlots:
            self.skills[skillId].changeCDStartTime()
        for skillId in self.auxiliarySkillSlots:
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

    def chgGunData(self, gunId):
        """
        切换炮台
        """
        # 判断是否满足炮台装备条件.
        if not gun_system.isCanEquip(self.userId, gunId, self.table.gameMode):
            ftlog.debug("chgGunData failed! userId =", self.userId, "gunId =", gunId, "mode =", self.table.gameMode)
            return
        if self.gunId == gunId:     # 当前火炮切换（升级、切换皮肤）
            gunData = gun_system.getGunData(self.userId, self.gunId, self.table.gameMode)
            self.skinId = gunData[gun_system.INDEX_SKINID]
            gun_system.setGunData(self.userId, self.gunId, [self.gunLv, self.gunExp, self.skinId], self.table.gameMode)
        else:                       # 切换至其他火炮
            # 先保存原炮台数据
            gun_system.setGunData(self.userId, self.gunId, [self.gunLv, self.gunExp, self.skinId], self.table.gameMode)
            self.gunId = gunId
            # 设置当前已装备火炮
            gunSkinIdKey = GameData.gunSkinId if self.table.gameMode == config.CLASSIC_MODE else GameData.gunSkinId_m
            gamedata.setGameAttr(self.userId, FISH_GAMEID, gunSkinIdKey, self.gunId)
            # 获取当前已装备火炮详细数据
            gunData = gun_system.getGunData(self.userId, self.gunId, self.table.gameMode)
            self.gunLv = gunData[gun_system.INDEX_LEVEL]
            self.gunExp = gunData[gun_system.INDEX_EXP]
            self.skinId = gunData[gun_system.INDEX_SKINID]

    def sendChgGunInfo(self):
        """
        发送火炮修改消息
        """
        message = MsgPack()
        message.setCmd("chg_gun")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", self.userId)
        message.setResult("seatId", self.seatId)
        message.setResult("gunId", self.gunId)
        message.setResult("gunLevel", self.gunLv)
        message.setResult("gameMode", self.table.gameMode)
        # message.setResult("skinId", self.skinId)
        # GameMsg.sendMsg(message, self.table.getBroadcastUids())
        uids = self.table.getBroadcastUids()
        clientUids = {}
        for _uid in uids:
            clientUids.setdefault(util.getClientId(_uid), []).append(_uid)
        for _cli, _uids in clientUids.iteritems():
            skins = config.getGunConf(self.gunId, _cli, mode=self.table.gameMode).get("skins")
            skinId = self.skinId if self.skinId in skins else skins[0]
            message.setResult("skinId", skinId)
            GameMsg.sendMsg(message, _uids)

    def refreshHonor(self):
        """刷新称号 称号"""
        self.ownedHonors = honor_system.getOwnedHonors(self.userId)
        honorId, _ = honor_system.getInstalledHonor(self.userId, self.ownedHonors)
        self.honorId = honorId if honorId >= 0 else 0

    def incrExp(self, gainExp):
        """
        增加玩家等级经验值
        """
        if gainExp > 0:
            self.exp += gainExp
        if ftlog.is_debug():
            ftlog.debug("incrExp, userId =", self.userId, "level =", self.level, "gainExp =", gainExp, "exp =",
                        self.exp)
        return self.exp

    def incExpLevel(self, nowExp):
        """
        玩家等级升级
        """
        userLevelConf = config.getUserLevelConf()
        lvUpExp = userLevelConf[self.level - 1]["exp"] if self.level <= len(userLevelConf) else userLevelConf[-1]["exp"]
        while nowExp >= lvUpExp > 0:
            nowExp -= lvUpExp
            self.exp -= lvUpExp             # 下一级需要经验
            self.level += 1                 # 等级
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.level, self.level)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.exp, self.exp)
            from newfish.game import TGFish
            from newfish.entity.event import UserLevelUpEvent
            event = UserLevelUpEvent(self.userId, FISH_GAMEID, self.level)
            TGFish.getEventBus().publishEvent(event)
            self.sendULevelUpMsg(self.level, self.exp)

    def sendULevelUpMsg(self, level, exp):
        """
        发送玩家等级升级消息
        """
        msg = MsgPack()
        msg.setCmd("lvup")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("lv", level)
        userLevelConf = config.getUserLevelConf()
        lvUpExp = userLevelConf[level - 1]["exp"] if level <= len(userLevelConf) else userLevelConf[-1]["exp"]
        msg.setResult("expPct", min(100, max(0, int(exp * 100. / lvUpExp))))
        rewards = userLevelConf[level - 1]["rewards"] if level <= len(userLevelConf) else userLevelConf[-1]["rewards"]
        if rewards:
            util.addRewards(self.userId, rewards, "BI_NFISH_USER_LEVEL_UP_REWARD", level)
        msg.setResult("rewards", rewards)
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())
        bireport.reportGameEvent("BI_NFISH_GE_USER_LEVEL_UP", self.userId, FISH_GAMEID, self.table.roomId,
                                 self.table.tableId, int(level), 0, 0, 0, [], self.clientId)
        if ftlog.is_debug():
            ftlog.debug("sendULevelUpMsg, userId =", self.userId, "msg =", msg)

    def incrGunExp(self, exp):
        """
        增加皮肤炮熟练度经验值
        """
        if self.table.runConfig.fishPool == 44003:
            exp *= 1.2
        elif self.table.runConfig.fishPool == 44004:
            exp *= 1.5
        elif self.table.runConfig.fishPool == 44005:
            exp *= 3
        self.gunExp += int(exp)
        maxLevelConf = config.getGunConf(self.gunId, self.clientId,
                config.getGunMaxLevel(self.gunId, self.clientId, self.table.gameMode), self.table.gameMode)
        self.gunExp = maxLevelConf["totalExp"] if self.gunExp > maxLevelConf["totalExp"] else self.gunExp
        return self.gunExp

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
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.dropPearlCount, self.dropPearlCount)    # 获得掉落珍珠的数量
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.fireCost, json.dumps(self.fireCost))    # 玩家各个渔场开火消耗
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.fireCount, json.dumps(self.fireCount))
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.lotteryFireCostChip, json.dumps(self.lotteryFireCostChip))
        if hasattr(self, "fireCostChip") and self.fireCostChip > 0:
            piggy_bank.fireCostChip(self.userId, self.clientId, self.vipLevel, self.fireCostChip)       # 存钱罐
            self.fireCostChip = 0
        if hasattr(self, "dailyProfitCoin") and self.table.typeName in config.NORMAL_ROOM_TYPE:         # 每日盈亏金币量K
            if self.dailyProfitCoin.get(self.dailyKey, 0) < 0:                                          # 获取数据存储key值
                if ftlog.is_debug():
                    ftlog.debug("dailyProfitCoin, userId =", self.userId, util.timestampToStr(int(self.dailyKey)), self.dailyProfitCoin[self.dailyKey])
                piggy_bank.LossCoin(self.userId, self.clientId, self.vipLevel, abs(self.dailyProfitCoin[self.dailyKey]))
                self.dailyProfitCoin[self.dailyKey] = 0
            _keys = [int(k) for k in self.dailyProfitCoin.keys()]
            _keys.sort()
            if len(_keys) > 1:
                del self.dailyProfitCoin[str(_keys[0])]
                if ftlog.is_debug():
                    ftlog.debug("del expired daily key, userId =", self.userId, util.timestampToStr(_keys[0]), _keys)
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.dailyProfitCoin, json.dumps(self.dailyProfitCoin))
        if self.table.typeName in [config.FISH_GRAND_PRIX]:
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.grandPrixProfitCoin, json.dumps(self.grandPrixProfitCoin))  # 大奖赛盈亏金币量
        if self.isSupplyBulletPowerMode():
            gamedata.setGameAttr(self.userId, FISH_GAMEID, ABTestData.bulletPowerPool, self.bulletPowerPool)    # 玩家子弹威力奖池.
        ts_keys = self.dailyFishPoolProfitCoin.get(str(self.table.runConfig.fishPool), {}).keys()               # 每日渔场盈亏金币量K
        if ts_keys:
            _keys = [int(_k) for _k in ts_keys]
            _keys.sort()
            if _keys[0] < util.getDayStartTimestamp(int(time.time())):
                del self.dailyFishPoolProfitCoin[str(self.table.runConfig.fishPool)][str(_keys[0])]
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.dailyFishPoolProfitCoin, json.dumps(self.dailyFishPoolProfitCoin))

    def dumpGunData(self):
        # 渔场中切换版本的断线重连可能会在玩家进入渔场前收到gunlist消息,此时需要更新clientId和皮肤数据.
        clientId = util.getClientId(self.userId)
        if clientId != self.clientId:
            ftlog.info("dumpGunData, ", self.userId, self.offline, self.gunId, self.skinId, self.clientId, clientId)
            self.clientId = clientId
            self.refreshGunSkin()
        gun_system.setGunData(self.userId, self.gunId, [self.gunLv, self.gunExp, self.skinId], self.table.gameMode)
        gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.gunSkinPool, json.dumps(self.gunPool))    # 皮肤炮奖池数据

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

    def addFire(self, bulletId, wpId, sendTimestamp, fpMultiple, skill=None, power=None, multiple=None,
                clientFire=True, targetPos=None, fishType=None, costChip=0):
        """
        添加开火信息
        :param bulletId: 子弹Id
        :param wpId: 武器Id
        :param sendTimestamp: 时间
        :param fpMultiple: 渔场倍率
        :param skill: 技能对象
        :param power: 威力
        :param multiple: 单倍|双倍炮
        :param clientFire: 客户端开火
        :param targetPos: 目标位置
        :param fishType: 鱼的Id
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
            "wpId": wpId,                          # 武器ID
            "skill": skill,                        # 技能对象
            "gunId": self.gunId,                   # 皮肤炮Id
            "gunLevel": self.gunLv,                # 皮肤炮等级
            "sendTimestamp": sendTimestamp,        # 发送时间
            "receiveTimestamp": nowTimestamp,      # 接收时间
            "power": power,                        # 威力
            "initPower": power,                    # 初始威力
            "multiple": multiple,                  # 单倍|双倍炮
            "targetPos": targetPos,                # 目标位置
            "fishType": fishType,                  # 鱼的Id
            "fpMultiple": fpMultiple,              # 渔场倍率
            "maxStage": len(power) - 1 if isinstance(power, list) and len(power) > 0 else 0    # 最大阶段
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
                self.gunEffectState(3, costChip)                              # 只有千炮渔场才有此对象

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
                self.delFire(bulletId)
        return wpId

    def getFireSkill(self, bulletId):
        """获取子弹的技能对象"""
        return self._fires.get(bulletId, {}).get("skill")

    def getFirePower(self, bulletId, stageId=0, wpId=0):
        """获取子弹的威力 第几阶段"""
        try:
            power = self._fires.get(bulletId, {}).get("power")
            power = power[stageId]
        except Exception as e:
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
        """
        扣减子弹威力
        """
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
                if util.getWeaponType(wpId) != config.GUN_WEAPON_TYPE:
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
        if gainChip > 0:
            self.addTableChip(gainChip, "BI_NFISH_CATCH_GAIN")
            self.totalGainChip += gainChip
            self.catchBonus += gainChip * config.getCommonValueByKey("friendHelpCoinMultiple")
        if gainCoupon > 0:              # 红包券
            changed = util.addItems(self.userId,
                                    [{"name": COUPON_KINDID, "count": int(gainCoupon)}],
                                    "BI_NFISH_CATCH_GAIN",
                                    self.table.roomId,
                                    roomId=self.table.roomId,
                                    tableId=self.table.tableId,
                                    clientId=self.clientId)
            change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.table.getBroadcastUids())
            datachangenotify.sendDataChangeNotify(FISH_GAMEID, self.userId, ["chip"])
        from newfish.game import TGFish
        for item in items:
            if util.isChestRewardId(item["itemId"]):    # 判断道具ID是否为宝箱
                from newfish.entity.chest import chest_system
                if chest_system.getChestIdleOrder(self.userId) == -1:       # 得到空闲的宝箱栏位置
                    pass
                else:
                    chest_system.newChestItem(self.userId, item["itemId"], "BI_NFISH_CATCH_GAIN")
            else:
                changed = util.addItems(self.userId,
                                        [{"name": item["itemId"], "count": int(item["count"])}],
                                        "BI_NFISH_CATCH_GAIN",
                                        self.table.roomId,
                                        roomId=self.table.roomId,
                                        tableId=self.table.tableId,
                                        clientId=self.clientId)
                change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.table.getBroadcastUids())
            if item["itemId"] in [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]:  # 青铜、白银、黄金招财珠
                bulletCoin = int(item["count"]) * BULLET_KINDIDS[item["itemId"]]
                self.totalGainChip += bulletCoin
                event = BulletChangeEvent(self.userId, FISH_GAMEID, item["itemId"], int(item["count"]), self.table.roomId)
                TGFish.getEventBus().publishEvent(event)
            elif item["itemId"] == STARFISH_KINDID:     # 海星
                starfishCount = int(item["count"])
                self.starfish += starfishCount
                event = StarfishChangeEvent(self.userId, FISH_GAMEID, starfishCount, self.table.bigRoomId)
                TGFish.getEventBus().publishEvent(event)
            elif item["itemId"] == PEARL_KINDID:        # 珍珠
                pearl = int(item["count"])
                self.pearlCount += pearl
                self.taskSystemUser and self.taskSystemUser.dealGetPearl(pearl)
                self._addPearlDropCount(pearl)

    def addCombo(self):
        """添加连击数 添加定时器"""
        self.combo += 1
        if self.comboTimer:
            self.comboTimer.cancel()
        self.comboTimer = FTLoopTimer(self._comboBudgetTime, 0, self._comboBudget)
        self.comboTimer.start()

    def _comboBudget(self):
        """连击奖励"""
        baseNum = 0
        addition = 0
        if self.combo >= 20:
            baseNum = self.combo // 5 * 5
        elif self.combo >= 15:
            baseNum = 13
        elif self.combo >= 10:
            baseNum = 8
        elif self.combo >= 5:
            baseNum = 3
        gunConf = config.getGunConf(self.gunId, self.clientId, self.gunLv, self.table.gameMode)
        if gunConf and gunConf["effectType"] == 1 and random.randint(1, 10000) <= gunConf["effectProbb"]:
            addition = gunConf["effectAddition"]
        gainChip = int(baseNum * self.fpMultiple)
        extraChip = max(int(gainChip * addition), 1) if gainChip > 0 and addition > 0 else 0
        comboChip = gainChip + extraChip
        if comboChip > 0:
            msg = MsgPack()
            msg.setCmd("comboReward")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", self.userId)
            msg.setResult("combo", self.combo)
            msg.setResult("gainChip", gainChip)         # 连击奖励
            msg.setResult("extraChip", extraChip)       # 额外加成金币
            GameMsg.sendMsg(msg, self.userId)
            changed = self.economicData.addGain([{"name": "tableChip", "count": int(comboChip)}],
                                                "BI_NFISH_CATCH_GAIN", self.table.roomId)
            change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.table.getBroadcastUids())
            self.addProfitCoin(comboChip)               # 增加收益

            if self.table.typeName in config.NORMAL_ROOM_TYPE:
                from newfish.entity.event import ComboEvent
                from newfish.game import TGFish
                event = ComboEvent(self.userId, FISH_GAMEID, self.combo, comboChip)
                TGFish.getEventBus().publishEvent(event)
                self.triggerComboEvent(event)
        self.combo = 0

    def checkConnect(self, isInvalid):
        """
        检查连接
        :param isInvalid: 是否是合法的捕获
        :return:
        """
        if self.invalidCatch >= 2 and ftlog.is_debug():
            ftlog.debug("checkConnect", self.userId, self.invalidCatch)
        if isInvalid:
            self.invalidCatch += 1
            if self.invalidCatch >= 10:
                msg = MsgPack()
                msg.setCmd("reset_connect")
                msg.setResult("gameId", FISH_GAMEID)
                msg.setResult("userId", self.userId)
                GameMsg.sendMsg(msg, self.userId)
                self.invalidCatch = 0
        else:
            self.invalidCatch = 0

    def gunChange(self, gLv):
        """
        切换火炮等级
        """
        reason = 0
        if gLv > self.gunLevel or not config.getGunLevelConf(gLv, self.table.gameMode):
            reason = 1
        else:
            if gLv < self.table.runConfig.minGunLevel:
                if self.nowGunLevel >= gLv:
                    reason = 2
            elif gLv > self.table.runConfig.maxGunLevel:
                return
            elif self.getUsingSkillInfo():      # 获取使用中的技能数据
                self.nowGunLevel = gLv
                return
        retMsg = MsgPack()
        retMsg.setCmd("gchg")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("gLv", gLv)
        retMsg.setResult("userId", self.userId)
        retMsg.setResult("seatId", self.seatId)
        retMsg.setResult("reason", reason)
        retMsg.setResult("gameMode", self.table.gameMode)
        GameMsg.sendMsg(retMsg, self.userId)
        if reason == 0:
            self.nowGunLevel = gLv
            result = retMsg.getKey("result")
            del result["reason"]
            GameMsg.sendMsg(retMsg, self.table.getBroadcastUids(self.userId))
            from newfish.game import TGFish
            event = ChangeGunLevelEvent(self.userId, FISH_GAMEID, self.table.bigRoomId, self.nowGunLevel)
            TGFish.getEventBus().publishEvent(event)

    def gunUpgrade(self, protect):
        """
        普通炮升级
        """
        lastFpMultiple = 1
        isUpgrade = gun_system.upgradeGun(self.userId, protect, self.table.gameMode)
        if isUpgrade:
            self.upGunLevel()
            self.gunChange(self.gunLevel)
            # # 升级后切换倍率
            # if self.isFpMultipleMode():
            #     fpMultiple = config.getGunLevelConf(self.nowGunLevel).get("unlockMultiple", 1)
            #     if False and lastFpMultiple < fpMultiple:
            #         self.changeFpMultiple(fpMultiple, True)

            # 渔场解锁提示.
            # nextRoomId = config.getCommonValueByKey("unlockNextRoomId")
            # if self.newbieMode in ["b", "c"] and self.level == 15 and nextRoomId:
            #     self.sendRoomUnlockMsg(nextRoomId)
            # else:# 渔场解锁提示.
            #     nextRoomKey = "unlockNextRoomIdLevel%d" % self.level
            #     nextRoomId = config.getCommonValueByKey(nextRoomKey)
            #     if nextRoomId:
            #         self.sendRoomUnlockMsg(nextRoomId)
            testMode = util.getNewbieABCTestMode(self.userId)
            unlockNextRoomIdList = config.getCommonValueByKey("unlockNextRoomIdList", [])
            for nextRoomId in unlockNextRoomIdList:
                minLevel = util.getRoomMinLevel(nextRoomId, testMode)
                minCoin = util.getRoomMinCoin(nextRoomId, testMode)
                if minLevel == self.level:
                    # 渔场解锁时自动补齐金币.
                    delta = 0
                    if minCoin > 0 and self.allChip < minCoin + 10000:
                        delta = minCoin + 10000 - self.allChip
                    if delta > 0:
                        util.addRewards(self.userId, [{"name": config.CHIP_KINDID, "count": delta}],
                                        "BI_NFISH_COMPENSTAE_UNLOCK_NEXT_ROOM_COIN", self.level)
                        self.addProfitCoin(delta)
                    if ftlog.is_debug():
                        ftlog.debug("unlock next room, userId =", self.userId, minLevel, minCoin, delta, self.allChip)
                    self.sendRoomUnlockMsg(nextRoomId)
            # # 使用B模式
            # # 50倍场，玩家升到17级，处于A测试模式时曲线设为9.
            # if self.table.runConfig.fishPool == 44003 and self.level == 17 and self.initCurve5017TestMode in ["a"]:
            #     if gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.setUserCurve5017) == 0:
            #         gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.setUserCurve5017, 1)
            #         _cnt = self.bankruptCount.get(str(self.table.runConfig.fishPool), 0)
            #         if _cnt == 0:
            #             _waveId = 9
            #         elif 0 < _cnt <= 2:
            #             _waveId = 6
            #         else:
            #             _waveId = 0
            #         if _waveId > 0:
            #             self.dynamicOdds.resetOdds(_waveId)

    def incrGunLevel(self, nowExp):
        """
        提升皮肤炮熟练度等级
        """
        oldLevel = self.gunLv
        maxLevel = config.getGunMaxLevel(self.gunId, self.clientId, self.table.gameMode)
        if oldLevel == maxLevel:
            return
        for x in range(1, maxLevel + 1):
            levelConf = config.getGunConf(self.gunId, self.clientId, x, self.table.gameMode)
            if nowExp <= levelConf["totalExp"]:
                break
        if x != oldLevel:
            self.gunLv = x
            self.chgGunData(self.gunId)                 # 更新皮肤炮数据
            if x > oldLevel:
                for level in range(oldLevel + 1, x + 1):
                    self.sendGunLevelUpMsg(level)

    def sendGunLevelUpMsg(self, level):
        """
        发送皮肤炮升级成功消息
        """
        msg = MsgPack()
        msg.setCmd("gun_lvup")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("gunId", self.gunId)
        msg.setResult("gunLevel", level)
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())

    def addProfitCoin(self, coin):
        """
        玩家金币增加
        """
        self.addLotteryPoolCoin(-coin)          # 增加房间金币总奖池
        self.addProfitChest(coin)
        self.recordProfitCoin(coin)             # 记录玩家在该房间的盈亏

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
        检查技能是否满足条件
        """
        reason = 0
        skill = self.getSkill(skillId, skillType)
        if skill:
            if select:
                bullet = self.tableChip // self.fpMultiple
                if self.usingSkill:
                    lastSkillId = self.usingSkill[-1].get("skillId")
                    lastSkillType = self.usingSkill[-1].get("skillType", 0)
                    lastSkill = self.getSkill(lastSkillId, lastSkillType)
                    # 如果上一个技能与当前选中技能不同，状态为装备中且取消后子弹可以购买当前选中技能，则取消上一个技能
                    if (lastSkillId != skillId or lastSkillType != skillType) and lastSkill and lastSkill.state == 1:
                        if lastSkill.getCost + self.clip + bullet >= skill.getCost:
                            lastSkill.use(0)
                if self.clip < skill.getCost:
                    if self.clip + bullet >= skill.getCost:
                        isOK = self.table.clip_add(self.userId, self.seatId, auto=1)
                        if not isOK:
                            reason = 1
                    else:
                        reason = 1  # 使用技能所需子弹不足
                elif skill.cdTimeLeft > 0 and self.isFinishRedTask:
                    reason = 2  # 技能正在冷却
                elif skill.state == 1:
                    reason = 3  # 技能正在装备中，选中失败
            else:
                if skill.state == 2:
                    reason = 4  # 技能正在使用中，取消失败
        else:
            reason = 5  # 技能槽没有该技能
        return reason

    def useSkill(self, skillId, select, skillType):
        """
        使用技能
        """
        reason = self._checkSkillCondition(skillId, select, skillType)
        if reason == 0:
            currSkill = self.getSkill(skillId, skillType)
            if select:  # 选中技能(装备技能)
                currSkill.use(1)  # 无之前技能记录或者已经被取消了上一个技能，直接装备技能
            else:  # 取消技能
                if len(self.usingSkill) == 1 and skillId == self.usingSkill[-1].get("skillId") \
                        and skillType == self.usingSkill[-1].get("skillType", 0):  # 只有当前技能
                    currSkill.use(0)
                    self.table.broadcastGunChange(self)
                elif len(self.usingSkill) > 1 and skillId == self.usingSkill[-1].get("skillId") \
                        and skillType == self.usingSkill[-1].get("skillType", 0):  # 存在技能使用记录
                    lastSkillId = self.usingSkill[-2].get("skillId")
                    lastSkillType = self.usingSkill[-2].get("skillType", 0)
                    lastSkill = self.getSkill(lastSkillId, lastSkillType)
                    currSkill.use(0)  # 取消当前技能， 并切换到上一个技能
                    if lastSkill:
                        lastSkill.use(1)
                else:  # 无之前技能使用记录或技能顺序错误，技能取消失败
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
            ftlog.info("installSkill->skills =",
                       self.userId, skillType,
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
            if skill.state == 1:    # 选中但未使用
                self.useSkill(skill.skillId, 0, 0)
            skill.clear()
        for skillId in self.auxiliarySkills:
            skill = self.getSkill(skillId, 1)
            if skill.state == 1:    # 选中但未使用
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
        """
        使用招财珠
        :param bulletKindId: 青铜、白银、黄金
        """
        msg = MsgPack()
        msg.setCmd("bullet_use")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("bullet", bulletKindId)
        if util.balanceItem(self.userId, bulletKindId) and \
                bulletKindId in [BRONZE_BULLET_KINDID, SILVER_BULLET_KINDID, GOLD_BULLET_KINDID]:
            changed = util.addItems(self.userId,
                                    [{"name": bulletKindId, "count": -1}],
                                    "ITEM_USE",
                                    roomId=self.table.roomId,
                                    tableId=self.table.tableId,
                                    clientId=self.clientId,
                                    changeNotify=True)
            if changed:
                change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.userId)
                bulletChip = BULLET_KINDIDS[bulletKindId]
                changed = self.economicData.addGain([{"name": "tableChip", "count": bulletChip}], "ITEM_USE", self.table.roomId)
                change_notify.changeNotify(self.userId, FISH_GAMEID, changed, self.table.getBroadcastUids())
                msg.setResult("chip", bulletChip)
                msg.setResult("code", 0)
                GameMsg.sendMsg(msg, self.table.getBroadcastUids())
                from newfish.game import TGFish
                event = BulletChangeEvent(self.userId, FISH_GAMEID)
                TGFish.getEventBus().publishEvent(event)
                return
        msg.setResult("code", 1)
        GameMsg.sendMsg(msg, self.userId)
        # 使用招财珠进入时，指定概率曲线
        # if self.table.runConfig.fishPool == 44005:
            # limitedDynamicOdds = gamedata.getGameAttrInt(self.userId, FISH_GAMEID, GameData.limitedDynamicOdds)
            # if limitedDynamicOdds == 0 and self.allChip < self.table.runConfig.minCoin and self.vipLevel <= 1:
            #     sectionId = 5
            #     self.dynamicOdds.resetOdds(sectionId)
            #     gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.limitedDynamicOdds, 1)

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

    def addAttackBossNum(self, fishMap, wpId=0):
        pass

    def dealCatchBoss(self, fishMap, catchUserId):
        pass

    def sendBufferInfos(self, isBroadcast=True):
        """
        发送玩家的buff信息
        """
        msg = MsgPack()
        msg.setCmd("buffer_infos")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        bufferInfos = []
        for bufferInfo in self.usedBufferInfos:
            if bufferInfo.isStart():
                buffer_ = {}
                buffer_["bufferId"] = bufferInfo.getBufferId()
                buffer_["startTime"] = bufferInfo.startTime
                buffer_["leftTime"] = bufferInfo.startTime + bufferInfo.getTotalEffectTime() - int(time.time())
                buffer_["totalTime"] = bufferInfo.getTotalEffectTime()
                buffer_["state"] = bufferInfo.getBufferState()
                bufferInfos.append(buffer_)
        msg.setResult("bufferInfos", bufferInfos)
        if bufferInfos:
            uIds = [self.userId]
            if isBroadcast:
                uIds = self.table.getBroadcastUids()
            GameMsg.sendMsg(msg, uIds)

    def getSkillCDAddition(self, weaponId):
        """
        获取技能cd的加成
        :param weaponId: 武器ID
        """
        percent = 0
        for bufferInfo in self.usedBufferInfos:
            percent += bufferInfo.getSkillCDPercent(weaponId)
        if ftlog.is_debug():
            ftlog.debug("getSkillCDAddition", percent)
        return percent

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

    def bufferRemove(self, bufferId):
        """删除玩家的buffer"""
        for bufferInfo in self.usedBufferInfos:
            if bufferInfo.getBufferId() == bufferId:
                bufferInfo.endBuffer()
                self.usedBufferInfos.remove(bufferInfo)

    def addOneBufferId(self, bufferId):
        pass

    def getCatchBufferId(self, bufferIds):
        return 0

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

    def dealEnterTable(self):
        """处理进入桌子"""
        self.sendBufferInfos(isBroadcast=False)
        gun_system.sendGunInfoMsg(self.userId, self.table.gameMode)     # 发送普通炮信息
        self.taskSystemUser and self.taskSystemUser.dealEnterTable(self.offline)    # 渔场内任务管理系统
        self.activitySystem and self.activitySystem.enterRoom(self.offline)     # 活动系统
        self.mainQuestSystem and self.mainQuestSystem.dealEnterTable(self.offline)  # 主线任务系统

    def reportTableData(self):
        normalFishCount, bossFishCount, multipleFishCount, totalFishCount = 0, 0, 0, 0
        for fishType, count in self._catchFishes.iteritems():
            bireport.reportGameEvent("BI_NFISH_GE_CATCH", self.userId, FISH_GAMEID, self.table.roomId,
                                     self.table.tableId, int(fishType), count, 0, 0, [], self.clientId)
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            if fishConf["type"] == 1:
                normalFishCount += count
            elif fishConf["type"] in config.BOSS_FISH_TYPE:         # Boss鱼
                bossFishCount += count
            elif fishConf["type"] in config.MULTIPLE_FISH_TYPE:     # 倍率鱼
                multipleFishCount += count
            totalFishCount += count
        # 5.1大厅福袋任务
        fishes = {"totalFishCount": totalFishCount, "bossFishCount": bossFishCount}
        from newfish.entity.fishactivity import fish_activity_system
        fish_activity_system.countTableData(self.userId, multipleFishCount, bossFishCount,
                                            self.totalGainChip,
                                            self.table.bigRoomId, self._catchFishes)
        # util.sendToHall51GameOverEvent(self.userId, self.table.roomId, self.table.tableId, fishes)
        bireport.reportGameEvent("BI_NFISH_GAME_TIME", self.userId, FISH_GAMEID, self.table.roomId,
                                self.table.tableId, self.gameTime, 0, 0, 0, [], self.clientId, 0, self.allChip)
        self._catchFishes = {}
        self.totalGainChip = 0
        self.gameTime = 0

    def saveUserData(self):
        """保存用户数据"""
        gamedata.setGameAttrs(self.userId, FISH_GAMEID,
            [
                GameData.profitChest,                   # 玩家在各场次的金币宝箱奖池
                GameData.profitCoin,                    # 玩家在各场次的盈亏金币
                GameData.bankruptCount,                 # 玩家各场次累计破产次数
                GameData.realProfitCoin                 # 各场次真实盈亏
            ],
            [json.dumps(self.profitForChest), json.dumps(self.profitForCoin), json.dumps(self.bankruptCount),
            json.dumps(self.realProfitCoin)]
        )
        weakdata.incrDayFishData(self.userId, WeakData.enterFishPoolTimes, 1)                           # 每日进入渔场次数
        from newfish.game import TGFish
        event = NetIncomeChangeEvent(self.userId, FISH_GAMEID, self.netIncome, self.table.bigRoomId)    # 渔场净收益变化事件
        TGFish.getEventBus().publishEvent(event)

    def triggerCatchFishEvent(self, event):
        pass

    def triggerComboEvent(self, event):
        """触发连击奖励事件"""
        pass

    def triggerUseSkillEvent(self, event):
        pass

    def triggerUseSkillItemEvent(self, event):
        """触发使用技能道具事件"""
        pass

    def refreshHoldCoin(self):
        """刷新大厅金币"""
        if self.userId > 0:
            self.hallCoin = self.chip
            self.taskSystemUser and self.taskSystemUser.refreshHoldCoin(self.holdCoin)

    def getPearlDropRatio(self, fpMultiple):
        """获取珍珠掉落基数"""
        vipConf = config.getVipConf(self.vipLevel)
        ratio = None
        dropCount = vipConf.get("dropPearlTotalCount", 0) if vipConf else 0
        if 0 <= dropCount <= self.dropPearlCount:
            ratio = vipConf.get("dropPearlRatioLimit")
        if ratio is None:
            ratio = config.getUlevel(self.level).get(str(fpMultiple), 0)
            ratio += self.incrPearlDropRatio
        if ftlog.is_debug():
            ftlog.debug("getPearlDropRatio===>", "userId=", self.userId, "fpMultiple =", fpMultiple, "vip=", self.vipLevel,
                    "dropCount=", self.dropPearlCount, "dropLimit=", dropCount,
                    "ratio", ratio, "incrRato=", self.incrPearlDropRatio)
        return ratio

    def _addPearlDropCount(self, count):
        """增加珍珠掉落数量"""
        self.dropPearlCount += count
        if ftlog.is_debug():
            ftlog.debug("addPearlDropCount===>", self.userId, count, self.dropPearlCount)

    def reportBIFeatureData(self, eventId, wpId, changeCoin):
        """
        用户特征BI数据
        """
        if self.table.typeName in config.NORMAL_ROOM_TYPE and time.time() - self.registTime <= 24 * 3600:
            changeCoin = int(changeCoin)
            bireport.reportGameEvent(eventId, self.userId, FISH_GAMEID, self.table.roomId,
                                     self.table.tableId, self.level, changeCoin, int(wpId),
                                     0, [], self.clientId, 0, self.holdCoin)

    def sendRoomUnlockMsg(self, roomId):
        """
        发送解锁新渔场弹窗
        """
        roomConf = gdata.getRoomConfigure(roomId)
        msg = MsgPack()
        msg.setCmd("room_unlock")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("nextRoomId", roomId)
        # msg.setResult("nextRoomName", roomConf["name"])
        msg.setResult("nextRoomName", config.getMultiLangTextConf(roomConf["name"], lang=self.lang))
        GameMsg.sendMsg(msg, self.userId)

    def isFpMultipleMode(self):
        """
        是否为渔场倍率模式
        """
        if self.table.typeName not in config.NORMAL_ROOM_TYPE:
            return False
        return self.fpMultipleTestMode in ["b"]

    def clipToTableChip(self):
        """
        子弹兑换成桌内金币
        """
        _chip = self.clip * self.fpMultiple
        self.clip = 0
        self.economicData.chgTableChip(_chip)
        self.economicData.chgBulletChip(-_chip)

    def changeFpMultiple(self, fpMultiple, ignoreFailed=False):
        """改变渔场倍率"""
        if isinstance(fpMultiple, (int, str)):
            fpMultiple = int(fpMultiple)
            code = self.checkChgFpMultiple(fpMultiple)
        else:
            code = 1
        mo = MsgPack()
        mo.setCmd("chg_multiple")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("code", code)
        mo.setResult("fpMultiple", fpMultiple)
        if code == 0:
            GameMsg.sendMsg(mo, self.table.getBroadcastUids())
            # 中断combo 中断连击奖励
            if self.combo > 0 and self.comboTimer:
                self.comboTimer.cancel()
                if ftlog.is_debug():
                    ftlog.debug("changeFpMultiple, cease combo, userId =", self.userId, "combo =", self.combo)
                self._comboBudget()
            # 调整子弹数量.
            self.clipToTableChip()              # 子弹兑换成桌内金币
            self.fpMultiple = fpMultiple
            self.matchingFishPool = self.getMatchingFishPool(self.fpMultiple)
            self.table.clip_add(self.userId, self.seatId, auto=1)   # 弹药添加
            self.dynamicOdds.changeOdds()       # 切换动态概率曲线
            if self.prizeWheel:
                fishPool = self.table.runConfig.fishPool if self.table.runConfig.fishPool not in [44601, 44501] else 44501
                self.prizeWheel.sendEnergyProgress(fishPool, self.fpMultiple, self.table.roomId, 0)
        elif not ignoreFailed:
            GameMsg.sendMsg(mo, self.userId)

    def checkChgFpMultiple(self, multiple):
        """
        切换玩家渔场倍率
        """
        multiple = int(multiple)
        lv = config.getGunMultipleConf().get(str(multiple))
        code = 1
        if self.table.typeName not in config.NORMAL_ROOM_TYPE:
            code = 2
        elif not self.isFpMultipleMode():
            code = 3
        # 有技能在选中或使用时不可以切换倍率.
        elif len(self.usingSkill) > 0:
            code = 4
        elif self.fpMultiple == multiple:
            code = 5
        elif multiple < self.table.runConfig.minMultiple or multiple > self.table.runConfig.maxMultiple:
            code = 6
        # 判断倍率是否已解锁.
        elif lv and lv <= self.gunLevel:
            code = 0
        if ftlog.is_debug():
            ftlog.debug("checkChgFpMultiple, userId =", self.userId, code, multiple, self.fpMultiple, type(multiple), type(self.fpMultiple), lv, self.gunLevel)
        return code

    def getMatchingFishPool(self, fpMultiple):
        """
        获取玩家渔场倍率对应的fishPool
        """
        fishPool = self.table.runConfig.fishPool
        if self.table.typeName not in config.NORMAL_ROOM_TYPE or not self.isFpMultipleMode():
            return 44005
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
            ftlog.debug("getFishPool, userId =", self.userId, "fishPool-multiple =", tmpList, "fpMultiple =", fpMultiple,
                    "tableFishPool =", self.table.runConfig.fishPool, "matchingFishPool =", fishPool)
        return 44005

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
                    if skillId in usingSkill:
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

    def addGrandPrixFishPoint(self, fishPoint, fishType, gunLevel):
        return 0

    def sendGrandPrixCatch(self, catchFishPoints):
        pass

    def isGrandPrixMode(self):
        """
        大奖赛比赛模式
        """
        return False

    def getMatchingFpMultiple(self, fp):
        """
        获取玩家渔场倍率对应的基础倍率
        """
        return self.table.runConfig.multiple

    def gunEffectState(self, _type=1, *args):
        """千炮场狂暴效果"""
        pass
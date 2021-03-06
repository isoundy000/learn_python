#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import json
import time
import traceback

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.util import strutil
from poker.entity.biz import bireport
import poker.util.timestamp as pktimestamp
from poker.entity.dao import userchip, userdata, gamedata
from hall.entity import hallvip, hallitem
from hall.servers.util.item_handler import ItemHelper
from newfish.entity import util, weakdata, user_system
from newfish.entity.lotterypool import robbery_lottery_pool
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, WeakData
from newfish.player.player_base import FishPlayer
from newfish.entity.event import GameTimeEvent, BulletChangeEvent, RobberyBulletChangeEvent
from newfish.entity.msg import GameMsg
from newfish.entity.honor import honor_system
from newfish.entity.ranking import ranking_system
from newfish.table.economic_data import EconomicData
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity.fishactivity.activity_table_system import ActivityTableSystem


class GameState:
    GAME_START = 0
    GAME_END = 1


class FishRobberyPlayer(FishPlayer):

    def __init__(self, table, seatIndex, clientId=None):
        self.trialMode = table.runConfig.trialMode                              # 试玩模式
        super(FishRobberyPlayer, self).__init__(table, seatIndex, clientId)

    def _onInit(self):
        self._loadUserData()
        self._loadRobberyData()
        self.lastActionTime = int(time.time())
        self.lastCatchTime = int(time.time())
        self._fires = {}
        self._catchFishes = {}
        self.clip = 0
        self.invalidCatch = 0
        self.enterTime = 0
        self.offline = 0
        self.gameTime = 0
        self.gunId = 0
        self.gunLv = 1
        self.state = GameState.GAME_START
        self.gameTimeTimer = FTLoopTimer(60, -1, self._incrGameTimer)
        self.gameTimeTimer.start()
        self.playTimeTimer = FTLoopTimer(self.table.runConfig.playTime, 0, self._playTimeUp)
        self.playTimeTimer.start()

    def clear(self):
        """清理数据"""
        try:
            self.clearTimer()
            self.dumpGameData()
            self.clearData()
            self.endTrialMode()
        except Exception, e:
            ftlog.error(self.userId, traceback.format_exc())

    def clearTimer(self):
        """清理定时器"""
        self.gameTimeTimer.cancel()
        self.playTimeTimer.cancel()

    def dumpGameData(self):
        """序列化保存数据"""
        if self.trialMode:
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.robberyTrialGunLevel, json.dumps(self.gunsLevel))   # 招财试玩模式火炮等级
        else:
            gamedata.setGameAttr(self.userId, FISH_GAMEID, GameData.robberyGunLevel, json.dumps(self.gunsLevel))
            bulletProfitCoin = robbery_lottery_pool.getBulletCoin(self.bulletProfit)
            weakdata.incrDayRobberyData(self.userId, WeakData.bulletProfitCoin, bulletProfitCoin)   # 每日招财模式盈亏金币数
            weakdata.incrMonthFishData(self.userId, WeakData.bulletProfitCoin, bulletProfitCoin)    # 每月招财模式盈亏金币数

    def clearData(self):
        """清理数据"""
        user_system.updateLoginData(self.userId)
        self.reportTableData()
        self.activitySystem and self.activitySystem.leaveRoom()                 # 活动系统
        self.activitySystem = None

    @property
    def allChip(self):
        return self.chip + self.tableChip + self.bulletChip

    @property
    def chip(self):
        return userchip.getChip(self.userId)

    @property
    def tableChip(self):
        return self.economicData.tableChip

    @property
    def bulletChip(self):
        return self.economicData.bulletChip

    def sendCountdown(self):
        """
        发送timer的剩余时间
        """
        msg = MsgPack()
        msg.setCmd("robbery_countdown")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", self.userId)
        msg.setResult("seatId", self.seatId)
        msg.setResult("state", self.state)
        msg.setResult("timeLeft", self.playTimeTimer.getTimeOut())
        GameMsg.sendMsg(msg, self.userId)

    def _incrGameTimer(self):
        if self.userId <= 0:
            return
        self.gameTime += 1
        self.activitySystem and self.activitySystem.incrGameTime()
        from newfish.game import TGFish
        event = GameTimeEvent(self.userId, FISH_GAMEID, self.table.roomId, self.table.tableId, self.table.runConfig.fishPool, 1, self.fpMultiple)
        TGFish.getEventBus().publishEvent(event)

    def _playTimeUp(self):
        """
        游戏时间结束
        """
        if self.userId <= 0:
            return
        self.state = GameState.GAME_END
        self.playTimeTimer = FTLoopTimer(30, 0, self.table.clearPlayer, self)
        self.playTimeTimer.start()
        self.sendCountdown()

    def _loadUserData(self):
        """
        加载玩家数据
        """
        self.economicData = EconomicData(self, self.table)
        self.name = util.getNickname(self.userId)
        self.charm, self.sex, self.purl = userdata.getAttrs(self.userId, ["charm", "sex", "purl"])
        self.level, self.gunLevel, self.exp, self.gameResolution = gamedata.getGameAttrs(
            self.userId, FISH_GAMEID, [GameData.level, GameData.gunLevel, GameData.exp, GameData.gameResolution])
        self.gameResolution = strutil.loads(self.gameResolution, False, True, [])
        self.bullets = {}
        self.usableBullets = self.table.runConfig.usableBullets
        if self.trialMode:
            self.beginTrialMode()
        for kindId in self.usableBullets:
            self.bullets[int(kindId)] = self.getBulletNum(kindId)
        kindId = sorted(self.bullets.iteritems(), key=lambda d: d[1])[-1][0]
        if self.bullets[kindId] == 0:
            kindId = self.table.runConfig.usableBullets[0]

        if self.trialMode:                                              # 试玩模式
            self.gunsLevel = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.robberyTrialGunLevel, {})
        else:
            self.gunsLevel = gamedata.getGameAttrJson(self.userId, FISH_GAMEID, GameData.robberyGunLevel, {})
        self.setSkillId(kindId)

        self.refreshVipLevel()
        self.refreshHonor()
        self.activitySystem = ActivityTableSystem(self.table, self)     # 活动系统

    def _loadRobberyData(self):
        """
        加载奖池相关数据
        """
        # 本次招财珠盈亏数据
        self.bulletProfit = [0, 0, 0]
        # 本次招财珠正向盈亏数据
        self.positiveBulletProfit = [0, 0, 0]
        # 本次累计获得招财珠数量
        self.bulletWin = 0
        # 上一次赢得招财珠峰值数据
        self.bulletWinMost = robbery_lottery_pool.getRobberyWinMostData(self.userId, trialMode=self.trialMode)
        # 上一次赢得招财珠峰值对应金币价值
        self.bulletWinMostCoin = 0 if self.trialMode else robbery_lottery_pool.getBulletCoin(self.bulletWinMost)
        # 上一次排名
        self.rank = 0
        if self.trialMode:
            return
        self.rank, _ = ranking_system.getUserRankAndRewards(ranking_system.RankType.TodayWinner, self.userId)

    def getBulletNum(self, kindId):
        """
        获取子弹数量
        """
        userAssets = hallitem.itemSystem.loadUserAssets(self.userId)
        surplusCount = userAssets.balance(FISH_GAMEID, "item:" + str(kindId), pktimestamp.getCurrentTimestamp())
        return surplusCount

    def setSkillId(self, skillId):
        """
        设置默认子弹，获取火炮等级
        """
        self.skillId = skillId
        nowGunLevel = self.gunsLevel.setdefault(str(self.skillId), self.table.runConfig.minGunLevel)
        maxGunLevel = self.table.runConfig.maxGunLevelLimit.get(str(skillId), self.table.runConfig.maxGunLevel)
        self.nowGunLevel = min(nowGunLevel, maxGunLevel)

    def setNowGunLevel(self, gunLevel):
        """设置炮的等级"""
        self.gunsLevel[str(self.skillId)] = gunLevel
        self.nowGunLevel = gunLevel
        maxGunLevel = self.table.runConfig.maxGunLevelLimit.get(str(self.skillId), self.table.runConfig.maxGunLevel)
        self.nowGunLevel = min(self.nowGunLevel, maxGunLevel)
        self.nowGunLevel = max(self.nowGunLevel, self.table.runConfig.minGunLevel)

    def refreshVipLevel(self):
        """刷新vip等级"""
        vipInfo = hallvip.userVipSystem.getVipInfo(self.userId)
        self.vipLevel = vipInfo.get("level", 0)

    def refreshHonor(self):
        """刷新勋章"""
        self.ownedHonors = honor_system.getOwnedHonors(self.userId)
        honorId, _ = honor_system.getInstalledHonor(self.userId, self.ownedHonors)
        self.honorId = honorId if honorId >= 0 else 0

    def incrExp(self, gainExp):
        return self.exp

    def catchBudgetRobbery(self, wpId, kindId, gainBullet, reason):
        """
        捕获结算
        """
        if reason == 0:
            costBullet = self.table.getCostBulletRobbery(wpId)
            count = gainBullet - costBullet
            if count > 0:
                eventId = "BI_NFISH_CATCH_GAIN"
            else:
                eventId = "BI_NFISH_GUN_FIRE"
            util.addItems(self.userId,
                          [{"name": kindId, "count": count}],
                          eventId,
                          wpId,
                          roomId=self.table.roomId,
                          tableId=self.table.tableId,
                          clientId=self.clientId,
                          param01=self.level)
            self.countRobberyProfit(kindId, count, costBullet)
        mo = ItemHelper.makeItemListResponseByGame(FISH_GAMEID, self.userId)
        GameMsg.sendMsg(mo, self.userId)

    def countRobberyProfit(self, kindId, count, costBullet):
        """
        计算个人盈亏数据
        """
        if self.trialMode:
            index = robbery_lottery_pool.TM_KINDIDS.index(kindId)
        else:
            index = robbery_lottery_pool.KINDIDS.index(kindId)
        self.bulletProfit[index] += count
        self.bulletWin += max(0, count)
        if self.trialMode:
            return
        from newfish.game import TGFish
        event = RobberyBulletChangeEvent(self.userId, FISH_GAMEID, kindId, count, costBullet)
        TGFish.getEventBus().publishEvent(event)

    def reportTableData(self):
        """上报桌子数据"""
        from newfish.game import TGFish
        event = BulletChangeEvent(self.userId, FISH_GAMEID)
        TGFish.getEventBus().publishEvent(event)
        totalFishCount = 0
        for fishType, count in self._catchFishes.iteritems():
            bireport.reportGameEvent("BI_NFISH_GE_CATCH", self.userId, FISH_GAMEID, self.table.roomId,
                                     self.table.tableId, int(fishType), count, 0, 0, [], self.clientId)
            totalFishCount += count
        if totalFishCount > 0:
            fish_activity_system.countRobberyTableData(self.userId, totalFishCount, self.table.bigRoomId)
        self._catchFishes = {}
        self.gameTime = 0
        fish_activity_system.countRobberyData(self.userId, self.table.bigRoomId, self.bulletWin, self.bulletProfit)
        if self.trialMode:
            return
        bulletProfitCoin = robbery_lottery_pool.getBulletCoin(self.bulletProfit)
        self.positiveBulletProfit = map(lambda num: max(0, num), self.bulletProfit)
        if bulletProfitCoin > self.bulletWinMostCoin:
            robbery_lottery_pool.updateDayWinMostRank(self.userId, self.positiveBulletProfit)
            robbery_lottery_pool.updateWeekWinMostRank(self.userId, self.positiveBulletProfit)

    def beginTrialMode(self):
        """
        初始试玩数量
        """
        for kindId, count in self.table.bulletInitCount.iteritems():
            _count = util.balanceItem(self.userId, kindId)
            if _count > count:
                util.consumeItems(self.userId, [{"name": kindId, "count": _count - count}], "ITEM_USE")
            elif _count < count:
                util.addItems(self.userId, [{"name": kindId, "count": count - _count}], "ITEM_USE", changeNotify=True)

    def endTrialMode(self):
        """
        清理试玩数据
        """
        for kindId, count in self.table.bulletInitCount.iteritems():
            _count = util.balanceItem(self.userId, kindId)
            if _count > 0:
                util.consumeItems(self.userId, [{"name": kindId, "count": _count}], "ITEM_USE")

    def refreshGunSkin(self):
        pass
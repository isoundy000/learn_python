#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/29
"""
大奖赛玩家逻辑
"""

import time
import json
import random
import copy
from collections import OrderedDict
from datetime import date, timedelta

from freetime.util import log as ftlog
from poker.entity.configure import gdata
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from poker.entity.biz import bireport
from poker.entity.dao import userchip, userdata, gamedata, daobase
from newfish.entity import change_notify, config, util, weakdata, mail_system, grand_prix
from newfish.player.friend_player import FishFriendPlayer
from newfish.entity.redis_keys import GameData, WeakData
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity.ranking import ranking_system
from newfish.entity.ranking.ranking_base import RankType
from newfish.entity.skill import skill_system
from newfish.entity.fishactivity import fish_activity_system
from newfish.entity import config, module_tip
from newfish.entity.fishactivity.fish_activity import TaskType
from newfish.entity.skill import skill_release
import poker.util.timestamp as pktimestamp
from newfish.entity import weakdata
from newfish.entity.redis_keys import WeakData
from poker.entity.dao import userdata
from newfish.entity.ranking.ranking_base import RankingBase
from newfish.entity.ranking.ranking_base import RankType, RankDefineIndex
from newfish.entity.grand_prix_prize_wheel import GrandPrixPrizeWheel
from newfish.entity.event import JoinGrandPrixEvent, FinishGrandPrixEvent
from newfish.game import TGFish


class SignupCode:           # 注册
    """
    报名状态码
    """
    SC_SUCC = 0             # 报名成功
    SC_FEE_NOT_ENOUGH = 1   # 报名费补足
    SC_NOT_OPEN = 2         # 比赛未开放
    SC_UNFINISH = 3         # 存在未完成的比赛



class FishGrandPrixPlayer(FishFriendPlayer):

    def __init__(self, table, seatIndex, clientId):
        super(FishGrandPrixPlayer, self).__init__(table, seatIndex, clientId)
        # 捕鱼积分
        self.grandPrixFishPoint = weakdata.getDayFishData(self.userId, WeakData.grandPrix_fishPoint, 0)
        # 大奖赛剩余开火次数
        self.grandPrixFireCount = weakdata.getDayFishData(self.userId, WeakData.grandPrix_fireCount, 0)
        # 大奖赛剩余技能使用次数
        self.grandPrixUseSkillTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_useSkillTimes, [])
        # 大奖赛目标鱼捕获数量
        self.grandPrixTargetFish = weakdata.getDayFishData(self.userId, WeakData.grandPrix_targetFish, {})
        # 大奖赛火炮等级和倍率
        self.grandPrixLevelFpMultiple = weakdata.getDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple)
        # 大奖赛开始的时间戳
        self.grandPrixStartTS = weakdata.getDayFishData(self.userId, WeakData.grandPrix_startTS, 0)
        # 大奖赛结束定时器
        self.grandPrixEndTimer = None

        self.grandPrixTipTimer = None
        # 大奖赛免费游戏次数
        self._freeTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_freeTimes, 0)
        self._paidTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_paidTimes, 0)

        self.levelAddition = config.getGunLevelConf(self.nowGunLevel, self.table.gameMode).get("levelAddition", 0.)

        self.fpMultipleTestMode = "b"

        self.multipleList = []                      # 10、50、200、500
        for v in gdata.roomIdDefineMap().values():
            roomConf = v.configure
            if roomConf.get("typeName") not in [config.FISH_FRIEND]:
                continue
            self.multipleList.append(roomConf.get("multiple", 1))
        self.multipleList.sort()

        self._rankListCache = []
        self._surpassUser = {}
        self.grandPrixSurpassCount = weakdata.getDayFishData(self.userId, WeakData.grandPrix_surpassCount, 0)
        self.bestPoint = weakdata.getDayFishData(self.userId, WeakData.grandPrix_point, 0)

        self.prizeWheel = GrandPrixPrizeWheel(self.userId, table.runConfig.fishPool, self.table.roomId)
        # 游戏时长（分钟）
        self.inGameTimes = 0

    def _incrGameTimer(self):
        if self.userId <= 0:
            return
        super(FishGrandPrixPlayer, self)._incrGameTimer()
        self.inGameTimes += 1
        if self.prizeWheel is None:
            return
        # 大奖赛转盘充能.
        for fpMultiple, coin in self.grandPrixProfitCoin.iteritems():
            if self.prizeWheel.lossCoin(self.fpMultiple, coin):
                self.grandPrixProfitCoin[str(fpMultiple)] = 0

    def checkChgFpMultiple(self, multiple):
        """
        切换玩家渔场倍率
        """
        # 大奖赛模式不可以切换倍率.
        if self.isGrandPrixMode():
            code = 7
        else:
            code = super(FishGrandPrixPlayer, self).checkChgFpMultiple(multiple)
        if ftlog.is_debug():
            ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "multiple =", multiple, "code =", code)
        return code
        # return super(FishGrandPrixPlayer, self).checkChgFpMultiple(multiple)

    def _checkSkillCondition(self, skillId, select, skillType):
        """
        检测技能使用条件
        """
        # 大奖赛模式限制技能槽的使用次数
        if self.isFpMultipleMode() and select:
            for idx, val in enumerate(self.grandPrixUseSkillTimes):
                if val.get("skillId") == skillId and val.get("skillType", 0) == skillType:
                    if ftlog.is_debug():
                        ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "skillId =", skillId,
                                    "skillType =", skillType, "useSkillTimes =", self.grandPrixUseSkillTimes)
                    if val.get("count") <= 0:
                        return 7
                    break
        return super(FishGrandPrixPlayer, self)._checkSkillCondition(skillId, select, skillType)

    def useSkill(self, skillId, select, skillType):
        """
        使用技能
        """
        reason = super(FishFriendPlayer, self).useSkill(skillId, select, skillType)
        if ftlog.is_debug():
            ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "skillId =", skillId, "select =", select,
                        "reason =", reason, "skillType =", skillType,
                        "skills =", self.skills.keys(), "auxiliarySkills =", self.auxiliarySkills.keys(),
                        "useSkillTimes =", self.grandPrixUseSkillTimes)

    def addFire(self, bulletId, wpId, sendTimestamp, fpMultiple, skill=None, power=None, multiple=None, clientFire=True,
                targetPos=None, fishType=None, costChip=0):
        """大奖赛开火"""
        super(FishFriendPlayer, self).addFire(bulletId, wpId, sendTimestamp, fpMultiple, skill, power, multiple,
                                              clientFire, targetPos, fishType, costChip)
        if self.prizeWheel and costChip:
            self.prizeWheel.fireCoin(self.fpMultiple, costChip)
        if clientFire and skill is None and self.isGrandPrixMode():
            self.grandPrixFireCount -= 1
            if self.grandPrixFireCount == 0 and self.grandPrixEndTimer:
                to = self.grandPrixEndTimer.getTimeOut()
                if to > 3:
                    self.grandPrixEndTimer.cancel()
                    self.grandPrixEndTimer = None
                    self.grandPrixEndTimer = FTLoopTimer(3, 0, self.endGrandPrix)
                    self.grandPrixEndTimer.start()
                ftlog.debug("FishGrandPrixPlayer, userId =", self.userId,
                            "fireCount =", self.grandPrixFireCount, "timeout =", to)

    def triggerUseSkillEvent(self, event):
        """大奖赛使用技能事件"""
        super(FishFriendPlayer, self).triggerUseSkillEvent(event)
        costChip = event.chip
        fpMultiple = event.fpMultiple
        if self.prizeWheel:
            self.prizeWheel.fireCoin(fpMultiple, costChip)

    def loadAllSkillData(self):
        """
        读取并初始化所有技能数据
        """
        super(FishGrandPrixPlayer, self).loadAllSkillData()

        self.auxiliarySkills = {}
        self._refreshSkillSlots(1)
        for skillId in self.auxiliarySkillSlots:
            self._loadSkillData(skillId, 1)

    def _refreshFpMultiple(self):
        """
        刷新使用的渔场倍率
        """
        levelFpMultiple = weakdata.getDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple)
        if levelFpMultiple:
            _, self.fpMultiple = levelFpMultiple
        else:
            self.fpMultiple = config.getGunLevelConf(self.gunLevel, self.table.gameMode).get("unlockMultiple", 1)
        self.fpMultiple = max(self.table.runConfig.minMultiple, min(self.fpMultiple, self.table.runConfig.maxMultiple))

    def _refreshGunLevel(self):
        """
        刷新火炮等级数据
        """
        levelFpMultiple = weakdata.getDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple)
        if levelFpMultiple:
            self.nowGunLevel, _ = levelFpMultiple
        else:
            self.nowGunLevel = self.gunLevel
        self.nowGunLevel = max(self.table.runConfig.minGunLevel, min(self.nowGunLevel, self.table.runConfig.maxGunLevel))

    def _refreshSkillSlots(self, skillType):
        """
        刷新技能数据
        """
        if skillType == 0:
            self.skillSlots = {}
        else:
            self.auxiliarySkillSlots = {}
        if self.grandPrixUseSkillTimes:
            for val in self.grandPrixUseSkillTimes:                 # 大奖赛剩余技能使用次数
                if isinstance(val, dict) and val.get("skillId"):
                    if val.get("skillType", 0) == skillType:
                        if skillType == 0:
                            self.skillSlots[val["skillId"]] = [val["state"], val["star"], val["grade"]]
                        else:
                            self.auxiliarySkillSlots[val["skillId"]] = [val["star"], val["grade"]]
            ftlog.info("_refreshSkillSlots, 2 =", self.userId, skillType, self.skillSlots, self.auxiliarySkillSlots)
        else:
            super(FishGrandPrixPlayer, self)._refreshSkillSlots(skillType)
            ftlog.info("_refreshSkillSlots =", self.userId, skillType, self.skillSlots, self.auxiliarySkillSlots)

    def clearTimer(self):
        super(FishGrandPrixPlayer, self).clearTimer()
        if self.grandPrixEndTimer:
            self.grandPrixEndTimer.cancel()
            self.grandPrixEndTimer = None
        if self.grandPrixTipTimer:
            self.grandPrixTipTimer.cancel()
            self.grandPrixTipTimer = None
        if self.inGameTimes:
            bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0,
                                     self.grandPrixStartTS, self.inGameTimes, 0, 0, [], util.getClientId(self.userId))
        if ftlog.is_debug():
            ftlog.debug("clearTimer, userId =", self.userId, self.grandPrixStartTS, self.inGameTimes)

    def gunChange(self, gLv):
        """炮改变等级 切换火炮等级"""
        if self.isGrandPrixMode():
            return
        super(FishGrandPrixPlayer, self).gunChange(gLv)
        self.levelAddition = config.getGunLevelConf(self.nowGunLevel, self.table.gameMode).get("levelAddition", 0.)





    def startGrandPrix(self, signUp):
        """
        大奖赛开始
        """
        # if not grand_prix.isGrandPrixOpenTime():
        #     self._resetGrandPrixData()
        #     self._freeTimes = self._paidTimes = 0
        #     weakdata.setDayFishData(self.userId, WeakData.grandPrix_freeTimes, 0)
        #     weakdata.setDayFishData(self.userId, WeakData.grandPrix_paidTimes, 0)
        curTime = int(time.time())
        dayStartTimestamp = util.getDayStartTimestamp(curTime)



    def endGrandPrix(self):
        """
        大奖赛结束
        """
        pass

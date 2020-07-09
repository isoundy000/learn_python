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
from newfish.player.multiple_player import FishMultiplePlayer
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


class FishGrandPrixPlayer(FishMultiplePlayer):

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
        # 大奖赛提示定时器
        self.grandPrixTipTimer = None
        # 大奖赛阶段奖励
        self.grandPrixGetPointsInfo = weakdata.getDayFishData(self.userId, WeakData.grandPrix_getPointsInfo, 0)
        # 大奖赛今日最高积分
        self.grandPrixTodayMaxPoints = weakdata.getDayFishData(self.userId, WeakData.grandPrix_todayMaxPoints, 0)
        self._freeTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_freeTimes, 0)
        self.levelAddition = config.getGunLevelConf(self.nowGunLevel, self.table.gameMode).get("levelAddition", 0.)  # 大奖赛火炮等级加成

        self.fpMultipleTestMode = "b"
        self.multipleList = []                      # 10、50、200、500
        for v in gdata.roomIdDefineMap().values():
            roomConf = v.configure
            if roomConf.get("typeName") not in [config.FISH_FRIEND]:
                continue
            self.multipleList.append(roomConf.get("multiple", 1))
        self.multipleList.sort()

        self._rankListCache = []                    # 超越玩家的集合
        self._surpassUser = {}
        self.grandPrixSurpassCount = weakdata.getDayFishData(self.userId, WeakData.grandPrix_surpassCount, 0)   # 大奖赛超越自己次数
        self.bestPoint = weakdata.getDayFishData(self.userId, WeakData.grandPrix_point, 0)

        # 游戏时长（分钟）
        self.inGameTimes = 0

    def _incrGameTimer(self):
        """增加游戏时长"""
        if self.userId <= 0:
            return
        super(FishGrandPrixPlayer, self)._incrGameTimer()
        self.inGameTimes += 1

    def checkChgFpMultiple(self, multiple):
        """
        切换玩家渔场倍率
        """
        # 大奖赛模式不可以切换倍率.
        if self.isGrandPrixMode():
            code = 7
        else:
            code = super(FishGrandPrixPlayer, self).checkChgFpMultiple(multiple)
        return code

    def _checkSkillCondition(self, skillId, select, skillType):
        """
        检测技能使用条件
        """
        # 大奖赛模式限制技能槽的使用次数
        if self.isGrandPrixMode() and select:
            for idx, val in enumerate(self.grandPrixUseSkillTimes):
                if val.get("skillId") == skillId and val.get("skillType", 0) == skillType:
                    if val.get("count") <= 0:
                        return 7
                    break
        return super(FishGrandPrixPlayer, self)._checkSkillCondition(skillId, select, skillType)

    def useSkill(self, skillId, select, skillType):
        """
        使用技能
        """
        super(FishGrandPrixPlayer, self).useSkill(skillId, select, skillType)

    def addFire(self, bulletId, wpId, sendTimestamp, fpMultiple, skill=None, power=None, multiple=None, clientFire=True,
                targetPos=None, fishType=None, costChip=0):
        """添加开火信息"""
        super(FishGrandPrixPlayer, self).addFire(bulletId, wpId, sendTimestamp, fpMultiple, skill, power, multiple,
                                              clientFire, targetPos, fishType, costChip)
        if clientFire and skill is None and self.isGrandPrixMode():
            self.grandPrixFireCount -= 1                                                # 开火次数减少
            if self.grandPrixFireCount == 0 and self.grandPrixEndTimer:                 # 结束的定时器
                to = self.grandPrixEndTimer.getTimeOut()
                if to > 3:
                    self.grandPrixEndTimer.cancel()
                    self.grandPrixEndTimer = None
                    self.grandPrixEndTimer = FTLoopTimer(3, 0, self.endGrandPrix)
                    self.grandPrixEndTimer.start()

    def triggerUseSkillEvent(self, event):
        """大奖赛使用技能事件"""
        super(FishGrandPrixPlayer, self).triggerUseSkillEvent(event)

    def loadAllSkillData(self):
        """
        读取并初始化所有技能数据
        """
        # 处于选中或使用中的技能
        super(FishGrandPrixPlayer, self).loadAllSkillData()

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

    def clearTimer(self):
        """清理提示和结束的定时器"""
        super(FishGrandPrixPlayer, self).clearTimer()
        if self.grandPrixEndTimer:
            self.grandPrixEndTimer.cancel()
            self.grandPrixEndTimer = None
        if self.grandPrixTipTimer:
            self.grandPrixTipTimer.cancel()
            self.grandPrixTipTimer = None
        if self.inGameTimes:
            bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0, self.grandPrixStartTS, self.inGameTimes, 0, 0, [], util.getClientId(self.userId))

    def gunChange(self, gLv):
        """炮改变等级 切换火炮等级 大奖赛等级加成"""
        # if self.isGrandPrixMode():                        # 可以改变火炮的等级
        #     return
        super(FishGrandPrixPlayer, self).gunChange(gLv)
        self.levelAddition = config.getGunLevelConf(self.nowGunLevel, self.table.gameMode).get("levelAddition", 0.)

    def checkCanFire(self, fPos, wpId, bulletId, skillId, skillType):
        """
        检测玩家是否可以开火
        """
        canFire, reason, clip, costBullet, extends, skill = \
            super(FishGrandPrixPlayer, self).checkCanFire(fPos, wpId, bulletId, skillId, skillType)
        if canFire and self.isGrandPrixMode() and self.grandPrixFireCount <= 0:
            canFire, reason = False, 8
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
        clip = params.get("clip")
        skillType = params.get("skillType", 0)
        lockFId = params.get("lockFId", 0)
        fPosx, fPosy = fPos
        retMsg = MsgPack()
        retMsg.setCmd("fire")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("wpId", wpId)
        retMsg.setResult("bulletId", bulletId)
        retMsg.setResult("skillId", skillId)
        retMsg.setResult("skillType", skillType)
        retMsg.setResult("extends", extends)
        retMsg.setResult("timestamp", timestamp)
        retMsg.setResult("reason", reason)
        retMsg.setResult("grandPrixFireCount", self.grandPrixFireCount)     # 大奖赛剩余开火次数
        retMsg.setResult("clip", clip)
        retMsg.setResult("lockFId", lockFId)
        superBullet = self.getFire(bulletId).get("superBullet", {})         # self.isSuperBullet(bulletId)
        retMsg.setResult("superBullet", 1 if superBullet else 0)            # 测试代码
        GameMsg.sendMsg(retMsg, userId)
        if canFire:
            retMsg.setResult("fPosx", fPosx)
            retMsg.setResult("fPosy", fPosy)
            retMsg.setResult("seatId", seatId)
            GameMsg.sendMsg(retMsg, self.table.getBroadcastUids(userId))

    def getMatchingFishPool(self, fpMultiple):
        """
        获取玩家渔场倍率对应的fishPool
        """
        return self.table.runConfig.fishPool

    def saveUserData(self):
        """保存用户数据"""
        super(FishGrandPrixPlayer, self).saveUserData()
        self.saveGrandPrixPoint()                               # 保存大奖赛积分

    def getTargetFishs(self):
        """
        返回目标鱼（魔术炮技能召唤使用）
        """
        fishes = super(FishGrandPrixPlayer, self).getTargetFishs()
        targetFish = [int(ft) for ft, val in self.grandPrixTargetFish.iteritems() if val[0] < val[1]]   # 0 < 5目标鱼数量
        if targetFish:
            fishes.extend(targetFish)
        return fishes

    def getMatchingFpMultiple(self, fpMultiple):
        """
        获取玩家渔场倍率对应的基础倍率
        """
        multiple = self.table.runConfig.multiple
        for mul in self.multipleList:
            if fpMultiple >= mul:
                multiple = mul
        ftlog.debug("getFishPool, userId =", self.userId, "multipleList =", self.multipleList, "fpMultiple =", fpMultiple,
                    "tableFishPool =", self.table.runConfig.fishPool, "multiple =", multiple)
        return multiple

    def isGrandPrixMode(self):
        """
        大奖赛比赛模式
        """
        return self.grandPrixStartTS > 0

    def _calcuCatchFishGrandPrixPoint(self, fishPoint):
        """
        计算捕鱼积分 去掉vip和挑战次数加成
        """
        vipAddition = config.getVipConf(self.vipLevel).get("grandPrixAddition", 0.)
        vipAdditionPoint = int(fishPoint * vipAddition + 0.5)
        levelAdditionPoint = int(fishPoint * self.levelAddition + 0.5)
        points = int(fishPoint + vipAdditionPoint + levelAdditionPoint)
        return points

    def saveGrandPrixPoint(self):
        """
        保存大奖赛积分
        """
        if not self.isGrandPrixMode():
            return 0, 0
        # 计算捕鱼积分
        grandPrixPoint = 0
        grandPrixFinalPoint = 0
        # 计算积分加成
        grandPrixPoint += self.grandPrixFishPoint
        if grandPrixPoint:
            grandPrixFinalPoint = self._calcuCatchFishGrandPrixPoint(grandPrixPoint)
        # 计入排行榜
        if grandPrixFinalPoint:
            ranking_system.refreshGrandPrixPoint(self.userId, grandPrixFinalPoint)
        # 保存大奖赛数据
        self._saveGrandPrixData()
        return grandPrixPoint, grandPrixFinalPoint                                          # 大奖赛积分 最后加成之后的积分

    def cancelUsingSkills(self):
        """
        取消处于使用中的技能
        """
        if self.usingSkill:                                                             # 有之前技能记录
            lastSkillId = self.usingSkill[-1].get("skillId")
            lastSkillType = self.usingSkill[-1].get("skillType", 0)
            lastSkill = self.getSkill(lastSkillId, lastSkillType)
            if lastSkill:
                if lastSkill.state == 1:
                    lastSkill.use(0)
                else:
                    self.removeUsingSkill(lastSkillId, lastSkillType)
                    orgState = lastSkill.state
                    lastSkill.state = 0
                    self.table.broadcastSkillUse(lastSkill, 0, self.userId, orgState)   # 广播选中/取消技能消息
                self.table.broadcastGunChange(self)                                     # 广播玩家现在的火炮等级

    def unloadSkills(self):
        """
        下载所有技能
        """
        for _skillId in self.skills.keys():
            _skill = self.getSkill(_skillId, 0)
            if not _skill:
                continue
            _skill.clear()
            del _skill

    def startGrandPrix(self, signUp):
        """
        大奖赛开始 1/0 报名大奖赛/直接进入渔场
        """
        curTime = int(time.time())
        dayStartTimestamp = util.getDayStartTimestamp(curTime)
        remainGrandPrixTimeSeconds = util.timeStrToInt(config.getGrandPrixConf("openTimeRange")[1]) - (curTime - dayStartTimestamp)     # 大奖赛剩余时间
        if signUp == 1:
            # 当局第一次进入大奖赛
            if self.grandPrixStartTS == 0:
                event = JoinGrandPrixEvent(self.userId, FISH_GAMEID, self.table.bigRoomId)              # 参加大奖赛事件
                TGFish.getEventBus().publishEvent(event)
                # 距离大奖赛结束不足10秒不可参赛
                if not grand_prix.isGrandPrixOpenTime() or remainGrandPrixTimeSeconds < 10:
                    code = SignupCode.SC_NOT_OPEN
                elif config.getVipConf(self.vipLevel).get("grandPrixFreeTimes", 0) > self._freeTimes:   # 用免费次数报名
                    self._freeTimes = weakdata.incrDayFishData(self.userId, WeakData.grandPrix_freeTimes, 1)
                    code = SignupCode.SC_SUCC
                else:
                    # 扣除报名费
                    fee = config.getGrandPrixConf("fee")[0]
                    _consume = [{"name": fee.get("name"), "count": fee.get("count")}]
                    _ret = util.consumeItems(self.userId, _consume, "ITEM_USE", self.table.roomId)
                    if _ret:
                        code = SignupCode.SC_SUCC
                    else:
                        code = SignupCode.SC_FEE_NOT_ENOUGH
                if code == SignupCode.SC_SUCC:
                    # 选择目标鱼
                    for _val in config.getGrandPrixConf("group").values():                          # 1、2、3个组
                        idx = random.randint(0, len(_val) - 1)                                      # 一组鱼
                        _cnt = config.getGrandPrixConf("target").get(str(_val[idx]), {}).get("count", 999)  # 谋一种鱼 捕获数量
                        _point = config.getGrandPrixConf("target").get(str(_val[idx]), {}).get("point", 0)  # 谋一种鱼 获得的积分
                        self.grandPrixTargetFish[str(_val[idx])] = [0, _cnt, _point]

                    # 备份技能数据.
                    self.grandPrixUseSkillTimes = []
                    for i in range(skill_system.MAX_INSTALL_NUM):   #  + skill_system.AUXILIARY_SKILL_NUM
                        self.grandPrixUseSkillTimes.append({
                            "skillId": 0, "state": 0, "star": 0, "grade": 0,
                            "count": config.getGrandPrixConf("fireCount")[1],               # 技能使用次数3
                            "skillType": 0 if i < skill_system.MAX_INSTALL_NUM else 1       # 0主技能 1辅助技能
                        })

                    for idx, _skillId in enumerate(self.skillSlots):
                        _skill = self.getSkill(_skillId, 0)
                        self.grandPrixUseSkillTimes[idx]["skillId"] = _skillId
                        self.grandPrixUseSkillTimes[idx]["state"] = _skill.skillState
                        self.grandPrixUseSkillTimes[idx]["star"] = _skill.skillStar
                        self.grandPrixUseSkillTimes[idx]["grade"] = _skill.skillGrade

                    fpMultiple = config.getGunLevelConf(self.gunLevel, self.table.gameMode).get("unlockMultiple", 1)    # 渔场解锁的倍率
                    fpMultiple = max(self.table.runConfig.minMultiple, min(fpMultiple, self.table.runConfig.maxMultiple))
                    if self.fpMultiple != fpMultiple:           # 修改渔场倍率
                        self.changeFpMultiple(fpMultiple)
                    nowGunLevel = 2100 + self.table.runConfig.minUserLevel
                    if self.nowGunLevel != nowGunLevel:         # 玩家火炮升级了 改变加成
                        self.gunChange(nowGunLevel)

                    if ftlog.is_debug():
                        ftlog.debug("grandPrixBIEvent 1, userId =", self.userId, self.grandPrixStartTS, self.inGameTimes)
                    if self.inGameTimes:
                        bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0,
                                                 self.grandPrixStartTS, self.inGameTimes, 0, 0, [],
                                                 util.getClientId(self.userId))
                        self.inGameTimes = 0

                    self.grandPrixLevelFpMultiple = [self.nowGunLevel, self.fpMultiple]     # 大奖赛火炮等级和倍率
                    self.grandPrixFishPoint = 0
                    self.grandPrixSurpassCount = 0
                    self.grandPrixStartTS = curTime                                         # 大奖赛开始的时间戳
                    self.grandPrixFireCount = config.getGrandPrixConf("fireCount")[0]
            else:
                # 现在不可参赛
                if not grand_prix.isGrandPrixOpenTime():
                    code = SignupCode.SC_NOT_OPEN
                else:
                    code = SignupCode.SC_SUCC

            if code == SignupCode.SC_SUCC:
                interval = max(3, remainGrandPrixTimeSeconds)
                if self.grandPrixFireCount == 0:                                                    # 3秒之后结束大奖赛
                    interval = 3
                if self.grandPrixEndTimer:
                    self.grandPrixEndTimer.cancel()
                    self.grandPrixEndTimer = None
                self.grandPrixEndTimer = FTLoopTimer(interval, 0, self.endGrandPrix)
                self.grandPrixEndTimer.start()

                # 取消处于使用中的技能，以免干扰技能使用次数计数
                if self.offline == 0:                                                               # 玩家在线
                    self.cancelUsingSkills()
                    self.unloadSkills()
                    self.loadAllSkillData()
                    self.syncSkillSlots()
            else:
                self._resetGrandPrixData()                                                          # 重置大奖赛相关数据
        else:
            code = SignupCode.SC_SUCC if not self.isGrandPrixMode() else SignupCode.SC_UNFINISH     # 大奖赛比赛模式
            if code == SignupCode.SC_SUCC:
                self._resetGrandPrixData()

        self._getSurpassTarget()

        remainFreeTimes = config.getVipConf(self.vipLevel).get("grandPrixFreeTimes", 0) - self._freeTimes
        mo = MsgPack()
        mo.setCmd("start_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("code", code)
        mo.setResult("signUp", signUp)                              # 报名大奖赛/直接进入渔场
        mo.setResult("signUpState", signUp)                         # 是否已报名大奖赛
        mo.setResult("remainFreeTimes", remainFreeTimes)
        mo.setResult("fireCount", self.grandPrixFireCount)
        mo.setResult("fishPoint", self.grandPrixFishPoint)
        mo.setResult("targetFish", self.grandPrixTargetFish)
        grandPrixUseSkillTimes = [val.get("count", 0) for val in self.grandPrixUseSkillTimes]
        mo.setResult("useSkillTimes", grandPrixUseSkillTimes)
        mo.setResult("firstEnterGrandPrix", 1 if code == SignupCode.SC_SUCC and signUp == 1 and self.grandPrixStartTS == curTime else 0)
        GameMsg.sendMsg(mo, self.userId)
        if code == SignupCode.SC_NOT_OPEN or code == SignupCode.SC_UNFINISH:
            self.sendGrandPrixInfo()

    def endGrandPrix(self):
        """
        大奖赛结束
        """
        if self.userId == 0:
            return
        if self.grandPrixEndTimer:
            self.grandPrixEndTimer.cancel()
            self.grandPrixEndTimer = None

        if not self.isGrandPrixMode():
            return

        grandPrixPoint, grandPrixFinalPoint = self.saveGrandPrixPoint()

        # 完成大奖赛事件
        event = FinishGrandPrixEvent(self.userId, FISH_GAMEID, self.table.bigRoomId, grandPrixFinalPoint)
        TGFish.getEventBus().publishEvent(event)

        bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_END", self.userId, FISH_GAMEID, 0, 0,
                                 grandPrixFinalPoint, 0, 0, 0, [], util.getClientId(self.userId))

        if self.inGameTimes:
            bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0,
                                     self.grandPrixStartTS, self.inGameTimes, 0, 0, [], util.getClientId(self.userId))
            self.inGameTimes = 0

        # 恢复技能数据
        self.cancelUsingSkills()    # 取消处于使用中的技能
        self.unloadSkills()         # 下载所有技能
        # 重置数据存档
        self._resetGrandPrixData()
        # 重新加载技能
        self.loadAllSkillData()     # 读取并初始化所有技能数据
        self.syncSkillSlots()       # 同步技能槽消息

        vipAddition = config.getVipConf(self.vipLevel).get("grandPrixAddition", 0.)

        mo = MsgPack()
        mo.setCmd("end_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("fishPoint", grandPrixPoint)
        mo.setResult("finalPoint", grandPrixFinalPoint)
        mo.setResult("levelAddition", ("%d%%(%d)" % (int(self.levelAddition * 100), int(grandPrixPoint * self.levelAddition + 0.5))))   # 炮倍加成
        mo.setResult("vipAddition", ("%d%%(%d)" % (int(vipAddition * 100), int(grandPrixPoint * vipAddition + 0.5))))                   # vip加成
        rank, rankRewards = ranking_system.getUserRankAndRewards(RankType.TodayGrandPrix, self.userId)
        mo.setResult("rank", rank)
        mo.setResult("rankRewards", rankRewards)
        mo.setResult("fee", config.getGrandPrixConf("fee"))
        mo.setResult("des", config.getMultiLangTextConf(config.getGrandPrixConf("info").get("endDes", ""), lang=self.lang))
        GameMsg.sendMsg(mo, self.userId)
        self.sendGrandPrixInfo()

    def _resetGrandPrixData(self):
        """
        重置大奖赛相关数据
        """
        self.grandPrixStartTS = 0                   # 大奖赛开始的时间戳
        self.grandPrixFireCount = 0                 # 大奖赛剩余开火次数
        self.grandPrixTargetFish = {}               # 大奖赛目标鱼捕获数量
        self.grandPrixUseSkillTimes = []            # 大奖赛剩余技能使用次数
        self.grandPrixFishPoint = 0                 # 捕鱼积分
        self.grandPrixSurpassCount = 0              # 大奖赛超越自己次数
        self.grandPrixLevelFpMultiple = None        # 大奖赛火炮等级和倍率
        self._rankListCache = []                    # 要超越的玩家缓存
        self._surpassUser = {}                      # 要超越玩家数据
        self._saveGrandPrixData()                   # 保存大奖赛信息
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_surpassCount, 0)    # 大奖赛超越自己次数

    def _saveGrandPrixData(self):
        """
        保存大奖赛数据
        """
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_startTS, self.grandPrixStartTS)
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_fireCount, self.grandPrixFireCount)
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_fishPoint, self.grandPrixFishPoint)
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_surpassCount, self.grandPrixSurpassCount)
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_useSkillTimes, json.dumps(self.grandPrixUseSkillTimes))
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_targetFish, json.dumps(self.grandPrixTargetFish))
        weakdata.setDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple, json.dumps(self.grandPrixLevelFpMultiple))

    def sendGrandPrixInfo(self):
        """
        发送大奖赛信息 大奖赛相关信息(进入渔场后服务器主动推送)
        """
        if not grand_prix.isGrandPrixOpenTime():            # 是否为大奖赛开放时段 00:00 —— 23: 30
            self._resetGrandPrixData()
            self._freeTimes = 0                                   # 免费次数
            weakdata.setDayFishData(self.userId, WeakData.grandPrix_freeTimes, 0)

        signUpState = 1 if self.isGrandPrixMode() else 0    # 是否已经报名
        remainFreeTimes = config.getVipConf(self.vipLevel).get("grandPrixFreeTimes", 0) - self._freeTimes   # 剩余免费次数
        openTime = "-".join(config.getGrandPrixConf("openTimeRange"))       # 时间范围

        mo = MsgPack()
        mo.setCmd("grand_prix_info")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("remainFreeTimes", remainFreeTimes)
        mo.setResult("fee", config.getGrandPrixConf("fee"))                         # 报名费
        mo.setResult("openTime", openTime)
        mo.setResult("isInOpenTime", 1 if grand_prix.isGrandPrixOpenTime() else 0)  # 大奖在是否在开放时间段
        mo.setResult("signUpState", signUpState)                                    # 是否已报名大奖赛
        mo.setResult("todayRankType", RankType.TodayGrandPrix)                      # 今日榜Type,使用fish_ranking获取排行榜数据,下同
        mo.setResult("todayDate", util.timestampToStr(int(time.time()), "%m/%d"))   # 今日榜时间
        mo.setResult("yesterdayRankType", RankType.LastGrandPrix)
        mo.setResult("yesterdayDate", util.timestampToStr(int(time.time() - 86400), "%m/%d"))
        mo.setResult("des", config.getMultiLangTextConf(config.getGrandPrixConf("info").get("des"), lang=self.lang))    # 每日积分超过2400送100珍珠，今日榜单每10分钟刷新1次，最终排名00:00公布
        mo.setResult("pointsInfo", grand_prix.getPointInfo(self.userId))            # 奖励积分 道具Id、道具数量、是否领取了奖励0|1
        mo.setResult("todayMaxPoints", weakdata.getDayFishData(self.userId, WeakData.grandPrix_todayMaxPoints, 0))      # 今日最高积分
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "mo =", mo)
        # # 已经报名则直接开始大奖赛
        # if signUpState == 1:
        #     self.startGrandPrix(signUpState)

    def addGrandPrixFishPoint(self, fishPoint, fishType):
        """
        添加大奖赛捕鱼积分
        """
        if self.isGrandPrixMode():
            self.grandPrixFishPoint += fishPoint
            if ftlog.is_debug():
                ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "fishType =", fishType,
                            "levelAddition =", self.levelAddition, "fishPoint =", fishPoint)
            fishType = int(fishType) % 100
            # 添加目标鱼积分
            for ft, val in self.grandPrixTargetFish.iteritems():
                if fishType == int(ft) % 100 and val[0] < val[1]:
                    self.grandPrixTargetFish[ft][0] += 1
                    if self.grandPrixTargetFish[ft][0] == val[1]:
                        self.grandPrixFishPoint += val[2]
                    if ftlog.is_debug():
                        ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "targetPoint =", val[2])
                    break

            if self.grandPrixFishPoint > self.bestPoint:    # 最好的积分
                self.grandPrixSurpassCount += 1             # 大奖赛超越自己次数
                self._surpassTarget()
        else:
            fishPoint = 0

        return fishPoint

    def sendGrandPrixCatch(self, catchFishPoints):
        """
        大奖赛捕获消息
        """
        mo = MsgPack()
        mo.setCmd("catch_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("catchFishPoints", catchFishPoints)        # [{"fId": 10010, "point": 5},], # 捕鱼积分
        mo.setResult("fishPoint", self.grandPrixFishPoint)      # 捕鱼积分
        mo.setResult("targetFish", self.grandPrixTargetFish)    # {"11011": [0, 10],},# 大奖赛目标鱼:[捕获数量, 目标数量]
        GameMsg.sendMsg(mo, self.userId)

    def setTipTimer(self):
        """
        设置比赛开始和结束的通知消息
        """
        if self.grandPrixTipTimer:
            self.grandPrixTipTimer.cancel()
            self.grandPrixTipTimer = None
            self.sendGrandPrixInfo()                                        # 发送大奖赛信息
        curTime = int(time.time())
        dayStartTS = util.getDayStartTimestamp(curTime)
        openTimeRange = config.getGrandPrixConf("openTimeRange")
        pastTime = curTime - dayStartTS                                     # 03:00|23:10
        beginTime = util.timeStrToInt(openTimeRange[0])                     # 00:00
        endTime = util.timeStrToInt(openTimeRange[1])                       # 23:00
        if pastTime < beginTime:
            interval = beginTime - pastTime + 5                             # 开始的通知
        elif beginTime <= pastTime <= endTime:
            interval = endTime - pastTime + 5                               # 结束的通知
        else:
            interval = 86400 + beginTime - pastTime + 5                     # 开始的通知
        self.grandPrixTipTimer = FTLoopTimer(interval, 0, self.setTipTimer) # 死循环
        self.grandPrixTipTimer.start()

    def _getSurpassTarget(self):
        """
        获取要超越的玩家数据
        """
        timestamp = pktimestamp.getCurrentTimestamp()
        rankClass = RankingBase(self.userId, RankType.TodayGrandPrix, RankDefineIndex.GrandPrix, clientId=None, httpRequest=False)
        if rankClass:
            rankingList = rankClass.getTopNRankUsers(timestamp)
            surpassTarget = config.getGrandPrixConf("surpassTarget")        # [100、80、... 3、2、1]
            masterSurpassTargets = []
            for rank in surpassTarget:
                idx = rank - 1
                if 0 <= idx < len(rankingList.rankingUserList):
                    player = rankingList.rankingUserList[idx]
                    name = util.getNickname(player.userId)
                    avatar = userdata.getAttr(player.userId, "purl")
                    masterSurpassTargets.append({
                        "userId": player.userId, "name": name, "score": player.score,
                        "rank": player.rank + 1, "avatar": avatar
                    })
            self._rankListCache = masterSurpassTargets

    def _surpassTarget(self):
        """请求大奖赛中超越玩家数据"""
        if self.userId:
            msg = MsgPack()
            msg.setCmd("g_surpass")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.table.roomId)
            msg.setResult("tableId", self.table.tableId)
            msg.setResult("userId", self.userId)
            if self.grandPrixSurpassCount <= 1 and self.bestPoint != 0:
                msg.setResult("bestScore", self.grandPrixFishPoint)
            if self._surpassUser.get(self.userId, None):
                if self.grandPrixFishPoint > self._surpassUser.get(self.userId).get("score"):
                    msg.setResult("target", self._surpassUser.get(self.userId))
            if self.grandPrixSurpassCount <= 1 or self._surpassUser.get(self.userId, None):
                GameMsg.sendMsg(msg, self.userId)
            self._updateSurpassUser()

    def _updateSurpassUser(self):
        """更新要超越的目标用户"""
        newTarget = None
        maxScore = max(self.grandPrixFishPoint, self.bestPoint)
        for tar in self._rankListCache:
            if maxScore < tar["score"] and tar["userId"] != self.userId:
                newTarget = tar
                break
        self._surpassUser[self.userId] = newTarget

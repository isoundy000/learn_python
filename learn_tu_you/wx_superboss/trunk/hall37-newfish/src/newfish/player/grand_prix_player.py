# -*- coding=utf-8 -*-
"""
大奖赛玩家逻辑
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/10/08

import time
import json
import random

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

    def _loadUserData(self):
        super(FishGrandPrixPlayer, self)._loadUserData()
        # 捕鱼积分
        self.grandPrixFishPoint = weakdata.getDayFishData(self.userId, WeakData.grandPrix_fishPoint, 0)
        # 大奖赛剩余开火次数
        self.grandPrixFireCount = weakdata.getDayFishData(self.userId, WeakData.grandPrix_fireCount, 0)
        # 大奖赛剩余技能使用次数
        self.grandPrixUseSkillTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_useSkillTimes, [])
        # 大奖赛目标鱼捕获数量
        self.grandPrixTargetFish = weakdata.getDayFishData(self.userId, WeakData.grandPrix_targetFish, {})
        # 大奖赛火炮等级和倍率
        # self.grandPrixLevelFpMultiple = weakdata.getDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple)
        # 大奖赛开始的时间戳
        self.grandPrixStartTS = weakdata.getDayFishData(self.userId, WeakData.grandPrix_startTS, 0)
        # 大奖赛结束定时器
        self.grandPrixEndTimer = None
        # 大奖赛提示定时器
        self.grandPrixTipTimer = None
        # 大奖赛阶段奖励
        self.grandPrixGetPointsInfo = weakdata.getDayFishData(self.userId, WeakData.grandPrix_getPointsInfo, [])
        self._freeTimes = weakdata.getDayFishData(self.userId, WeakData.grandPrix_freeTimes, 0)

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
        self.inGameTimes = 0                        # 游戏时长（分钟）

    def _incrGameTimer(self):
        """增加游戏时长"""
        if self.userId <= 0:
            return
        super(FishGrandPrixPlayer, self)._incrGameTimer()
        self.inGameTimes += 1

    def _checkSkillCondition(self, skillId, select, skillType=0):
        """
        检测技能使用条件
        """
        if self.isGrandPrixMode() and select:       # 大奖赛模式限制技能槽的使用次数
            for idx, val in enumerate(self.grandPrixUseSkillTimes):
                if val.get("skillId") == skillId and val.get("skillType", 0) == skillType:
                    if val.get("count") <= 0:
                        return 7
                    break
        return super(FishGrandPrixPlayer, self)._checkSkillCondition(skillId, select, skillType)

    def addFire(self, bulletId, wpId, sendTimestamp, fpMultiple, gunMultiple=1, gunX=1, skill=None, power=None,
                clientFire=True, targetPos=None, fishType=None, costChip=0, superBullet=None):
        """添加开火信息"""
        super(FishGrandPrixPlayer, self).addFire(bulletId, wpId, sendTimestamp, fpMultiple, gunMultiple, gunX,
                                                 skill, power, clientFire, targetPos, fishType, costChip, superBullet)
        if clientFire and skill is None and self.isGrandPrixMode():
            self.grandPrixFireCount -= 1                                                # 开火次数减少
            if self.grandPrixFireCount == 0:                                            # 结束比赛
                self.endGrandPrix()

    # def refreshGunLevel(self):
    #     """
    #     刷新火炮等级数据
    #     """
    #     levelFpMultiple = weakdata.getDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple)
    #     if levelFpMultiple:
    #         self.nowGunLevel, _ = levelFpMultiple
    #     else:
    #     self.nowGunLevel = self.gunLevel
    #     self.nowGunLevel = max(self.table.runConfig.minGunLevel, min(self.nowGunLevel, self.table.runConfig.maxGunLevel))

    def _refreshSkillSlots(self, skillType=0):
        """
        刷新技能数据 安装技能槽
        """
        if skillType == 0:
            self.skillSlots = {}
        if self.grandPrixUseSkillTimes:
            for val in self.grandPrixUseSkillTimes:
                if isinstance(val, dict) and val.get("skillId"):
                    if val.get("skillType", 0) == skillType:
                        if skillType == 0:
                            self.skillSlots[val["skillId"]] = [val["state"], val["star"], val["grade"]]
        else:
            super(FishGrandPrixPlayer, self)._refreshSkillSlots(skillType)

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
        retMsg.setResult("userId", userId)
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

    def saveUserData(self):
        """保存用户数据"""
        super(FishGrandPrixPlayer, self).saveUserData()
        self.saveGrandPrixPoint()                                           # 保存大奖赛积分

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
        return multiple

    def isGrandPrixMode(self):
        """
        大奖赛比赛模式
        """
        return self.grandPrixStartTS > 0

    def _calcuCatchFishGrandPrixPoint(self, fishPoint, gunX):
        """
        计算捕鱼积分 炮倍和vip的加成
        """
        if ftlog.is_debug():
            ftlog.debug('calcuCatchFishGrandPrixPoint', fishPoint, gunX)
        vipAddition = config.getVipConf(self.vipLevel).get("grandPrixAddition", 0.)
        gunXAddition = self.getGunXAddition(gunX)
        if ftlog.is_debug():
            ftlog.debug('calcuCatchFishGrandPrixPoint1', vipAddition, gunXAddition)
        point = fishPoint * 100
        points = point * (1 + vipAddition) * (1 + gunXAddition)
        return int(points)

    def getGunXAddition(self, gunX):
        """
        根据开火时候[炮倍 * 炮(单倍率|双倍率)]确定 加成值
        """
        gunMInfo = config.getGrandPrixConf("gunMultiAddition")
        for info in gunMInfo:
            if info["rangeList"][0] <= gunX <= info["rangeList"][1]:
                return info["addition"]
        return 0

    def saveGrandPrixPoint(self):
        """
        保存大奖赛积分
        """
        if not self.isGrandPrixMode():
            return 0, 0
        grandPrixFinalPoint = self.grandPrixFishPoint
        # 计入排行榜
        if grandPrixFinalPoint:
            ranking_system.refreshGrandPrixPoint(self.userId, grandPrixFinalPoint)
        # 保存大奖赛数据
        self._saveGrandPrixData()
        return int(grandPrixFinalPoint)                                                 # 最后的积分

    def cancelUsingSkills(self):
        """
        取消处于使用中的技能
        """
        if not self.usingSkill:                                                         # 有之前技能记录
            return
        lastSkillId = self.usingSkill[-1].get("skillId")
        lastSkillType = self.usingSkill[-1].get("skillType", 0)
        lastSkill = self.getSkill(lastSkillId, lastSkillType)
        if not lastSkill:
            return
        if lastSkill.state == 1:
            lastSkill.use(0)
        else:
            self.removeUsingSkill(lastSkillId, lastSkillType)
            orgState = lastSkill.state
            lastSkill.state = 0
            self.table.broadcastSkillUse(lastSkill, 0, self.userId, orgState)           # 广播选中/取消技能消息
        self.table.broadcastGunChange(self)                                             # 广播玩家现在的火炮等级

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

    def startGrandPrix(self):
        """
        大奖赛开始 grandPrixStartTS=0 报名大奖赛/ grandPrixStartTS > 0 直接进入渔场
        """
        curTime = int(time.time())
        dayStartTimestamp = util.getDayStartTimestamp(curTime)
        remainGrandPrixTimeSeconds = util.timeStrToInt(config.getGrandPrixConf("openTimeRange")[1]) - (curTime - dayStartTimestamp)     # 大奖赛剩余时间
        # 当局进入大奖赛
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
                for _val in config.getGrandPrixConf("group").values():                                  # 1、2、3个组
                    idx = random.randint(0, len(_val) - 1)                                              # 一组鱼
                    _cnt = config.getGrandPrixConf("target").get(str(_val[idx]), {}).get("count", 999)  # 某一种鱼 捕获数量
                    _point = config.getGrandPrixConf("target").get(str(_val[idx]), {}).get("point", 0)  # 某一种鱼 获得的积分
                    self.grandPrixTargetFish[str(_val[idx])] = [0, _cnt, _point]

                # 备份技能数据.
                self.grandPrixUseSkillTimes = []
                for i in range(skill_system.MAX_INSTALL_NUM - 1):
                    self.grandPrixUseSkillTimes.append({
                        "skillId": 0, "state": 0, "star": 0, "grade": 0,
                        "count": config.getGrandPrixConf("fireCount")[1],                       # 技能使用次数3
                        "skillType": 0 if i < skill_system.MAX_INSTALL_NUM else 1               # 0主技能 1辅助技能
                    })

                for idx, _skillId in enumerate(self.skillSlots):
                    _skill = self.getSkill(_skillId, 0)
                    self.grandPrixUseSkillTimes[idx]["skillId"] = _skillId
                    self.grandPrixUseSkillTimes[idx]["state"] = _skill.skillState
                    self.grandPrixUseSkillTimes[idx]["star"] = _skill.skillStar
                    self.grandPrixUseSkillTimes[idx]["grade"] = _skill.skillGrade

                if self.inGameTimes:
                    bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0, self.grandPrixStartTS, self.inGameTimes, 0, 0, [], util.getClientId(self.userId))
                    self.inGameTimes = 0

                self.grandPrixFishPoint = 0
                self.grandPrixSurpassCount = 0
                self.grandPrixStartTS = curTime                                                 # 大奖赛开始的时间戳
                self.grandPrixFireCount = config.getGrandPrixConf("fireCount")[0]
                self._saveGrandPrixData()                                                       # 保存大奖赛数据
        else:
            if not grand_prix.isGrandPrixOpenTime():                                            # 现在不可参赛
                code = SignupCode.SC_NOT_OPEN
            elif not self.isGrandPrixMode():
                code = SignupCode.SC_SUCC
            else:
                code = SignupCode.SC_UNFINISH

        if code in [SignupCode.SC_SUCC, SignupCode.SC_UNFINISH]:
            interval = max(0.1, remainGrandPrixTimeSeconds)
            if self.grandPrixFireCount == 0:                                                    # 3秒之后结束大奖赛
                interval = 0.1
            if self.grandPrixEndTimer:
                self.grandPrixEndTimer.cancel()
                self.grandPrixEndTimer = None
            self.grandPrixEndTimer = FTLoopTimer(interval, 0, self.endGrandPrix)                # 启动结束定时器
            self.grandPrixEndTimer.start()
            # 取消处于使用中的技能，以免干扰技能使用次数计数
            if self.offline == 0:                                                               # 玩家在线
                self.cancelUsingSkills()
                self.unloadSkills()
                self.loadAllSkillData()
                self.syncSkillSlots()
        elif code == SignupCode.SC_NOT_OPEN:                                                    # 没开启
            self._resetGrandPrixData()                                                          # 重置大奖赛相关数据

        self._getSurpassTarget()                                                                # 获取要超越的玩家数据
        mo = MsgPack()
        mo.setCmd("start_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("fireCount", self.grandPrixFireCount)
        mo.setResult("fishPoint", self.grandPrixFishPoint)
        mo.setResult("targetFish", self.grandPrixTargetFish)
        mo.setResult("useSkillTimes", {val.get("skillId", 0): val.get("count", 0) for val in self.grandPrixUseSkillTimes})
        mo.setResult("pointsInfo", grand_prix.getPointInfo(self.userId))  # 奖励积分 道具Id、道具数量、是否领取了奖励0|1
        mo.setResult("todayMaxPoints", weakdata.getDayFishData(self.userId, WeakData.grandPrix_point, 0))  # 今日最高积分
        GameMsg.sendMsg(mo, self.userId)

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

        grandPrixFinalPoint = self.saveGrandPrixPoint()
        # 完成大奖赛事件
        event = FinishGrandPrixEvent(self.userId, FISH_GAMEID, self.table.bigRoomId, grandPrixFinalPoint)
        TGFish.getEventBus().publishEvent(event)
        bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_END", self.userId, FISH_GAMEID, 0, 0, grandPrixFinalPoint, 0, 0, 0, [], util.getClientId(self.userId))
        if self.inGameTimes:
            bireport.reportGameEvent("BI_NFISH_GRAND_PRIX_INGAMETIMES", self.userId, FISH_GAMEID, 0, 0, self.grandPrixStartTS, self.inGameTimes, 0, 0, [], util.getClientId(self.userId))
            self.inGameTimes = 0

        self.cancelUsingSkills()                    # 恢复技能数据 取消处于使用中的技能
        self.unloadSkills()                         # 下载所有技能
        self._resetGrandPrixData()                  # 重置数据存档
        self.loadAllSkillData()                     # 重新加载技能 读取并初始化所有技能数据
        self.syncSkillSlots()                       # 同步技能槽消息
        rank, rankRewards = ranking_system.getUserRankAndRewards(RankType.TodayGrandPrix, self.userId)
        if ftlog.is_debug():
            ftlog.debug("endGrandPrix", self.grandPrixStartTS, self.grandPrixFireCount, self.grandPrixFishPoint)
        mo = MsgPack()
        mo.setCmd("end_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("fishPoint", grandPrixFinalPoint)
        mo.setResult("rank", rank)
        mo.setResult("rankRewards", rankRewards)
        mo.setResult("fee", config.getGrandPrixConf("fee"))
        mo.setResult("tabs", ranking_system.getRankingTabs(self.userId, util.getClientId(self.userId), RankType.TodayGrandPrix, rankDetail=True))
        GameMsg.sendMsg(mo, self.userId)
        self.sendGrandPrixInfo()
        self.table.clearPlayer(self)                # 从桌子中踢掉玩家

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
        # self.grandPrixLevelFpMultiple = None        # 大奖赛火炮等级和倍率
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
        # weakdata.setDayFishData(self.userId, WeakData.grandPrix_levelFpMultiple, json.dumps(self.grandPrixLevelFpMultiple))

    def sendGrandPrixInfo(self):
        """
        发送大奖赛信息 大奖赛相关信息(进入渔场后服务器主动推送)
        """
        if not grand_prix.isGrandPrixOpenTime():                                    # 是否为大奖赛开放时段 00:00 —— 23:00
            self._resetGrandPrixData()
            self._freeTimes = 0                                                     # 免费次数
            weakdata.setDayFishData(self.userId, WeakData.grandPrix_getPointsInfo, json.dumps([]))
            weakdata.setDayFishData(self.userId, WeakData.grandPrix_freeTimes, self._freeTimes)
        if ftlog.is_debug():
            ftlog.debug("sendGrandPrixInfo", self.grandPrixStartTS, self.isGrandPrixMode())
        signUpState = 1 if self.isGrandPrixMode() else 0                            # 是否已经报名
        remainFreeTimes = config.getVipConf(self.vipLevel).get("grandPrixFreeTimes", 0) - self._freeTimes   # 剩余免费次数
        openTime = "-".join(config.getGrandPrixConf("openTimeRange"))               # 时间范围
        mo = MsgPack()
        mo.setCmd("grand_prix_info")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("remainFreeTimes", remainFreeTimes)
        mo.setResult("fee", config.getGrandPrixConf("fee"))                         # 报名费
        mo.setResult("openTime", openTime)                                          # 00:00 - 23:00
        mo.setResult("isInOpenTime", 1 if grand_prix.isGrandPrixOpenTime() else 0)  # 大奖在是否在开放时间段
        mo.setResult("signUpState", signUpState)                                    # 是否已报名大奖赛
        mo.setResult("todayRankType", RankType.TodayGrandPrix)                      # 今日榜Type,使用fish_ranking获取排行榜数据,下同
        mo.setResult("todayDate", util.timestampToStr(int(time.time()), "%m/%d"))   # 今日榜时间
        mo.setResult("yesterdayRankType", RankType.LastGrandPrix)
        mo.setResult("yesterdayDate", util.timestampToStr(int(time.time() - 86400), "%m/%d"))
        mo.setResult("des", config.getMultiLangTextConf(config.getGrandPrixConf("info").get("des"), lang=self.lang))    # 每日积分超过2400送100珍珠，今日榜单每10分钟刷新1次，最终排名00:00公布
        mo.setResult("pointsInfo", grand_prix.getPointInfo(self.userId))            # 奖励积分 道具Id、道具数量、是否领取了奖励0|1
        mo.setResult("todayMaxPoints", weakdata.getDayFishData(self.userId, WeakData.grandPrix_point, 0))      # 今日最高积分
        GameMsg.sendMsg(mo, self.userId)
        if ftlog.is_debug():
            ftlog.debug("FishGrandPrixPlayer, userId =", self.userId, "mo =", mo)

    def addGrandPrixFishPoint(self, fishPoint, fishType, gunX):
        """
        添加大奖赛捕鱼积分
        """
        if self.isGrandPrixMode():
            fishPoint = self._calcuCatchFishGrandPrixPoint(fishPoint, gunX)         # 计算捕获 vip加成 + 火炮倍率加成
            self.grandPrixFishPoint += fishPoint
            fishType = int(fishType) % 100
            for ft, val in self.grandPrixTargetFish.iteritems():                    # 添加目标鱼积分
                if fishType == int(ft) % 100 and val[0] < val[1]:
                    self.grandPrixTargetFish[ft][0] += 1
                    if self.grandPrixTargetFish[ft][0] == val[1]:
                        self.grandPrixFishPoint += val[2]
                    break
            if self.grandPrixFishPoint > self.bestPoint:                            # 最好的积分
                self.grandPrixSurpassCount += 1                                     # 大奖赛超越自己次数
                self._surpassTarget()
        else:
            fishPoint = 0
        return fishPoint

    def getPointReward(self, userId):
        """
        是否获取积分阶段奖励
        """
        rewards = []
        for info in config.getGrandPrixConf("stageInfo"):
            point = info["point"]
            reward = info["rewards"]
            if self.grandPrixFishPoint >= point and point not in self.grandPrixGetPointsInfo:
                rewards.extend(reward)
                self.grandPrixGetPointsInfo.append(point)
        if rewards:
            util.addRewards(userId, rewards, "BI_GRAND_PRIX_POINT_REWARD")          # 添加奖励
            weakdata.setDayFishData(userId, WeakData.grandPrix_getPointsInfo, json.dumps(self.grandPrixGetPointsInfo))
        return rewards

    def sendGrandPrixCatch(self, catchFishPoints):
        """
        大奖赛捕获消息
        """
        mo = MsgPack()
        mo.setCmd("catch_grand_prix")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("catchFishPoints", catchFishPoints)                    # [{"fId": 10010, "point": 5},], # 捕鱼积分
        mo.setResult("fishPoint", self.grandPrixFishPoint)                  # 捕鱼积分
        mo.setResult("targetFish", self.grandPrixTargetFish)                # {"11011": [0, 10],},   # 大奖赛目标鱼:[捕获数量, 目标数量]
        mo.setResult("rewards", self.getPointReward(self.userId))           # [{"name": 101, "count": 1000}, {"name": 101, "count": 2000}], # 大奖赛积分奖励
        mo.setResult("pointsInfo", grand_prix.getPointInfo(self.userId))    # 奖励积分 道具Id、道具数量、是否领取了奖励0|1
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

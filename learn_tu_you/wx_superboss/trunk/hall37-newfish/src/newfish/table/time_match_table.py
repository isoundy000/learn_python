#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import time
import copy
import random
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.biz import bireport
from poker.entity.dao import onlinedata
from newfish.room.timematchctrl.utils import Logger
from newfish.table.multiple_table import FishMultipleTable
from newfish.entity.event import CatchEvent, EnterTableEvent
from newfish.player.time_match_player import FishTimeMatchPlayer
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID, CHIP_KINDID
from newfish.entity.msg import GameMsg
from newfish.entity.fishgroup.fish_group_system import FishGroupSystem
from newfish.entity.fishgroup.normal_fish_group import NormalFishGroup
from newfish.entity.fishgroup.buffer_fish_group import BufferFishGroup
from newfish.entity.fishgroup.multiple_fish_group import MultipleFishGroup



class MatchState:
    DEFAULT = 0
    READY = 1
    START = 2
    END = 3


class FishTimeMatchTable(FishTable):

    def __init__(self, room, tableId):
        super(FishTimeMatchTable, self).__init__(room, tableId)
        self.clearTableData()
        # 用户离线等待时间
        self._offlineWaitSeconds = 600
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 600
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 600
        # 准备倒计时
        self._readySeconds = 5
        # 排名刷新间隔
        self._loopSeconds = 5
        # 初始化定时器
        self._readyTimer = None
        self._startTimer = None
        self._loopTimer = None
        # 比赛技能
        self._matchSkills = None
        # 可用action
        self.actionMap = {
            "robot_leave": self._robotLeave,
            "catch": self._verifyCatch,
            "skill_use": self._skill_use,
            "skill_install": self._skill_install,
            "skill_replace": self._skill_replace,
            "smile": self.doTableSmilies,
            "honor_push": self._honor_push,
            "honor_replace": self._honor_replace,
            "guns_list": self._guns_list,
            "guns_pool": self._guns_pool,
            "treasure_rewards": self._getTreasureRewards,
            "item_use": self.item_use,                          # 使用道具技能
        }
        self._logger = Logger()
        self._logger.add("cls=", self.__class__.__name__)
        self._logger.add("gameId", self.gameId)
        self._logger.add("roomId", room.roomId)
        self._logger.add("tableId", tableId)
        self._logger.add("matchId", room.bigmatchId)

    def clearTableData(self):
        """
        清理桌子数据和状态
        """
        # 比赛状态
        self._matchState = MatchState.DEFAULT
        # 比赛桌详情
        self._match_table_info = None
        # 比赛任务数据
        self._usersData = {}

    def clearAllTimer(self):
        """
        清理所有定时器
        """
        if self._logger.isDebug():
            self._logger.debug("clearAllTimer, tableId =", self.tableId)
        if self._readyTimer:
            self._readyTimer.cancel()
            self._readyTimer = None
        if self._startTimer:
            self._startTimer.cancel()
            self._startTimer = None
        if self._loopTimer:
            self._loopTimer.cancel()
            self._loopTimer = None
        if self.bufferFishGroup:
            self.bufferFishGroup.cancelNextGroupTimer()
        if self.multipleFishGroup:
            self.multipleFishGroup.cancelNextGroupTimer()

    def startFishGroup(self):
        """
        启动鱼阵
        """
        if self.runConfig.allNormalGroupIds:
            self.normalFishGroup = NormalFishGroup(self)
        # buffer鱼初始化
        if self.runConfig.allBufferGroupIds:
            self.bufferFishGroup = BufferFishGroup(self)
        # 随机倍率鱼初始化
        if self.runConfig.allMultipleGroupIds:
            self.multipleFishGroup = MultipleFishGroup(self)

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishTimeMatchPlayer(table, seatIndex, clientId)

    def _doTableManage(self, msg, action):
        """
        处理来自大比赛的table_manage命令
        """
        if action == "m_table_start":
            self.doMatchTableStart(msg)
        elif action == "m_table_info":
            self.doUpdateMatchTableInfo(msg)
        elif action == "m_table_update":
            self.doUpdateMatchRankInfo(msg)
        elif action == "m_table_clear":
            self.doMatchTableClear(msg)
        elif action == "m_table_over":
            self.doMatchOver(msg)
        elif action == "m_user_giveup":
            self.doUserGiveup(msg)
        else:
            super(FishTimeMatchTable, self)._doTableManage(msg, action)

    def doMatchTableStart(self, msg):
        """开始比赛桌子启动"""
        if self._logger.isDebug():
            self._logger.debug("doMatchTableStart", "msg=", msg)
        table_info = msg.getKey("params")

        self._doUpdateTableInfo(table_info)                                 #
        self._doMatchQuickStart()                                           # 开始
        self.bufferFishGroup and self.bufferFishGroup.initGroup(self._match_table_info["tableRankRatio"])
        self.multipleFishGroup and self.multipleFishGroup.initGroup(self._match_table_info["tableRankRatio"])
        if self._logger.isDebug():
            self._logger.debug("doMatchTableStart, tableId =", self.tableId, "readyTimer =", self._readyTimer)
        if not self._readyTimer:
            self._matchState = MatchState.READY
            self._readyTimer = FTLoopTimer(self._readySeconds, 0, self._matchStartTime)
            self._readyTimer.start()

        if self._logger.isDebug():
            self._logger.debug("doMatchTableStart OK", "msg=", msg)

    def doUpdateMatchTableInfo(self, msg):
        """更新比赛桌子信息"""
        if self._logger.isDebug():
            self._logger.debug("doUpdateMatchTableInfo", "msg=", msg)
        table_info = msg.getKey("params")
        self._doUpdateTableInfo(table_info)

    def doUpdateMatchRankInfo(self, msg):
        """更新排行榜信息"""
        if self._logger.isDebug():
            self._logger.debug("doUpdateMatchRankInfo", "msg=", msg)
        rank_info = msg.getKey("params")
        self._doUpdateRankInfo(rank_info)

    def doMatchTableClear(self, msg):
        """清理比赛桌子"""
        if self._logger.isDebug():
            self._logger.debug("doMatchTableClear", "msg=", msg)
        params = msg.getKey("params")
        matchId = params.get("matchId", -1)
        if matchId != self.room.bigmatchId:
            self._logger.error("doMatchTableClear", "msg=", msg, "err=", "DiffMatchId")
            return
        self._doMatchTableClear()

    def _doMatchTableClear(self):
        # 清理本桌玩家的在线状态
        for player in self.players:
            if player and player.userId > 0:
                self._clearPlayer(None, player.userId, player.seatId)
        self.clearTableData()
        self.clearAllTimer()

    def doMatchOver(self, msg):
        """比赛完成"""
        if self._logger.isDebug():
            self._logger.debug("doMatchOver", "msg=", msg)
        params = msg.getKey("params")
        matchId = params.get("matchId", -1)
        if matchId != self.room.bigmatchId:
            self._logger.error("doMatchOver", "msg=", msg, "err=", "DiffMatchId")
            return
        self._doMatchTableClear()

    def doUserGiveup(self, msg):
        """放弃比赛"""
        if self._logger.isDebug():
            self._logger.debug("doUserGiveup", "msg=", msg)
        params = msg.getKey("params")
        userId = params.get("userId", -1)
        matchId = params.get("matchId", -1)
        if matchId != self.room.bigmatchId:
            self._logger.error("doUserGiveup", "msg=", msg, "err=", "DiffMatchId")
        player = self.getPlayer(userId)
        from newfish.entity.event import MatchGiveUpEvent
        from newfish.game import TGFish
        event = MatchGiveUpEvent(userId, FISH_GAMEID, self.room.bigmatchId)
        TGFish.getEventBus().publishEvent(event)
        if player:
            self._clearPlayer(None, player.userId, player.seatId)
        if self.playersNum == 0:
            self._doMatchTableClear()

    def _doSit(self, msg, userId, seatId, clientId):
        """
        玩家操作, 尝试再当前的某个座位上坐下
        """
        ret = self._doSitDown(msg, userId, seatId, clientId)
        return ret

    def _doSitDown(self, msg, userId, seatId, clientId):
        """
        比赛牌桌只有玩家断线重连时才会触发坐下操作，既重新坐回牌桌
        """
        if seatId != 0:
            if self.seats[seatId - 1].userId == 0:
                onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
                ftlog.warn("reconnect user is cleaned from table", "seats =", self.seats)
                return False
            elif userId != self.seats[seatId - 1].userId:
                onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
                ftlog.warn("reconnect user id is not matched", "seats =", self.seats)
                return False
            else:
                ftlog.info("user reconect, userId:", userId)
                onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
                self.players[seatId - 1].offline = 1
                self.players[seatId - 1].clientId = clientId
                self.players[seatId - 1].lang = util.getLanguage(userId, clientId)
                self.players[seatId - 1].refreshGunSkin()
                self._sendTableInfo(userId, seatId)
                self._updateMatchInfo(userId)
                self._updateMatchRank(userId)
                self._updateMatchTask(userId)
                self.players[seatId - 1].dealEnterTable()
                self.players[seatId - 1].enterTime = int(time.time())
                self.players[seatId - 1].offline = 0
                from newfish.game import TGFish
                event = EnterTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId, 1)
                TGFish.getEventBus().publishEvent(event)
                return True
        else:
            for i in range(len(self.seats)):
                if self.seats[i].userId == userId:
                    ftlog.info("lost user reconect, userId:", userId, "i =", i)
                    onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, i + 1)
                    self.players[i].offline = 1
                    self.players[i].clientId = clientId
                    self.players[i].lang = util.getLanguage(userId, clientId)
                    self.players[i].refreshGunSkin()
                    self._sendTableInfo(userId, i + 1)
                    self._updateMatchInfo(userId)
                    self._updateMatchRank(userId)
                    self._updateMatchTask(userId)
                    self.players[i].dealEnterTable()
                    self.players[i].enterTime = int(time.time())
                    self.players[i].offline = 0
                    from newfish.game import TGFish
                    event = EnterTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId, 1)
                    TGFish.getEventBus().publishEvent(event)
                    return True

    def _doUpdateTableInfo(self, tableInfo):
        """比赛参数|获取比赛技能"""
        self._match_table_info = tableInfo
        self._matchSkills = self._match_table_info.get("skills")

    def _doUpdateRankInfo(self, rankInfo):
        """更新排名信息"""
        seats = rankInfo["seats"]
        for seat in seats:
            userId = seat["userId"]
            rank = seat["rank"]
            player = self.getPlayer(userId)
            if player:
                player.rank = rank
                self._updateMatchRank(userId)

    def _doMatchQuickStart(self):
        """比赛快速开始"""
        seats = self._match_table_info["seats"]
        for seat in seats:
            userId = seat["userId"]
            seatId = seat["seatId"]
            clientId = util.getClientId(userId)
            player = self.getPlayer(userId)
            if not player:
                self.doMatchSitDown(userId, seatId, clientId)
                player = self.getPlayer(userId)
                if player:
                    player.currentTask = ["time_match", self.roomId, 1, copy.deepcopy(self._match_table_info["targets"])]
                    self._usersData[userId] = {"uid": userId,
                                               "targets": copy.deepcopy(self._match_table_info["targets"]),
                                               "results": {}}

    def doMatchSitDown(self, userId, seatId, clientId):
        """比赛入座"""
        self.seats[seatId - 1].userId = userId
        self.players[seatId - 1] = self.createPlayer(self, seatId - 1, clientId)                # 创建玩家
        self.players[seatId - 1].clip = self._match_table_info["bullet"]                        # 玩家子弹
        onlinedata.addOnlineLoc(userId, self.roomId, self.tableId, seatId)
        self._sendTableInfo(userId, seatId)                                                     # 发送table_info
        self._broadcastPlayerSit(userId, seatId)                                                # 广播玩家坐下
        self.players[seatId - 1].enterTime = int(time.time())
        self.players[seatId - 1].offline = 0
        from newfish.game import TGFish
        event = EnterTableEvent(userId, FISH_GAMEID, self.roomId, self.tableId, seatId)
        TGFish.getEventBus().publishEvent(event)
        bireport.reportGameEvent("BI_NFISH_TABLE_ENTER", userId, FISH_GAMEID, self.roomId,
                                 self.tableId, self.players[seatId - 1].level, 0, 0, 0, [], clientId)

    def getCostBullet(self, gunId, gunLevel, wpConf, clientId):
        """获取消耗的子弹"""
        costBullet = 1
        return costBullet

    def _broadcastPlayerLeave(self, userId, seatId):
        """广播玩家离开"""
        msg = MsgPack()
        msg.setCmd("leave")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("userId", userId)
        msg.setResult("seatId", seatId)
        GameMsg.sendMsg(msg, self.getBroadcastUids(userId))

    def _matchStartTime(self):
        """
        比赛开始，设置比赛结束时间点和更新排名机制
        """
        self._matchState = MatchState.START
        for player in self.players:
            if player:
                self._updateMatchInfo(player.userId)
                self._updateMatchRank(player.userId)
        if self._logger.isDebug():
            self._logger.debug("_matchStartTime, tableId =", self.tableId, "startTimer =", self._startTimer, "loopTimer =", self._loopTimer)
        self._startTimer = FTLoopTimer(self.runConfig.playingTime, 0, self._matchTimeUp)
        self._startTimer.start()
        self._loopTimer = FTLoopTimer(self._loopSeconds, -1, self._matchUpdateRank)
        self._loopTimer.start()

    def _matchTimeUp(self):
        """
        比赛结束，处理结果，清理玩家
        """
        if self._loopTimer:
            self._loopTimer.cancel()
        self._matchState = MatchState.END
        FTLoopTimer(0.5, 0, self.room.matchPlugin.doWinLose, self.room, self).start()
        for player in self.players:
            if player and player.userId:
                player.clearTimer()

    def _matchUpdateRank(self):
        """
        定时更新排名机制
        """
        if self.getRobotUserCount() == self.playersNum:
            for player in self.players:
                if player and player.userId <= config.ROBOT_MAX_USER_ID:
                    maxScore = int(self._match_table_info["bullet"] * 1.2)
                    score = random.randint(maxScore / 2, maxScore)
                    gainChip = score / (self.runConfig.playingTime / 5)
                    player.catchBudget(gainChip, 0, [])
        self.room.matchPlugin.doUpdate(self.room, self)
        if int(self._startTimer.getTimeOut()) <= self._loopSeconds:
            self._loopTimer.cancel()

    def _updateMatchInfo(self, userId):
        """更新比赛信息"""
        player = self.getPlayer(userId)
        if player and player.userId:
            msg = MsgPack()
            msg.setCmd("m_info")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("seatId", player.seatId)
            msg.setResult("userId", player.userId)
            msg.setResult("timeLong", self.runConfig.playingTime)
            msg.setResult("timeLeft", int(self._startTimer.getTimeOut()) if self._startTimer else self.runConfig.playingTime)
            msg.setResult("targets", self._match_table_info["targets"])
            GameMsg.sendMsg(msg, player.userId)

    def _updateMatchRank(self, userId):
        """比赛排名"""
        player = self.getPlayer(userId)
        if player and player.userId and self._match_table_info:
            msg = MsgPack()
            msg.setCmd("m_update")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("seatId", player.seatId)
            msg.setResult("userId", player.userId)
            msg.setResult("rank", [player.rank, self._match_table_info["playerCount"]])
            GameMsg.sendMsg(msg, player.userId)

    def _updateMatchTask(self, userId):
        """更新比赛任务"""
        player = self.getPlayer(userId)
        usersData = self._usersData.get(userId, {})
        if player and usersData and usersData["results"]:
            msg = MsgPack()
            msg.setCmd("m_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("seatId", player.seatId)
            msg.setResult("userId", player.userId)
            msg.setResult("targets", usersData["results"])
            GameMsg.sendMsg(msg, player.userId)

    def getProbbCoefficient(self, player, fishInfo):
        """概率基数"""
        if fishInfo["type"] in [3, 21] or fishInfo["multiple"] > 1:
            j1 = player.matchLuckyValue / 7500.0 + 1.0 / 3
            c = self._match_table_info["realPlayerCount"]
            k = float(4 * c) / (3 * c - 1)
            b = 1 - float(2 * c) / (3 * c - 1)
            j2 = 1                                                          # k * min(player.rank, c) / c + b
            j = (j1 + j2) * 0.5
            ftlog.debug("getProbbCoefficient", player, fishInfo,
                        "luckyValue =", player.matchLuckyValue,
                        "rank =", player.rank,
                        "j1 =", j1, "c =", c, "k =", k, "b =", b,
                        "j2 =", j2, "j =", j)
            return j
        return 1

    def dealKillFishGain(self, fId, player, fpMultiple, gunMultiple=1, bufferCoinAdd=1, wpType=None, extends=None, gunX=1):
        """
        处理打死鱼获得的奖励
        :param fId: 被捕获鱼的ID
        :param player: 捕鱼者
        :param fpMultiple: 渔场倍率
        :param gunMultiple: 炮的倍率
        :param bufferCoinAdd: buffer加成金币系数（暂时无用）
        :param wpType: 武器类型
        :param extends: 扩展数据
        :param gunX: 炮的倍数
        """
        gainChip = 0
        gain = []
        gainMap = {}
        fishType = self.fishMap[fId]["fishType"]
        fixedMultiple = self.fishMap[fId]["multiple"]
        fishConf = config.getMatchFishConf(fishType)
        if fishConf["score"] > 0:
            gainMap["fId"] = fId
            gainMap["fishType"] = fishType
            taskMultiple = 1
            target1 = self._match_table_info["targets"].get("target1", 0)
            target2 = self._match_table_info["targets"].get("target2", 0)
            multipleTarget1 = 14000 + target1 % 11000
            multipleTarget2 = 14000 + target2 % 11000
            if fishType == target1 or fishType == target2 or \
               fishType == multipleTarget1 or fishType == multipleTarget2:
                taskMultiple = fishConf.get("multiple", 1)
            if fishConf["type"] in config.MULTIPLE_FISH_TYPE:
                multiple = self.getMultipleFishMultiple(player, fishConf, fpMultiple, gunMultiple, gunX)
                gainMap["itemId"] = CHIP_KINDID
                gainMap["count"] = int(fishConf["score"] * fpMultiple * gunX * taskMultiple * multiple * bufferCoinAdd)
                gainChip = int(gainMap["count"])
                gain.append(gainMap)
            else:
                gainMap["itemId"] = CHIP_KINDID
                gainMap["count"] = int(fishConf["score"] * fpMultiple * gunX * taskMultiple * fixedMultiple * bufferCoinAdd)
                gainChip = int(gainMap["count"])
                gain.append(gainMap)
        else:
            if fishConf["type"] in config.BUFFER_FISH_TYPE:  # 捕获buffer鱼
                bufferId = player.getCatchBufferId(fishConf["itemId"])
                if bufferId > 0:
                    gainMap["fId"] = fId
                    gainMap["fishType"] = fishType
                    gainMap["itemId"] = bufferId
                    gainMap["count"] = 1
                gain.append(gainMap)
        return gainChip, gain, 0

    def getMultipleFishMultiple(self, player, fishConf, fpMultiple, gunMultiple, gunX):
        """
        获得倍率鱼的倍率
        """
        randInt = random.randint(1, 10000)
        for multipleMap in config.getMatchMultipleFishConf(self.runConfig.fishPool, player.matchLuckyValue):
            probb = multipleMap["probb"]
            if probb[0] <= randInt <= probb[-1]:
                return multipleMap["multiple"]
        return 1

    def _verifyCatch(self, msg, userId, seatId):
        if self._matchState == MatchState.END:
            return
        super(FishTimeMatchTable, self)._verifyCatch(msg, userId, seatId)

    def dealCatch(self, bulletId, wpId, player, catch, gain, gainChip, exp, fpMultiple, extends=None, skillId=0, stageId=0, isFraud=False, skillType=0):
        """处理捕获"""
        if self._matchState == MatchState.END:
            return
        self._retVerifyCatch(player, bulletId, catch, gain, extends, skillId, stageId, fpMultiple, isFraud=isFraud, skillType=skillType)
        gainCoupon = 0
        items = []
        for gainMap in gain:
            fishConf = config.getFishConf(gainMap["fishType"], self.typeName, fpMultiple)
            if fishConf["type"] in config.BUFFER_FISH_TYPE:
                player.addOneBufferId(gainMap["itemId"])
            if fishConf["type"] in config.LOG_OUTPUT_FISH_TYPE:
                ftlog.info("dealCatch->fishType",
                           "userId =", player.userId,
                           "fishType =", fishConf["type"],
                           "wpId =", wpId,
                           "gainMap =", gainMap,
                           "gainChip =", gainChip)
        player.catchBudget(gainChip, gainCoupon, items, wpId=wpId)
        self._afterCatch(bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends, skillType=skillType)

    def _afterCatch(self, bulletId, wpId, player, catch, gain, gainChip, fpMultiple, extends=None, skillId=0, isFraud=False, skillType=0, catchFishMultiple=None):
        """捕获之后"""
        fishTypes = []
        for catchMap in catch:
            if catchMap["reason"] == 0:
                fId = catchMap["fId"]
                self.setFishDied(fId)
                fishType = self.fishMap[fId]["fishType"]
                fishTypes.append(fishType)
        event = CatchEvent(player.userId, FISH_GAMEID, self.roomId, self.tableId, fishTypes, wpId, gainChip, fpMultiple)
        self._dealCatchEvent(event)

    def _dealCatchEvent(self, event):
        """处理捕获事件"""
        if event.tableId == self.tableId:
            usersData = self._usersData.get(event.userId, {})
            if not usersData:
                ftlog.debug("_dealCatchEvent->invalid userId", event.userId)
                return
            fishTypes = event.fishTypes
            targets = usersData["targets"]
            target1 = targets.get("target1", 0)
            multipleTarget1 = 14000 + target1 % 11000
            target2 = targets.get("target2", 0)
            multipleTarget2 = 14000 + target2 % 11000
            if (target1 in fishTypes or multipleTarget1 in fishTypes) and target1 not in usersData["results"]:
                usersData["results"][target1] = 0
            if (target2 in fishTypes or multipleTarget2 in fishTypes) and target2 not in usersData["results"]:
                usersData["results"][target2] = 0
            if target1 in fishTypes or multipleTarget1 in fishTypes:
                score = fishTypes.count(target1) + fishTypes.count(multipleTarget1)
                usersData["results"][target1] += score
            if target2 in fishTypes or multipleTarget2 in fishTypes:
                score = fishTypes.count(target2) + fishTypes.count(multipleTarget2)
                usersData["results"][target2] += score
            self._updateMatchTask(event.userId)
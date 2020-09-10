#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/9/8

import math
import time
from datetime import datetime

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.biz import bireport
from poker.entity.dao import userdata, gamedata, sessiondata
from poker.protocol import router
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import daobase
from hall.entity import hallvip, datachangenotify
from hall.servers.util.rpc import user_remote
from newfish.entity.honor import honor_system
from newfish.room.timematchctrl.interface import SigninRecordDao, \
    SigninRecord, MatchStatusDao, MatchStatus
from newfish.entity import util, config, mail_system, vip_system
from newfish.entity.config import FISH_GAMEID
from newfish.entity.match_record import MatchRecord
from newfish.servers.util.rpc import match_remote
from newfish.room.timematchctrl.const import MatchFinishReason, \
    WaitReason, GroupingType
from newfish.room.timematchctrl.exceptions import \
    BadStateException, SigninFeeNotEnoughException
from newfish.room.timematchctrl.interface import SignerInfoLoader, \
    TableController, MatchStage, MatchFactory, PlayerNotifier, MatchRewards, \
    MatchUserIF, SigninFee
from newfish.room.timematchctrl.models import Player, Table, \
    PlayerSort, PlayerQueuing, Signer
from newfish.room.timematchctrl.utils import Logger
from newfish.entity.msg import GameMsg
from newfish.entity.redis_keys import GameData


class SigninRecordDaoRedis(SigninRecordDao):
    """报名记录操作redis"""
    def __init__(self, gameId):
        self._gameId = gameId
        self._logger = Logger()

    def buildKey(self, matchId, ctrlRoomId, instId):
        return "msignin4:%s:%s:%s" % (self._gameId, ctrlRoomId, instId)

    @classmethod
    def decodeRecord(cls, userId, jstr):
        d = strutil.loads(jstr)
        record = SigninRecord(userId)
        record.signinTime = d["st"]
        fee = d.get("fee")
        if fee:
            record.fee = TYContentItem.decodeFromDict(fee)
        return record

    @classmethod
    def encodeRecord(cls, record):
        d = {"st": record.signinTime}
        if record.fee:
            d["fee"] = record.fee.toDict()
        return strutil.dumps(d)

    def loadAll(self, matchId, instId, ctrlRoomId):
        ret = []
        key = self.buildKey(matchId, instId, ctrlRoomId)
        datas = daobase.executeMixCmd("hgetall", key)
        if datas:
            i = 0
            while (i + 1 < len(datas)):
                try:
                    userId = int(datas[i])
                    record = self.decodeRecord(userId, datas[i+1])
                    ret.append(record)
                except:
                    self._logger.error("SigninRecordDaoRedis.loadAll",
                                       "matchId=", matchId,
                                       "instId=", instId,
                                       "ctrlRoomId=", ctrlRoomId,
                                       "Bad SigninRecord data: [%s, %s]" % (datas[i], datas[i+1]))
                i += 2
        return ret
    
    def add(self, matchId, ctrlRoomId, instId, record):
        key = self.buildKey(matchId, ctrlRoomId, instId)
        if self._logger.isDebug():
            self._logger.debug("SigninRecordDaoRedis.add",
                               "matchId=", matchId,
                               "ctrlRoomId=", ctrlRoomId,
                               "instId=", instId,
                               "key=", key,
                               "record=", self.encodeRecord(record),
                               "userId=", record.userId)
        return daobase.executeMixCmd("hsetnx", key, record.userId, self.encodeRecord(record)) == 1
    
    def remove(self, matchId, ctrlRoomId, instId, userId):
        key = self.buildKey(matchId, ctrlRoomId, instId)
        if self._logger.isDebug():
            self._logger.debug("SigninRecordDaoRedis.remove",
                               "matchId=", matchId,
                               "ctrlRoomId=", ctrlRoomId,
                               "instId=", instId,
                               "userId=", userId,
                               "key=", key)
        daobase.executeMixCmd("hdel", key, userId)
    
    def removeAll(self, matchId, ctrlRoomId, instId):
        key = self.buildKey(matchId, ctrlRoomId, instId)
        if self._logger.isDebug():
            self._logger.debug("SigninRecordDaoRedis.removeAll",
                               "matchId=", matchId,
                               "ctrlRoomId=", ctrlRoomId,
                               "instId=", instId,
                               "key=", key)
        daobase.executeMixCmd("del", key)


class MatchStatusDaoRedis(MatchStatusDao):
    """比赛状态的操作redis"""
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add("roomId", self._room.roomId)

    def load(self, matchId):
        """
        加载比赛信息
        @return: MatchStatus
        """
        key = "mstatus:%s" % (self._room.gameId)
        jstr = daobase.executeMixCmd("hget", key, matchId)
        if jstr:
            d = strutil.loads(jstr)
            return MatchStatus(matchId, d["seq"], d["startTime"], d.get("skills"), d.get("targets"))
        return None

    def save(self, status):
        """
        保存比赛信息
        """
        try:
            key = "mstatus:%s" % (self._room.gameId)
            d = {"seq": status.sequence, "startTime": status.startTime, "skills": status.skills}
            jstr = strutil.dumps(d)
            daobase.executeMixCmd("hset", key, status.matchId, jstr)
        except:
            self._logger.error("MatchStatusDaoRedis.save",
                               "matchId=", status.matchId,
                               "instId=", status.instId,
                               "startTime=", status.startTime,
                               "skills=", status.skills)

    def getNextMatchingSequence(self, matchId):
        """
        下场比赛的轮次ID
        """
        key = "matchingId:%s" % (self._room.gameId)
        self._logger.hinfo("MatchStatusDaoRedis.getNextMatchingSequence",
                           "matchId=", matchId,
                           "key=", key)
        return daobase.executeMixCmd("hincrby", key, matchId, 1)


class MatchRankDaoRedis(object):
    """比赛排行信息"""
    def __init__(self, master):
        self._master = master
        self.key = "mrank:%s:%s:%s" % (self._master.gameId, self._master.roomId, self._master.matchId)
        self.saveTimestamp = 0
        self._logger = Logger()
        self._logger.add("cls", self.__class__.__name__)
        self._logger.add("roomId", self._master.roomId)
        self._logger.add("matchId", self._master.matchId)
        self._logger.add("key", self.key)

    def load(self, startTime):
        """
        加载排名信息
        """
        try:
            self._master.rankList = []
            self._master.playerMap.clear()
            if daobase.executeMixCmd("HEXISTS", self.key, startTime):
                jstr = daobase.executeMixCmd("hget", self.key, startTime)
                if jstr:
                    rankData = strutil.loads(jstr)
                    for item in rankData:
                        player = TimePointPlayer(item["userId"])
                        player.score = item["score"]
                        player.rank = item["rank"]
                        player.userName = str(item["name"])
                        # player.fee = item["fee"]
                        player.signinTime = item["signinTime"]
                        player.luckyValue = item["luckyValue"]
                        player.playCount = item["playCount"]
                        player.averageRank = item["averageRank"]
                        player.instId = item["instId"]
                        player.clientId = item["clientId"]
                        self._master.rankList.append(player)
                        self._master.playerMap[player.userId] = player
                        self._master.userPlayedTimes[player.userId] = item["playedTimes"]
                        if player.userId > config.ROBOT_MAX_USER_ID:
                            self._master.realPlayerSet.add(player.userId)
                    if len(self._master.playerMap) > 0:
                        self._master.updateRankTime = pktimestamp.getCurrentTimestamp()
                    self._logger.debug("load", "startTime=", startTime, "rankSize=", len(rankData))
                else:
                    self._logger.debug("load, data empty !", "startTime=", startTime)
            else:
                self._logger.debug("load, key not exist !", "startTime=", startTime)
        except:
            self._logger.error("load", "startTime=", startTime)

    def save(self, startTime):
        """
        保存排名信息
        """
        timestamp = pktimestamp.getCurrentTimestamp()
        if timestamp - self.saveTimestamp < 60 or len(self._master.rankList) == 0:
            return
        self.saveTimestamp = timestamp
        try:
            rankData = []
            for player in self._master.rankList:
                playerDict = {}
                playerDict["userId"] = player.userId
                playerDict["rank"] = player.rank
                playerDict["score"] = player.score
                # playerDict["fee"] = player.fee
                playerDict["name"] = player.userName
                playerDict["signinTime"] = player.signinTime
                playerDict["luckyValue"] = player.luckyValue
                playerDict["playCount"] = player.playCount
                playerDict["averageRank"] = player.averageRank
                playerDict["instId"] = player.instId
                playerDict["clientId"] = player.clientId
                playerDict["playedTimes"] = self._master.userPlayedTimes.get(player.userId, 1)
                rankData.append(playerDict)
            jstr = strutil.dumps(rankData)
            daobase.executeMixCmd("hset", self.key, startTime, jstr)
            self._logger.debug("save", "startTime=", startTime, "rankSize=", len(rankData))
        except:
            self._logger.error("save", "startTime=", startTime)

    def remove(self, startTime):
        """
        移除排名信息
        """
        daobase.executeMixCmd("hdel", self.key, startTime)
        self._logger.debug("remove", "startTime=", startTime)


class SigninFeeTime(SigninFee):
    """报名费"""
    def __init__(self, room):
        self._room = room
        self._logger = Logger()

    def collectFee(self, matchId, roomId, instId, userId, fee):
        """
        收取用户报名费
        """
        if userId <= config.ROBOT_MAX_USER_ID:
            return

        contentItemList = [{"itemId": fee.assetKindId, "count": fee.count}]
        assetKindId, count = user_remote.consumeAssets(self._room.gameId, userId, contentItemList,
                                                       "MATCH_SIGNIN_FEE", self._room.roomId)

        self._logger.info("SigninFeeTime.collectFee matchId=", matchId,
                          "roomId=", roomId,
                          "instId=", instId,
                          "userId=", userId,
                          "fee=", fee.toDict(),
                          "assetKindId=", assetKindId,
                          "count=", count)
        if assetKindId:
            raise SigninFeeNotEnoughException(fee)
        return fee

    def returnFee(self, matchId, roomId, instId, userId, fee):
        """
        退还报名费
        """
        try:
            if userId <= config.ROBOT_MAX_USER_ID:
                return
            contentItemList = [{"itemId": fee.assetKindId, "count": fee.count}]
            user_remote.addAssets(self._room.gameId, userId, contentItemList, "MATCH_RETURN_FEE", self._room.roomId)
            self._logger.info("SigninFeeTime.returnFee matchId=", matchId,
                              "roomId=", roomId,
                              "instId=", instId,
                              "userId=", userId,
                              "fee=", fee.toDict())
        except:
            self._logger.error()


def cmpPlayers(p1, p2):
    # 分数多的排名靠前
    ret = cmp(p1.score, p2.score)
    if ret != 0:
        return -ret
    return cmp(p1.signinTime, p2.signinTime)


class TimePlayer(Player):
    def __init__(self, userId):
        super(TimePlayer, self).__init__(userId)
        self._clientVersion = 0
        self.score = 0
        self.waitReason = WaitReason.UNKNOWN
        self.matchAdditions = []  # 比赛加成数据  0---加成前值 1--vip加成值 2--炮等级加成值


class TimePointPlayer(TimePlayer):
    def __init__(self, userId):
        super(TimePointPlayer, self).__init__(userId)


class SignerInfoLoaderTime(SignerInfoLoader):
    """报名信息"""
    def __init__(self):
        self._logger = Logger()

    def fillSigner(self, signer):
        """
        """
        try:
            userName = util.getNickname(signer.userId)
            sessionClientId = userdata.getAttr(signer.userId, "sessionClientId")
            signer.userName = strutil.ensureString(userName)
            signer.clientId = strutil.ensureString(sessionClientId)
        except:
            self._logger.error("SignerInfoLoaderTime.fillSigner")
        return signer


class TableControllerTime(TableController):

    def __init__(self, area):
        self.area = area
        self._logger = Logger()
        self._logger.add("cls=", self.__class__.__name__)

    @classmethod
    def buildTableInfoMessage(cls, table, msg):
        """构建桌子信息"""
        seats = []
        group = table.group
        for seat in table.seats:
            if seat.player:
                seatInfo = {}
                seatInfo["userId"] = seat.player.userId
                seatInfo["seatId"] = seat.player.seatId
                seatInfo["clientId"] = seat.player.clientId
                seats.append(seatInfo)
        msg.setParam("seats", seats)
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", group.area.matchId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("bullet", group.matchConf.bullet)
        msg.setParam("playerCount", group.startPlayerCount)
        msg.setParam("realPlayerCount", group.realPlayerCount)
        msg.setParam("tableRankRatio", table.tableRankRatio)
        targets = group.area.findTargets(group.instId)
        skills = group.area.master.skills
        msg.setParam("targets", targets if targets else {})
        msg.setParam("skills", skills if skills else [])
        return msg

    @classmethod
    def buildPlayerRankMessage(cls, table, msg):
        """构建玩家排行榜信息"""
        seats = []
        group = table.group
        stage = table.group.stage
        for seat in table.seats:
            if seat.player:
                seatInfo = {}
                seatInfo["userId"] = seat.player.userId
                seatInfo["seatId"] = seat.player.seatId
                seatInfo["rank"] = seat.player.rank
                seats.append(seatInfo)
        msg.setParam("seats", seats)
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", group.area.matchId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        return msg

    @classmethod
    def buildTableStartMessage(cls, table):
        """桌子开始的信息"""
        msg = MsgPack()
        msg.setCmd("table_manage")
        msg.setParam("action", "m_table_start")
        return cls.buildTableInfoMessage(table, msg)

    @classmethod
    def buildUpdateMessage(cls, table):
        """更新排行榜信息"""
        msg = MsgPack()
        msg.setCmd("table_manage")
        msg.setParam("action", "m_table_update")
        return cls.buildPlayerRankMessage(table, msg)

    @classmethod
    def buildTableClearMessage(cls, table):
        """清理桌子信息"""
        msg = MsgPack()
        msg.setCmd("table_manage")
        msg.setParam("action", "m_table_clear")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.group.matchId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        return msg

    def startTable(self, table):
        """
        让桌子开始
        """
        try:
            self._logger.info("startTable",
                              "groupId=", table.group.groupId,
                              "tableId=", table.tableId,
                              "userIds=", table.getUserIdList())
            # 发送tableStart
            message = self.buildTableStartMessage(table)
            router.sendTableServer(message, table.roomId)
        except:
            self._logger.error("startTable",
                               "groupId=", table.group.groupId,
                               "tableId=", table.tableId,
                               "userIds=", table.getUserIdList())

    def update(self, table):
        """
        更新桌子内用户排名
        """
        if table is None:
            self._logger.error("update, None table !")
            return

        try:
            self._logger.info("update",
                              "groupId=", table.group.groupId,
                              "tableId=", table.tableId,
                              "userIds=", table.getUserIdList())
            # 发送tableStart
            message = self.buildUpdateMessage(table)
            router.sendTableServer(message, table.roomId)
        except:
            self._logger.error("update",
                               "groupId=", table.group.groupId,
                               "tableId=", table.tableId,
                               "userIds=", table.getUserIdList())


    def clearTable(self, table):
        """
        清理桌子
        """
        # 发送tableClear
        try:
            tableClearMessage = self.buildTableClearMessage(table)
            router.sendTableServer(tableClearMessage, table.roomId)
        except:
            self._logger.error("clearTable",
                               "groupId=", table.group.groupId,
                               "tableId=", table.tableId,
                               "userIds=", table.getUserIdList())

    def userGiveup(self, table, seat):
        """
        用户放弃比赛
        """
        try:
            msg = MsgPack()
            msg.setCmd("table_manage")
            msg.setParam("action", "m_user_giveup")
            msg.setParam("gameId", table.gameId)
            msg.setParam("matchId", table.group.matchId)
            msg.setParam("roomId", table.roomId)
            msg.setParam("tableId", table.tableId)
            msg.setParam("userId", seat.player.userId)
            msg.setParam("seatId", seat.seatId)
            router.sendTableServer(msg, table.roomId)
        except:
            self._logger.error("userGiveup",
                               "groupId=", table.group.groupId,
                               "tableId=", table.tableId,
                               "userId=", seat.player.userId if seat.player else 0,
                               "userIds=", table.getUserIdList())


class TableControllerTimePoint(TableControllerTime):
    """限时回馈赛"""
    def __init__(self, area):
        super(TableControllerTimePoint, self).__init__(area)

    @classmethod
    def buildTableInfoMessage(cls, table, msg):
        """获取桌子信息"""
        seats = []
        group = table.group
        for seat in table.seats:
            if seat.player:
                seatInfo = {}
                seatInfo["userId"] = seat.player.userId
                seatInfo["seatId"] = seat.player.seatId
                seatInfo["clientId"] = seat.player.clientId
                seats.append(seatInfo)

        msg.setParam("seats", seats)
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", group.area.matchId)
        msg.setParam("roomId", table.roomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("bullet", group.matchConf.bullet)
        msg.setParam("playerCount", group.startPlayerCount)
        msg.setParam("realPlayerCount", group.realPlayerCount)
        msg.setParam("tableRankRatio", table.tableRankRatio)
        targets = group.area.findTargets(group.instId)
        msg.setParam("targets", targets if targets else {})
        msg.setParam("surpassTargets", group.stage.masterSurpassTargets)
        msg.setParam("bestScore", group.stage.playerBestScore)
        msg.setParam("totalPlayerCount", group.stage.masterRankSize())
        msg.setParam("skills", group.area.master.skills)
        return msg


class MatchRewardsTime(MatchRewards):
    """比赛奖励"""
    def __init__(self, room):
        self._room = room
        self._logger = Logger()
        self._logger.add("cls=", self.__class__.__name__)
        self._logger.add("roomId", self._room.roomId)

    def sendRewards(self, player, rankRewards):
        """给用户发送奖励"""
        try:
            self._logger.info("sendRewards",
                              "userId=", player.userId,
                              "groupId=", player.group.groupId if player.group else None,
                              "score=", player.score,
                              "rank=", player.rank,
                              "rankRewards=", rankRewards.rewards)
            user_remote.addAssets(self._room.gameId, player.userId, rankRewards.rewards,
                                  "MATCH_REWARD", 0, self._room.bigRoomId, self._room.roomId,
                                  int(player.group.instId), player.rank)
            honor_system.sendMatchRewardMail(player.userId, self._room.bigRoomId, player.rank)
            from newfish.game import TGFish
            from newfish.entity.event import MatchRewardEvent
            event = MatchRewardEvent(player.userId, FISH_GAMEID, self._room.bigRoomId,
                                     player.rank, util.convertToFishItems(rankRewards.rewards))
            TGFish.getEventBus().publishEvent(event)
            if rankRewards.message:
                lang = util.getLanguage(player.userId)
                message = strutil.replaceParams(rankRewards.message, {
                    "rank": player.rank,
                    "rewardContent": rankRewards.desc,
                    "matchName": config.getMultiLangTextConf(self._room.roomConf.get("name", ""), lang=lang)
                })
                GameMsg.sendPrivate(self._room.gameId, player.userId, 0, message)
        except:
            self._logger.error("sendRewards",
                               "userId=", player.userId,
                               "groupId=", player.group.groupId if player.group else None,
                               "score=", player.score,
                               "rank=", player.rank,
                               "rankRewards=", rankRewards.rewards)


class MatchRewardsTimePoint(MatchRewardsTime):
    """限时回馈赛奖励"""
    def __init__(self, room):
        super(MatchRewardsTimePoint, self).__init__(room)

    def sendRewards(self, player, rankRewards):
        """给用户发送奖励"""
        try:
            self._logger.info("sendRewards",
                              "userId=", player.userId,
                              "groupId=", player.group.groupId if player.group else None,
                              "score=", player.score,
                              "rank=", player.rank,
                              "rankRewards=", rankRewards.rewards)

            if rankRewards.message:
                lang = util.getLanguage(player.userId)
                string = config.getMultiLangTextConf(rankRewards.message, lang=lang)
                matchName = config.getMultiLangTextConf(self._room.roomConf.get("name", ""), lang=lang)
                message = strutil.replaceParams(string, {"rank": player.rank, "score": player.score, "matchName": matchName})
                GameMsg.sendPrivate(self._room.gameId, player.userId, 0, message)
                rewardsList = util.convertToFishItems(rankRewards.rewards)
                mail_system.sendSystemMail(player.userId, mail_system.MailRewardType.MatchReward, rewardsList, message)

            # honor_system.sendMatchRewardMail(player.userId, self._room.bigRoomId, player.rank)
            bireport.reportGameEvent("BI_NFISH_GE_MATCH_REWARDS", player.userId, self._room.gameId,
                                     self._room.bigRoomId, int(player.instId), player.rank, player.luckyValue,
                                     player.score, player.playCount, [], sessiondata.getClientId(player.userId))
            from newfish.game import TGFish
            from newfish.entity.event import MatchRewardEvent
            event = MatchRewardEvent(player.userId, FISH_GAMEID, self._room.bigRoomId,
                                     player.rank, util.convertToFishItems(rankRewards.rewards))
            TGFish.getEventBus().publishEvent(event)
        except:
            self._logger.error("sendRewards",
                               "userId=", player.userId,
                               "groupId=", player.group.groupId if player.group else None,
                               "score=", player.score,
                               "rank=", player.rank,
                               "rankRewards=", rankRewards.rewards)


class MatchUserIFTime(MatchUserIF):
    """比赛玩家"""
    def __init__(self, room, tableId, seatId):
        self._room = room
        self._tableId = tableId
        self._seatId = seatId
        self._logger = Logger()

    def createUser(self, matchId, ctrlRoomId, instId, userId, fee):
        contentItem = {"itemId": fee.assetKindId, "count": fee.count} if fee else None
        return match_remote.createMatchUser(self._room.gameId, userId, contentItem, self._room.bigRoomId, instId, ctrlRoomId)

    def removeUser(self, matchId, ctrlRoomId, instId, userId):
        match_remote.removeMatchUser(self._room.gameId, userId, self._room.bigRoomId, instId, ctrlRoomId)

    def lockUser(self, matchId, ctrlRoomId, instId, userId, clientId):
        """
        锁定用户
        """
        return match_remote.lockMatchUser(self._room.gameId, userId, self._room.bigRoomId, instId, ctrlRoomId,
                                          self._tableId, self._seatId, clientId)

    def unlockUser(self, matchId, ctrlRoomId, instId, userId):
        """
        解锁用户并删除数据
        """
        match_remote.unlockMatchUser(self._room.gameId, userId, self._room.bigRoomId, instId, ctrlRoomId,
                                     self._tableId, self._seatId)


def getMatchName(room, player):
    lang = util.getLanguage(player.userId)
    roomName = config.getMultiLangTextConf(room.roomConf["name"], lang=lang)
    if player.group.isGrouping:
        return "%s%s" % (roomName, player.group.groupName)
    return roomName


def buildLoserInfo(room, player):
    return "比赛：%s\n名次：第%d名\n胜败乃兵家常事 大侠请重新来过！" % (getMatchName(room, player), player.rank)


def buildWinInfo(room, player, rankRewards):
    if rankRewards:
        return "比赛：%s\n名次：第%d名\n奖励：%s\n奖励已发放，请您查收。" % (getMatchName(room, player), player.rank, rankRewards.desc)
    return "比赛：%s\n名次：第%d名\n。" % (getMatchName(room, player), player.rank)


class PlayerNotifierTime(PlayerNotifier):
    def __init__(self, room):
        self._room = room
        self._rankListCache = []
        self._logger = Logger()
        self._logger.add("cls=", self.__class__.__name__)

    def notifyMatchCancelled(self, signer, reason, message=None):
        """
        通知用户比赛由于reason取消了
        """
        try:
            msg = MsgPack()
            msg.setCmd("m_over")
            msg.setResult("gameId", self._room.gameId)
            msg.setResult("roomId", self._room.roomId)
            msg.setResult("reason", reason)
            msg.setResult("info", message or MatchFinishReason.toString(signer.userId, reason))
            router.sendToUser(msg, signer.userId)
        except:
            self._logger.error("notifyMatchCancelled",
                               "userId=", signer.userId,
                               "instId=", signer.instId,
                               "reason=", reason,
                               "message=", message)

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        try:
            if (reason == MatchFinishReason.USER_WIN or reason == MatchFinishReason.USER_LOSER):
                try:
                    self.calculateMatchLuckyValue(player)
                    match_remote.publishMatchWinloseEvent(player.userId,
                                                          self._room.gameId,
                                                          self._room.match.matchId,
                                                          1 if player.group.isGrouping else 0,
                                                          reason == MatchFinishReason.USER_WIN,
                                                          player.rank,
                                                          player.group.startPlayerCount,
                                                          rankRewards.conf if rankRewards else None,
                                                          player.luckyValue)
                except:
                    self._logger.error("notifyMatchOver",
                                       "userId=", player.userId,
                                       "matchId=", self._room.match.matchId,
                                       "groupId=", player.group.groupId,
                                       "reason=", reason,
                                       "rank=", player.rank,
                                       "rankRewards=", rankRewards.rewards)

            msg = MsgPack()
            msg.setCmd("m_over")
            msg.setResult("gameId", self._room.gameId)
            msg.setResult("roomId", self._room.roomId)
            msg.setResult("userId", player.userId)
            msg.setResult("reason", reason)
            msg.setResult("rank", [player.rank, player.group.totalPlayerCount])
            if player.beatDownUserName:
                msg.setResult("beatDownUser", player.beatDownUserName)  # 击败了谁(昵称)，拼接富文本使用

            if rankRewards or reason == MatchFinishReason.USER_WIN:
                msg.setResult("info", buildWinInfo(self._room, player, rankRewards))  # 前端实现是用来提取其奖励信息，用于显示在奖状上
            else:
                msg.setResult("info", buildLoserInfo(self._room, player))

            msg.setResult("date", str(datetime.now().date().today()))  # //奖状界面日期+时间
            msg.setResult("time", time.strftime("%H:%M", time.localtime(time.time())))  # //奖状界面日期+时间
            msg.setResult("mname", getMatchName(self._room, player))  # 比赛名称
            msg.setResult("mranks", self.getMatchRank(player.userId))
            router.sendToUser(msg, player.userId)

            sequence = int(player.group.instId)
            self.report_bi_game_event("MATCH_FINISH", player.userId, player.group.matchId, 0,
                                      sequence, player.score, player.luckyValue, player.rank, [], "match_end")

            if self._logger.isDebug():
                self._logger.debug("notifyMatchOver", "msg=", msg)
            # record = MatchRecord.loadRecord(self._room.gameId, player.userId, self._room.match.matchId)
            # if record:
            #     msg.setResult("mrecord", {"bestRank": record.bestRank,
            #                               "bestRankDate":record.bestRankDate,
            #                               "isGroup":record.isGroup,
            #                               "crownCount":record.crownCount,
            #                               "playCount":record.playCount
            #                               })
            # else:
            #     msg.setResult("mrecord", {"bestRank": player.rank,
            #                               "bestRankDate":int(time.time()),
            #                               "isGroup":1 if player.group.isGrouping else 0,
            #                               "crownCount":1 if player.rank == 1 else 0,
            #                               "playCount":1
            #                               })
        except:
            self._logger.error("notifyMatchOver",
                               "userId=", player.userId,
                               "groupId=", player.group.groupId,
                               "reason=", reason,
                               "rankRewards=", rankRewards.rewards if rankRewards else None)

    def notifyMatchGiveupFailed(self, player, message):
        """
        通知用户不能放弃比赛
        """
        try:
            msg = MsgPack()
            msg.setCmd("room")
            msg.setError(-1, message)
            router.sendToUser(msg, player.userId)
        except:
            self._logger.error("notifyMatchGiveupFailed",
                               "userId=", player.userId,
                               "groupId=", player.group.groupId,
                               "message=", message)

    def notifyMatchUpdate(self, player):
        """
        通知比赛更新
        """
        pass
        # from newfish.room.timematchctrl.match import TimeMatch
        # try:
        #     msg = MsgPack()
        #     msg.setCmd("m_update")
        #     msg.setResult("_debug_user_%d_" % (1), player.userId)
        #     TimeMatch.getMatchStates(self._room, player.userId, msg)
        #     router.sendToUser(msg, player.userId)
        # except:
        #     self._logger.error("PlayerNotifierTime.notifyMatchUpdate",
        #                        "userId=", player.userId,
        #                        "groupId=", player.group.groupId)

    def getMatchRank(self, userId):
        """
        比赛排行榜
        """
        # from newfish.room.timematchctrl.match import TimeMatch
        mranks = []
        score = 0
        rank = 0
        rewards = []
        matchAdd = []
        ownPlayer = [player for player in self._room.matchMaster.rankList if player.userId == userId]
        if ownPlayer:
            player = ownPlayer[0]
            score = player.score
            rank = player.rank
            rankRewards = self._room._getRewards(player.rank)
            matchAdd = player.matchAdditions
            if rankRewards:
                rewards = self._room.matchPlugin.buildRewards(rankRewards)

        name = util.getNickname(userId)
        avatar = userdata.getAttr(userId, "purl")
        mranks.append({"userId": userId,
                      "name": name,
                      "score": score,
                      "rank": rank,
                      "avatar": avatar,
                      "vip": hallvip.userVipSystem.getVipInfo(userId).get("level", 0),
                      "rewards": rewards,
                      "matchAdd": matchAdd})
        if not self._rankListCache:
            for player in self._room.matchMaster.rankList[:50]:
                name = util.getNickname(player.userId)
                avatar = userdata.getAttr(player.userId, "purl")
                rankRewards = self._room._getRewards(player.rank)
                rewards = []
                if rankRewards:
                    rewards = self._room.matchPlugin.buildRewards(rankRewards)
                self._rankListCache.append({"userId": player.userId,
                                                       "name": name,
                                                       "score": player.score,
                                                       "rank": player.rank,
                                                       "avatar": avatar,
                                                       "vip": hallvip.userVipSystem.getVipInfo(player.userId).get("level", 0),
                                                       "rewards": rewards})
        mranks.extend(self._rankListCache)
        return mranks

    def calculateMatchLuckyValue(self, player):
        """
        计算比赛幸运值
        """
        c = max(player.group.realPlayerCount, 1)
        k = 4000 / (0.9 * c - 1)
        b = -0.5 * (0.9 * c + 1) * k
        value = k * player.rank + b
        changeLuckyValue = max(value, -2000)
        changeLuckyValue = min(changeLuckyValue, 2000)
        player.luckyValue += changeLuckyValue
        player.luckyValue = int(player.luckyValue)
        player.luckyValue = max(player.luckyValue, 0)
        player.luckyValue = min(player.luckyValue, 10000)
        self._logger.debug("calculateMatchLuckyValue->", player.userId, changeLuckyValue, player.luckyValue)


    def notifyMatchWait(self, player, step=None):
        """
        通知用户等待
        """
        pass
        # self.notifyMatchRank(player)
        # self.notifyMatchUpdate(player)
        # msg = MsgPack()
        # msg.setCmd("m_wait")
        # msg.setResult("gameId", self._room.gameId)
        # msg.setResult("roomId", self._room.bigRoomId)
        # msg.setResult("playMode", self._room.roomConf["playMode"])
        # msg.setResult("tableId", player.group.area.tableId)
        # msg.setResult("mname", self._room.roomConf["name"])
        # steps = []
        # for i, stageConf in enumerate(player.group.matchConf.stages):
        #     isCurrent = True if i == player.group.stageIndex else False
        #     if stageConf.groupingType != GroupingType.TYPE_NO_GROUP:
        #         des = "每组%s人晋级" % (stageConf.riseUserCount)
        #     else:
        #         des = "%s人晋级" % (stageConf.riseUserCount)
        #     stepInfo = {"des": des}
        #     if isCurrent:
        #         stepInfo["isCurrent"] = 1
        #     stepInfo["name"] = stageConf.name
        #     steps.append(stepInfo)
        # msg.setResult("steps", steps)
        # router.sendToUser(msg, player.userId)

    def notifyMatchStart(self, instId, signers):
        """
        通知用户比赛开始
        """
        try:
            self._logger.info("notifyMatchStart",
                              "instId=", instId,
                              "userCount=", len(signers))
            self._rankListCache = []
            mstart = MsgPack()
            mstart.setCmd("m_start")
            mstart.setResult("gameId", self._room.gameId)
            mstart.setResult("roomId", self._room.roomId)

            userIds = [p.userId for p in signers]
            self._logger.info("notifyMatchStart begin send tcp m_start",
                              "instId=", instId,
                              "userCount=", len(signers))
            if userIds:
                router.sendToUsers(mstart, userIds)
                self._logger.info("notifyMatchStart end send tcp m_start",
                                  "instId=", instId,
                                  "userCount=", len(signers))
                sequence = int(instId)
                FTLoopTimer(3, 0, self.notifyMatchStartDelayReport_, signers, self._room.bigRoomId, sequence, 0).start()
                self._logger.info("notifyMatchStart begin send bi report async",
                                  "instId=", instId,
                                  "userCount=", len(signers))
        except:
            self._logger.error("notifyMatchStart",
                               "instId=", instId,
                               "userCount=", len(signers))

    def notifyStageStart(self, player):
        """
        通知用户正在配桌
        """
        pass


    def notifyMatchStartDelayReport_(self, signers, roomId, sequence, index):
        self._logger.info("notifyMatchStartDelayReport_",
                          "index=", index,
                          "total=", len(signers))
        nindex = self.notifyMatchStartDelayReport(signers, roomId, sequence, index)
        if nindex < 0:
            self._logger.info("notifyMatchStartDelayReport_ end")
        else:
            FTLoopTimer(0.1, 0, self.notifyMatchStartDelayReport_, signers, self._room.roomId, sequence, nindex).start()


    def notifyMatchStartDelayReport(self, signers, roomId, sequence, index):
        ulen = len(signers)
        blockc = 0
        while index < ulen:
            signer = signers[index]
            self.report_bi_game_event("MATCH_START", signer.userId, roomId, 0,
                                      sequence, 0, signer.luckyValue, 0, [], "match_start")
            index += 1
            blockc += 1
            if blockc > 10:
                return index
        return -1


    def report_bi_game_event(self, eventId, userId, roomId, tableId, roundId, detalChip, state1, state2, cardlist, tag=""):
        try:
            clientId = sessiondata.getClientId(userId)
            bireport.reportGameEvent(eventId, userId, FISH_GAMEID, roomId, tableId, roundId, detalChip, state1, state2, cardlist, clientId)
            if eventId == "MATCH_START":
                util.sendToHall51MatchOverEvent(userId, roomId)
            self._logger.debug("report_bi_game_event tag=", tag,
                               "eventId=", eventId,
                               "userId=", userId,
                               "gameId=", FISH_GAMEID,
                               "roomId=", roomId,
                               "tableId=", tableId,
                               "roundId=", roundId,
                               "detalChip=", detalChip,
                               "state1=", state1,
                               "state2=", state2,
                               "cardlist=", cardlist)
        except:
            self._logger.error("report_bi_game_event error tag=", tag,
                               "eventId=", eventId,
                               "userId=", userId,
                               "gameId=", FISH_GAMEID,
                               "roomId=", roomId,
                               "tableId=", tableId,
                               "roundId=", roundId,
                               "detalChip=", detalChip,
                               "state1=", state1,
                               "state2=", state2,
                               "cardlist=", cardlist)


class PlayerNotifierTimePoint(PlayerNotifierTime):
    def __init__(self, room):
        super(PlayerNotifierTimePoint, self).__init__(room)

    def notifyMatchOver(self, player, reason, rankRewards):
        """
        通知用户比赛结束了
        """
        try:
            msg = MsgPack()
            msg.setCmd("m_over")
            msg.setResult("gameId", self._room.gameId)
            msg.setResult("roomId", self._room.roomId)
            msg.setResult("userId", player.userId)
            msg.setResult("reason", reason)
            msg.setResult("rank", [player.rank, player.group.stage.masterRankSize()])
            # if player.beatDownUserName:
            #     msg.setResult("beatDownUser", player.beatDownUserName)  # 击败了谁(昵称)，拼接富文本使用
            #
            # # if rankRewards or reason == MatchFinishReason.USER_WIN:
            #     msg.setResult("info", buildWinInfo(self._room, player, rankRewards))  # 前端实现是用来提取其奖励信息，用于显示在奖状上
            # else:
            #     msg.setResult("info", buildLoserInfo(self._room, player))
            msg.setResult("date", str(datetime.now().date().today()))  # //奖状界面日期+时间
            msg.setResult("time", time.strftime("%H:%M", time.localtime(time.time())))  # //奖状界面日期+时间
            msg.setResult("mname", getMatchName(self._room, player))  # 比赛名称
            msg.setResult("mranks", self.getMatchRank(player.userId, player.group.stage.masterRankList))
            router.sendToUser(msg, player.userId)

            sequence = int(player.group.instId)
            self.report_bi_game_event("MATCH_FINISH", player.userId, player.group.matchId, 0,
                                      sequence, player.score, player.luckyValue, player.rank, [], "match_end")
            if self._logger.isDebug():
                self._logger.debug("notifyMatchOver", "msg=", msg, "rankSize=", len(player.group.stage.masterRankList))
        except:
            self._logger.error("notifyMatchOver",
                               "userId=", player.userId,
                               "groupId=", player.group.groupId,
                               "reason=", reason,
                               "rankRewards=", rankRewards.rewards if rankRewards else None)

    def getMatchRank(self, userId, rankList=None):
        """
        比赛排行榜
        """
        if rankList is None:
            rankList = self._room.matchMaster.rankList

        mranks = []
        # score = 0
        # rank = 0
        # rewards = []
        # matchAdd = []
        # ownPlayer = [player for player in rankList if player.userId == userId]
        # if ownPlayer:
        #     player = ownPlayer[0]
        #     score = player.score
        #     rank = player.rank
        #     matchAdd = player.matchAdditions
        #     rewards = self._room.getRankBuildRewards(rank)
        #
        # name, _, avatar = self._room.getUserInfo(userId)
        # mranks.append({"userId": userId,
        #               "name": name,
        #               "score": score,
        #               "rank": rank,
        #               "avatar": avatar,
        #               "vip": hallvip.userVipSystem.getVipInfo(userId).get("level", 0),
        #               "rewards": rewards,
        #               "matchAdd": matchAdd})
        #
        # for player in rankList[:50]:
        #     name, _, avatar = self._room.getUserInfo(player.userId)
        #     rewards = self._room.getRankBuildRewards(player.rank)
        #     mranks.append({"userId": player.userId,
        #                    "name": name,
        #                    "score": player.score,
        #                    "rank": player.rank,
        #                    "avatar": avatar,
        #                    "vip": hallvip.userVipSystem.getVipInfo(player.userId).get("level", 0),
        #                    "rewards": rewards})
        for i, player in enumerate(rankList):
            score = player.score
            rank = player.rank
            if i < 50:
                name, _, avatar = self._room.getUserInfo(player.userId)
                rewards = self._room.getRankBuildRewards(rank)
                mranks.append({"userId": player.userId,
                               "name": name,
                               "score": score,
                               "rank": rank,
                               "avatar": avatar,
                               "vip": hallvip.userVipSystem.getVipInfo(player.userId).get("level", 0),
                               "rewards": rewards})
            if player.userId == userId:
                matchAdd = player.matchAdditions
                name, _, avatar = self._room.getUserInfo(userId)
                rewards = self._room.getRankBuildRewards(rank)
                ownerData = {"userId": player.userId,
                               "name": name,
                               "score": score,
                               "rank": rank,
                               "avatar": avatar,
                               "vip": hallvip.userVipSystem.getVipInfo(userId).get("level", 0),
                               "rewards": rewards,
                               "matchAdd": matchAdd}
                if len(mranks) == 0:
                    mranks.append(ownerData)
                else:
                    mranks.insert(0, ownerData)
        return mranks


class TimeStage(MatchStage):
    """比赛阶段"""
    def __init__(self, stageConf, group):
        super(TimeStage, self).__init__(stageConf, group)
        # value=list<Player>
        self._giveupPlayerList = []
        self._winlosePlayerList = []
        # 等待开局的玩家
        self._waitPlayerList = []
        # 所有桌子排名比例
        self._allTableRankRatioList = []
        # 正在使用的桌子
        self._busyTableSet = set()
        # 空闲的桌子
        self._idleTableList = []
        # 所有桌子
        self._allTableSet = set()
        # 完成比赛的玩家
        self._finishPlayerSet = set()

        # 最后一次检查超时桌子的时间
        self._lastCheckTimeoutTableTime = None
        self._hasTimeoutTable = False
        self._processWaitPlayerCount = 0
        # 总排行榜，按照player.si从大到小排序
        self._rankList = []

    @property
    def matchId(self):
        return self.group.matchId

    @property
    def roomId(self):
        return self.area.roomId

    @property
    def instId(self):
        return self.group.instId

    @property
    def playerCount(self):
        return self.group.playerCount

    @property
    def isGrouping(self):
        return self.group.isGrouping

    @property
    def rankList(self):
        return self._rankList

    def calcUncompleteTableCount(self, player):
        busyTableCount = len(self._busyTableSet)
        waitUserCount = len(self._waitPlayerList)
        ret = int(busyTableCount + waitUserCount / self.matchConf.tableSeatCount)
        if self._logger.isDebug():
            self._logger.debug("calcUncompleteTableCount",
                               "userId=", player.userId,
                               "busyTableCount=", busyTableCount,
                               "waitUserCount=", waitUserCount,
                               "ret=", ret)
        return ret

    def calcTotalRemTimes(self, timestamp):
        return 100

    @property
    def isLastStage(self):
        return self.stageIndex + 1 >= len(self.matchConf.stages)

    def _sortMatchRanks(self):
        self._rankList.sort(cmp=cmpPlayers)
        for i, player in enumerate(self._rankList):
            player.rank = i + 1

    def update(self, table):
        self._sortMatchRanks()
        assert table
        self.area.tableController.update(table)

    def giveup(self, player):
        table = player.table
        if table:
            self.area.tableController.userGiveup(table, player.seat)
            table.standup(player)
            if table.idleSeatCount == table.seatCount:
                self._releaseTable(table)
        self._addGiveupPlayer(player)
        self.group.totalPlayerCount -= 1
        return True

    def winlose(self, player, score):
        assert (player.group == self.group)
        table = player.table

        if self.group.state != 1:
            self._logger.error("winlose fail",
                               "groupState=", self.group.state,
                               "userId=", player.userId,
                               "tableId=", table.tableId if table else None,
                               "score=", score,
                               "busyTableCount=", len(self._busyTableSet))
            raise BadStateException()
        player._state = Player.ST_WINLOSE
        player.score = score
        self.updateMatchOverScore(player)
        self._sortMatchRanks()
        assert (player.table)

        self._logger.info("winlose ok",
                          "groupState=", self.group.state,
                          "userId=", player.userId,
                          "tableId=", table.tableId if table else None,
                          "seatId=", player.seat.seatId if player.seat else None,
                          "score=", score,
                          "rank=", player.rank,
                          "rankListCount=", len(self._rankList),
                          "busyTableCount=", len(self._busyTableSet))

        # 添加到winlose列表
        self._addWinlosePlayer(player)
        if table.getPlayingPlayerCount() <= 0:
            # 让该桌子上的用户站起并释放桌子
            self._clearAndReleaseTable(table)

    def start(self):
        self._rankList = sorted(self.group._playerMap.values(), cmp=PlayerSort.cmpBySigninTime)
        self._logger.info("start ...",
                          "groupState=", self.group.state,
                          "playerCount=", self.playerCount,
                          "idleTableCount=", self.area.tableManager.idleTableCount)

        if self.playerCount < self.matchConf.start.userMinCount:
            # 人数不足
            self._logger.info("start fail",
                              "groupState=", self.group.state,
                              "userCount=", self.playerCount,
                              "err=", "NotEnoughUser")
            return False, MatchFinishReason.USER_NOT_ENOUGH

        needTableCount = self.calcNeedTableCount()
        if self.area.tableManager.idleTableCount < needTableCount:
            # 桌子资源不足
            self._logger.error("start fail",
                               "groupState=", self.group.state,
                               "playerCount=", self.playerCount,
                               "idleTableCount=", self.area.tableManager.idleTableCount,
                               "err=", "NotEnoughTable")
            return False, MatchFinishReason.RESOURCE_NOT_ENOUGH

        timestamp = pktimestamp.getCurrentTimestamp()

        # 借桌子
        self._idleTableList = self.area.tableManager.borrowTables(needTableCount)
        self._allTableSet = set(self._idleTableList)

        # 初始化用户数据
        if self.stageIndex == 0:
            self._sortMatchRanks()
        self._initPlayerDatas()
        self._initWaitPlayerList()

        self._lastCheckTimeoutTableTime = timestamp + self.matchConf.start.tableTimes

        for player in self._waitPlayerList:
            self.area.playerNotifier.notifyStageStart(player)

        self._logger.info("start ok",
                          "groupState=", self.group.state,
                          "playerCount=", self.playerCount,
                          "idleTableCount=", self.area.tableManager.idleTableCount)
        return True, None

    def kill(self, reason):
        self.finish(reason)

    def finish(self, reason):
        self._logger.info("finish ...",
                          "groupState=", self.group.state,
                          "busyTableCount=", len(self._busyTableSet),
                          "winlosePlayersCount=", len(self._winlosePlayerList),
                          "reason=", reason)

        rankList = self._rankList[:]
        if reason == MatchFinishReason.FINISH:
            riseUserCount = min(self.stageConf.riseUserCount, len(self._rankList))
            if len(self._busyTableSet) > 0:
                self._logger.error("finish issue",
                                   "groupState=", self.group.state,
                                   "busyTableCount=", len(self._busyTableSet),
                                   "winlosePlayersCount=", len(self._winlosePlayerList),
                                   "reason=", reason,
                                   "err=", "HaveBusyTable")

            if len(self._winlosePlayerList) != 0:
                self._logger.error("finish issue",
                                   "groupState=", self.group.state,
                                   "busyTableCount=", len(self._busyTableSet),
                                   "winlosePlayersCount=", len(self._winlosePlayerList),
                                   "reason=", reason,
                                   "err=", "HaveWinlosePlayer")

            while len(self._rankList) > riseUserCount:
                self._outPlayer(self._rankList[-1], MatchFinishReason.USER_LOSER)

            if self.stageIndex + 1 >= len(self.matchConf.stages):
                # 最后一个阶段, 给晋级的人发奖
                while self._rankList:
                    self._outPlayer(self._rankList[-1], MatchFinishReason.USER_WIN)
        else:
            # 释放所有桌子
            for table in self._busyTableSet:
                self._clearTable(table)
            self._busyTableSet.clear()

            while self._rankList:
                self._outPlayer(self._rankList[-1], reason)

        if reason == MatchFinishReason.FINISH:
            self._sendRewards(rankList)
        elif reason in [MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH]:
            self._unlockUsers(rankList)

        self._releaseResource()

        self._logger.info("_doFinish ok",
                          "groupState=", self.group.state,
                          "reason=", reason)

    def isStageFinished(self):
        return len(self._finishPlayerSet) >= len(self._rankList)

    def processStage(self):
        if self._logger.isDebug():
            self._logger.debug("processStage",
                               "groupState=", self.group.state)

        self._lastActiveTime = pktimestamp.getCurrentTimestamp()

        self._processTimeoutTables()
        self._processGiveupPlayers()
        self._processWinlosePlayers()
        self._processWaitPlayers()
        self._reclaimTables()

        if len(self._waitPlayerList) >= self.matchConf.tableSeatCount:
            return 0.08
        return 1

    def calcNeedTableCount(self):
        return (self.playerCount + self.matchConf.tableSeatCount - 1) / self.matchConf.tableSeatCount

    def _sendRewards(self, rankList):
        for player in rankList:
            rankRewards = self._getRewards(player)
            if rankRewards and player.userId > config.ROBOT_MAX_USER_ID:
                self.area.matchRewards.sendRewards(player, rankRewards)
            self.area.matchUserIF.unlockUser(self.matchId, self.roomId, self.instId, player.userId)

    def _unlockUsers(self, rankList):
        for player in rankList:
            self.area.matchUserIF.unlockUser(self.matchId, self.roomId, self.instId, player.userId)

    def _outPlayer(self, player, reason=MatchFinishReason.USER_LOSER):
        if self._logger.isDebug():
            self._logger.debug("_outPlayer",
                               "userId=", player.userId,
                               "reason=", reason)
        player._state = Player.ST_OVER
        try:
            assert (player.userId)
            # 玩家完成比赛
            self._doPlayerMatchOver(player, reason)
            # 删除player
            if self.group.findPlayer(player.userId):
                self.group.removePlayer(player)
            # 删除排名
            if player in self._rankList:
                self._rankList.remove(player)
            # 删除已完成的用户
            if player in self._finishPlayerSet:
                self._finishPlayerSet.discard(player)
        except:
            self._logger.error("_outPlayer",
                               "userId=", player.userId,
                               "rank=", player.rank,
                               "reason=", reason)

    def _doPlayerMatchOver(self, player, reason):
        # 解锁玩家
        rankRewards = None

        if (reason == MatchFinishReason.USER_WIN
            or reason == MatchFinishReason.USER_LOSER):
            rankRewards = self._getRewards(player)
            if rankRewards:
                reason = MatchFinishReason.USER_WIN
            self.area.playerNotifier.notifyMatchOver(player, reason, rankRewards)
        else:
            self.area.playerNotifier.notifyMatchCancelled(player, reason)
        self._logger.info("UserMatchOver",
                          "matchId=", self.matchId,
                          "instId=", self.instId,
                          "stageIndex=", self.stageIndex,
                          "userId=", player.userId,
                          "score=", player.score,
                          "rank=", player.rank,
                          "reason=", reason,
                          "remUserCount=", len(self._rankList),
                          "rankRewards=", rankRewards.rewards if rankRewards else None)

    def _getRewards(self, player):
        # 看当前阶段是否有配置奖励
        rankRewardsList = self.stageConf.rankRewardsList if self.isGrouping else self.matchConf.rankRewardsList
        if self._logger.isDebug():
            self._logger.debug("_getRewards",
                               "userId=", player.userId,
                               "rank=", player.rank,
                               "rankRewardsList=", rankRewardsList,
                               "stageConf.rankRewards=", self.stageConf.rankRewardsList)
        if rankRewardsList:
            for rankRewards in rankRewardsList:
                if ((rankRewards.startRank == -1 or player.rank >= rankRewards.startRank)
                   and (rankRewards.endRank == -1 or player.rank <= rankRewards.endRank)):
                    return rankRewards
        return None

    def _initWaitPlayerList(self):
        # 排序
        self._waitPlayerList = []
        waitPlayers = PlayerQueuing.sort(self.stageConf.seatQueuing, self._rankList)

        tempPlayers = []
        allTableRankList = []
        for index in xrange(0, len(waitPlayers), self.matchConf.tableSeatCount):
            players = waitPlayers[index:index + self.matchConf.tableSeatCount]
            tableRank = sum([p.averageRank for p in players]) / len(players)
            allTableRankList.append([index, tableRank])
            for player in players:
                self._addWaitPlayer(player)
                temp = [player.userId, player.luckyValue, player.playCount, player.averageRank]
                tempPlayers.append(temp)
        newAllTableRankList = sorted(allTableRankList, key=lambda x: x[1])
        for _, tableRank in enumerate(allTableRankList):
            tableRankRatio = round((newAllTableRankList.index(tableRank) + 1.0) / len(allTableRankList), 2)
            self._allTableRankRatioList.append(tableRankRatio)

        if self._logger.isDebug():
            self._logger.debug("_initWaitPlayerList",
                               "groupState=", self.group.state,
                               "userIds=", [p.userId for p in self._rankList],
                               "_allTableRankRatioList=", self._allTableRankRatioList)
        # byeCount = len(waitPlayers) % self.matchConf.tableSeatCount
        # for i in xrange(byeCount):
        #     self._waitPlayerList[-1 - i].waitReason = WaitReason.BYE

    def _initPlayerDatas(self):
        for i, player in enumerate(self._rankList):
            player.waitTimes = 0
            player.score = 0
            player.rank = i + 1
            if self._logger.isDebug():
                self._logger.debug("_initPlayerDatas",
                                   "state=", self.group.state,
                                   "userId=", player.userId,
                                   "score=", player.score)

    def _addGiveupPlayer(self, player):
        self._giveupPlayerList.append(player)

    def _addWinlosePlayer(self, player):
        self._winlosePlayerList.append(player)

    def _addWaitPlayer(self, player):
        player._state = Player.ST_WAIT
        player.waitReason = WaitReason.WAIT
        self._waitPlayerList.append(player)

    def _finishPlayer(self, player):
        player._state = Player.ST_WAIT
        player.waitReason = WaitReason.RISE
        self._finishPlayerSet.add(player)
        self._logger.info("_playerFinishCount",
                          "userId=", player.userId,
                          "totalFinishUserCount=", len(self._finishPlayerSet))

    def _borrowTable(self):
        # 借用桌子
        assert (len(self._idleTableList) > 0)
        table = self._idleTableList.pop(0)
        self._busyTableSet.add(table)
        self._logger.info("_borrowTable",
                          "tableId=", table.tableId,
                          "idleTableCount=", len(self._idleTableList))
        return table

    def _releaseTable(self, table):
        # 释放桌子
        assert (table.idleSeatCount == table.seatCount)
        self._logger.info("_releaseTable",
                          "tableId=", table.tableId)
        table._group = None
        table._playTime = None
        table._tableRankRatio = 0
        self._busyTableSet.remove(table)
        self._idleTableList.append(table)

    def _clearTable(self, table):
        if self._logger.isDebug():
            self._logger.debug("_clearTable",
                               "tableId=", table.tableId)
        players = []
        self.area.tableController.clearTable(table)
        for seat in table.seats:
            if seat.player:
                players.append(seat.player)
                if self._logger.isDebug():
                    self._logger.debug("_clearTable standup",
                                       "tableId=", table.tableId,
                                       "seatId=", seat.seatId,
                                       "userId=", seat.player.userId)
                table.standup(seat.player)

        for player in players:
            try:
                self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, player.userId, player.clientId)
            except:
                self._logger.error("_clearTable lockUserFail",
                                   "tableId=", table.tableId,
                                   "userId=", player.userId)

    def _clearAndReleaseTable(self, table):
        if self._logger.isDebug():
            self._logger.debug("_clearAndReleaseTable",
                               "tableId=", table.tableId)
        players = []
        self.area.tableController.clearTable(table)
        for seat in table.seats:
            if seat.player:
                players.append(seat.player)
                if self._logger.isDebug():
                    self._logger.debug("_clearAndReleaseTable standup",
                                       "tableId=", table.tableId,
                                       "seatId=", seat.seatId,
                                       "userId=", seat.player.userId)
                table.standup(seat.player)

        self._releaseTable(table)

        for player in players:
            try:
                self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, player.userId, player.clientId)
            except:
                self._logger.error("_clearAndReleaseTable lockUserFail",
                                   "tableId=", table.tableId,
                                   "userId=", player.userId)

    def _releaseResource(self):
        self._finishPlayerSet.clear()
        self._winlosePlayerList = []
        for table in self._busyTableSet:
            self._clearTable(table)
        self._busyTableSet.clear()
        self._idleTableList = []
        self.area.tableManager.returnTables(self._allTableSet)
        self._allTableSet.clear()

    def _reclaimTables(self):
        needCount = self.calcNeedTableCount()
        reclaimCount = len(self._allTableSet) - needCount
        if self._logger.isDebug():
            self._logger.debug("_reclaimTables",
                               "needCount=", needCount,
                               "reclaimCount=", reclaimCount,
                               "allCount=", len(self._allTableSet),
                               "tableManager.idleCount=", self.area.tableManager.idleTableCount)

        if reclaimCount > 0:
            count = min(reclaimCount, len(self._idleTableList))
            tables = self._idleTableList[0:count]
            self._idleTableList = self._idleTableList[count:]
            self.area.tableManager.returnTables(tables)
            for table in tables:
                self._allTableSet.remove(table)
            self._logger.info("_reclaimTables",
                              "needCount=", needCount,
                              "reclaimCount=", reclaimCount,
                              "realReclaimCount=", count,
                              "allCount=", len(self._allTableSet),
                              "tableManager.idleCount=", self.area.tableManager.idleTableCount)

    def _calcMaxProcessPlayerCount(self):
        count = 200
        try:
            maxPlayerPerRoom = self.area.tableManager.getTableCountPerRoom() * self.matchConf.tableSeatCount
            countPerRoom = int((maxPlayerPerRoom / self.matchConf.start.startMatchSpeed + 10) / 10)
            count = min(200, self.area.tableManager.roomCount * countPerRoom)
            if self._logger.isDebug():
                self._logger.debug("_calcMaxProcessPlayerCount",
                                   "maxPlayerPerRoom=", maxPlayerPerRoom,
                                   "startMatchSpeed=", self.matchConf.start.startMatchSpeed,
                                   "countPerRoom=", countPerRoom,
                                   "count=", count)
        except:
            self._logger.error("TimeStage._calcMaxProcessPlayerCount")
        return count

    def _processTimeoutTables(self):
        if self._logger.isDebug():
            self._logger.debug("_processTimeoutTables",
                               "groupState=", self.group.state,
                               "busyTableCount=", len(self._busyTableSet),
                               "hasTimeoutTable=", self._hasTimeoutTable,
                               "lastCheckTimeoutTableTime=", self._lastCheckTimeoutTableTime)
        timestamp = pktimestamp.getCurrentTimestamp()
        # 每tableTimeoutCheckInterval秒检查一次
        if (self._hasTimeoutTable
            or (timestamp - self._lastCheckTimeoutTableTime >= self.stageConf.tableTimeoutCheckInterval)):
            self._lastCheckTimeoutTableTime = timestamp
            overtimeTables = []
            for table in self._busyTableSet:
                if timestamp - table.playTime >= self.matchConf.start.tableTimes:
                    overtimeTables.append(table)
            processCount = min(len(overtimeTables), 10)
            for table in overtimeTables:
                processCount -= 1
                if not table.playTime:
                    self._logger.warn("_processTimeoutTables notPlayTime",
                                      "groupState=", self.group.state,
                                      "tableId=", table.tableId,
                                      "timestamp=", timestamp)
                else:
                    self._logger.info("_processTimeoutTables tableTimeout",
                                      "groupState=", self.group.state,
                                      "tableId=", table.tableId,
                                      "playTimes=", (timestamp - table.playTime))
                    if timestamp - table.playTime >= self.matchConf.start.tableTimes:
                        playerList = table.getPlayingPlayerList()
                        for player in playerList:
                            self.winlose(player, 0)
                if processCount <= 0:
                    break
            self._hasTimeoutTable = processCount < len(overtimeTables)

    def _processGiveupPlayers(self):
        if self._logger.isDebug():
            self._logger.debug("_processGiveupPlayers",
                               "groupState=", self.group.state,
                               "giveupPlayersCount=", len(self._giveupPlayerList))
        for player in self._giveupPlayerList:
            self._outPlayer(player, MatchFinishReason.GIVEUP)
            self.area.matchUserIF.unlockUser(self.matchId, self.roomId, self.instId, player.userId)
        self._giveupPlayerList = []

    def _processWinlosePlayers(self):
        if self._logger.isDebug():
            self._logger.debug("_processWinlosePlayers",
                               "groupState=", self.group.state,
                               "winlosePlayersCount=", len(self._winlosePlayerList))

        # 等待所有人完成
        if self._winlosePlayerList and len(self._winlosePlayerList) >= len(self._rankList):
            winlosePlayerList = self._winlosePlayerList
            self._winlosePlayerList = []

            for player in winlosePlayerList:
                self._logger.info("_processWinlosePlayers",
                                  "groupState=", self.group.state,
                                  "userId=", player.userId)
                self._finishPlayer(player)

    def _processWaitPlayers(self):
        if self._logger.isDebug():
            self._logger.debug("_processWaitPlayers",
                               "groupState=", self.group.state,
                               "processWaitPlayerCount=", self._processWaitPlayerCount,
                               "startPlayerCount=", self.group.startPlayerCount,
                               "waitUserIds=", [p.userId for p in self._waitPlayerList])

        isAllProcess = self._processWaitPlayerCount >= self.group.startPlayerCount

        # 检查剩余的玩家能不能凑够一桌
        # waitCount = len(self._waitPlayerList)
        # if waitCount < self.matchConf.tableSeatCount:
        #     if (waitCount > 0
        #         and (len(self._finishPlayerSet) + waitCount) >= len(self._rankList)):
        #         # 凑不够一桌，直接结算轮空的用户完成
        #         self._logger.info("TimeStage._processWaitPlayers",
        #                           "groupState=", self.group.state,
        #                           "playerCount=", self.playerCount,
        #                           "waitUserIds=", [p.userId for p in self._waitPlayerList],
        #                           "err=", "UserNotEnough")
        #         waitPlayerList = self._waitPlayerList
        #         self._waitPlayerList = []
        #         for player in waitPlayerList:
        #             player.cardCount += 1
        #             self.winlose(player, 0, True, True)
        #     return

        # 计算本次处理多少玩家
        processCount = max(self._calcMaxProcessPlayerCount(), self.matchConf.tableSeatCount)
        processCount = min(processCount - processCount % self.matchConf.tableSeatCount, len(self._waitPlayerList))
        processTableCount = int(math.ceil(float(processCount) / self.matchConf.tableSeatCount))
        processTableRankRatioList = self._allTableRankRatioList[0:processTableCount]
        self._allTableRankRatioList = self._allTableRankRatioList[processTableCount:]
        processPlayerList = self._waitPlayerList[0:processCount]
        self._waitPlayerList = self._waitPlayerList[processCount:]

        processedCount = 0
        if self._logger.isDebug():
            self._logger.debug("_processWaitPlayers",
                               "groupState=", self.group.state,
                               "playerCount=", self.playerCount,
                               "processCount=", processCount,
                               "len(_allTableRankRatioList)", len(self._allTableRankRatioList))
        while (processedCount < processCount):
            players = processPlayerList[processedCount:processedCount + self.matchConf.tableSeatCount]
            processedCount += len(players)
            self._startTable(players, processTableRankRatioList.pop(0))
            self._processWaitPlayerCount += len(players)

        if not isAllProcess and self._processWaitPlayerCount >= self.group.startPlayerCount:
            self._logger.info("_processWaitPlayers",
                              "groupState=", self.group.state,
                              "processWaitPlayerCount=", self._processWaitPlayerCount,
                              "startPlayerCount=", self.group.startPlayerCount,
                              "isAllProcessFinish=", True)

    def _startTable(self, players, tableRankRatio):
        # 分配桌子
        table = self._borrowTable()
        assert (table is not None)
        table._group = self.group
        table._playTime = pktimestamp.getCurrentTimestamp()
        table._tableRankRatio = tableRankRatio
        robotCount = len([player for player in players if player.userId <= config.ROBOT_MAX_USER_ID])
        for player in players:
            if robotCount < len(players) and player.userId <= config.ROBOT_MAX_USER_ID:
                FTLoopTimer(self.matchConf.playingTime / 10, 0, self.giveup, player).start()
                continue
            if player.state != Player.ST_WAIT:
                self._logger.error("_processWaitPlayers",
                                   "groupState=", self.group.state,
                                   "userId=", player.userId,
                                   "playerState=", player.state,
                                   "err=", "BadUserState")
                assert (player.state == Player.ST_WAIT)

            player._state = Player.ST_PLAYING
            player.waitReason = WaitReason.UNKNOWN
            if player.seat:
                self._logger.error("_startTable",
                                   "groupState=", self.group.state,
                                   "userId=", player.userId,
                                   "seatLoc=", player.seat.location,
                                   "err=", "SeatNotEmpty")
                assert (player.seat is None)
            table.sitdown(player)
            assert (player.seat)

            if self._logger.isDebug():
                self._logger.debug("_startTable",
                                   "groupState=", self.group.state,
                                   "userId=", player.userId,
                                   "sitdown=", player.seat.location)

        self.area.tableController.startTable(table)
        self._logger.info("_startTable",
                          "groupState=", self.group.state,
                          "tableId=", table.tableId,
                          "userIds=", table.getUserIdList(),
                          "processWaitPlayerCount=", self._processWaitPlayerCount,
                          "startPlayerCount=", self.group.startPlayerCount)

    def updateMatchOverScore(self, player):
        vipLevel = hallvip.userVipSystem.getUserVip(player.userId).vipLevel.level
        gunLevel = gamedata.getGameAttrInt(player.userId, FISH_GAMEID, GameData.gunLevel)
        weapLevel = min(gunLevel, self.area.room.roomConf.get("maxGunLevel"))

        vipPrecent = vip_system.getMatchVipAddition(player.userId, vipLevel)
        vipAddition = int(player.score * vipPrecent)

        weaponPrecent = config.getWeaponConf(weapLevel).get("matchAddition", 0)
        weapAddition = int(weaponPrecent * player.score)
        player.matchAdditions = [player.score, vipPrecent, weaponPrecent]
        ftlog.debug("matchOver_addition==", player.matchAdditions, gunLevel, self.area.room.roomConf.get("maxGunLevel"), weapLevel)
        player.score = player.score + vipAddition + weapAddition


class TimeMatchFactory(MatchFactory):
    def newStage(self, stageConf, group):
        """
        创建阶段
        """
        return TimeStage(stageConf, group)

    def newSigner(self, userId, instId, matchId):
        return Signer(userId, instId, matchId)

    def newPlayer(self, signer):
        """
        创建一个Player
        """
        player = TimePlayer(signer.userId)
        player.instId = signer.instId
        player.userName = signer.userName
        player.fee = signer.fee
        player.signinTime = signer.signinTime
        player.clientId = signer.clientId
        player.luckyValue = signer.luckyValue
        player.playCount = signer.playCount
        player.averageRank = signer.averageRank
        return player


class TimePointStage(TimeStage):
    def __init__(self, stageConf, group):
        super(TimePointStage, self).__init__(stageConf, group)
        self._masterRankList = []
        self._masterPlayerMap = {}
        self.masterSurpassTargets = []
        self.playerBestScore = {}

    def _releaseResource(self):
        super(TimePointStage, self)._releaseResource()
        self._masterRankList = []
        self._masterPlayerMap.clear()
        self.masterSurpassTargets = []
        self.playerBestScore.clear()

    @property
    def masterRankList(self):
        return self._masterRankList

    def masterRankSize(self):
        return len(self._masterPlayerMap)

    def start(self):
        """
        玩家游戏时锁榜，游戏中此榜不更新
        """
        ok, reason = super(TimePointStage, self).start()
        for k, v in self.group.area.master.playerMap.iteritems():
            player = TimePointPlayer(v.userId)
            player.score = v.score
            player.rank = v.rank
            player.instId = v.instId
            player.userName = v.userName
            player.fee = v.fee
            player.signinTime = v.signinTime
            player.clientId = v.clientId
            player.luckyValue = v.luckyValue
            player.playCount = v.playCount
            player.averageRank = v.averageRank
            self._masterPlayerMap[k] = player

        for player in self._rankList:
            self.playerBestScore[player.userId] = 0
            if self._masterPlayerMap.get(player.userId):
                self.playerBestScore[player.userId] = self._masterPlayerMap[player.userId].score
            self._masterPlayerMap[player.userId] = player
        self._masterRankList = self._masterPlayerMap.values()
        self._sortMatchRanks()
        surpassTarget = config.getSurpassTargetConf()
        self.masterSurpassTargets = []
        for rank in surpassTarget:
            idx = rank - 1
            if 0 <= idx < len(self._masterRankList):
                player = self._masterRankList[idx]
                name, _, avatar = self.group.area.room.getUserInfo(player.userId)
                self.masterSurpassTargets.append({"userId": player.userId,
                                                  "name": name,
                                                  "score": player.score,
                                                  "rank": player.rank,
                                                  "avatar": avatar})
        self._logger.debug("start", "surpassTargetsCount=", len(self.masterSurpassTargets))
        return ok, reason

    def _sortMatchRanks(self):
        """
        更新玩家在锁定的总榜中的排名
        """
        self._masterRankList.sort(cmp=cmpPlayers)
        for i, player in enumerate(self._masterRankList):
            player.rank = i + 1

    def giveup(self, player):
        table = player.table
        if table:
            self.area.tableController.userGiveup(table, player.seat)
            table.standup(player)
            if table.idleSeatCount == table.seatCount:
                self._releaseTable(table)
        self._addGiveupPlayer(player)
        self.group.totalPlayerCount -= 1
        return True

    def finish(self, reason):
        self._logger.info("finish ...",
                          "groupState=", self.group.state,
                          "busyTableCount=", len(self._busyTableSet),
                          "winlosePlayersCount=", len(self._winlosePlayerList),
                          "reason=", reason)

        rankList = self._rankList[:]
        if reason == MatchFinishReason.FINISH:
            riseUserCount = min(self.stageConf.riseUserCount, len(self._rankList))
            if len(self._busyTableSet) > 0:
                self._logger.error("finish issue",
                                   "groupState=", self.group.state,
                                   "busyTableCount=", len(self._busyTableSet),
                                   "winlosePlayersCount=", len(self._winlosePlayerList),
                                   "reason=", reason,
                                   "err=", "HaveBusyTable")

            if len(self._winlosePlayerList) != 0:
                self._logger.error("finish issue",
                                   "groupState=", self.group.state,
                                   "busyTableCount=", len(self._busyTableSet),
                                   "winlosePlayersCount=", len(self._winlosePlayerList),
                                   "reason=", reason,
                                   "err=", "HaveWinlosePlayer")

            while len(self._rankList) > riseUserCount:
                self._outPlayer(self._rankList[-1], MatchFinishReason.USER_LOSER)

            if self.stageIndex + 1 >= len(self.matchConf.stages):
                # 最后一个阶段, 给晋级的人发奖
                while self._rankList:
                    self._outPlayer(self._rankList[-1], MatchFinishReason.USER_WIN)
        else:
            # 释放所有桌子
            for table in self._busyTableSet:
                self._clearTable(table)
            self._busyTableSet.clear()

            while self._rankList:
                self._outPlayer(self._rankList[-1], reason)

        if reason == MatchFinishReason.FINISH:
            # self._sendRewards(rankList)
            self._unlockUsers(rankList)
        elif reason in [MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH]:
            self._unlockUsers(rankList)

        self._releaseResource()

        self._logger.info("_doFinish ok",
                          "groupState=", self.group.state,
                          "reason=", reason)

    def _outPlayer(self, player, reason=MatchFinishReason.USER_LOSER):
        if self._logger.isDebug():
            self._logger.debug("_outPlayer",
                               "userId=", player.userId,
                               "reason=", reason)
        player._state = Player.ST_OVER
        try:
            assert (player.userId)
            # 玩家完成比赛
            self._doPlayerMatchOver(player, reason)
            # 删除player
            if self.group.findPlayer(player.userId):
                self.group.removePlayer(player)
            # 删除排名
            if player in self._rankList:
                self._rankList.remove(player)
            # 删除已完成的用户
            if player in self._finishPlayerSet:
                self._finishPlayerSet.discard(player)

            self.area.master.userPlayedTimes.setdefault(player.userId, 0)
            self.area.master.userPlayedTimes[player.userId] += 1
        except:
            self._logger.error("_outPlayer",
                               "userId=", player.userId,
                               "rank=", player.rank,
                               "reason=", reason)

    def _doPlayerMatchOver(self, player, reason):
        # 解锁玩家
        rankRewards = None

        if (reason == MatchFinishReason.USER_WIN
                or reason == MatchFinishReason.USER_LOSER
                or reason == MatchFinishReason.GIVEUP):
            rankRewards = self._getRewards(player)
            if rankRewards and reason != MatchFinishReason.GIVEUP:
                reason = MatchFinishReason.USER_WIN
            self.area.playerNotifier.notifyMatchOver(player, reason, rankRewards)
        else:
            self.area.playerNotifier.notifyMatchCancelled(player, reason)
        self._logger.info("UserMatchOver",
                          "matchId=", self.matchId,
                          "instId=", self.instId,
                          "stageIndex=", self.stageIndex,
                          "userId=", player.userId,
                          "score=", player.score,
                          "rank=", player.rank,
                          "reason=", reason,
                          "remUserCount=", len(self._rankList),
                          "rankRewards=", rankRewards.rewards if rankRewards else None)

    def _addGiveupPlayer(self, player):
        """
        提前离开游戏的玩家也算作完成的玩家，成绩有效
        """
        self._giveupPlayerList.append(player)
        self._finishPlayerSet.add(player)


class TimePointMatchFactory(MatchFactory):
    """
    定时积分赛工厂类，用于创建此比赛相关的stage和player
    """
    def newStage(self, stageConf, group):
        """
        创建阶段
        """
        return TimePointStage(stageConf, group)

    def newSigner(self, userId, instId, matchId):
        return Signer(userId, instId, matchId)

    def newPlayer(self, signer):
        """
        创建一个Player
        """
        player = TimePointPlayer(signer.userId)
        player.instId = signer.instId
        player.userName = signer.userName
        player.fee = signer.fee
        player.signinTime = signer.signinTime
        player.clientId = signer.clientId
        player.luckyValue = signer.luckyValue
        player.playCount = signer.playCount
        player.averageRank = signer.averageRank
        return player

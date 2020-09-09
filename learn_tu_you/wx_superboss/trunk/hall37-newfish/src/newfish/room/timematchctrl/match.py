#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/10
import time
import random
from datetime import datetime

from freetime.core.tasklet import FTTasklet
from freetime.entity.msg import MsgPack
import freetime.util.log as ftlog
from poker.entity.configure import configure, gdata
from poker.entity.dao import gamedata
from poker.entity.biz.content import TYContentItem
from poker.entity.game.rooms import roominfo
from poker.entity.game.rooms.roominfo import MatchRoomInfo
from hall.entity import hallconf, hallitem, hallvip
from newfish.room.timematchctrl.const import WaitReason
from newfish.room.timematchctrl.interfaceimpl import \
    MatchStatusDaoRedis, SigninRecordDaoRedis, MatchRankDaoRedis
from poker.protocol import router, runcmd
from poker.util import strutil
import poker.util.timestamp as pktimestamp
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.servers.util.rpc import user_rpc
from newfish.room.timematchctrl.const import FeeType, \
    MatchFinishReason, GroupingType
from newfish.room.timematchctrl.exceptions import \
    SigninException, SigninConditionNotEnoughException, \
    SigninStoppedException, AlreadySigninException, SigninNotStartException, \
    SigninFullException, BadStateException, MatchStoppedException, \
    AlreadyInMatchException, AlreadySigninOtherException, SigninVersionDisableException
from newfish.room.timematchctrl.interface import SigninRecord, \
    MatchStatus
from newfish.room.timematchctrl.models import Signer, \
    GroupNameGenerator, PlayerGrouping
from newfish.room.timematchctrl.utils import HeartbeatAble, Logger
from newfish.room.timematchctrl.interfaceimpl import TableControllerTime, \
    PlayerNotifierTime, MatchRewardsTime, MatchUserIFTime, \
    SignerInfoLoaderTime, TimeMatchFactory, SigninFeeTime, \
    TableControllerTimePoint, PlayerNotifierTimePoint, MatchRewardsTimePoint, TimePointMatchFactory
from newfish.entity.match_record import MatchRecord
from copy import deepcopy


class MatchInst(HeartbeatAble):
    """比赛实例"""
    ST_IDLE = 0
    ST_SIGNIN = 1
    ST_PREPARE = 2
    ST_STARTING = 3
    ST_STARTED = 4
    ST_FINAL = 5

    def __init__(self, area, instId, startTime, needLoad):
        super(MatchInst, self).__init__(1)
        # 赛区
        self.area = area
        # 实例ID
        self.instId = instId
        # 开赛时间
        self.startTime = startTime
        # 比赛关闭时间
        self.closeTime = self.matchConf.start.calcCloseTime(startTime)
        # 比赛结算时间
        self.rewardTime = self.matchConf.start.calcRewardTime(startTime)
        # 比赛结束时间
        self.endTime = self.matchConf.start.calcEndTime(startTime)
        # 单次随机报名人数
        self.singleSignerNum = 0
        # 所有报名过的玩家
        self.signerRecord = set()
        # 状态
        self._state = MatchInst.ST_IDLE
        # key=userId, value=Signer
        self._signerMap = {}
        # 真实玩家数量
        self._realSignerCount = 0
        # 是否需要加载
        self._needLoad = needLoad

        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("roomId", self.roomId)
        self._logger.add("instId", self.instId)

    @property
    def matchId(self):
        return self.area.matchId

    @property
    def matchConf(self):
        return self.area.matchConf

    @property
    def roomId(self):
        return self.area.roomId

    @property
    def state(self):
        return self._state

    @property
    def needLoad(self):
        return self._needLoad

    @property
    def signerCount(self):
        return len(self._signerMap)

    @property
    def realSignerCount(self):
        return self._realSignerCount

    @property
    def signerMap(self):
        return self._signerMap

    @property
    def master(self):
        return self.area.master

    def findSigner(self, userId):
        return self._signerMap.get(userId)

    def getTotalSignerCount(self):
        return self.signerCount

    def startSignin(self):
        """
        开始报名
        """
        self._heart.postCall(self._doStartSignin)

    def prepare(self):
        """
        准备阶段开始
        """
        self._heart.postCall(self._doPrepare)

    def cancel(self, reason):
        """
        比赛取消
        """
        self._heart.postCall(self._doCancel, reason)

    def start(self):
        """
        比赛开始
        """
        self._heart.postCall(self._doStart)

    def final(self):
        """
        结束
        """
        self._heart.postCall(self._doFinal)

    def _doStartSignin(self):
        if self._state < MatchInst.ST_SIGNIN:
            self._state = MatchInst.ST_SIGNIN
            self._doStartSigninImpl()
        else:
            self._logger.warn("MatchInst._doStartSignin fail",
                              "state=", self._state,
                              "err=", "BadState")

    def _doPrepare(self):
        if self._state < MatchInst.ST_PREPARE:
            self._state = MatchInst.ST_PREPARE
            self._doPrepareImpl()
        else:
            self._logger.warn("MatchInst._doPrepare fail",
                              "state=", self._state,
                              "err=", "BadState")

    def _doCancel(self, reason):
        if self._state < MatchInst.ST_FINAL:
            self._state = MatchInst.ST_FINAL
            self._doCancelImpl(reason)
        else:
            self._logger.warn("MatchInst._doCancel fail",
                              "state=", self._state,
                              "reason=", reason,
                              "err=", "BadState")

    def _doStart(self):
        if self._state < MatchInst.ST_STARTING:
            self._state = MatchInst.ST_STARTING
            self._doStartImpl()
        else:
            self._logger.warn("MatchInst._doStart fail",
                              "state=", self._state,
                              "err=", "BadState")

    def _doFinal(self):
        if self._state < MatchInst.ST_FINAL:
            self._state = MatchInst.ST_FINAL
            self._doFinalImpl()
        else:
            self._logger.warn("MatchInst._doFinal fail",
                              "state=", self._state,
                              "err=", "BadState")

    def _doStartSigninImpl(self):
        pass

    def _doPrepareImpl(self):
        pass

    def _doCancelImpl(self, reason):
        pass

    def _doStartImpl(self):
        pass

    def _doFinalImpl(self):
        pass


class MatchInstLocal(MatchInst):
    """比赛实例本地"""
    def __init__(self, area, instId, startTime, needLoad):
        super(MatchInstLocal, self).__init__(area, instId, startTime, needLoad)
        # 比赛目标鱼
        self.targets = {}

    def addInitSigners(self, signers):
        for signer in signers:
            # 记录
            self.area.signinRecordDao.add(self.matchId, self.roomId, self.instId,
                                          SigninRecord(signer.userId, signer.signinTime, signer.fee))

            # 创建MatchUser
            self.area.matchUserIF.createUser(self.matchId, self.roomId, self.instId, signer.userId, signer.fee)

    def signin(self, userId, feeIndex):
        # 检查参数
        if (self.matchConf.fees and (feeIndex < 0 or feeIndex >= len(self.matchConf.fees))):
            raise SigninException()

        # 检查是否可以报名
        self._ensureCanSignin(userId)
        # 报名费
        timestamp = pktimestamp.getCurrentTimestamp()
        fee = self.matchConf.fees[feeIndex] if self.matchConf.fees else None
        # 报名逻辑
        signer = self._doSignin(userId, fee, timestamp)

        self._logger.hinfo("MatchInstLocal.signin ok",
                           "state=", self._state,
                           "userId=", userId,
                           "signerCount=", self.signerCount,
                           "fee=", signer.fee.toDict() if signer.fee else None)
        return signer

    def signout(self, signer):
        assert (signer.inst == self)

        if self._state != MatchInst.ST_SIGNIN:
            raise SigninStoppedException()

        del self._signerMap[signer.userId]
        if signer.userId > config.ROBOT_MAX_USER_ID:
            self._realSignerCount -= 1

        # 删除SigninRecord
        self.area.signinRecordDao.remove(self.matchId, self.roomId, self.instId, signer.userId)
        # 退费
        if signer.fee:
            self.area.signinFee.returnFee(self.matchId, self.roomId, self.instId, signer.userId, signer.fee)
        # 删除MatchPlayer
        self.area.matchUserIF.removeUser(self.matchId, self.roomId, self.instId, signer.userId)

        self._logger.hinfo("MatchInstLocal.signout ok",
                           "state=", self._state,
                           "userId=", signer.userId,
                           "fee=", signer.fee.toDict() if signer.fee else None,
                           "signerCount=", self.signerCount)

    def enter(self, signer):
        assert (signer.inst == self)
        canEnter = False
        if self.matchConf.start.isTimePointType():
            if self._state == MatchInst.ST_STARTED:
                timestamp = pktimestamp.getCurrentTimestamp()
                if timestamp >= self.closeTime:
                    raise MatchStoppedException()
                else:
                    canEnter = True
                    self._lockSigner(signer)
                    self.area.playerNotifier.notifyMatchStart(self.instId, [signer])
                    self.area.signinRecordDao.remove(self.matchId, self.roomId, self.instId, signer.userId)
                    del self._signerMap[signer.userId]
            else:
                raise BadStateException()
        else:
            canEnter = (self._state == MatchInst.ST_SIGNIN or self._state == MatchInst.ST_PREPARE)

        # if self._state == MatchInst.ST_SIGNIN or self._state == MatchInst.ST_PREPARE:
        if canEnter is True:
            signer.isEnter = True
            self._fillSigner(signer)
            self._logger.info("MatchInstLocal.enter ok",
                              "state=", self._state,
                              "userId=", signer.userId,
                              "userName=", signer.userName,
                              "clientId=", signer.clientId,
                              "signerCount=", self.signerCount)
        else:
            raise AlreadyInMatchException()

    def leave(self, signer):
        assert (signer.inst == self)
        if self._state == MatchInst.ST_SIGNIN or self._state == MatchInst.ST_PREPARE:
            signer.isEnter = False
            signer.isLocked = False
            self._logger.info("MatchInstLocal.leave ok",
                              "state=", self._state,
                              "userId=", signer.userId,
                              "signerCount=", self.signerCount)
        else:
            raise AlreadyInMatchException()

    def buildStatus(self):
        # return MatchInstStatus(self.instId, self._state, self.signerCount)
        pass

    def _doInit(self):
        self._logger.info("MatchInstLocal._doInit ...",
                          "state=", self._state)
        if self._needLoad:
            records = self.area.signinRecordDao.loadAll(self.matchId, self.roomId, self.instId)
            if records:
                for record in records:
                    signer = Signer(record.userId, self.instId, self.matchId)
                    signer.inst = self
                    self._signerMap[signer.userId] = signer
        self._logger.info("MatchInstLocal._doInit ok",
                          "state=", self._state)
        return 1

    def _doStartSigninImpl(self):
        self._logger.info("MatchInstLocal._doStartSigninImpl ...",
                          "state=", self._state)
        self._logger.info("MatchInstLocal._doStartSigninImpl ok",
                          "state=", self._state)

    def _doPrepareImpl(self):
        self._logger.info("MatchInstLocal._doPrepareImpl ...",
                          "state=", self._state)
        startTime = time.time()
        self._prelockSigners(self._signerMap.values()[:])
        self._logger.info("MatchInstLocal._doPrepareImpl ok",
                          "state=", self._state,
                          "signerCount=", self.signerCount,
                          "usedTime=", time.time() - startTime)
        self._logger.info("MatchInstLocal._doPrepareImpl ok",
                          "state=", self._state)

    def _doStartImpl(self):
        self._logger.hinfo("MatchInstLocal._doStartImpl ...",
                           "state=", self._state)

        startTime = time.time()
        self._totalSignerCount = self.signerCount
        self._lockSigners()
        self._logger.hinfo("MatchInstLocal._doStart lockOk",
                           "state=", self._state,
                           "signerCount=", self.signerCount,
                           "usedTime=", time.time() - startTime)

        if not self.matchConf.start.isUserCountType() and not self.matchConf.start.isTimePointType():
            self.area.playerNotifier.notifyMatchStart(self.instId, self._signerMap.values())
        self.area.signinRecordDao.removeAll(self.matchId, self.roomId, self.instId)
        self._state = MatchInst.ST_STARTED

        self.area.onInstStarted(self)

        self._logger.hinfo("MatchInstLocal._doStartImpl ok",
                           "state=", self._state)

    def _doCancelImpl(self, reason):
        self._logger.info("MatchInstLocal._doCancelImpl ...",
                          "state=", self._state,
                          "reason=", reason)
        for signer in self._signerMap.values():
            self._cancelSigner(signer, reason)
        self._signerMap = {}
        self._logger.info("MatchInstLocal._doCancelImpl ok",
                          "state=", self._state,
                          "rerason=", reason)

    def _doFinalImpl(self):
        self._logger.info("MatchInstLocal._doFinalImpl ...",
                          "state=", self._state)
        self._logger.info("MatchInstLocal._doFinalImpl ok",
                          "state=", self._state)

    def _doSignin(self, userId, fee, timestamp):
        signer = None
        try:
            signer = self.area.matchFactory.newSigner(userId, self.instId, self.matchId)
            signer.signinTime = timestamp
            signer.inst = self
            # 收费
            if fee:
                self.area.signinFee.collectFee(self.matchId, self.roomId, self.instId, userId, fee)
                signer.fee = fee

            # 记录
            add = self.area.signinRecordDao.add(self.matchId, self.roomId, self.instId,
                                                SigninRecord(userId, signer.signinTime, fee))

            # 创建MatchUser
            ec = self.area.matchUserIF.createUser(self.matchId, self.roomId, self.instId, userId, fee)

            # 检查是否其它tasklet也报名了
            exists = self.findSigner(userId)
            if exists:
                raise AlreadySigninException()

            # 增加signer
            self._signerMap[userId] = signer
            # 记录真实玩家数
            if userId > config.ROBOT_MAX_USER_ID:
                self._realSignerCount += 1
            self._fillSigner(signer)

            if ec != 0:
                raise AlreadySigninException()

            if not add:
                # 之前已经报过名
                raise AlreadySigninException()
            return signer
        except:
            if signer and signer.fee:
                # 退还报名费
                self.area.signinFee.returnFee(self.matchId, self.roomId, self.instId, userId, signer.fee)
            raise

    def _fillSigner(self, signer):
        self.area.signerInfoLoader.fillSigner(signer)
        if self._logger.isDebug():
            self._logger.debug("MatchInstLocal._fillSigner",
                               "userId=", signer.userId,
                               "userName=", signer.userName,
                               "clientId=", signer.clientId)

    def _prelockSigners(self, signers):
        for signer in signers:
            self._lockSigner(signer)

    def _lockSigner(self, signer):
        if (not signer.isLocked
            and signer.isEnter
            and self.area.matchUserIF.lockUser(self.matchId, self.roomId, self.instId, signer.userId, signer.clientId)):
            if self._logger.isDebug():
                self._logger.debug("MatchInstLocal._lockSigner Ok",
                                   "userId=", signer.userId,
                                   "userName=", signer.userName,
                                   "clientId=", signer.clientId)
            signer.isLocked = True
        return signer.isLocked

    def _unlockSigner(self, signer, returnFee=False):
        if signer.isLocked:
            signer.isLocked = False
        # 退费
        if returnFee and signer.fee:
            self.area.signinFee.returnFee(self.matchId, self.roomId, self.instId, signer.userId, signer.fee)
        # 解锁
        self.area.matchUserIF.unlockUser(self.matchId, self.roomId, self.instId, signer.userId)

    def _lockSigners(self):
        nolocks = []
        for signer in self._signerMap.values():
            if not self._lockSigner(signer):
                nolocks.append(signer)
        for signer in nolocks:
            self._kickoutSigner(signer)
        return nolocks

    def _kickoutSigner(self, signer):
        try:
            returnFees = (self.matchConf.start.feeType == FeeType.TYPE_RETURN or signer.isEnter)
            self._unlockSigner(signer, returnFees)
            del self._signerMap[signer.userId]
            kickoutReason = "not lock" if signer.isEnter else "not enter"
            self._logger.info("MatchInstLocal._kickoutSigner ok",
                              "userId=", signer.userId,
                              "kickoutReason=", kickoutReason)
        except:
            self._logger.error("MatchInstLocal._kickoutSigner ERROR", signer.userId)

    def _cancelSigner(self, signer, reason):
        returnFees = (self.matchConf.start.feeType == FeeType.TYPE_RETURN or signer.isEnter) \
                     and reason in (MatchFinishReason.USER_NOT_ENOUGH, MatchFinishReason.RESOURCE_NOT_ENOUGH)
        self._unlockSigner(signer, returnFees)
        self.area.playerNotifier.notifyMatchCancelled(signer, reason)
        self._logger.info("MatchInstLocal._cancelSigner ok",
                          "userId=", signer.userId,
                          "reason=", reason,
                          "returnFees=", returnFees)

    def _ensureCanSignin(self, userId):
        # 报名还未开始
        if self._state < MatchInst.ST_SIGNIN:
            raise SigninNotStartException()

        # 报名已经截止
        if self.matchConf.start.isTimePointType():
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp < self.startTime or timestamp > self.closeTime:
                raise SigninStoppedException()
        else:
            if self._state >= MatchInst.ST_PREPARE:
                raise SigninStoppedException()

        # 已经报名
        if self.findSigner(userId):
            raise AlreadySigninException()

        # 检查报名人数是否已满
        if (self.matchConf.start.isTimingType()
            and self.signerCount >= self.matchConf.start.signinMaxCountPerMatch):
            raise SigninFullException()

        # 已经报名其他场次
        ctrlRoomId, startTime = util.getFishMatchSigninInfo(userId)
        if ctrlRoomId:
            roomConfig = gdata.getRoomConfigure(ctrlRoomId)
            type = None
            if roomConfig.get("matchConf") and roomConfig["matchConf"].get("start"):
                type = roomConfig["matchConf"]["start"].get("type", None)
            # 可以同时报名多个定时积分赛
            if self.matchConf.start.isTimePointType() and self.matchConf.start.type == type:
                pass
            else:
                raise AlreadySigninOtherException()

    def _doHeartbeat(self):
        return 1


class MatchGroup(HeartbeatAble):
    ST_IDLE = 0
    ST_START = 1
    ST_FINISHING = 2
    ST_FINISH = 3
    ST_FINALING = 4
    ST_FINAL = 5

    def __init__(self, area, instId, matchingId, groupId, groupIndex,
                 groupName, stageIndex, isGrouping, totalPlayerCount, realPlayerCount):
        super(MatchGroup, self).__init__(1)
        self.area = area
        self.instId = instId
        self.matchingId = matchingId
        self.groupId = groupId
        self.groupIndex = groupIndex
        self.groupName = groupName
        self.stageIndex = stageIndex
        self.isGrouping = isGrouping
        self.totalPlayerCount = totalPlayerCount
        self.realPlayerCount = realPlayerCount

        # key=userId, value=Player
        self._playerMap = {}
        self._state = MatchGroup.ST_IDLE

        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("instId", self.instId)
        self._logger.add("groupId", self.groupId)
        self._logger.add("matchingId", self.matchingId)
        self._logger.add("stageIndex", self.stageIndex)

    @property
    def matchId(self):
        return self.area.matchId

    @property
    def matchConf(self):
        return self.area.matchConf

    @property
    def state(self):
        return self._state

    @property
    def playerMap(self):
        return self._playerMap

    @property
    def playerCount(self):
        return len(self._playerMap)

    def getRisePlayers(self):
        return self._playerMap.values()

    def findPlayer(self, userId):
        """
        查找Player
        """
        return self._playerMap.get(userId)

    def removePlayer(self, player):
        assert (player.group == self)
        del self._playerMap[player.userId]

    def addPlayers(self, players):
        """
        给该分组增加一个player，必须在开始之前调用
        """
        if self._state == MatchGroup.ST_IDLE:
            for player in players:
                if self.findPlayer(player.userId):
                    self._logger.warn("MatchGroup._doAddPlayers state=", self._state,
                                      "userId=", player.userId,
                                      "err=", "AlreadyInGroup")
                else:
                    player._group = self
                    self._playerMap[player.userId] = player
            self._logger.info("MatchGroup._doAddPlayers state=", self._state,
                              "playerCount=", len(players))
        else:
            self._logger.error("MatchGroup.addPlayers state=", self._state,
                               "playerCount=", len(players))

    def finishGroup(self, reason):
        """
        杀掉该分组
        """
        self._heart.postCall(self._doFinish, reason)

    def finalGroup(self):
        self._heart.postCall(self._doFinal)

    def _doInit(self):
        return 1

    def _doFinish(self, reason):
        if self._state < MatchGroup.ST_FINISHING:
            self._state = MatchGroup.ST_FINISH

            self._doFinishImpl(reason)

            self._logger.hinfo("MatchGroup._doFinish ok",
                               "state=", self._state,
                               "reason=", reason)
        else:
            self._logger.error("MatchGroup._doFinish fail",
                               "state=", self._state,
                               "reason=", reason,
                               "err=", "BadState")

    def _doFinal(self):
        self._logger.info("MatchGroup._doFinal ...",
                          "state=", self._state)
        if self._state == MatchGroup.ST_FINISH:
            self._state = MatchGroup.ST_FINALING
            self.stopHeart()
            try:
                self._doFinalImpl()
                self._logger.info("MatchGroup._doFinal ok",
                                  "state=", self._state)
            except:
                self._logger.error("MatchGroup._doFinal fail",
                                   "state=", self._state)
            self._state = MatchGroup.ST_FINAL
        else:
            self._logger.error("MatchGroup._doFinal fail",
                               "state=", self._state,
                               "err=", "BadState")

    def _doFinishImpl(self, reason):
        raise NotImplementedError

    def _doFinalImpl(self):
        raise NotImplementedError

    def _doHeartbeat(self):
        return 1


class MatchGroupLocal(MatchGroup):
    """
    一个比赛分组
    """

    def __init__(self, area, instId, matchingId, groupId, groupIndex,
                 groupName, stageIndex, isGrouping, totalPlayerCount, realPlayerCount):
        super(MatchGroupLocal, self).__init__(area, instId, matchingId, groupId, groupIndex,
                                              groupName, stageIndex, isGrouping, totalPlayerCount, realPlayerCount)
        # 本组开始时的
        self._startPlayerCount = 0
        # 阶段
        self._stage = None
        # 该分组启动时间
        self._startTime = 0
        # 随后活跃时间
        self._lastActiveTime = 0

    @property
    def stage(self):
        return self._stage

    @property
    def startPlayerCount(self):
        return self._startPlayerCount

    def setStage(self, stage):
        self._stage = stage

    def calcTotalUncompleteTableCount(self, player):
        return self._stage.calcUncompleteTableCount(player)

    def _doInit(self):
        self._logger.info("MatchGroupLocal._doInit ...",
                          "state=", self._state)
        self._state = MatchGroup.ST_START
        self._startTime = pktimestamp.getCurrentTimestamp()
        self._lastActiveTime = self._startTime
        self._startPlayerCount = len(self._playerMap)

        ok, reason = self._stage.start()

        if not ok:
            self._doFinish(reason)

        self._logger.info("MatchGroupLocal._doInit ok",
                          "state=", self._state)
        return 1

    def _doFinishImpl(self, reason):
        self._stage.finish(reason)

    def _doFinalImpl(self):
        self._logger.info("MatchGroupLocal._doFinalImpl ...",
                          "state=", self._state)
        self._logger.info("MatchGroupLocal._doFinalImpl ok",
                          "state=", self._state)

    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug("MatchGroupLocal._doHeartbeat",
                               "state=", self._state)
        ret = 1
        if self._state == MatchGroup.ST_START:
            ret = self._stage.processStage()
        if self._state == MatchGroup.ST_START:
            if self._stage.isStageFinished():
                if self._stage.rankList:
                    if self.matchConf.start.isTimePointType():
                        if self._logger.isDebug():
                            self._logger.debug("MatchGroupLocal._doHeartbeat",
                                               "stage.rankList=", self._stage.rankList)
                        updateRank = False
                        for player in self._stage.rankList:
                            val = self.area.master.playerMap.get(int(player.userId))
                            if val is None or player.score > val.score:
                                updateRank = True
                                self.area.master.playerMap[int(player.userId)] = player
                                if player.userId > config.ROBOT_MAX_USER_ID:
                                    self.area.master.realPlayerSet.add(player.userId)
                        if updateRank:
                            self.area.master.updateRankTime = pktimestamp.getCurrentTimestamp()
                            if self._logger.isDebug():
                                self._logger.debug("match over, need update rank!", "updateTime=",
                                                   self.area.master.updateRankTime, "playerCount=",
                                                   len(self.area.master.playerMap), "rankCount=",
                                                   len(self.area.master.rankList))
                    else:
                        self.area.master.rankList = self._stage.rankList[:]
                        # self.area.master.rankListCache = []
                        # self._sendLed(self.area.master.rankList[0])
                        # self._sendMatchOverEvent(self.area.master.rankList)
                        self.area.master.sendMatchOverAndLed()
                self._doFinish(MatchFinishReason.FINISH)
        if self._state < MatchGroup.ST_FINISH:
            timestamp = pktimestamp.getCurrentTimestamp()
            if timestamp - self._startTime > self.matchConf.start.maxPlayTime:
                self._doFinish(MatchFinishReason.OVERTIME)
        return ret

        # def _sendLed(self, player):
        #     if self.area.master.matchConfig.fishPool == 44104:
        #         return
        #     msg = u"恭喜玩家%s获得“%s”红包赛的冠军，成功赢得%s" % (player.userName, self.area.master.roomName, self.area.master.fristReward)
        #     user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1)
        #
        # def _sendMatchOverEvent(self, rankList):
        #     from newfish.entity.event import MatchOverEvent
        #     from newfish.game import TGFish
        #     for player in rankList:
        #         event = MatchOverEvent(player.userId, FISH_GAMEID, self.area.room.bigRoomId, player.rank)
        #         TGFish.getEventBus().publishEvent(event)
        #         ftlog.info("MatchGroupLocal._sendMatchOverEvent", player.userId, player.rank, player.score, player.userName)


class MatchArea(HeartbeatAble):
    def __init__(self, matchConf, interval):
        super(MatchArea, self).__init__(interval)
        # 比赛配置
        self.matchConf = matchConf
        # 当前赛区运行的分组
        self._groupMap = {}

    @property
    def matchId(self):
        return self.matchConf.matchId

    @property
    def tableId(self):
        return self.matchConf.tableId

    @property
    def groupMap(self):
        return self._groupMap

    def findPlayer(self, userId):
        for group in self._groupMap.values():
            player = group.findPlayer(userId)
            if player:
                return player
        return None

    def isOnline(self):
        """
        赛区是否在线
        """
        return False

    def newInst(self, instId, startTime, needLoad):
        """
        新建一个新的比赛实例
        """
        raise NotImplementedError

    def newGroup(self, instId, matchingId, groupId,
                 groupIndex, groupName, stageIndex, isGrouping,
                 totalPlayerCount, realPlayerCount):
        """
        创建一个新的分组
        """
        raise NotImplementedError

    def findGroup(self, groupId):
        """
        根据groupId查找Group
        """
        raise NotImplementedError


class MatchAreaLocal(MatchArea):
    def __init__(self, master, room, matchConf):
        super(MatchAreaLocal, self).__init__(matchConf, 1)
        # 房间
        self.room = room
        # 主控
        self.master = master
        # 当前分区所有比赛实例 key=instId, value=MatchInst
        self._instMap = {}
        # 当前比赛实例
        self._curInst = None
        # 工厂类
        self.matchFactory = None
        # 所有比赛实例中的目标鱼
        self.targetsMap = {}

        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("roomId", self.room.roomId)

    @property
    def roomId(self):
        return self.room.roomId

    @property
    def gameId(self):
        return self.room.gameId

    @property
    def curInst(self):
        return self._curInst

    @property
    def signerCount(self):
        return self.curInst.signerCount if self.curInst else 0

    def findInst(self, instId):
        return self._instMap.get(instId)

    def findTargets(self, instId):
        return self.targetsMap.get(instId)

    def isOnline(self):
        """
        本地的赛区始终在线
        """
        return True

    def newInst(self, instId, startTime, needLoad):
        """
        创建比赛实例
        """
        self._logger.info("MatchAreaLocal.createInst ...",
                          "instId=", instId,
                          "startTime=", startTime,
                          "needLoad=", needLoad,
                          "curInstId=", self._curInst.instId if self._curInst else None)

        self._curInst = MatchInstLocal(self, instId, startTime, needLoad)
        self._instMap[instId] = self._curInst
        self._curInst.targets = self.master.targets
        self.targetsMap[instId] = self._curInst.targets
        self._logger.info("MatchAreaLocal.createInst ok",
                          "startTime=", startTime,
                          "needLoad=", needLoad,
                          "instId=", instId,
                          "targets=", self._curInst.targets)
        return self._curInst

    def newGroup(self, instId, matchingId, groupId, groupIndex,
                 groupName, stageIndex, isGrouping,
                 totalPlayerCount, realPlayerCount):
        """
        创建分组
        """
        group = self.findGroup(groupId)
        if group:
            self._logger.error("MatchAreaLocal.createGroup fail",
                               "instId=", instId,
                               "matchingId=", matchingId,
                               "groupId=", groupId,
                               "groupIndex=", groupIndex,
                               "groupName=", groupName,
                               "stageIndex=", stageIndex,
                               "isGrouping=", isGrouping,
                               "totalPlayerCount=", totalPlayerCount,
                               "realPlayerCount=", realPlayerCount,
                               "err=", "GroupExists")
            raise BadStateException()

        group = MatchGroupLocal(self, instId, matchingId, groupId, groupIndex,
                                groupName, stageIndex, isGrouping, totalPlayerCount, realPlayerCount)
        stage = self.matchFactory.newStage(self.matchConf.stages[stageIndex], group)
        group.setStage(stage)
        self._groupMap[groupId] = group

        self._logger.info("MatchAreaLocal.createGroup ok",
                          "instId=", instId,
                          "matchingId=", matchingId,
                          "groupId=", groupId,
                          "groupName=", groupName,
                          "stageIndex=", stageIndex,
                          "isGrouping=", isGrouping,
                          "totalPlayerCount=", totalPlayerCount,
                          "realPlayerCount=", realPlayerCount)
        return group

    def findGroup(self, groupId):
        """
        根据groupId查找Group
        """
        return self._groupMap.get(groupId)

    def findSigner(self, userId):
        """
        根据userId查找Signer
        """
        return self._curInst.findSigner(userId) if self._curInst else None

    def findPlayer(self, userId):
        """
        根据userId查找Player
        """
        for group in self._groupMap.values():
            player = group.findPlayer(userId)
            if player:
                return player
        return None

    def signin(self, userId, feeIndex):
        """
        玩家报名
        """
        if not self._curInst:
            raise MatchStoppedException()

        if self.findPlayer(userId):
            raise AlreadyInMatchException()

        return self._curInst.signin(userId, feeIndex)

    def signout(self, userId):
        """
        玩家退赛
        """
        if not self._curInst:
            raise MatchStoppedException()

        signer = self._curInst.findSigner(userId)
        if not signer:
            self._logger.warn("MatchAreaLocal.signout fail",
                              "userId=", userId,
                              "err=", "NotFoundPlayer")
            return
        self._curInst.signout(signer)

    def giveup(self, userId):
        """
        玩家放弃比赛
        """
        player = self.findPlayer(userId)
        if not player:
            self._logger.warn("MatchArea.giveup fail",
                              "userId=", userId,
                              "err=", "NotFoundPlayer")
            return False
        return player.group.stage.giveup(player)

    def enter(self, userId):
        """
        进入报名页
        """
        if self._curInst:
            signer = self._curInst.findSigner(userId)
            if signer:
                self._curInst.enter(signer)

    def leave(self, userId):
        """
        离开报名页
        """
        if self._curInst:
            signer = self._curInst.findSigner(userId)
            if signer:
                self._curInst.leave(signer)

    def onInstStarted(self, inst):
        """
        暂时不做处理，因为只处理本地
        """
        self._logger.info("MatchAreaLocal.onInstStarted instId=", inst.instId)

    def _doInit(self):
        self._logger.info("MatchAreaLocal._doInit ...")
        self._logger.info("MatchAreaLocal._doInit ok")
        return 1

    def _doHeartbeat(self):
        for inst in self._instMap.values()[:]:
            if inst.state == MatchInst.ST_FINAL:
                del self._instMap[inst.instId]
                self._logger.info("MatchAreaLocal._doHeartbeat removeInst",
                                  "instId=", inst.instId)
        for group in self._groupMap.values()[:]:
            if group.state == MatchGroup.ST_FINAL:
                del self._groupMap[group.groupId]
                self._logger.info("MatchAreaLocal._doHeartbeat removeGroup",
                                  "groupId=", group.instId)
        return 1


class TimeMatch(object):

    _matchMap = {}

    WINLOSE_SLEEP = 0

    @classmethod
    def getMatch(cls, roomId):
        """获取比赛"""
        return cls._matchMap.get(roomId, None)

    @classmethod
    def fmtScore(cls, score, n=2):
        """格式积分"""
        fmt = "%d" if int(score) == score else "%%.%sf" % (n)
        return fmt % score

    @classmethod
    def setMatch(cls, roomId, match):
        """房间|比赛"""
        cls._matchMap[roomId] = match

    @classmethod
    def isMaster(cls, conf, room):
        return room.roomId == cls.getMasterRoomId(conf, room)

    @classmethod
    def getMasterRoomId(cls, conf, room):
        """获取主房间Id"""
        if conf.start.isUserCountType():
            return room.roomId
        ctrlRoomIdList = sorted(gdata.bigRoomidsMap().get(room.bigRoomId, []))
        return ctrlRoomIdList[0]

    @classmethod
    def buildMatch(cls, conf, room):
        """构建比赛"""
        ctrlRoomIdList = gdata.bigRoomidsMap().get(room.bigRoomId, [])
        if conf.start.isUserCountType():
            conf.start.userMaxCountPerMatch = conf.start.userMaxCount
            conf.start.signinMaxCount = conf.start.signinMaxCount
        else:
            conf.start.userMaxCountPerMatch = int(conf.start.userMaxCount / max(len(ctrlRoomIdList), 1))
            conf.start.signinMaxCountPerMatch = int(conf.start.signinMaxCount / max(len(ctrlRoomIdList), 1))

        master = MatchMaster(room, conf)
        master.matchStatusDao = MatchStatusDaoRedis(room)
        master.matchFactory = TimePointMatchFactory()
        area = MatchAreaLocal(master, room, conf)



class MatchMaster(HeartbeatAble):

    ST_IDLE = 0
    ST_ALL_AREA_ONLINE = 1
    ST_LOAD = 2

    HEARTBEAT_TO_AREA_INTERVAL = 5

    def __init__(self, room, matchConf):
        super(MatchMaster, self).__init__(1)        # 启动心跳定时器
        self.matchId = matchConf.matchId
        # 所在房间
        self.room = room
        # 比赛配置
        self.matchConf = matchConf
        # value=MatchArea
        self._areas = []
        # key=roomId, value=MatchArea
        self._areaMap = {}
        # 比赛状态数据
        self.matchStatusDao = None
        # 比赛技能
        self.skills = None
        # 比赛目标
        self.targets = None
        # inst
        self._instCtrl = None
        # 状态
        self._state = MatchMaster.ST_IDLE
        # 所有进行的比赛
        self._matchingMap = {}
        # 最后心跳到分赛区的时间
        self._lastHeartbeatToAreaTime = 0
        # 上次比赛排行榜
        self.rankList = []
        # 排行榜排序时间
        self._sortRankTime = None
        # 排行榜更新时间
        self.updateRankTime = None
        # 排行榜缓存数据
        self.rankListCache = []
        # 玩家在比赛阶段游戏的次数
        self.userPlayedTimes = {}
        # uid，player
        self._playerMap = {}
        # 真实玩家
        self.realPlayerSet = set()
        # 排行榜缓存
        self.rankListDao = MatchRankDaoRedis(self)

        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("roomId", self.roomId)

    @property
    def playerMap(self):
        return self._playerMap

    @property
    def areas(self):
        return self._areas

    @property
    def areaCount(self):
        return len(self._areas)

    @property
    def instCtrl(self):
        return self._instCtrl

    @property
    def roomId(self):
        return self.room.roomId

    @property
    def gameId(self):
        return self.room.gameId

    @property
    def roomName(self):
        return self.matchConf.name

    @property
    def matchConfig(self):
        return self.matchConf

    @property
    def fristReward(self):
        if self.matchConf.rankRewardsList and len(self.matchConf.rankRewardsList) > 0:
            rewardStr = u"" + self.matchConf.rankRewardsList[0].desc
            return rewardStr
        return ""

    @property
    def firstRewardData(self):
        if self.matchConf.rankRewardsList and len(self.matchConf.rankRewardsList) > 0 \
                and len(self.matchConf.rankRewardsList[0].rewards) > 0:
            return self.matchConf.rankRewardsList[0].rewards[0]
        return {}

    def findArea(self, roomId):
        return self._areaMap.get(roomId)

    def addArea(self, area):
        if not self.matchConf.start.isUserCountType():
            # 人满开赛不支持分组，只能有一个Local赛区
            assert(len(self._areaMap) == 0)
            assert(isinstance(area, MatchAreaLocal))
        else:
            assert(not self.findArea(area.roomId))
        self._areaMap[area.roomId] = area
        self._areas.append(area)

    def _doInit(self):
        assert(self._areas)
        for area in self._areas:
            area.startHeart()
        return 1
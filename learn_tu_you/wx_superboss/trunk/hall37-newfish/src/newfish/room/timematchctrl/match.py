# -*- coding:utf-8 -*-
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
from newfish.room.timematchctrl.utils import HeartbeatAble, \
    Logger
from newfish.room.timematchctrl.interfaceimpl import TableControllerTime, \
    PlayerNotifierTime, MatchRewardsTime, MatchUserIFTime, \
    SignerInfoLoaderTime, TimeMatchFactory, SigninFeeTime, \
    TableControllerTimePoint, PlayerNotifierTimePoint, MatchRewardsTimePoint, TimePointMatchFactory
from newfish.entity.match_record import MatchRecord
from copy import deepcopy


class MatchInst(HeartbeatAble):
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

    def __init__(self, area, instId, startTime, needLoad):
        super(MatchInstLocal, self).__init__(area, instId, startTime, needLoad)
        # 比赛目标鱼
        self.targets = {}
        
    def addInitSigners(self, signers):
        for signer in signers:
            # 记录
            self.area.signinRecordDao.add(self.matchId, self.roomId, self.instId, SigninRecord(signer.userId, signer.signinTime, signer.fee))
            
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
        assert(signer.inst == self)
        
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
        assert(signer.inst == self)
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
        assert(signer.inst == self)
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
        #return MatchInstStatus(self.instId, self._state, self.signerCount)
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
            add = self.area.signinRecordDao.add(self.matchId, self.roomId, self.instId, SigninRecord(userId, signer.signinTime, fee))
            
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
        if (self.matchConf.start.isTimingType() and self.signerCount >= self.matchConf.start.signinMaxCountPerMatch):
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
        assert(player.group == self)
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

    
class MatchInstCtrl(HeartbeatAble):
    STARTING_TIMEOUT = 180
    
    def __init__(self, master, status, needLoad, signers=None):
        super(MatchInstCtrl, self).__init__(1)
        self.master = master
        self.status = status
        self.prepareTime = None
        self.signinTime = None
        self.closeTime = None
        self.rewardTime = None
        self.needLoad = needLoad
        if status.startTime and self.matchConf.start.isTimingType():
            self.prepareTime = master.matchConf.start.calcPrepareTime(status.startTime)
            self.signinTime = master.matchConf.start.calcSigninTime(status.startTime)
        # if status.startTime and self.matchConf.start.isTimePointType():
            self.closeTime = master.matchConf.start.calcCloseTime(status.startTime)
            self.rewardTime = master.matchConf.start.calcRewardTime(status.startTime)
            
        self._state = MatchInst.ST_IDLE
        self._startingTime = None
        self._initSigners = signers
        # 记录生成的matching数量，以免重复
        self.matchingIdx = 1
        
        # key=roomId, value=MatchInst
        self._instMap = {}
        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("instId", self.instId)
        self._logger.add("startTime", self.startTime)
        self._logger.add("signinTime", self.signinTime)
        self._logger.add("needLoad", self.needLoad)

    
    @property
    def matchId(self):
        return self.master.matchId
    
    @property
    def state(self):
        return self._state

    @property
    def matchConf(self):
        return self.master.matchConf
    
    @property
    def instId(self):
        return self.status.instId
    
    @property
    def startTime(self):
        return self.status.startTime

    @property
    def totalIdleTableCount(self):
        idleTableCount = 0
        for area in self.master.areas:
            idleTableCount += area.tableManager.idleTableCount
        return idleTableCount

    def totalNeedTableCount(self, signerCount):
        needTableCount = (signerCount + self.matchConf.tableSeatCount - 1) / self.matchConf.tableSeatCount
        return needTableCount

    def cancel(self, reason):
        self._heart.postCall(self._doCancel, reason)
        
    def calcTotalSignerCount(self):
        count = 0
        for inst in self._instMap.values():
            count += inst.signerCount
        return count

    def _doInit(self):
        assert(self._state == MatchInst.ST_IDLE)
        self._logger.info("MatchInstCtrl._doInit ...",
                          "state=", self._state)
        if self._initSigners:
            assert(len(self.master.areas) == 1)
            
        for area in self.master.areas:
            inst = area.newInst(self.instId, self.startTime, self.needLoad)
            self._instMap[area.roomId] = inst
            if self._initSigners:
                assert(isinstance(inst, MatchInstLocal))
                inst.addInitSigners(self._initSigners)
            inst.startHeart()
            
        self._logger.info("MatchInstCtrl._doInit ok",
                          "state=", self._state)
        return 1
    
    def _doStartSignin(self):
        self._logger.info("MatchInstCtrl._doStartSignin ...",
                          "state=", self._state)
        assert(self._state == MatchInst.ST_IDLE)
        self._state = MatchInst.ST_SIGNIN
        for inst in self._instMap.values():
            inst.startSignin()
        self._logger.info("MatchInstCtrl._doStartSignin ok",
                          "state=", self._state)
    
    def _doPrepare(self):
        self._logger.info("MatchInstCtrl._doPrepare ...",
                          "state=", self._state)
        assert(self._state < MatchInst.ST_PREPARE)
        self._state = MatchInst.ST_PREPARE
        for inst in self._instMap.values():
            inst.prepare()
        self._logger.info("MatchInstCtrl._doPrepare ok",
                          "state=", self._state)
        
    def _doStart(self):
        self._logger.info("MatchInstCtrl._doStart ...",
                          "state=", self._state)
        assert(self._state in (MatchInst.ST_SIGNIN, MatchInst.ST_PREPARE))
        self._state = MatchInst.ST_STARTING
        self._startingTime = pktimestamp.getCurrentTimestamp()
        for inst in self._instMap.values():
            inst.start()
        self._logger.info("MatchInstCtrl._doStart ok",
                          "state=", self._state)
        
    def _doCancel(self, reason):
        self._logger.info("MatchInstCtrl._doCancel",
                          "state=", self._state,
                          "reason=", reason)
        if self._state < MatchInst.ST_FINAL:
            self._state = MatchInst.ST_FINAL
            for inst in self._instMap.values():
                inst.cancel(reason)
            
    def _doFinal(self):
        self._logger.info("MatchInstCtrl._doFinal",
                          "state=", self._state)
        if self._state < MatchInst.ST_FINAL:
            self._state = MatchInst.ST_FINAL
            for inst in self._instMap.values():
                inst.final()
    
    def _isAllStarted(self):
        for inst in self._instMap.values():
            if inst.state != MatchInst.ST_STARTED:
                return False
        return True
    
    def _isStartingTimeout(self):
        if self._state == MatchInst.ST_STARTING:
            ts = pktimestamp.getCurrentTimestamp()
            return (ts - self._startingTime) >= MatchInstCtrl.STARTING_TIMEOUT
        return False
    
    def _cancelTimeoutInst(self):
        for inst in self._instMap.values():
            if inst.state != MatchInst.ST_STARTED:
                inst.cancel(MatchFinishReason.OVERTIME)
                        
    def _collectSignerMap(self):
        signerMap = {}
        for inst in self._instMap.values():
            if inst.state == MatchInst.ST_STARTED:
                signerMap.update(inst.signerMap)
        return signerMap
    
    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug("MatchInstCtrl._doHeartbeat", "state=", self._state)
            
        if self._state == MatchInst.ST_IDLE:
            if (not self.signinTime or pktimestamp.getCurrentTimestamp() >= self.signinTime):
                self._doStartSignin()

        if self._state == MatchInst.ST_SIGNIN:
            if (self.prepareTime and pktimestamp.getCurrentTimestamp() >= self.prepareTime):
                self._doPrepare()

        if self._state in (MatchInst.ST_SIGNIN, MatchInst.ST_PREPARE):
            if self.startTime:
                self._sendLed(self.startTime - pktimestamp.getCurrentTimestamp())

                if pktimestamp.getCurrentTimestamp() >= self.startTime:
                    self._doStart()
            else:
                inst = self._instMap.values()[0]
                if self._logger.isDebug():
                    self._logger.debug("MatchInstCtrl._doHeartbeat",
                                       "timestamp=", pktimestamp.getCurrentTimestamp(),
                                       "state=", self._state,
                                       "totalSignerCount=", inst.signerCount,
                                       "startUserCount=", self.matchConf.start.userCount)
                if inst.signerCount >= self.matchConf.start.userCount:
                    self._doStart()
                
        if self._state == MatchInst.ST_STARTING:
            if self.matchConf.start.isTimePointType():
                self._state = MatchInst.ST_STARTED
                # 比赛开始后清理排行榜
                self.master.rankList = []
                self.master.rankListCache = []
                self.master.rankListDao.load(self.startTime)
            elif self._isAllStarted() or self._isStartingTimeout():
                self._state = MatchInst.ST_STARTED
                self._cancelTimeoutInst()
                signerMap = self._collectSignerMap()
                
                if self._logger.isDebug():
                    self._logger.debug("MatchInstCtrl._doHeartbeat",
                                       "state=", self._state,
                                       "signerCount=", len(signerMap),
                                       "userIds=", signerMap.keys())
            
                if self.startTime:  # 定时赛
                    if len(signerMap) < self.matchConf.start.userMinCount:
                        # 人数不足
                        self._doCancel(MatchFinishReason.USER_NOT_ENOUGH)
                        signerMap = {}
                    if self.totalIdleTableCount < self.totalNeedTableCount(len(signerMap)):
                        # 桌子资源不够
                        self._doCancel(MatchFinishReason.RESOURCE_NOT_ENOUGH)
                        signerMap = {}
                    self._doFinal()
                    self.master._setupNextInst(self, None, 1)
                    if signerMap:
                        self.master._startMatching(self, 1, signerMap.values())
                else:               # 人满赛
                    signers = sorted(signerMap.values(), key=lambda s: s.signinTime)
                    num = 1
                    signersList = []
                    while len(signers) >= self.matchConf.start.userCount:
                        signersList.append(signers[0:self.matchConf.start.userCount])
                        signers = signers[self.matchConf.start.userCount:]
                        num += 1
                    self._doFinal()
                    self.master._setupNextInst(self, signers, num)
                    for signers in signersList:
                        self.master._startMatching(self, num, signers)

        if self._state == MatchInst.ST_STARTED:
            # 定时积分赛在结算时刻发奖和更新玩家幸运值
            if self.matchConf.start.isTimePointType():
                if self.rewardTime and pktimestamp.getCurrentTimestamp() >= self.rewardTime:
                    self._doFinal()
                    self.master.updateRankTime = pktimestamp.getCurrentTimestamp()
                    self.master.sortRanks()
                    self.master.sendRewards(self.master.room.match.matchRewards)
                    self.master.sendMatchOverAndLed()
                    self.master.updateLastRank()
                    self.master.rankListDao.remove(self.startTime)
                    self.master._setupNextInst(self, None, 1)
                else:
                    self.master.sortRanks()
                    self.master.rankListDao.save(self.startTime)

        if self._state == MatchInst.ST_FINAL:
            self.stopHeart()

        return 1

    def _sendLed(self, curTime):
        if self.master.matchConfig.fishPool == 44104 or not self.startTime:
            return
        strTime = time.strftime("%H:%M", time.localtime(self.startTime))
        if curTime == 1200 and self.matchConf.start.isTimePointType() is False:
            # msg = u"%s开始的\"%s\"红包赛可以报名了，请进入红包赛场及时报名吧！冠军奖励:%s"
            for lang in util.getAllLanguage():
                roomName = config.getMultiLangTextConf(self.master.roomName, lang=lang)
                fristReward = config.getMultiLangTextConf(self.master.fristReward, lang=lang)
                mid = "ID_LED_MATCH_SIGNIN_TIP"
                msg = config.getMultiLangTextConf(mid, lang=lang) % (strTime, roomName, fristReward)
                user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, id=mid, lang=lang)
        elif curTime == 600 or curTime == 480 or curTime == 180:
            # msg = u"%s开始的\"%s\"红包赛就要开赛了，想参加比赛的渔友不要错过哦！冠军奖励:%s"
            for lang in util.getAllLanguage():
                roomName = config.getMultiLangTextConf(self.master.roomName, lang=lang)
                fristReward = config.getMultiLangTextConf(self.master.fristReward, lang=lang)
                mid = "ID_LED_MATCH_START_TIP_1"
                msg = config.getMultiLangTextConf(mid, lang=lang) % (strTime, roomName, fristReward)
                user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, id=mid, lang=lang)
        elif curTime == 120:
            # msg = u"%s开始的\"%s\"红包赛马上要开赛了，再不报名就要错过本次比赛了哟！冠军奖励:%s"
            for lang in util.getAllLanguage():
                roomName = config.getMultiLangTextConf(self.master.roomName, lang=lang)
                fristReward = config.getMultiLangTextConf(self.master.fristReward, lang=lang)
                mid = "ID_LED_MATCH_START_TIP_2"
                msg = config.getMultiLangTextConf(mid, lang=lang) % (strTime, roomName, fristReward)
                user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, id=mid, lang=lang)


class MatchStageCtrl(object):
    """
    比赛阶段控制，启动阶段，创建player分组，完成阶段
    """
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    ST_FINAL = 3
    
    def __init__(self, matching, stageConf):
        # 比赛
        self.matching = matching
        # 阶段配置
        self.stageConf = stageConf
        # 该阶段所有分组key=groupId, value=MatchGroup
        self._groupMap = {}
        # 状态
        self._state = MatchStageCtrl.ST_IDLE
        self._logger = Logger()
        self._logger.add("instId", self.instId)
        self._logger.add("matchingId", self.matchingId)
        self._logger.add("stageIndex", self.stageIndex)
        
    @property
    def instId(self):
        return self.matching.instId
    
    @property
    def matchingId(self):
        return self.matching.matchingId
    
    @property
    def master(self):
        return self.matching.master
    
    @property
    def stageIndex(self):
        return self.stageConf.index
    
    @property
    def matchConf(self):
        return self.matching.matchConf
    
    @property
    def state(self):
        return self._state
    
    def getAllRisePlayerList(self):
        playerMap = {}
        for group in self._groupMap.values():
            players = group.getRisePlayers()
            for player in players:
                playerMap[player.userId] = player
        return playerMap.values()
    
    def startStage(self, playerList):
        """
        启动该阶段
        """
        self._logger.info("MatchStageCtrl.startStage",
                          "userIds=", [p.userId for p in playerList])
        # 对players进行分组
        isGrouping, groupPlayerLists = self.groupingPlayerList(playerList, self.stageConf, self.matchConf.tableSeatCount)
        for i, groupPlayerList in enumerate(groupPlayerLists):
            groupId = "%s.%s.%s" % (self.matchingId, self.stageIndex, i + 1)
            groupName = GroupNameGenerator.generateGroupName(len(groupPlayerLists), i)
            area = self.master.areas[i % len(self.master.areas)]
            group = area.newGroup(self.instId, self.matchingId, groupId, i,
                                  groupName, self.stageIndex, isGrouping,
                                  self.matching.startPlayerCount, self.matching.realPlayerCount)
            group.addPlayers(groupPlayerList)
            self._groupMap[groupId] = group
            
        # 启动所有分组
        for group in self._groupMap.values():
            # 启动分组
            group.startHeart()
            
        self._state = MatchStageCtrl.ST_START
            
    def finalStage(self):
        """
        完成该阶段
        """
        for group in self._groupMap.values():
            # 终止分组
            group.finalGroup()
    
    @classmethod
    def groupingPlayerList(cls, playerList, stageConf, tableSeatCount):
        groupPlayersList = None
        isGrouping = True
        if stageConf.groupingType == GroupingType.TYPE_GROUP_COUNT:
            groupPlayersList = PlayerGrouping.groupingByGroupCount(playerList, stageConf.groupingGroupCount, tableSeatCount)
        elif stageConf.groupingType == GroupingType.TYPE_USER_COUNT:
            groupPlayersList = PlayerGrouping.groupingByMaxUserCountPerGroup(playerList, stageConf.groupingUserCount, tableSeatCount)
        else:
            groupPlayersList = [playerList[:]]
            isGrouping = False
        return isGrouping, groupPlayersList
    
    def _isAllGroupFinish(self):
        if self._logger.isDebug():
            self._logger.debug("MatchStageCtrl._isAllGroupFinish",
                               "state=", self._state,
                               "groups=", self._groupMap.keys())
        for group in self._groupMap.values():
            if group.state < MatchGroup.ST_FINISH:
                return False
        return True
    
    def _processStage(self):
        if self._logger.isDebug():
            self._logger.debug("MatchStageCtrl._processStage",
                               "state=", self._state)

        if self._state == MatchStageCtrl.ST_START:
            if self._isAllGroupFinish():
                self._state = MatchStageCtrl.ST_FINISH


class Matching(HeartbeatAble):
    """
    一个发奖单元
    """
    ST_IDLE = 0
    ST_START = 1
    ST_FINISH = 2
    
    HEARTBEAT_INTERVAL = 2
    
    def __init__(self, master, instId, matchingId, signers):
        super(Matching, self).__init__(1)
        # 主控对象
        self.master = master
        # 比赛实例ID
        self.instId = instId
        self.matchingId = matchingId
        # 报名玩家
        self._signers = signers
        # 状态
        self._state = Matching.ST_IDLE
        # 所有阶段
        self._stages = None
        # 当前阶段
        self._stage = None
        # 开赛时的人数
        self._startPlayerCount = 0
        # 真实玩家数
        self._realPlayerCount = 0

        # 日志
        self._logger = Logger()
        self._logger.add("matchId", self.matchId)
        self._logger.add("instId", self.instId)
        self._logger.add("matchingId", self.matchingId)

        
    @property
    def matchId(self):
        return self.master.matchId
    
    @property
    def matchConf(self):
        return self.master.matchConf
    
    @property
    def state(self):
        return self._state
    
    @property
    def startPlayerCount(self):
        return self._startPlayerCount

    @property
    def realPlayerCount(self):
        return self._realPlayerCount

    @property
    def signers(self):
        return self._signers
    
    def findFirstStage(self, signerCount):
        if self.matchConf.start.selectFirstStage: 
            for stage in self._stages:
                if signerCount > stage.stageConf.riseUserCount:
                    return stage
        return self._stages[0]
    
    def signersToPlayers(self, signers):
        ret = []
        for i, signer in enumerate(signers):
            player = self.master.matchFactory.newPlayer(signer)
            player.playerNo = i + 1
            ret.append(player)
            if player.userId > config.ROBOT_MAX_USER_ID:
                self._realPlayerCount += 1
        return ret
    
    def _createStages(self, stageConfs):
        ret = []
        for stageConf in stageConfs:
            stage = MatchStageCtrl(self, stageConf)
            ret.append(stage)
        return ret
    
    def _doInit(self):
        self._state = Matching.ST_START
        
        # 根据人数找到最合适的第一阶段
        self._stages = self._createStages(self.matchConf.stages)
        self._startPlayerCount = len(self._signers)
        self._stage = self.findFirstStage(self._startPlayerCount)
        
        self._logger.info("Matching._doInit ...",
                          "state=", self._state,
                          "userCount=", self._startPlayerCount,
                          "firstStageIndex=", self._stage.stageIndex)
        
        playerList = self.signersToPlayers(self._signers)
        self._stage.startStage(playerList)
        
        self._logger.info("Matching._doInit ok",
                          "state=", self._state,
                          "userCount=", self._startPlayerCount,
                          "firstStageIndex=", self._stage.stageIndex)
        return 1
    
    def _doHeartbeat(self):
        if self._logger.isDebug():
            self._logger.debug("Matching._doHeartbeat",
                               "state=", self._state,
                               "stageIndex=", self._stage.stageIndex if self._stage else None)
        if self._stage and self._state == Matching.ST_START:
            self._stage._processStage()
            
        if self._stage and self._stage.state == MatchStageCtrl.ST_FINISH:
            self._startNextStage()
            
        return Matching.HEARTBEAT_INTERVAL
    
    def _startNextStage(self):
        playerList = self._stage.getAllRisePlayerList()
        nextStage = self._getNextStage(self._stage)
        self._logger.hinfo("Matching._startNextStage",
                           "state=", self._state,
                           "stageIndex=", self._stage.stageIndex,
                           "nextStageIndex=", nextStage.stageIndex if nextStage else None,
                           "nextStageState=", nextStage.state if nextStage else None,
                           "playerCount=", len(playerList))
        self._stage.finalStage()
        if nextStage:
            self._stage = nextStage
            self._stage.startStage(playerList)
        else:
            self._doFinish()
            
    def _getNextStage(self, stage):
        nextStageIndex = stage.stageIndex + 1
        if nextStageIndex < len(self._stages):
            return self._stages[nextStageIndex]
        return None
    
    def _doFinish(self):
        self._state = Matching.ST_FINISH
        self._logger.info("Matching._doFinish ...",
                          "state=", self._state)
        self.stopHeart()
        self._logger.info("Matching._doFinish ok",
                          "state=", self._state)


class MatchMaster(HeartbeatAble):

    ST_IDLE = 0
    ST_ALL_AREA_ONLINE = 1
    ST_LOAD = 2
    
    HEARTBEAT_TO_AREA_INTERVAL = 5
    
    def __init__(self, room, matchConf):
        super(MatchMaster, self).__init__(1)
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
            rewardStr = u"" +self.matchConf.rankRewardsList[0].desc
            return rewardStr
        return ""

    @property
    def firstRewardData(self):
        if self.matchConf.rankRewardsList and len(self.matchConf.rankRewardsList) > 0\
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
    
    def _startMatching(self, instCtrl, num, signers):
        matchingId = "%s.%s" % (instCtrl.instId, num)
        matching = Matching(self, instCtrl.instId, matchingId, signers)
        instCtrl.matchingIdx += 1
        self._matchingMap[matchingId] = matching
        self._logger.info("MatchMaster._startMatching ...",
                          "matchingId=", matchingId,
                          "signerCount=", len(signers))
        
        matching.startHeart()
        
        self._logger.info("MatchMaster._startMatching",
                           "matchingId=", matchingId,
                           "signers=", [signer.userId for signer in signers],
                           "signerCount=", len(signers))

    def startMatching(self, singers):
        self._startMatching(self._instCtrl, self._instCtrl.matchingIdx, singers)

    def _getSkills(self, matchId):
        """
        获取比赛使用的技能
        """
        conf = config.getTimePointMatchSkillConf().get(str(matchId))
        idx = util.selectIdxByWeight(conf["weight_1"])
        skill1 = conf["skill_1"][idx]
        try:
            idx1 = conf["skill_2"].index(skill1)
        except:
            self._logger.error("_getSkills matchId=, ", matchId, "skill_list", conf["skill_2"], "skill", skill1)
            idx1 = -1
        weight_2 = deepcopy(conf["weight_2"])
        skill_2 = deepcopy(conf["skill_2"])
        if idx1 == -1:
            idx2 = util.selectIdxByWeight(weight_2)
            skill2 = skill_2[idx2]
        else:
            skill_2.pop(idx1)
            weight_2.pop(idx1)
            idx2 = util.selectIdxByWeight(weight_2)
            skill2 = skill_2[idx2]
        return [skill1, skill2]

    def _getTargets(self):
        allMatchFish = config.getAllMatchFish(self.matchConf.fishPool)
        targets = random.sample(allMatchFish, 2)
        targetsMap = {
            "target1": targets[0],
            "multiple1": allMatchFish[targets[0]],
            "target2": targets[1],
            "multiple2": allMatchFish[targets[1]]
        }
        return targetsMap
    
    def _setupNextInst(self, instCtrl, signers, matchingCount):
        timestamp = pktimestamp.getCurrentTimestamp()
        startTime = self.matchConf.start.calcNextStartTime(timestamp + 1)
        skills = self._getSkills(self.matchId)
        targets = self._getTargets()
        if startTime or self.matchConf.start.isUserCountType():
            status = MatchStatus(self.matchId, instCtrl.status.sequence + matchingCount, startTime, skills, targets)
            self.matchStatusDao.save(status)
            self.skills = status.skills
            self.targets = status.targets
            self._instCtrl = MatchInstCtrl(self, status, False, signers)
            self._instCtrl.startHeart()
            roomInfo = self._buildRoomInfo()
            if self._logger.isDebug():
                self._logger.debug("MatchMaster._setupNextInst saveRoomInfo",
                                   "roomInfo=", roomInfo.toDict())
            roominfo.saveRoomInfo(self.gameId, roomInfo)
        else:
            assert(not signers)
            self._instCtrl = None
            roominfo.removeRoomInfo(self.gameId, self.roomId)
        self._logger.info("MatchMaster._setupNextInst ok",
                          "instId=", instCtrl.instId,
                          "timestamp=", timestamp,
                          "matchingCount=", matchingCount,
                          "nextInstId=", self._instCtrl.instId if self._instCtrl else None,
                          "startTime=", self._instCtrl.startTime if self._instCtrl else None,
                          "signinTime=", self._instCtrl.signinTime if self._instCtrl else None,
                          "rewardTime=", self._instCtrl.rewardTime if self._instCtrl else None,
                          "closeTime=", self._instCtrl.closeTime if self._instCtrl else None,
                          "signers=", [s.userId for s in signers] if signers else None)
        return self._instCtrl
    
    def _isAllAreaOnline(self):
        for area in self._areas:
            if not area.isOnline():
                return False
        return True
            
    def _doLoad(self):
        assert(self._state == MatchMaster.ST_ALL_AREA_ONLINE)
        self._state = MatchMaster.ST_LOAD
        
        self._logger.info("MatchMaster._doLoad ...",
                          "state=", self._state)
        
        timestamp = pktimestamp.getCurrentTimestamp()
        startTime = self.matchConf.start.calcNextStartTime(timestamp)
        skills = self._getSkills(self.matchId)
        targets = self._getTargets()
        status = self.matchStatusDao.load(self.matchId)
        needLoad = False
        
        if status:
            self._logger.debug("_doLoad", "startTime=", startTime, "status.startTime=", status.startTime,
                               "status.sequence=", status.sequence, "matchId =", self.matchId, "ts =", timestamp)
            # 如果没有下一场了，或者当前场已经过期
            if startTime is None or startTime != status.startTime:
                endTime = self.matchConf.start.calcEndTime(status.startTime)
                # 如果定时积分赛本赛段已开启还没有结束，需要恢复;其余情况，则需要重新加载
                if endTime is not None and self.matchConf.start.isTimePointType() and status.startTime <= timestamp < endTime:
                    needLoad = True
                    startTime = status.startTime
                    # endTime = self.matchConf.start.calcEndTime(status.startTime)
                    self._logger.debug("_doLoad, from dao", "startTime=", startTime, "status.startTime=", status.startTime,
                                       "endTime=", endTime, "matchId=", self.matchId, "status=", status)
                else:
                    instCtrl = MatchInstCtrl(self, status, needLoad, None)
                    instCtrl.startHeart()
                    instCtrl.cancel(MatchFinishReason.OVERTIME)
                    status = MatchStatus(self.matchId, status.sequence + 1, startTime, skills, targets)
            else:
                needLoad = True
            status.startTime = startTime
            status.skills = status.skills or skills
            status.targets = status.targets or targets
        else:
            status = MatchStatus(self.matchId, 1, startTime, skills, targets)

        self.matchStatusDao.save(status)
        self.skills = status.skills
        self.targets = status.targets
        
        roominfo.removeRoomInfo(self.gameId, self.roomId)
        
        if status.startTime or self.matchConf.start.isUserCountType():
            self._instCtrl = MatchInstCtrl(self, status, needLoad, None)
            self._instCtrl.startHeart()
            roomInfo = self._buildRoomInfo()
            roominfo.saveRoomInfo(self.gameId, roomInfo)
            
        self._logger.info("MatchMaster._doLoad ok",
                          "state=", self._state,
                          "instId=", self._instCtrl.instId if self._instCtrl else None,
                          "needLoad =", needLoad,
                          "startTime=", util.timestampToStr(self._instCtrl.startTime) if self._instCtrl.startTime else None)

    def _processMatching(self):
        if self._matchingMap:
            matchingList = list(self._matchingMap.values())
            for matching in matchingList:
                if matching.state == Matching.ST_FINISH:
                    del self._matchingMap[matching.matchingId]
                    self._logger.info("MatchMaster._processMatching matchingFinished",
                                      "matchingId=", matching.matchingId)
    
    def _calcMatchingPlayerCount(self):
        ret = 0
        for area in self._areaMap.values():
            for group in area.groupMap.values():
                ret += group.playerCount
        return ret
    
    def _buildRoomInfo(self):
        roomInfo = MatchRoomInfo()
        roomInfo.roomId = strutil.getBigRoomIdFromInstanceRoomId(self.roomId)
        roomInfo.playerCount = self._calcMatchingPlayerCount()
        roomInfo.signinCount = self._instCtrl.calcTotalSignerCount() if self._instCtrl else 0
        roomInfo.startType = self.matchConf.start.type
        roomInfo.instId = self._instCtrl.instId if self._instCtrl else None
        roomInfo.fees = []
        if self.matchConf.fees:
            for fee in self.matchConf.fees:
                roomInfo.fees.append(TYContentItem(fee.assetKindId, fee.count))
        if self._instCtrl and self.matchConf.start.isTimingType():
            roomInfo.startTime = self._instCtrl.startTime
        return roomInfo
    
    def _heartbeatToAllArea(self):
        if self._logger.isDebug():
            self._logger.debug("MatchMaster._heartbeatToAllArea")
    
    def _doHeartbeat(self):
        timestamp = pktimestamp.getCurrentTimestamp()
        if self._logger.isDebug():
            self._logger.debug("MatchMaster._doHeartbeat",
                               "timestamp=", timestamp,
                               "areaCount=", self.areaCount,
                               "matchingCount=", len(self._matchingMap),
                               "state=", self._state)
        if self._state == MatchMaster.ST_IDLE:
            if self._isAllAreaOnline():
                self._state = MatchMaster.ST_ALL_AREA_ONLINE
                self._logger.info("MatchMaster._doHeartbeat allAreaOnline",
                                  "areaCount=", self.areaCount)
                
        if self._state == MatchMaster.ST_ALL_AREA_ONLINE:
            self._doLoad()
        
        if self._state == MatchMaster.ST_LOAD:
            self._processMatching()
            
        if self._state >= MatchMaster.ST_ALL_AREA_ONLINE:
            if (not self._lastHeartbeatToAreaTime
                or timestamp - self._lastHeartbeatToAreaTime > MatchMaster.HEARTBEAT_TO_AREA_INTERVAL):
                self._lastHeartbeatToAreaTime = timestamp
                self._heartbeatToAllArea()
                roomInfo = self._buildRoomInfo()
                if self._logger.isDebug():
                    self._logger.debug("MatchMaster._doHeartbeatImpl",
                                       "roomInfo=", roomInfo.toDict())
                roominfo.saveRoomInfo(self.gameId, roomInfo)
        return 1

    def sortRanks(self):
        if self._sortRankTime is None or self.updateRankTime >= self._sortRankTime or len(self.rankList) != len(self._playerMap):
            self._sortRankTime = pktimestamp.getCurrentTimestamp()
            self.rankList = self.playerMap.values()
            self.rankList.sort(cmp=cmpPlayers)
            for i, player in enumerate(self.rankList):
                player.rank = i + 1
            self.rankListCache = []
            if self._logger.isDebug():
                self._logger.debug("sortRanks", "rankListCount=", len(self.rankList), "sortTime=", self._sortRankTime)

    def _sendLed(self):
        if len(self.rankList) == 0:
            return
        player = self.rankList[0]
        if self.matchConfig.fishPool == 44104:
            return
        # msg = u"恭喜玩家%s获得“%s”红包赛的冠军，成功赢得%s"
        roomName = config.getMultiLangTextConf(self.roomName)
        msg = config.getMultiLangTextConf("ID_LED_FEEDBACK_MATCH_REWARD").format(player.userName, roomName, self.fristReward)
        mtype = "old"
        rewardData = self.firstRewardData
        mid = ""
        if rewardData is not None:
            count = rewardData["count"]
            if rewardData["itemId"] == "user:chip":
                pass
            elif rewardData["itemId"] == "user:coupon":
                mid = "ID_LED_GET_MATCH_FIRST_COUPON"
                msg = config.getMultiLangTextConf(mid).format(
                        player.userName, roomName, count * config.COUPON_DISPLAY_RATE,
                        count * config.COUPON_DISPLAY_RATE)
                mtype = "new"
            else:
                assetKind = hallitem.itemSystem.findAssetKind(rewardData["itemId"])
                itemId = int(rewardData["itemId"].split(":")[1])
                if itemId in config.BULLET_KINDID and assetKind:
                    mid = "ID_LED_GET_MATCH_FIRST_BULLET"
                    msg = config.getMultiLangTextConf(mid).format(
                            player.userName, roomName, count, assetKind.displayName,
                            util.formatScore(count * config.BULLET_KINDIDS[itemId]))
        user_rpc.sendLed(FISH_GAMEID, msg, isMatch=1, type=mtype, id=mid)

    def _sendMatchOverEvent(self):
        from newfish.entity.event import MatchOverEvent
        from newfish.game import TGFish
        for player in self.rankList:
            event = MatchOverEvent(player.userId, FISH_GAMEID, self.room.bigRoomId, player.rank)
            TGFish.getEventBus().publishEvent(event)
            self._logger.debug("MatchMaster._sendMatchOverEvent", player.userId, player.rank, player.score, player.userName)

    def sendRewards(self, matchRewards):
        """
        发放比赛奖励
        """
        from newfish.robot import robotutil
        for player in self.rankList:
            rankRewards = self.room.getRankRewards(player.rank)
            if player.userId > config.ROBOT_MAX_USER_ID and rankRewards:
                matchRewards.sendRewards(player, rankRewards)
                self.updateMatchLuckyValue(player)
        robotutil.sendRobotNotifyShutDownByRoom(self.roomId, self.gameId)

    def updateLastRank(self):
        from newfish.entity.ranking import ranking_system
        userScores = []
        for player in self.rankList:
            userScores.append({"userId": player.userId, "score": player.score, "signinTime": player.signinTime})
        ranking_system.refreshMatchRankData(self.matchConfig.fishPool, userScores)

    def sendMatchOverAndLed(self):
        self._logger.debug("MatchMaster.sendMatchOverAndLed", "rankListSize=", len(self.rankList))
        self.userPlayedTimes.clear()
        self._playerMap.clear()
        self.realPlayerSet.clear()
        
        self.rankListCache = []
        self._sendLed()
        self._sendMatchOverEvent()

    @classmethod
    def calculateMachLuckyValueChanged(cls, rank, realPlayerCount):
        """
        幸运值公式
        """
        c = max(realPlayerCount, 1)
        k = 4000 / (0.9 * c - 1)
        b = -0.5 * (0.9 * c + 1) * k
        value = k * rank + b
        changeLuckyValue = max(value, -2000)
        changeLuckyValue = min(changeLuckyValue, 2000)
        return changeLuckyValue

    def updateMatchLuckyValue(self, player):
        """
        更新玩家幸运值
        """
        if player.userId <= config.ROBOT_MAX_USER_ID:
            return
        realPlayerCount = len(self.realPlayerSet)
        changeLuckyValue = MatchMaster.calculateMachLuckyValueChanged(player.rank, realPlayerCount)
        # 更新玩家幸运值.
        record = MatchRecord.loadRecord(FISH_GAMEID, player.userId, int(self.room.match.matchId))
        self._logger.debug("updateMatchLuckyValue, update", player.userId, player.luckyValue, record.luckyValue)
        player.luckyValue = record.luckyValue

        player.luckyValue += changeLuckyValue
        player.luckyValue = int(player.luckyValue)
        player.luckyValue = max(player.luckyValue, 0)
        vip = hallvip.userVipSystem.getUserVip(player.userId).vipLevel.level
        key = "initLuckyValue:%d" % int(self.room.match.matchId)
        maxLuckyVal = config.getVipConf(vip).get(key, 10000)
        player.luckyValue = min(player.luckyValue, maxLuckyVal)
        self._logger.debug("updateMatchLuckyValue", player.userId, changeLuckyValue, player.luckyValue, maxLuckyVal, key)

        from newfish.servers.util.rpc import match_remote
        match_remote.publishMatchWinloseEvent(player.userId, self.room.gameId, self.room.match.matchId, 0, True, player.rank, realPlayerCount, None, player.luckyValue)


def cmpPlayers(p1, p2):
    # 分数多的排名靠前
    ret = cmp(p1.score, p2.score)
    if ret != 0:
        return -ret
    return cmp(p1.signinTime, p2.signinTime)


class TimeMatch(object):

    _matchMap = {}

    WINLOSE_SLEEP = 0

    @classmethod
    def getMatch(cls, roomId):
        return cls._matchMap.get(roomId, None)

    @classmethod
    def fmtScore(cls, score, n=2):
        fmt = "%d" if int(score) == score else "%%.%sf" % (n)
        return fmt % score

    @classmethod
    def setMatch(cls, roomId, match):
        cls._matchMap[roomId] = match

    @classmethod
    def isMaster(cls, conf, room):
        return room.roomId == cls.getMasterRoomId(conf, room)

    @classmethod
    def getMasterRoomId(cls, conf, room):
        if conf.start.isUserCountType():
            return room.roomId
        ctrlRoomIdList = sorted(gdata.bigRoomidsMap().get(room.bigRoomId, []))
        return ctrlRoomIdList[0]

    @classmethod
    def buildMatch(cls, conf, room):
        ctrlRoomIdList = gdata.bigRoomidsMap().get(room.bigRoomId, [])
        if conf.start.isUserCountType():
            conf.start.userMaxCountPerMatch = conf.start.userMaxCount
            conf.start.signinMaxCount = conf.start.signinMaxCount
        else:
            conf.start.userMaxCountPerMatch = int(conf.start.userMaxCount / max(len(ctrlRoomIdList), 1))
            conf.start.signinMaxCountPerMatch = int(conf.start.signinMaxCount / max(len(ctrlRoomIdList), 1))

        master = MatchMaster(room, conf)
        master.matchStatusDao = MatchStatusDaoRedis(room)
        master.matchFactory = TimeMatchFactory()
        area = MatchAreaLocal(master, room, conf)
        master.addArea(area)

        ftlog.info("TimeMatch.buildMatch roomId=", room.roomId,
                   "ctrlRoomIdList=", ctrlRoomIdList,
                   "ctrlRoomCount=", len(ctrlRoomIdList),
                   "userMaxCount=", conf.start.userMaxCount,
                   "userMaxCountPerMatch=", conf.start.userMaxCountPerMatch,
                   "signinMaxCount=", conf.start.signinMaxCount,
                   "signinMaxCountPerMatch=", conf.start.signinMaxCountPerMatch)

        area.signinRecordDao = SigninRecordDaoRedis(room.gameId)
        area.tableController = TableControllerTime(area)
        area.playerNotifier = PlayerNotifierTime(room)
        area.matchRewards = MatchRewardsTime(room)
        area.matchUserIF = MatchUserIFTime(room, conf.tableId, conf.seatId)
        area.signerInfoLoader = SignerInfoLoaderTime()
        area.matchFactory = TimeMatchFactory()
        area.signinFee = SigninFeeTime(room)

        return area, master

    @classmethod
    def getMatchStatesByInst(cls, match, room, inst, mo):
        mo.setResult("roomId", room.bigRoomId)
        mo.setResult("state", cls.convertState(inst.state) if inst else 0)
        mo.setResult("inst", inst.instId if inst else str(room.roomId))
        mo.setResult("curPlayer", inst.getTotalSignerCount() if inst else 0)
        mo.setResult("curTimeLeft", cls.getMatchCurTimeLeft(inst))
        mo.setResult("startTime", datetime.fromtimestamp(inst.startTime).strftime("%Y-%m-%d %H:%M") if inst and inst.startTime else "")

    @classmethod
    def getMatchStatesByPlayer(cls, match, room, player, mo):
        mo.setResult("roomId", room.bigRoomId)
        mo.setResult("state", 20)
        mo.setResult("inst", player.instId)
        mo.setResult("curPlayer", player.group.playerCount)
        mo.setResult("curTimeLeft", 0)
        mo.setResult("startTime", "")

        tcount = player.group.calcTotalUncompleteTableCount(player)
        if ftlog.is_debug():
            ftlog.debug("TimeMatch.getMatchStatesByPlayer roomId=", room.bigRoomId,
                        "instId=", player.instId,
                        "userId=", player.userId,
                        "tcount=", tcount)

        progress = cls.getMatchProgress(player)
        allcount = player.group.playerCount

        _, clientVer, _ = strutil.parseClientId(player.clientId)
        waitInfo = {
            "uncompleted": tcount,                          # 还有几桌未完成
            "tableRunk": "%d/3" % player.tableRank,         # 本桌排名
            "runk": "%d/%d" % (player.rank, allcount),      # 总排名
            "chip": float(cls.fmtScore(player.score))       # 当前积分
        }
        if clientVer >= 3.37:
            waitInfo["info"] = cls._buildWaitInfoMsg(room, player)
        mo.setResult("waitInfo", waitInfo)
        mo.setResult("progress", progress)

    @classmethod
    def getMatchStates(cls, room, userId, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, u"非比赛房间")
            return

        player = match.findPlayer(userId)
        if player:
            cls.getMatchStatesByPlayer(match, room, player, mo)
        else:
            signer = match.findSigner(userId)
            inst = signer.inst if signer else match.curInst
            cls.getMatchStatesByInst(match, room, inst, mo)

        bigRoomId = gdata.getBigRoomId(room.roomId)
        roomInfo = util.loadAllRoomInfo().get(bigRoomId)

        mo.setResult("onlinePlayerCount", roomInfo.playerCount if roomInfo else 0)
        mo.setResult("signinPlayerCount", roomInfo.signinCount if roomInfo else 0)

    @classmethod
    def getMatchInfo(cls, room, uid, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, "not a match room")
            return

        inst = match.curInst
        conf = inst.matchConf if inst else match.matchConf
        signer = match.findSigner(uid)
        lang = util.getLanguage(uid)
        info = {}
        info["name"] = config.getMultiLangTextConf(room.roomConf["name"], lang=lang)
        info["minPlayer"] = conf.start.userMinCount
        info["maxPlayer"] = conf.start.userMaxCount
        info["state"] = 1 if signer else 0
        info["signinPlayerCount"] = match.signerCount
        info["curTimeLeft"] = cls.getMatchCurTimeLeft(inst) if inst else 0
        mo.setResult("info", info)
        mo.setResult("startTime", inst.startTime if inst and inst.startTime else 0)
        mo.setResult("fees", cls.buildFees(conf))
        mo.setResult("rankRewards", cls.buildRankRewards(conf.rankRewardsList))
        mo.setResult("duration", int(cls.calcMatchDuration(conf) / 60))
        mo.setResult("tips", {
            "infos": conf.tips.infos,
            "interval": conf.tips.interval
        })
        # record = MatchRecord.loadRecord(room.gameId, uid, match.matchConf.recordId)
        # if record:
        #     mo.setResult("mrecord", {"bestRank": record.bestRank,
        #                              "bestRankDate": record.bestRankDate,
        #                              "isGroup": record.isGroup,
        #                              "crownCount": record.crownCount,
        #                              "playCount": record.playCount})

    @classmethod
    def getMatchSigninPlayerCount(cls, roomId):
        bigRoomId = gdata.getBigRoomId(roomId)
        roomInfo = util.loadAllRoomInfo().get(bigRoomId)
        return roomInfo.signinCount if roomInfo else 0

    @classmethod
    def getUserIndex(cls, matchTableInfo, uid):
        for i, seatInfo in enumerate(matchTableInfo["seats"]):
            if seatInfo["userId"] == uid:
                return i
        return -1

    @classmethod
    def doUpdate(cls, room, table):
        if not table._match_table_info:
            ftlog.warn("TimeMatch.doUpdate roomId=", room.roomId,
                       "tableId=", table.tableId,
                       "err=", "not matchTableInfo")
            return
        # 发送给match manager
        users = []
        for i, player in enumerate(table.players):
            if player and player.userId:
                user = {}
                user["userId"] = player.userId
                user["seatId"] = player.seatId
                user["score"] = player.tableChip
                users.append(user)

        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "update")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.room.bigmatchId)
        msg.setParam("roomId", table.room.ctrlRoomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("users", users)
        router.sendRoomServer(msg, table.room.ctrlRoomId)

    @classmethod
    def doWinLose(cls, room, table):
        if not table._match_table_info:
            ftlog.warn("TimeMatch.doWinLoseTable roomId=", room.roomId,
                       "tableId=", table.tableId,
                       "err=", "not matchTableInfo")
            return
        # 发送给match manager
        users = []
        for i, player in enumerate(table.players):
            if player and player.userId:
                user = {}
                user["userId"] = player.userId
                user["seatId"] = player.seatId
                user["score"] = player.tableChip
                users.append(user)

        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "winlose")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.room.bigmatchId)
        msg.setParam("roomId", table.room.ctrlRoomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("users", users)

        if cls.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(cls.WINLOSE_SLEEP)
        router.sendRoomServer(msg, table.room.ctrlRoomId)

    @classmethod
    def handleMatchException(cls, room, ex, uid, mo):
        lang = util.getLanguage(uid)
        message = config.getMultiLangTextConf("ID_MATCH_ERR_MSG:%d" % int(ex.errorCode), lang=lang)
        ftlog.warn("TimeMatch.handleMatchException",
                   "roomId=", room.roomId,
                   "userId=", uid,
                   "ex=", "%s:%s" % (ex.errorCode, message))
        mo.setResult("error", {"code": ex.errorCode, "info": message})
        router.sendToUser(mo, uid)

    @classmethod
    def _handleSigninException(cls, room, ex, uid, mo):
        pass

    @classmethod
    def _handleSigninFeeNotEnoughException(cls, room, ex, uid, mo):
        pass

    @classmethod
    def buildStages(cls, stages):
        ret = []
        for stage in stages:
            matchName = ""
            n = -1
            dec = "%s人晋级" % (stage.riseUserCount)
            if stage.name.find("海选赛") != -1:
                matchName = "haixuansai"
            elif stage.name.find("晋级赛") != -1:
                matchName = "jinjisai"
            elif stage.name.find("分组赛") != -1:
                matchName = "fenzusai"
            elif stage.name.find("强赛") != -1:
                matchName = "n_qiangsai"
                n = int(stage.name[0:stage.name.find("强赛")])
            elif stage.name.find("总决赛") != -1:
                matchName = "zongjuesai"
            elif stage.name.find("决赛") != -1:
                matchName = "juesai"
            ret.append({"isPass": False, "stationType": matchName, "n": n, "isHere": False, "description": dec,
                        "name": stage.name})
        return ret

    @classmethod
    def buildFeesList(cls, userId, fees):
        ret = []  # 返回付费列表[{type,desc,selected,img}，{...}]
        # 不用写单位的道具类型集合
        notNeedUnit = ("user:chip", "user:exp", "user:charm", "ddz:master.score")
        for fee in fees:
            assetKind = hallitem.itemSystem.findAssetKind(fee.assetKindId)
            if fee.count > 0 and assetKind:
                desc = ""
                if fee.assetKindId in notNeedUnit:
                    desc = str(fee.count) + assetKind.displayName
                else:
                    desc = str(fee.count) + assetKind.units + assetKind.displayName
                timestamp = pktimestamp.getCurrentTimestamp()
                userAssets = hallitem.itemSystem.loadUserAssets(userId)
                myCount = userAssets.balance(FISH_GAMEID, fee.assetKindId, timestamp)
                ret.append({"type": fee.assetKindId, "desc": desc, "img": assetKind.pic, "selected": False,
                            "fulfilled": 1 if myCount >= fee.count else 0})
        return ret

    @classmethod
    def buildFees(cls, conf):
        ret = []
        fee = conf.fees[0]
        if conf.discountTime:
            startTime = util.getTimestampFromStr(conf.discountTime[0])
            endTime = util.getTimestampFromStr(conf.discountTime[1])
            if startTime <= int(time.time()) <= endTime:
                fee = conf.fees[1]
        ret.append({"kindId": fee.assetKindId, "count": fee.count})
        return ret

    @classmethod
    def calcMatchDuration(cls, conf):
        return conf.start.tableTimes

    @classmethod
    def getMatchCurTimeLeft(cls, inst):
        timestamp = pktimestamp.getCurrentTimestamp()
        if (inst
            and inst.matchConf.start.isTimingType()
            and inst.state < inst.ST_STARTING
            and inst.startTime > timestamp):
            return inst.startTime - timestamp
        return 0

    @classmethod
    def convertState(cls, state):
        if MatchInst.ST_IDLE <= state < MatchInst.ST_STARTED:
            return 0
        if MatchInst.ST_STARTED <= state < MatchInst.ST_FINAL:
            return 10
        return 20

    @classmethod
    def getMatchProgress(cls, player):
        return player.group.stage.calcTotalRemTimes(pktimestamp.getCurrentTimestamp())

    @classmethod
    def buildRankRewards(cls, rankRewardsList, defaultEnd=10000):
        ret = []
        for rankRewards in rankRewardsList:
            rewards = cls.buildRewards(rankRewards)
            ret.append({
                "range": {"s": rankRewards.startRank,
                          "e": rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                "rewards": rewards
            })
        return ret

    @classmethod
    def buildRewards(cls, rankRewards):
        rewards = []
        for r in rankRewards.rewards:
            assetKind = hallitem.itemSystem.findAssetKind(r["itemId"])
            count = r["count"]
            if count <= 0:
                continue
            if assetKind:
                if assetKind.kindId == "user:coupon":
                    count *= config.COUPON_DISPLAY_RATE
                    count = "%.2f" % count
                rewards.append({"name": assetKind.displayName,
                                "kindId": assetKind.kindId,
                                "num": r["count"],
                                "unit": assetKind.units,
                                "desc": "%sx%s" % (assetKind.displayName, count),
                                "img": assetKind.pic
                                })
        return rewards

    @classmethod
    def ensureCanSignInMatch(cls, room, userId, mo):
        from newfish.entity import util
        if not util.isFinishAllNewbieTask(userId):
            raise SigninConditionNotEnoughException()
        if not util.isUsableClientVersion(userId):
            raise SigninVersionDisableException()

    @classmethod
    def _buildWaitInfoMsg(cls, room, player):
        conf = {}
        if player.waitReason == WaitReason.BYE:
            # 轮空提示
            return conf.get("byeMsg", u"轮空等待")
        elif player.waitReason == WaitReason.RISE:
            # 晋级等待
            if player.rank < player.stage.stageConf.riseUserCount:
                return conf.get("maybeRiseMsg", u"您非常有可能晋级，请耐心等待")
            return conf.get("riseMsg", u"请耐心等待其他玩家")
        return conf.get("waitMsg", u"请耐心等待其他玩家")


class TimePointMatch(object):

    _matchMap = {}  # roomId, matchArea

    WINLOSE_SLEEP = 0

    @classmethod
    def getMatch(cls, roomId):
        return cls._matchMap.get(roomId, None)

    @classmethod
    def fmtScore(cls, score, n=2):
        fmt = "%d" if int(score) == score else "%%.%sf" % (n,)
        return fmt % score

    @classmethod
    def setMatch(cls, roomId, match):
        cls._matchMap[roomId] = match   # matchArea

    @classmethod
    def isMaster(cls, conf, room):
        return room.roomId == cls.getMasterRoomId(conf, room)

    @classmethod
    def getMasterRoomId(cls, conf, room):
        if conf.start.isUserCountType():
            return room.roomId
        ctrlRoomIdList = sorted(gdata.bigRoomidsMap().get(room.bigRoomId, []))
        return ctrlRoomIdList[0]

    @classmethod
    def buildRewards(cls, rankRewards):
        rewards = []
        for r in rankRewards.rewards:
            assetKind = hallitem.itemSystem.findAssetKind(r["itemId"])
            count = r["count"]
            if count <= 0:
                continue
            if assetKind:
                if assetKind.kindId == "user:coupon":
                    count *= config.COUPON_DISPLAY_RATE
                    count = "%.2f" % count
                rewards.append({
                    "name": assetKind.displayName,
                    "kindId": assetKind.kindId,
                    "num": r["count"],
                    "unit": assetKind.units,
                    "desc": "%sx%s" % (assetKind.displayName, count),
                    "img": assetKind.pic
                })
        return rewards

    @classmethod
    def buildMatch(cls, conf, room):
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
        master.addArea(area)

        ftlog.info("TimePointMatch.buildMatch roomId=", room.roomId,
                   "ctrlRoomIdList=", ctrlRoomIdList,
                   "ctrlRoomCount=", len(ctrlRoomIdList),
                   "userMaxCount=", conf.start.userMaxCount,
                   "userMaxCountPerMatch=", conf.start.userMaxCountPerMatch,
                   "signinMaxCount=", conf.start.signinMaxCount,
                   "signinMaxCountPerMatch=", conf.start.signinMaxCountPerMatch)

        area.signinRecordDao = SigninRecordDaoRedis(room.gameId)
        area.tableController = TableControllerTimePoint(area)
        area.playerNotifier = PlayerNotifierTimePoint(room)
        area.matchRewards = MatchRewardsTimePoint(room)
        area.matchUserIF = MatchUserIFTime(room, conf.tableId, conf.seatId)
        area.signerInfoLoader = SignerInfoLoaderTime()
        area.matchFactory = TimePointMatchFactory()
        area.signinFee = SigninFeeTime(room)
        return area, master

    @classmethod
    def getMatchStatesByInst(cls, match, room, inst, mo):
        mo.setResult("roomId", room.bigRoomId)
        mo.setResult("state", cls.convertState(inst.state) if inst else 0)
        mo.setResult("inst", inst.instId if inst else str(room.roomId))
        mo.setResult("curPlayer", inst.getTotalSignerCount() if inst else 0)
        mo.setResult("curTimeLeft", cls.getMatchCurTimeLeft(inst))
        mo.setResult("startTime", datetime.fromtimestamp(inst.startTime).strftime(
            "%Y-%m-%d %H:%M") if inst and inst.startTime else "")

    @classmethod
    def getMatchStatesByPlayer(cls, match, room, player, mo):
        mo.setResult("roomId", room.bigRoomId)
        mo.setResult("state", 20)
        mo.setResult("inst", player.instId)
        mo.setResult("curPlayer", player.group.playerCount)
        mo.setResult("curTimeLeft", 0)
        mo.setResult("startTime", "")

        tcount = player.group.calcTotalUncompleteTableCount(player)
        if ftlog.is_debug():
            ftlog.debug("TimePointMatch.getMatchStatesByPlayer roomId=", room.bigRoomId,
                        "instId=", player.instId,
                        "userId=", player.userId,
                        "tcount=", tcount)
        progress = cls.getMatchProgress(player)
        allcount = player.group.playerCount

        _, clientVer, _ = strutil.parseClientId(player.clientId)
        waitInfo = {
            "uncompleted": tcount,                          # 还有几桌未完成
            "tableRunk": "%d/3" % player.tableRank,         # 本桌排名
            "runk": "%d/%d" % (player.rank, allcount),      # 总排名
            "chip": float(cls.fmtScore(player.score))       # 当前积分
        }
        if clientVer >= 3.37:
            waitInfo["info"] = cls._buildWaitInfoMsg(room, player)
        mo.setResult("waitInfo", waitInfo)
        mo.setResult("progress", progress)

    @classmethod
    def getMatchStates(cls, room, userId, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, u"非比赛房间")
            return

        player = match.findPlayer(userId)
        if player:
            cls.getMatchStatesByPlayer(match, room, player, mo)
        else:
            signer = match.findSigner(userId)
            inst = signer.inst if signer else match.curInst
            cls.getMatchStatesByInst(match, room, inst, mo)

        bigRoomId = gdata.getBigRoomId(room.roomId)
        roomInfo = util.loadAllRoomInfo().get(bigRoomId)

        mo.setResult("onlinePlayerCount", roomInfo.playerCount if roomInfo else 0)
        mo.setResult("signinPlayerCount", roomInfo.signinCount if roomInfo else 0)

    @classmethod
    def getStartCloseTime(cls, match):
        inst = match.curInst
        startTime = inst.startTime if inst and inst.startTime else 0
        closeTime = inst.closeTime if inst and inst.closeTime else 0
        return startTime, closeTime

    @classmethod
    def getMatchInfo(cls, room, uid, mo):
        match = cls.getMatch(room.roomId)
        if not match:
            mo.setError(1, "not a match room")
            return

        inst = match.curInst
        conf = inst.matchConf if inst else match.matchConf
        signer = match.findSigner(uid)
        lang = util.getLanguage(uid)
        info = {}
        info["name"] = config.getMultiLangTextConf(room.roomConf["name"], lang=lang)
        info["minPlayer"] = conf.start.userMinCount
        info["maxPlayer"] = conf.start.userMaxCount
        info["state"] = 1 if signer else 0
        info["signinPlayerCount"] = match.signerCount
        info["curTimeLeft"] = cls.getMatchCurTimeLeft(inst) if inst else 0
        mo.setResult("info", info)
        mo.setResult("startTime", inst.startTime if inst and inst.startTime else 0)
        if conf.start.isTimePointType():
            mo.setResult("closeTime", inst.closeTime if inst and inst.closeTime else 0)
            mo.setResult("endTime", inst.endTime if inst and inst.endTime else 0)
            score = 0
            rank = 0
            if match.master.playerMap.get(int(uid)):
                score = match.master.playerMap[int(uid)].score
                rank = match.master.playerMap[int(uid)].rank
            totalPlayer = len(match.master.playerMap)
            mo.setResult("bestScore", score)
            mo.setResult("rank", rank)
            mo.setResult("total", totalPlayer)
        mo.setResult("fees", cls.buildFees(conf))
        mo.setResult("rankRewards", cls.buildRankRewards(conf.rankRewardsList))
        mo.setResult("duration", int(cls.calcMatchDuration(conf) / 60))
        mo.setResult("tips", {
            "infos": conf.tips.infos,
            "interval": conf.tips.interval
        })
        playedTimes = match.master.userPlayedTimes.get(uid, 0)
        mo.setResult("playedTimes", playedTimes)
        mo.setResult("maxPlayTimes", conf.start.maxGameTimes)
        mo.setResult("skills", match.master.skills)
        # record = MatchRecord.loadRecord(room.gameId, uid, match.matchConf.recordId)
        # if record:
        #     mo.setResult("mrecord", {"bestRank": record.bestRank,
        #                              "bestRankDate": record.bestRankDate,
        #                              "isGroup": record.isGroup,
        #                              "crownCount": record.crownCount,
        #                              "playCount": record.playCount})

    @classmethod
    def getMatchSigninPlayerCount(cls, roomId):
        bigRoomId = gdata.getBigRoomId(roomId)
        roomInfo = util.loadAllRoomInfo().get(bigRoomId)
        return roomInfo.signinCount if roomInfo else 0


    @classmethod
    def getUserIndex(cls, matchTableInfo, uid):
        for i, seatInfo in enumerate(matchTableInfo["seats"]):
            if seatInfo["userId"] == uid:
                return i
        return -1

    @classmethod
    def doUpdate(cls, room, table):
        if not table._match_table_info:
            ftlog.warn("TimePointMatch.doUpdate roomId=", room.roomId,
                       "tableId=", table.tableId,
                       "err=", "not matchTableInfo")
            return
        # 发送给match manager
        users = []
        for i, player in enumerate(table.players):
            if player and player.userId:
                user = {}
                user["userId"] = player.userId
                user["seatId"] = player.seatId
                user["score"] = player.tableChip
                users.append(user)

        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "update")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.room.bigmatchId)
        msg.setParam("roomId", table.room.ctrlRoomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("users", users)
        router.sendRoomServer(msg, table.room.ctrlRoomId)


    @classmethod
    def doWinLose(cls, room, table):
        if not table._match_table_info:
            ftlog.warn("TimePointMatch.doWinLoseTable roomId=", room.roomId,
                       "tableId=", table.tableId,
                       "err=", "not matchTableInfo")
            return
        # 发送给match manager
        users = []
        for i, player in enumerate(table.players):
            if player and player.userId:
                user = {}
                user["userId"] = player.userId
                user["seatId"] = player.seatId
                user["score"] = player.tableChip
                users.append(user)

        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "winlose")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.room.bigmatchId)
        msg.setParam("roomId", table.room.ctrlRoomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("users", users)

        if cls.WINLOSE_SLEEP > 0:
            FTTasklet.getCurrentFTTasklet().sleepNb(cls.WINLOSE_SLEEP)
        router.sendRoomServer(msg, table.room.ctrlRoomId)

    @classmethod
    def handleMatchException(cls, room, ex, uid, mo):
        lang = util.getLanguage(uid)
        message = config.getMultiLangTextConf("ID_MATCH_ERR_MSG:%d" % int(ex.errorCode), lang=lang)
        ftlog.warn("TimePointMatch.handleMatchException",
                   "roomId=", room.roomId,
                   "userId=", uid,
                   "ex=", "%s:%s" % (ex.errorCode, message))
        mo.setResult("error", {"code": ex.errorCode, "info": message})
        router.sendToUser(mo, uid)

    @classmethod
    def _handleSigninException(cls, room, ex, uid, mo):
        pass

    @classmethod
    def _handleSigninFeeNotEnoughException(cls, room, ex, uid, mo):
        pass

    @classmethod
    def buildStages(cls, stages):
        ret = []
        for stage in stages:
            matchName = ""
            n = -1
            dec = "%s人晋级" % (stage.riseUserCount)
            if stage.name.find("海选赛") != -1:
                matchName = "haixuansai"
            elif stage.name.find("晋级赛") != -1:
                matchName = "jinjisai"
            elif stage.name.find("分组赛") != -1:
                matchName = "fenzusai"
            elif stage.name.find("强赛") != -1:
                matchName = "n_qiangsai"
                n = int(stage.name[0:stage.name.find("强赛")])
            elif stage.name.find("总决赛") != -1:
                matchName = "zongjuesai"
            elif stage.name.find("决赛") != -1:
                matchName = "juesai"
            ret.append({"isPass": False, "stationType": matchName, "n": n, "isHere": False, "description": dec,
                        "name": stage.name})
        return ret

    @classmethod
    def buildFeesList(cls, userId, fees):
        ret = []  # 返回付费列表[{type,desc,selected,img}，{...}]
        # 不用写单位的道具类型集合
        notNeedUnit = ("user:chip", "user:exp", "user:charm", "ddz:master.score")
        for fee in fees:
            assetKind = hallitem.itemSystem.findAssetKind(fee.assetKindId)
            if fee.count > 0 and assetKind:
                if fee.assetKindId in notNeedUnit:
                    desc = str(fee.count) + assetKind.displayName
                else:
                    desc = str(fee.count) + assetKind.units + assetKind.displayName
                timestamp = pktimestamp.getCurrentTimestamp()
                userAssets = hallitem.itemSystem.loadUserAssets(userId)
                myCount = userAssets.balance(FISH_GAMEID, fee.assetKindId, timestamp)
                ret.append({"type": fee.assetKindId, "desc": desc, "img": assetKind.pic, "selected": False,
                            "fulfilled": 1 if myCount >= fee.count else 0})
        return ret

    @classmethod
    def buildFees(cls, conf):
        ret = []
        fee = conf.fees[0]
        if conf.discountTime:
            startTime = util.getTimestampFromStr(conf.discountTime[0])
            endTime = util.getTimestampFromStr(conf.discountTime[1])
            if startTime <= int(time.time()) <= endTime:
                fee = conf.fees[1]
        ret.append({"kindId": fee.assetKindId, "count": fee.count})
        return ret

    @classmethod
    def calcMatchDuration(cls, conf):
        return conf.start.tableTimes

    @classmethod
    def getMatchCurTimeLeft(cls, inst):
        """
        距离比赛开始的剩余时间
        """
        timestamp = pktimestamp.getCurrentTimestamp()
        if (inst
            and inst.matchConf.start.isTimingType()
            and inst.state < inst.ST_STARTING
            and inst.startTime > timestamp):
            return inst.startTime - timestamp
        return 0

    @classmethod
    def getMatchCloseTimeLeft(cls, inst):
        """
        距离比赛关闭的剩余时间
        """
        timestamp = pktimestamp.getCurrentTimestamp()
        if (inst
            and inst.matchConf.start.isTimingType()
            and inst.state == inst.ST_STARTED
            and inst.closeTime > timestamp):
            return inst.closeTime - timestamp
        return 0

    @classmethod
    def convertState(cls, state):
        if (MatchInst.ST_IDLE <= state < MatchInst.ST_STARTED):
            return 0
        if (MatchInst.ST_STARTED <= state < MatchInst.ST_FINAL):
            return 10
        return 20

    @classmethod
    def getMatchProgress(cls, player):
        return player.group.stage.calcTotalRemTimes(pktimestamp.getCurrentTimestamp())

    @classmethod
    def buildRankRewards(cls, rankRewardsList, defaultEnd=10000):
        ret = []
        for rankRewards in rankRewardsList:
            rewards = cls.buildRewards(rankRewards)
            ret.append({
                "range": {"s": rankRewards.startRank,
                          "e": rankRewards.endRank if rankRewards.endRank > 0 else defaultEnd},
                "rewards": rewards
            })
        return ret

    @classmethod
    def ensureCanSignInMatch(cls, room, userId, mo):
        from newfish.entity import util
        if not util.isFinishAllNewbieTask(userId):
            raise SigninConditionNotEnoughException()
        if not util.isUsableClientVersion(userId):
            raise SigninVersionDisableException()

    @classmethod
    def _buildWaitInfoMsg(cls, room, player):
        conf = {}
        if player.waitReason == WaitReason.BYE:
            # 轮空提示
            return conf.get("byeMsg", u"轮空等待")
        elif player.waitReason == WaitReason.RISE:
            # 晋级等待
            if player.rank < player.stage.stageConf.riseUserCount:
                return conf.get("maybeRiseMsg", u"您非常有可能晋级，请耐心等待")
            return conf.get("riseMsg", u"请耐心等待其他玩家")
        return conf.get("waitMsg", u"请耐心等待其他玩家")

    @classmethod
    def returnFee(cls, room, table):
        # 发送给match manager
        users = []
        for i, player in enumerate(table.players):
            if player and player.userId:
                user = {}
                user["userId"] = player.userId
                users.append(user)

        msg = MsgPack()
        msg.setCmd("room")
        msg.setParam("action", "return_fee")
        msg.setParam("gameId", table.gameId)
        msg.setParam("matchId", table.room.bigmatchId)
        msg.setParam("roomId", table.room.ctrlRoomId)
        msg.setParam("tableId", table.tableId)
        msg.setParam("users", users)
        router.sendRoomServer(msg, table.room.ctrlRoomId)
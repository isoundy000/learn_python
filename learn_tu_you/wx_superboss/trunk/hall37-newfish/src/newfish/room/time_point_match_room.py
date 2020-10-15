# -*- coding=utf-8 -*-
"""
定时积分赛
"""
# @Author  : Kangxiaopeng
# @Time    : 2018/11/12

import time
import random

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack

from poker.entity.configure import gdata
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
from poker.entity.dao import userdata, onlinedata
import poker.util.timestamp as pktimestamp
from newfish.room.timematchctrl.interfaceimpl import TimePointPlayer
from newfish.room.time_match_room import FishTimeMatchRoom
from newfish.entity import util, config, mail_system
from newfish.room.timematchctrl.exceptions import MatchException, SigninException, BadStateException, \
    NotSigninException, AlreadySigninException, RunOutSigninChanceException, MaintenanceException
from newfish.room.timematchctrl.match import TimePointMatch


class FishTimePointMatchRoom(FishTimeMatchRoom):
    """
    定时积分赛房间
    """
    def __init__(self, roomdefine):
        self.rankRewardsMap = {}
        self.rankBuildRewardsMap = {}
        self.userInfoMap = {}
        self.userInfoCacheTime = {}
        self.userVipMap = {}
        self.userFee = {}
        super(FishTimePointMatchRoom, self).__init__(roomdefine, TimePointMatch)
        self._logger.info("serverType=", gdata.serverType())

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.time_point_match_table import FishTimePointMatchTable
        table = FishTimePointMatchTable(self, tableId)
        return table

    def initMatch(self):
        super(FishTimePointMatchRoom, self).initMatch()
        self.rankRewardsMap.clear()
        self.rankBuildRewardsMap.clear()
        self.userInfoMap.clear()
        self.userInfoCacheTime.clear()
        self.userVipMap.clear()
        self.userFee.clear()

    def doEnter(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doEnter",
                               "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_enter")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        try:
            onlineLocList = onlinedata.getOnlineLocList(userId)
            self._logger.debug("doEnter",
                               "userId=", userId,
                               "onlinedata=", onlineLocList)
            if onlineLocList:
                raise BadStateException()

            signer = self.match.findSigner(userId)
            self._logger.debug("doEnter", "signer=", signer)
            if signer:
                if not signer.isEnter:
                    self.matchMaster.startMatching([signer])
                    self.userFee[int(userId)] = signer.fee.toDict()
                    self.match.enter(userId)
                    mo.setResult("enter", 1)
                    mo.setResult("targets", self.match.curInst.targets if self.match.curInst else {})
                    router.sendToUser(mo, userId)
                else:
                    raise AlreadySigninException()
            else:
                raise NotSigninException()
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)

    def doGetDescription(self, userId):
        """
        获取比赛相关描述
        """
        if self._logger.isDebug():
            self._logger.debug("doGetDescription",
                               "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_des")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        mo.setResult("matchType", "point")
        self.matchPlugin.getMatchInfo(self, userId, mo)
        router.sendToUser(mo, userId)

    def getMatchStartCloseTime(self):
        """
        获取比赛开始关闭时间
        """
        if self.matchPlugin and self.match:
            return self.matchPlugin.getStartCloseTime(self.match)
        return None, None

    def getUserInfo(self, userId):
        curTime = int(time.time())
        # 存储的额外数据太多了清理一下
        if len(self.userInfoMap) >= 200:
            self.userInfoMap.clear()
            self.userInfoCacheTime.clear()
        # 没有数据或缓存时间过长重新获取数据.
        if self.userInfoMap.get(userId, None) is None or curTime - self.userInfoCacheTime.get(userId, 0) >= 60:
            name = util.getNickname(userId)
            sex, purl = userdata.getAttrs(userId, ["sex", "purl"])
            self.userInfoMap[userId] = (name, sex, purl)
            self.userInfoCacheTime[userId] = curTime
        return self.userInfoMap.get(userId)

    def getUserVip(self, userId):
        """
        缓存玩家vip数据
        """
        if len(self.userVipMap) >= 200:
            self.userVipMap.clear()
        ts = time.time()
        self.userVipMap.setdefault(userId, {"ts": 0, "vip": 0})
        if ts - self.userVipMap[userId]["ts"] > 60:
            self.userVipMap[userId]["vip"] = util.getVipShowLevel(userId)
            self.userVipMap[userId]["ts"] = time.time()
        return self.userVipMap[userId]["vip"]

    def getRankList(self, userId):
        """
        获取玩家自己和排行榜前50的分数和奖励等数据
        """
        ranks = []
        score = 0
        rank = 0
        rewards = []
        ownPlayer = [player for player in self.matchMaster.rankList if player.userId == userId]
        if ownPlayer:
            player = ownPlayer[0]
            score = player.score
            rank = player.rank
            rewards = self.getRankBuildRewards(rank)
        name, sex, avatar = self.getUserInfo(userId)
        ranks.append({"userId": userId,
                      "name": name,
                      "sex": sex,
                      "score": score,
                      "rank": rank,
                      "avatar": avatar,
                      "vip": self.getUserVip(userId),
                      "rewards": rewards})
        if not self.matchMaster.rankListCache:
            for player in self.matchMaster.rankList[:50]:
                name, sex, avatar = self.getUserInfo(player.userId)
                rewards = self.getRankBuildRewards(player.rank)
                self.matchMaster.rankListCache.append({"userId": player.userId,
                                                       "name": name,
                                                       "sex": sex,
                                                       "score": player.score,
                                                       "rank": player.rank,
                                                       "avatar": avatar,
                                                       "vip": self.getUserVip(player.userId),
                                                       "rewards": rewards})
        ranks.extend(self.matchMaster.rankListCache)
        self._logger.debug("getRankList", "userId=", userId, "ranks=", ranks)
        return ranks

    def getRankRewards(self, rank):
        """
        获取等级原始奖励数据
        """
        rewards = None
        if self.rankRewardsMap.get(rank, None) is None:
            rankRewardsList = self.matchMaster.matchConf.rankRewardsList
            if rankRewardsList:
                for rankRewards in rankRewardsList:
                    if ((rankRewards.startRank == -1 or rank >= rankRewards.startRank)
                            and (rankRewards.endRank == -1 or rank <= rankRewards.endRank)):
                        rewards = rankRewards
                        break
            self.rankRewardsMap[rank] = rewards
        else:
            rewards = self.rankRewardsMap[rank]
        return rewards

    def getRankBuildRewards(self, rank):
        """
        获取等级最终奖励数据
        """
        rewards = []
        if self.rankBuildRewardsMap.get(rank, None) is None:
            rankRewards = self.getRankRewards(rank)
            if rankRewards:
                rewards = self.matchPlugin.buildRewards(rankRewards)
            self.rankBuildRewardsMap[rank] = rewards
        else:
            rewards = self.rankBuildRewardsMap[rank]
        return rewards

    def doSignin(self, userId, feeIndex=0):
        """
        比赛报名，扣费
        """
        if self.match.matchConf.discountTime:
            startTime = util.getTimestampFromStr(self.match.matchConf.discountTime[0])
            endTime = util.getTimestampFromStr(self.match.matchConf.discountTime[1])
            if startTime <= int(time.time()) <= endTime:
                feeIndex = 1
        if self._logger.isDebug():
            self._logger.debug("doSignin", "userId=", userId, "feeIndex=", feeIndex, "status=", self.runStatus)
        mo = MsgPack()
        mo.setCmd("m_signin")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        mo.setResult("matchType", "point")
        try:
            if self.runStatus != self.ROOM_STATUS_RUN:
                raise MaintenanceException()
            else:
                playedTimes = self.matchMaster.userPlayedTimes.get(userId, 0)
                maxGameTimes = self.match.matchConf.start.maxGameTimes
                if playedTimes >= maxGameTimes > -1:
                    raise RunOutSigninChanceException()
                else:
                    isIn, _, _, _ = util.isInFishTable(userId)
                    if isIn:
                        raise SigninException()
                    else:
                        if userId > config.ROBOT_MAX_USER_ID:
                            self.matchPlugin.ensureCanSignInMatch(self, userId, mo)
                        signer = self.match.signin(userId, feeIndex)
                        if signer:
                            mo.setResult("signin", 1)
                            mo.setResult("signinPlayerCount", self.match.signerCount)
                            if userId > config.ROBOT_MAX_USER_ID:
                                self.reportBiGameEvent("MATCH_SIGN_UP", userId, self.roomId, 0, 0, 0, 0, 0, [], "match_signin")
                        else:
                            raise SigninException()
                        router.sendToUser(mo, userId)
                        if TYPlayer.isHuman(userId):
                            self._notifyRobotSigninMatch(signer)
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)

    def doSignout(self, userId):
        """
        取消棋报名
        """
        mo = MsgPack()
        mo.setCmd("m_signout")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        mo.setResult("error", {"code": -1, "info": "不能取消报名"})
        router.sendToUser(mo, userId)

    def _notifyRobotSigninMatch(self, signer):
        if self._logger.isDebug():
            self._logger.warn("TYGroupMatchRoom._notifyRobotSigninMatch",
                              "userId=", signer.userId,
                              "instId=", signer.inst,
                              "hasrobot", self.roomConf.get("hasrobot"),
                              signer.inst.realSignerCount, self.roomConf["robotUserMaxCount"], signer.inst.signerRecord)
        if self.roomConf.get("hasrobot"):
            if signer.inst.realSignerCount >= self.roomConf["robotUserMaxCount"] or signer.userId in signer.inst.signerRecord:
                return
            signer.inst.signerRecord.add(signer.userId)
            timeLeft = self.matchPlugin.getMatchCloseTimeLeft(signer.inst)
            signer.inst.singleSignerNum += 1
            randomSignerCount = random.randint(1, 2)
            if signer.inst.singleSignerNum >= 1:   #报名几个人添加机器人
                signer.inst.singleSignerNum = 0
                if timeLeft < 6:
                    self._callRobotSigninMatch(randomSignerCount)
                else:
                    FTLoopTimer(random.randint(5, 30), 0, self._callRobotSigninMatch, randomSignerCount).start()

    def _callRobotSigninMatch(self, count=1):
        self._logger.debug("MatchRoom._callRobotSigninMatch", count)
        for _ in xrange(count):
            ruid = random.randint(1, 200)
            # 有机器人直接进榜.
            if userdata.checkUserData(ruid):
                rname = userdata.getAttr(ruid, "name")
                self.addMatchRobotUser(ruid, rname)
            else:# 没有机器人召唤机器人登录.
                mo = MsgPack()
                mo.setCmd("robotmgr")
                mo.setAction("callmatch")
                mo.setParam("gameId", self.gameId)
                mo.setParam("roomId", self.roomId)
                mo.setParam("robotCount", 1)
                router.sendRobotServer(mo)
                self._logger.warn("_callRobotSigninMatch, add robot failed, ruid =", ruid)

    def addMatchRobotUser(self, userId, name):
        self._logger.debug("MatchRoom.addMatchRobotUser", userId, name)
        bulletNum = self.roomConf.get("matchConf", {}).get("bullet", 0) * 1.2
        score = random.randint(bulletNum * 0.5, bulletNum)

        matchMaster = self.matchMaster
        if not matchMaster or not matchMaster.instCtrl:
            self._logger.debug("match_rank_add_player", self)
            return
        instId = matchMaster.instCtrl.instId
        player = None
        if not matchMaster.playerMap.get(userId):
            player = TimePointPlayer(userId)
            player.instId = instId
            player.userName = name
            player.fee = 0
            player.signinTime = pktimestamp.getCurrentTimestamp()
            player.clientId = config.CLIENTID_ROBOT
            player.luckyValue = 0
            player.playCount = 0
            player.averageRank = 0
            player.score = score
        else:
            player = matchMaster.playerMap.get(userId)
            player.score = score
        matchMaster.playerMap[userId] = player
        matchMaster.updateRankTime = pktimestamp.getCurrentTimestamp()

    def doReturnFee(self, msg):
        """
        停服准备返还玩家报名费
        """
        # des = u"由于游戏维护导致您离开了比赛，特将此次报名费全额返还，请您查收！非常抱歉给您带来不便，祝您游戏愉快！"
        userList = msg.getParam("users")
        assert (isinstance(userList, list))
        for user in userList:
            userId = user.get("userId", 0)
            if userId <= config.ROBOT_MAX_USER_ID:
                continue
            lang = util.getLanguage(userId)
            des = config.getMultiLangTextConf("ID_DO_RETURN_FEE_MESSAGE", lang=lang)
            player = self.match.findPlayer(userId)
            if player and self.userFee.get(userId, None):
                fee = self.userFee.get(int(userId))
                rewardsList = []
                if fee:
                    rewardsList = util.convertToFishItems(fee)
                self._logger.debug("doReturnFee", "userId=", userId, "fee=", rewardsList)
                self.match.matchUserIF.unlockUser(self.matchId, self.roomId, player.instId, userId)
                if rewardsList:
                    mail_system.sendSystemMail(userId, mail_system.MailRewardType.SystemCompensate, rewardsList, des)
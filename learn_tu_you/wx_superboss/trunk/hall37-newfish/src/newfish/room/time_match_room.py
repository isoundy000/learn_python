# -*- coding=utf-8 -*-
"""
Created by lichen on 2017/6/16.
"""


import functools
import random
import time

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from poker.entity.configure import gdata
from poker.entity.game.rooms.room import TYRoom
from poker.entity.game.tables.table_player import TYPlayer
from poker.protocol import router
from poker.entity.dao import userdata, onlinedata
from hall.entity import hallvip
from newfish.entity import util, config
from newfish.entity.quick_start import FishQuickStart
from newfish.room.timematchctrl.config import MatchConfig
from newfish.room.timematchctrl.exceptions import MatchException, SigninException, BadStateException
from newfish.room.timematchctrl.models import TableManager
from newfish.room.timematchctrl.utils import Logger
from newfish.room.timematchctrl.match import TimeMatch


class FishTimeMatchRoom(TYRoom):
    """
    捕鱼回馈赛房间
    """
    def __init__(self, roomdefine, plugin=None):
        super(FishTimeMatchRoom, self).__init__(roomdefine)
        self.bigmatchId = self.bigRoomId
        if plugin is None:
            self.matchPlugin = TimeMatch
        else:
            self.matchPlugin = plugin
        self.match = None
        self.matchMaster = None
        self._logger = Logger()
        self._logger.add("cls", self.__class__.__name__)
        self._logger.add("roomId", self.roomId)
        self._logger.add("bigmatchId", self.bigmatchId)
        serverType = gdata.serverType()
        if serverType == gdata.SRV_TYPE_ROOM:
            self.initMatch()                                                    # 此处会给self.match赋值

    def newTable(self, tableId):
        """
        在GT中创建TYTable的实例
        """
        from newfish.table.time_match_table import FishTimeMatchTable
        table = FishTimeMatchTable(self, tableId)
        return table

    def initializedGT(self, shadowRoomId, tableCount):
        pass

    def initMatch(self):
        """初始化比赛"""
        assert (self.matchPlugin.getMatch(self.roomId) is None)
        self._logger.info("initMatch ...")
        conf = MatchConfig.parse(self.gameId, self.roomId, self.bigmatchId, self.roomConf["name"], self.matchConf)
        conf.tableId = self.roomId * 10000                                      # 用来表示玩家在房间队列的特殊tableId
        conf.seatId = 1

        tableManager = TableManager(self, conf.tableSeatCount)
        shadowRoomIds = self.roomDefine.shadowRoomIds

        self._logger.info("initMatch", "shadowRoomIds=", list(shadowRoomIds))
        for roomId in shadowRoomIds:
            count = self.roomDefine.configure["gameTableCount"]
            baseid = roomId * 10000
            self._logger.info("initMatch addTables", "shadowRoomId=", roomId, "tableCount=", count, "baseid=", baseid)
            tableManager.addTables(roomId, baseid, count)

        random.shuffle(tableManager._idleTables)
        match, master = self.matchPlugin.buildMatch(conf, self)
        match.tableManager = tableManager

        if gdata.mode() == gdata.RUN_MODE_ONLINE:
            playerCapacity = tableManager.allTableCount * tableManager.tableSeatCount
            if playerCapacity <= conf.start.userMaxCountPerMatch:
                self._logger.error("initMatch", "allTableCount=", tableManager.allTableCount,
                                   "tableSeatCount=", tableManager.tableSeatCount,
                                   "playerCapacity=", playerCapacity,
                                   "userMaxCount=", conf.start.userMaxCount,
                                   "confUserMaxCountPerMatch=", conf.start.userMaxCountPerMatch,
                                   "err=", "NotEnoughTable")
            # assert (playerCapacity > conf.start.userMaxCountPerMatch)

        self.match = match
        self.matchMaster = master
        self.matchPlugin.setMatch(self.roomId, match)
        if master:
            master.startHeart()

    def doEnter(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doEnter", "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_enter")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        try:
            onlineLocList = onlinedata.getOnlineLocList(userId)
            self._logger.debug("doEnter", "userId=", userId, "onlinedata=", onlineLocList)
            if onlineLocList:
                raise BadStateException()
            self.match.enter(userId)
            mo.setResult("enter", 1)
            mo.setResult("targets", self.match.curInst.targets if self.match.curInst else {})
            router.sendToUser(mo, userId)
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)

    def doLeave(self, userId, msg):
        if self._logger.isDebug():
            self._logger.debug("doLeave", "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_leave")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        try:
            self.match.leave(userId)
            router.sendToUser(mo, userId)
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)

    def doGetDescription(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doGetDescription", "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_des")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        self.matchPlugin.getMatchInfo(self, userId, mo)
        router.sendToUser(mo, userId)

    def _getMatchStates(self, userId):
        pass
        # mo = MsgPack()
        # mo.setCmd("m_update")
        # self.matchPlugin.getMatchStates(self, userId, mo)
        # router.sendToUser(mo, userId)

    def doGetNews(self, userId):
        mo = MsgPack()
        mo.setCmd("m_news")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        mo.setResult("signinPlayerCount", self.match.signerCount)
        router.sendToUser(mo, userId)

    def doGetRankList(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doGetRankList", "userId=", userId, "rankList=", self.matchMaster.rankList)
        mo = MsgPack()
        mo.setCmd("m_rank")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        mo.setResult("mranks", self.getRankList(userId))
        router.sendToUser(mo, userId)

    def getRankList(self, userId):
        ranks = []
        score = 0
        rank = 0
        rewards = []
        ownPlayer = [player for player in self.matchMaster.rankList if player.userId == userId]
        if ownPlayer:
            player = ownPlayer[0]
            score = player.score
            rank = player.rank
            rankRewards = self._getRewards(player.rank)
            if rankRewards:
                rewards = TimeMatch.buildRewards(rankRewards)
        name = util.getNickname(userId)
        sex, avatar = userdata.getAttrs(userId, ["sex", "purl"])
        ranks.append({
            "userId": userId,
            "name": name,
            "sex": sex,
            "score": score,
            "rank": rank,
            "avatar": avatar,
            "vip": util.getVipShowLevel(userId),
            "rewards": rewards
        })
        if not self.matchMaster.rankListCache:
            for player in self.matchMaster.rankList[:50]:
                name = util.getNickname(player.userId)
                sex, avatar = userdata.getAttrs(player.userId, ["sex", "purl"])
                rankRewards = self._getRewards(player.rank)
                rewards = []
                if rankRewards:
                    rewards = TimeMatch.buildRewards(rankRewards)
                self.matchMaster.rankListCache.append({
                    "userId": player.userId,
                    "name": name,
                    "sex": sex,
                    "score": player.score,
                    "rank": player.rank,
                    "avatar": avatar,
                    "vip": util.getVipShowLevel(player.userId),
                    "rewards": rewards
                })
        ranks.extend(self.matchMaster.rankListCache)
        return ranks

    def _getRewards(self, rank):
        rankRewardsList = self.matchMaster.matchConf.rankRewardsList
        if not rankRewardsList:
            return
        for rankRewards in rankRewardsList:
            if ((rankRewards.startRank == -1 or rank >= rankRewards.startRank)
                and (rankRewards.endRank == -1 or rank <= rankRewards.endRank)):
                return rankRewards

    def getUserMatchSignin(self, userId):
        if self.match.curInst:
            signer = self.match.curInst.findSigner(userId)
            if signer:
                return self.match.curInst.startTime
        return 0

    def doSignin(self, userId, feeIndex=0):
        """
        比赛报名
        """
        if self.match.matchConf.discountTime:
            startTime = util.getTimestampFromStr(self.match.matchConf.discountTime[0])
            endTime = util.getTimestampFromStr(self.match.matchConf.discountTime[1])
            if startTime <= int(time.time()) <= endTime:
                feeIndex = 1
        if self._logger.isDebug():
            self._logger.debug("doSignin", "userId=", userId, "feeIndex=", feeIndex)
        mo = MsgPack()
        mo.setCmd("m_signin")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        try:
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
        # self._getMatchStates(userId)

    def doSignout(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doSignout", "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_signout")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        try:
            if self.match.signout(userId):
                self.reportBiGameEvent("MATCH_SIGN_OUT", userId, self.roomId, 0, 0, 0, 0, 0, [], "match_signout")
            mo.setResult("signout", 1)
            mo.setResult("signinPlayerCount", self.match.signerCount)
            router.sendToUser(mo, userId)
        except MatchException, e:
            self.matchPlugin.handleMatchException(self, e, userId, mo)

    def doGiveup(self, userId):
        if self._logger.isDebug():
            self._logger.debug("doGiveup", "userId=", userId)
        mo = MsgPack()
        mo.setCmd("m_giveup")
        mo.setResult("gameId", self.gameId)
        mo.setResult("roomId", self.roomId)
        mo.setResult("userId", userId)
        lang = util.getLanguage(userId)
        try:
            if self.match.giveup(userId):
                mo.setResult("giveup", 1)
            else:
                # mo.setResult("error", {"code": -1, "info": "不能退出比赛"})
                mo.setResult("error", {"code": -1, "info": config.getMultiLangTextConf("ID_MATCH_FORBID_GIVE_UP", lang=lang)})
        except:
            mo.setResult("error", {"code": -1, "info": config.getMultiLangTextConf("ID_MATCH_FORBID_GIVE_UP", lang=lang)})
        router.sendToUser(mo, userId)

    def doUpdate(self, msg):
        matchId = msg.getParam("matchId", 0)
        tableId = msg.getParam("tableId", 0)

        if self._logger.isDebug():
            self._logger.debug("doUpdateInfo", "matchId=", matchId, "tableId=", tableId)
        userList = msg.getParam("users")
        assert (isinstance(userList, list))
        player = None
        for user in userList:
            userId = user.get("userId", 0)
            seatId = user.get("seatId", 0)
            score = user.get("score", 0)
            if userId <= 0:
                continue
            player = self.match.findPlayer(userId)
            if not player:
                continue
            player.score = score
            if self._logger.isDebug():
                self._logger.debug("doUpdateInfo", "mid=", matchId, "tableId=", tableId, "userId=", userId, "seatId=", seatId, "score=", score, "player=", player)
        if player and player.table:
            player.group.stage.update(player.table)

    def doWinlose(self, msg):
        matchId = msg.getParam("matchId", 0)
        tableId = msg.getParam("tableId", 0)

        if self._logger.isDebug():
            self._logger.debug("doWinlose", "matchId=", matchId, "tableId=", tableId)

        userWinloseList = msg.getParam("users")
        assert (isinstance(userWinloseList, list))

        for userWinlose in userWinloseList:
            userId = userWinlose.get("userId", 0)
            seatId = userWinlose.get("seatId", 0)
            score = userWinlose.get("score", 0)
            if userId <= 0:
                continue
            player = self.match.findPlayer(userId)
            if self._logger.isDebug():
                self._logger.debug("doWinlose", "matchId=", matchId, "tableId=", tableId, "userId=", userId, "seatId=", seatId, "score=", score, "player=", player)
            if player:
                player.group.stage.winlose(player, score)

    def doQuickStart(self, msg):
        userId = msg.getParam("userId")
        tableId = msg.getParam("tableId")
        shadowRoomId = msg.getParam("shadowRoomId")
        clientId = msg.getParam("clientId")

        self._logger.info("doQuickStart", "userId=", userId, "tableId=", tableId, "shadowRoomId=", shadowRoomId, "clientId=", clientId)
        player = self.match.findPlayer(userId)
        if player is None:
            self._logger.warn("doQuickStart", "userId=", userId, "tableId=", tableId, "shadowRoomId=", shadowRoomId, "clientId=", clientId, "err=", "NotFoundPlayer")
            try:
                onlinedata.removeOnlineLoc(userId, self.roomId, tableId)
            except:
                self._logger.warn("doQuickStart", "userId=", userId, "tableId=", tableId, "shadowRoomId=", shadowRoomId, "clientId=", clientId)
            isOk = False
        else:
            isOk = True
        # if not isOk:
        #     FishQuickStart.onQuickStartFailed(FishQuickStart.ENTER_ROOM_REASON_STATE_ERROR,
        #                                       userId, clientId, shadowRoomId)
        """
        if isOk:
            reason = self.ENTER_ROOM_REASON_OK
            self.sendQuickStartRes(self.gameId, userId, reason, self.roomId, self.match.tableId)
            # 如果用户已经被分组则发送等待信息
            if player.group:
                self.match.playerNotifier.notifyMatchWait(player, player.group)
        else:
            reason = self.ENTER_ROOM_REASON_INNER_ERROR
            info = u"渔场太火爆啦，请稍后再试！"
            self.sendQuickStartRes(self.gameId, userId, reason, self.roomId, 0, info)
        """

    def _getMatchRanksQuick(self, userId):
        player = self.match.findPlayer(userId)
        if not player or not player.group:
            return
        # self.match.playerNotifier.notifyMatchRank(player)

    def _notifyRobotSigninMatch(self, signer):
        if self._logger.isDebug():
            self._logger.warn("TYGroupMatchRoom._notifyRobotSigninMatch", "userId=", signer.userId, "instId=", signer.inst)
        if self.roomConf.get("hasrobot"):
            if signer.inst.realSignerCount >= self.roomConf["robotUserMaxCount"] or signer.userId in signer.inst.signerRecord:
                return
            signer.inst.signerRecord.add(signer.userId)
            startConf = self.match.matchConf.start
            timeLeft = self.matchPlugin.getMatchCurTimeLeft(signer.inst)
            if timeLeft > startConf.signinTimes / 3 * 2:
                signer.inst.singleSignerNum += 1
                randomSignerCount = random.randint(3, 5)
                if self.match.matchConf.fishPool == 44101:
                    randomSignerCount = random.randint(6, 10)
                if signer.inst.singleSignerNum >= randomSignerCount:
                    signer.inst.singleSignerNum = 0
                    FTLoopTimer(random.randint(5, 30), 0, self._callRobotSigninMatch).start()
            elif timeLeft > startConf.signinTimes / 3:
                signer.inst.singleSignerNum += 1
                randomSignerCount = 1
                if self.match.matchConf.fishPool == 44101:
                    randomSignerCount = random.randint(1, 2)
                if signer.inst.singleSignerNum >= randomSignerCount:
                    signer.inst.singleSignerNum = 0
                    FTLoopTimer(random.randint(5, 30), 0, self._callRobotSigninMatch).start()
            else:
                if float(max(signer.inst.realSignerCount, 1)) / max(signer.inst.signerCount, 1) > 0.45:
                    randomRobotCount = random.randint(3, 5)
                    randomInterval = random.randint(5, 30)
                    if self.match.matchConf.fishPool == 44101:
                        randomRobotCount = random.randint(1, 3)
                    interval = round(float(randomInterval) / randomRobotCount, 2)
                    if timeLeft > 30:
                        for _ in xrange(randomRobotCount):
                            FTLoopTimer(interval, 0, self._callRobotSigninMatch).start()
                    elif timeLeft > 10:
                        randomInterval = random.randint(0, timeLeft - 5)
                        interval = round(float(randomInterval) / randomRobotCount, 2)
                        for _ in xrange(randomRobotCount):
                            FTLoopTimer(interval, 0, self._callRobotSigninMatch).start()

    def _callRobotSigninMatch(self, count=1):
        mo = MsgPack()
        mo.setCmd("robotmgr")
        mo.setAction("callmatch")
        mo.setParam("gameId", self.gameId)
        mo.setParam("roomId", self.roomId)
        mo.setParam("robotCount", count)
        router.sendRobotServer(mo)

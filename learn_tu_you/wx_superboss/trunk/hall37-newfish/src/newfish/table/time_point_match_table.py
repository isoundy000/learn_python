#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

from freetime.entity.msg import MsgPack

from newfish.entity.msg import GameMsg
from newfish.entity.config import FISH_GAMEID
from newfish.table.time_match_table import FishTimeMatchTable
from newfish.entity.fishgroup.buffer_fish_group import BufferFishGroup
from newfish.entity.fishgroup.multiple_fish_group import MultipleFishGroup


class MatchState:
    DEFAULT = 0
    READY = 1
    START = 2
    END = 3


class FishTimePointMatchTable(FishTimeMatchTable):

    def __init__(self, room, tableId):
        super(FishTimePointMatchTable, self).__init__(room, tableId)
        # 可用action
        self.actionMap = {
            "leave": self._clearPlayer,                         # 玩家退出
            "robot_leave": self._robotLeave,                    # 机器人退出
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
        self._rankListCache = []
        self._playerBestScore = {}
        self._surpassUser = {}

    def clearTableData(self):
        """
        清理桌子数据和状态
        """
        super(FishTimePointMatchTable, self).clearTableData()
        # name, uid, sex, url...
        self._rankListCache = []
        # uid, bestScore
        self._playerBestScore = {}
        # uid, rankCache
        self._surpassUser = {}

    def startFishGroup(self):
        """
        启动鱼阵
        """
        super(FishTimePointMatchTable, self).startFishGroup()
        # buffer鱼初始化
        if self.runConfig.allBufferGroupIds:
            self.bufferFishGroup = BufferFishGroup(self)
        # 随机倍率鱼初始化
        if self.runConfig.allMultipleGroupIds:
            self.multipleFishGroup = MultipleFishGroup(self)

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
            super(FishTimePointMatchTable, self)._doTableManage(msg, action)

    def doMatchTableStart(self, msg):
        """比赛开始"""
        super(FishTimePointMatchTable, self).doMatchTableStart(msg)
        self._rankListCache = self._match_table_info["surpassTargets"]
        # self._rankListCache = self._rankListCache[::-1]
        self._playerBestScore = self._match_table_info["bestScore"]
        if self._logger.isDebug():
            self._logger.debug("doMatchTableStart", "bestScore=", self._playerBestScore,
                               "rankListCache=", self._rankListCache, "matchSkills=", self._matchSkills)

    def doUserGiveup(self, msg):
        """放弃"""
        if self._logger.isDebug():
            self._logger.debug("doUserGiveup", "msg=", msg)
        params = msg.getKey("params")
        userId = params.get("userId", -1)
        matchId = params.get("matchId", -1)
        if matchId != self.room.bigmatchId:
            self._logger.error("doUserGiveup", "msg=", msg, "err=", "DiffMatchId")
        player = self.getPlayer(userId)
        # from newfish.entity.event import MatchGiveUpEvent
        # from newfish.game import TGFish
        # event = MatchGiveUpEvent(userId, FISH_GAMEID, self.room.bigmatchId)
        # TGFish.getEventBus().publishEvent(event)
        if player:
            self._clearPlayer(None, player.userId, player.seatId)
        if self.playersNum == 0:
            self._doMatchTableClear()

    def _verifyCatch(self, msg, userId, seatId):
        if self._matchState == MatchState.END:
            return
        super(FishTimePointMatchTable, self)._verifyCatch(msg, userId, seatId)

    def _updateMatchRank(self, userId):
        """更新比赛排名"""
        player = self.getPlayer(userId)
        if player and player.userId and self._match_table_info:
            if player.rank == 0:
                player.rank = self._match_table_info["totalPlayerCount"]
            msg = MsgPack()
            msg.setCmd("m_update")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("seatId", player.seatId)
            msg.setResult("userId", player.userId)
            msg.setResult("rank", [player.rank, self._match_table_info["totalPlayerCount"]])
            GameMsg.sendMsg(msg, player.userId)

    def _surpassTarget(self, msg, userId, seatId):
        """超越目标"""
        player = self.getPlayer(userId)
        if player and player.userId:
            self._updateSurpassUser(player)
            msg = MsgPack()
            msg.setCmd("m_surpass")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("userId", player.userId)
            msg.setResult("bestScore", self._playerBestScore.get(str(userId), 0))
            if self._surpassUser.get(userId, None):
                msg.setResult("target", self._surpassUser.get(userId))
            GameMsg.sendMsg(msg, player.userId)
            if self._logger.isDebug():
                self._logger.debug("_surpassTarget", "userId", userId, "score=",
                                   self._playerBestScore.get(str(userId), 0),
                                   "playerBestScore=", self._playerBestScore)

    def _updateSurpassUser(self, player):
        """更新超越的用户"""
        if player and self._logger.isDebug():
            self._logger.debug("_updateSurpassUser 1", "userId=", player.userId, "rank=",
                               player.rank, "score=", player.tableChip)
        if player and player.userId and self._match_table_info and player.rank == 0:
            player.rank = self._match_table_info["totalPlayerCount"]
        newTarget = None
        maxScore = max(player.tableChip, self._playerBestScore.get(str(player.userId), 0))
        for tar in self._rankListCache:
            if maxScore < tar["score"] and tar["userId"] != player.userId:
                newTarget = tar
                break
        self._surpassUser[player.userId] = newTarget
        if self._logger.isDebug():
            self._logger.debug("_updateSurpassUser 2", "userId=", player.userId, "rank=", player.rank,
                               "target=", newTarget, "maxScore=", maxScore)

    def _doShutDown(self):
        """
        桌子同步安全操作方法
        桌子关闭, 此方法由安全进程结束的方法调用
        """
        if self._logger.isDebug():
            self._logger.debug("_doShutDown")
        self.room.matchPlugin.returnFee(self.room, self)
        for i in range(self.maxSeatN):
            player = self.players[i]
            if player and player.userId:
                msg = MsgPack()
                msg.setCmd("leave")
                msg.setResult("gameId", FISH_GAMEID)
                msg.setResult("userId", player.userId)
                msg.setResult("seatId", player.seatId)
                GameMsg.sendMsg(msg, self.getBroadcastUids())
        super(FishTimePointMatchTable, self)._doShutDown()
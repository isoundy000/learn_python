#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import time
import random
import copy

from freetime.util import log as ftlog
from freetime.core.lock import locked
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.biz.exceptions import TYBizException
from poker.entity.dao import onlinedata
from poker.entity.dao import userdata
from poker.entity.biz import bireport
from poker.entity.game.tables.table_seat import TYSeat
from hall.entity import hallvip, datachangenotify
from newfish.entity import config
from newfish.entity.config import FISH_GAMEID
from newfish.table.table_base import FishTable
from newfish.entity import util
from newfish.entity.msg import GameMsg
from newfish.player.fight_player import FishFightPlayer
from newfish.entity.event import EnterTableEvent, LeaveTableEvent
from newfish.room.timematchctrl.utils import Logger
from newfish.entity import mail_system, fight_history
from newfish.entity.event import CatchEvent
from newfish.entity.fishactivity import fish_activity_system
from newfish.servers.room.rpc import room_remote


class TableDetails(object):

    def __init__(self):
        self.ftId = None
        self.userId = None
        self.fee = None

    def fromDict(self, d):
        self.ftId = d["ftId"]
        self.fee = d["fee"]
        self.userId = d["userId"]
        return self


class TableState(object):

    DEFAULT = 0     # 默认状态
    NOTFULL = 1     # 人未满
    FULL = 2        # 人已满
    READY = 3       # 准备
    START = 4       # 开始
    END = 5         # 结束


class TableClearState(object):
    END = 0         # 正常结束
    GIVEUP = 1      # 用户放弃


class FishFightTable(FishTable):
    """渔友竞技桌子"""
    def __init__(self, room, tableId):
        super(FishFightTable, self).__init__(room, tableId)
        self.clearTableData()
        # 用户离线等待时间
        self._offlineWaitSeconds = 1200
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 1200
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 1200
        # 桌子过期时间
        self._tableExpiresTime = 600
        # 准备倒计时
        self._readySeconds = 4
        # 初始化定时器
        self._expiresTimer = None
        self._readyTimer = None
        self._beginTimer = None
        # 最大人数
        self.tableSeatCount = self.runConfig.matchConf["table.seat.count"]
        # table_call可用action
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
            "ft_start": self.doFTStart,
            "ft_leave": self.doUserLeave,
            "treasure_rewards": self._getTreasureRewards
        }
        self._logger = Logger()
        self._logger.add("gameId", self.gameId)
        self._logger.add("roomId", room.roomId)
        self._logger.add("tableId", tableId)

    @property
    def ftId(self):
        return self.ftTable.ftId if self.ftTable else 0

    @property
    def ftTable(self):
        return self._ftTable

    def clearTableData(self):
        """
        清理桌子数据和状态
        """
        ftlog.debug("friendTable.clear-->begin", "tableId=", self.tableId)
        self._tableState = TableState.DEFAULT                   # 桌子状态
        # 桌子详情(房号、房主、服务费)
        self._ftTable = None
        self._beginTime = None
        self._usersData = {}
        self.targets = {}
        self.ftRanks = []
        self.winnerId = None
        self.otherId = None
        self._overState = None
        ftlog.debug("friendTable.clear-->end", "tableId=", self.tableId)

    def clearAllTimer(self):
        """
        清理所有的计时器
        """
        if self._readyTimer:
            self._readyTimer.cancel()
            self._readyTimer = None
        if self._beginTimer:
            self._beginTimer.cancel()
            self._beginTimer = None
        if self._expiresTimer:
            self._expiresTimer.cancel()
            self._expiresTimer = None

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishFightPlayer(table, seatIndex, clientId)

    @locked
    def doFTEnter(self, ftId, userId, seatId):
        """进入桌子"""
        ftlog.info("FishFriendTable.doFTEnter", "tableId=", self.tableId, "ftId=", ftId, "seatId=", seatId)
        lang = util.getLanguage(userId)
        if ftId != self.ftId:
            raise TYBizException(1, config.getMultiLangTextConf("ID_INPUT_ROOMID_ERROR_INFO", lang=lang))

        player = self.getPlayer(userId)
        if player and player.userId:
            self.sendFriendDetails(userId)
        else:
            if self._expiresTimer:                              # 重置桌子超时计时器
                self._expiresTimer.cancel()
                self._expiresTimer = None
            self._expiresTimer = FTLoopTimer(self._tableExpiresTime, 0, self._tableExpires)
            self._expiresTimer.start()
            self._doTableQuickStart(userId, seatId)             # 用户进入
            self.sendFriendDetails(userId)                      # 发送对战详情信息
            if userId != self.ftTable.userId:                   # 记录参与者Id
                self.otherId = userId
                fight_history.addOneHistory(userId, self.ftTable.userId, fight_history.HistoryType.Enter, self.ftId, self.ftTable.fee)  # 进入房间记录
        return 0





    def sendFriendDetails(self, userId):
        """发送好友竞技的详情"""
        self._updateFriendInfo(userId)
        self._updateFriendTask()
        if self._tableState >= TableState.READY:
            self._ftStart(userId)

    def _updateFriendInfo(self, userId):
        """更新好友消息"""
        ftPlayer = self.getPlayer(self.ftTable.userId)
        ftName = ""
        if ftPlayer:
            ftName = ftPlayer.name
        player = self.getPlayer(userId)
        if player and player.userId:
            msg = MsgPack()
            msg.setCmd("ft_info")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("roomId", self.roomId)
            msg.setResult("tableId", self.tableId)
            msg.setResult("seatId", player.seatId)
            msg.setResult("userId", player.userId)
            msg.setResult("tableState", self._tableState)
            msg.setResult("reward", self.ftTable.fee)
            msg.setResult("ftId", self.ftTable.ftId)
            msg.setResult("ftUserName", ftName)
            msg.setResult("ftUserId", self.ftTable.userId)
            msg.setResult("timeLong", self.runConfig.playingTime)
            msg.setResult("expirseTime", int(self._expiresTimer.getTimeOut()) if self._expiresTimer else self._tableExpiresTime)
            msg.setResult("targets", self.targets)
            GameMsg.sendMsg(msg, player.userId)




    def _tableExpires(self):
        """桌子过期了"""
        if self._tableState < TableState.START:
            self._sendExpriseHistory()
            self._sendLeaveMsg(reason=1)
            self._clearTable()
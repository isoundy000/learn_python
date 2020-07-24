#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
"""
招财模式渔场
"""

import random
import time

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from poker.entity.biz import bireport
from poker.entity.dao import onlinedata
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from hall.entity import datachangenotify
from newfish.entity import util, weakdata, mail_system
from newfish.servers.util.rpc import user_rpc
from newfish.entity.event import EnterTableEvent, LeaveTableEvent, RobberyBulletProfitEvent
from newfish.entity.lotterypool import robbery_lottery_pool
from newfish.player.robbery_player import FishRobberyPlayer
from newfish.robot import robotutil
from newfish.table.table_base import FishTable
from newfish.entity import config, store
from newfish.entity.ranking import ranking_system
from newfish.entity.redis_keys import WeakData
from newfish.entity.config import FISH_GAMEID, BULLET_KINDIDS, BRONZE_BULLET_KINDID, \
    TM_BULLET_KINDIDS
from newfish.entity.msg import GameMsg
from newfish.entity.event import CatchEvent
from newfish.entity.honor import honor_system


class FishRobberyTable(FishTable):

    def __init__(self, room, tableId):
        super(FishRobberyTable, self).__init__(room, tableId)
        # 用户离线等待时间
        self._offlineWaitSeconds = 999
        # 用户空闲超时时间
        self._idleTimeOutSeconds = 999
        # 用户无子弹时超时时间
        self._inactiveTimeOutSeconds = 999

        # table_call可用action
        self.actionMap = {
            "leave": self._clearPlayer,                     # 离开渔场
            "catch": self._verifyCatch,                     # 捕鱼
            "skill_use": self._skill_use,                   # 使用技能
            "chat": self._doTableChat,                      # 聊天
            "smile": self.doTableSmilies,                   # 表情
            "honor_push": self._honor_push,                 #
            "honor_replace": self._honor_replace,
            "treasure_rewards": self._getTreasureRewards,
            "fishActivityBtns": self._activity_all_btns,
        }
        # fish_table_call可用action
        self.actionMap2 = {
            "fire": self._verifyFire,
            "gchg": self._gunChange,
            "ping": self._ping
        }
        # 初始子弹数量
        self.bulletInitCount = self.runConfig.datas.get("bulletInitCount", {})
        # 捕获概率系数
        self.probbRatio = self.runConfig.datas.get("probbRatio", 1)

    def createPlayer(self, table, seatIndex, clientId):
        """
        新创建Player对象
        """
        return FishRobberyPlayer(table, seatIndex, clientId)

    def _verifyFire(self, msg, userId, seatId):
        """验证开火"""
        wpId = msg.getParam("wpId")
        fPosx = msg.getParam("fPosx")
        fPosy = msg.getParam("fPosy")
        bulletId = msg.getParam("bulletId")
        skillId = msg.getParam("skillId")
        timestamp = msg.getParam("timestamp", 0)
        wpConf = config.getWeaponConf(wpId, mode=self.gameMode)
        reason = 0
        player = self.players[seatId - 1]
        wpType = util.getWeaponType(wpId)
        if wpType != config.ROBBERY_WEAPON_TYPE:                                # 招财模式火炮
            reason = 1
        retMsg = MsgPack()
        retMsg.setCmd("fire")
        retMsg.setResult("gameId", FISH_GAMEID)
        retMsg.setResult("wpId", wpId)
        retMsg.setResult("bulletId", bulletId)
        retMsg.setResult("skillId", skillId)
        retMsg.setResult("timestamp", timestamp)
        retMsg.setResult("reason", reason)
        GameMsg.sendMsg(retMsg, userId)
        if reason == 0:
            retMsg.setResult("fPosx", fPosx)
            retMsg.setResult("fPosy", fPosy)
            retMsg.setResult("seatId", seatId)
            GameMsg.sendMsg(retMsg, self.getBroadcastUids(userId))
            player.addFire(bulletId, wpId, timestamp, player.fpMultiple)

    def _verifyCatch(self, msg, userId, seatId):
        """验证捕获"""
        wpId = msg.getParam("wpId")
        fIds = msg.getParam("fIds")
        skillId = msg.getParam("skillId")
        bulletId = msg.getParam("bulletId")
        player = self.players[seatId - 1]
        wpIdFire = player.getFireWpId(bulletId)
        wpType = util.getWeaponType(wpId)
        if ftlog.is_debug():
            ftlog.debug("_verifyCatch->msg =", msg, userId, wpIdFire, wpType)
        reason = 0
        if not fIds or len(fIds) > 1:
            reason = 1

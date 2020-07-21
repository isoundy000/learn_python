# -*- coding=utf-8 -*-

import random
import time
import json
from copy import deepcopy

from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.entity.dao import onlinedata, userdata, userchip
from poker.entity.game.tables.table_seat import TYSeat
from poker.protocol import router
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.robot import robotutil
from newfish.entity.honor import honor_system


def _doSit(self, msg, userId, seatId, clientId):
    """
    玩家操作, 尝试再当前的某个座位上坐下
    """
    ret = False
    try:
        ret = self._doSitDown(msg, userId, seatId, clientId)
        if self.hasRobot:
            if not ret and userId < config.ROBOT_MAX_USER_ID:
                mo = MsgPack()
                mo.setCmd("robotmgr")
                mo.setAction("robotSitFailed")
                mo.setParam("gameId", self.room.gameId)
                mo.setParam("roomId", self.room.roomId)
                mo.setParam("tableId", self.tableId)
                mo.setParam("userId", userId)
                router.sendRobotServer(mo)
            if userId > config.ROBOT_MAX_USER_ID and self.getRobotUserCount() == 0:
                robotutil.sendRobotNotifyCallUp(self)
    except:
        onlinedata.removeOnlineLoc(userId, self.roomId, self.tableId)
        ftlog.warn("_doSit error", msg, userId, seatId, clientId, self.tableId)
    return ret


def _sendTableInfo(self, userId, seatId):
    msg = MsgPack()
    msg.setCmd("table_info")
    msg.setResult("gameId", FISH_GAMEID)
    msg.setResult("roomId", self.roomId)
    msg.setResult("tableId", self.tableId)
    msg.setResult("seatId", seatId)
    msg.setResult("seatNum", self.maxSeatN)
    msg.setResult("typeName", self.typeName)
    msg.setResult("multiple", self.runConfig.multiple)
    _player = self.getPlayer(userId)
    msg.setResult("buyLimitChip", self.runConfig.minCoin)
    msg.setResult("maxSkillLevel", self.runConfig.maxSkillLevel)
    msg.setResult("minGunLevel", self.runConfig.minGunLevel)
    msg.setResult("maxGunLevel", self.runConfig.maxGunLevel)
    msg.setResult("isMatch", self.runConfig.isMatch)
    msg.setResult("matchType", self.runConfig.matchType)
    msg.setResult("tStartTime", self.startTime)
    msg.setResult("nowServerTime", time.time())
    msg.setResult("coinShortage", self.runConfig.coinShortage)
    expressionConf = config.getExpressionConf(self.bigRoomId)
    expressions = []
    for _, expression in expressionConf.iteritems():
        expressions.append(expression)
    msg.setResult("expressions", expressions)
    ftlog.debug("_sendTableInfo->msg =", msg)
    players = []
    for i in xrange(0, self.maxSeatN):
        if self.seats[i].userId != 0 and self.players[i]:
            info = self._getPlayerInfo(i + 1)
            if info:
                players.append(info)
        elif self.seats[i].userId != 0 and not self.players[i]:
            ftlog.error("_sendTableInfo error", self.seats[i].userId, self.tableId)
            self.seats[i] = TYSeat(self)
    msg.setResult("players", players)
    groups = []
    for i in xrange(0, len(self.normalFishGroups)):
        group = self.normalFishGroups[i]
        if group.isAlive(self._getNowTableTime()):
            groups.append(self._getGroupInfo(group))
    for i in xrange(0, len(self.callFishGroups)):
        group = self.callFishGroups[i]
        if group.isAlive(self._getNowTableTime(), self) and group.isVisible(self, userId):
            groups.append(self._getGroupInfo(group))

    msg.setResult("groups", groups)
    # 根据clientId判断是否屏蔽兑换提示.
    isIgnored = config.isClientIgnoredConf("exchangeTip", 1, _player.clientId or util.getClientId(userId))
    msg.setResult("ignoreExchageTip", 1 if isIgnored else 0)
    GameMsg.sendMsg(msg, userId)
    if _player and hasattr(_player, "prizeWheel") and _player.prizeWheel:
        _player.prizeWheel.sendEnergyProgress(self.runConfig.fishPool, _player.fpMultiple, self.roomId, 0)
    if _player and _player.compAct:
        _player.compAct.sendInspireInfo()


def _getPlayerInfo(self, seatId):
    ftlog.debug("_getPlayerInfo->seatId =", seatId, "userId =", self.seats[seatId - 1].userId)
    info = {}
    p = self.players[seatId - 1]
    if not p:
        ftlog.error("_getPlayerInfo error", self.seats[seatId - 1].userId, self.tableId)
        self.seats[seatId - 1] = TYSeat(self)
        return info
    info["userId"] = p.userId
    info["seatId"] = seatId
    info["name"] = p.name
    info["offline"] = p.offline
    info["uLv"] = p.level
    info["gLv"] = p.gunLevel
    info["gLvNow"] = p.nowGunLevel
    info["gunLevel"] = p.gunLv
    info["exp"] = p.exp
    info["skillSlots"] = p.getSkillSlotsInfo(0)
    info["auxiliarySkillSlots"] = p.getSkillSlotsInfo(1)
    info["usingSkill"] = p.getUsingSkillInfo()
    info["chip"] = p.chip
    info["tableChip"] = p.tableChip
    info["clip"] = p.clip
    info["honors"] = honor_system.getHonorList(p.userId)
    info["gunId"] = p.gunId
    info["gunSkinId"] = p.skinId
    info["charm"] = p.charm
    info["sex"] = p.sex
    info["vipLv"] = util.getVipShowLevel(p.userId)
    info["purl"] = p.purl
    info["redState"] = p.redState
    info["fpMultiple"] = p.fpMultiple
    info["gameResolution"] = p.gameResolution
    return info


def _main():
    from newfish.table.table_base import FishTable
    FishTable._doSit = _doSit
    FishTable._sendTableInfo = _sendTableInfo
    FishTable._getPlayerInfo = _getPlayerInfo


from freetime.core.timer import FTLoopTimer
FTLoopTimer(0.1, 0, _main).start()
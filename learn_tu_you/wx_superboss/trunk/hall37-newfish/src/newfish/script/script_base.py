# -*- coding=utf-8 -*-
"""
机器人脚本
"""
# @Author  : Kangxiaopeng
# @Time    : 2019/1/16

import random
import time

from freetime.core.timer import FTLoopTimer
from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.robot import robotutil

FIRE_TARGET_POS = {
                    1: {"start": [0, 320], "end": [1136, 640]},
                    2: {"start": [0, 640], "end": [1136, 320]},
                    3: {"start": [0, 0], "end": [1136, 320]},
                    4: {"start": [0, 320], "end": [1136, 0]}
                  }


class ScriptBase(object):

    @classmethod
    def createScript(cls, player):
        script = None
        fishPool = player.table.runConfig.fishPool
        conf = config.getRobotConf("robotScript").get(str(fishPool), {})
        scriptsConf = conf.get("scripts", [])
        if conf.get("enable", 0) == 1 and len(scriptsConf) > 0:
            level = 0
            fireRange = []
            idleRange = []
            leaveRange = []
            probb = random.randint(0, 10000)
            for script in scriptsConf:
                if script.get("probb", 0) == 0:
                    continue
                if probb > script.get("probb", 0) > 0:
                    probb -= script["probb"]
                else:
                    level = script["level"]
                    fireRange = script["fireRange"]
                    idleRange = script["idleRange"]
                    leaveRange = script["leaveRange"]
            if level == 1:
                from newfish.script.script_easy import ScriptEasy1
                script = ScriptEasy1(player, fireRange, idleRange, leaveRange)#Script%s%d % ("Easy", level)
        ftlog.debug("createScript", player.userId, fishPool, scriptsConf, (script is not None))
        return script

    def __init__(self, player, fireRange, idleRange, leaveRange):
        self.player = player
        self.userId = player.userId
        self.player.table.clip_add(player.userId, player.seatId)
        ftlog.debug("__init__", player.userId, player.chip, player.clip)
        self.fireInterval = config.getGunLevelConf(self.nowGunLevel, self.player.table.gameMode).get("interval", 0.3)
        self.updateTimer = None
        self.updateTimer = FTLoopTimer(5, -1, self._update)
        self.updateTimer.start()
        self.fireTimer = None
        self.fireTargetPos = [0, 0]
        self.bulletId = 0
        # 空闲次数
        self.idleCount = 0
        # 开火次数
        self.fireCount = 0
        # 等待离开
        self.waitLeaveCount = 0
        # 表情
        self.exp = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.fireRange = fireRange
        self.idleRange = idleRange
        self.leaveRange = leaveRange
        self.updateCount = 0
        self.needClear = False
        # 全是机器人的计数
        self.allRobotCount = 0

    @property
    def table(self):
        return self.player.table

    # @property
    # def userId(self):
    #     return self.player.userId

    @property
    def seatId(self):
        return self.player.seatId

    @property
    def nowGunLevel(self):
        return self.player.nowGunLevel

    @property
    def clip(self):
        return self.player.clip

    def clear(self):
        self._clearData()

    def _clearData(self):
        ftlog.debug("_clearData", self.userId, self.table.tableId)
        if self.updateTimer:
            self.updateTimer.cancel()
            self.updateTimer = None
        else:
            return
        if self.fireTimer:
            self.fireTimer.cancel()
        self.bulletId = 1
        self.fireCount = 0
        self.idleCount = 0
        self.waitLeaveCount = 0
        robotutil.sendRobotNotifyShutDownByUserId(self.table, self.userId)
        self.table.clearPlayer(self.player)

    def _update(self):
        pass

    def _updateFireTarget(self):
        pass

    def _fire(self):
        self.bulletId += 1
        self.bulletId %= 90
        if self.bulletId == 0:
            self.bulletId += 1
        self.player.lastActionTime = int(time.time())
        canFire = self.table.fire(self.userId, self.seatId, self.fireTargetPos, self.nowGunLevel, self.bulletId, 0, self.player.lastActionTime, 0)
        self.fireCount -= 1
        if canFire and self.fireCount > 0:
            self.fireTimer = FTLoopTimer(self.fireInterval, 0, self._fire)
            self.fireTimer.start()
        else:
            self.fireCount = 0
            self.fireTimer = None
            if canFire:
                self.idleCount = random.randint(self.idleRange[0], self.idleRange[1])
                ftlog.debug("_fire, idle", self.userId, self.idleCount)
            else:
                self.waitLeaveCount = random.randint(self.leaveRange[0], self.leaveRange[1])
                ftlog.debug("_fire, wait leave", self.userId, self.waitLeaveCount)

        # ftlog.debug("_update", self.userId, self.seatId, self.nowGunLevel, self.bulletId,
        #             self.chip, self.fireCount, self.fireTargetPos)

    def _isNeedCancelTimer(self):
        if self.updateTimer and (self.userId == 0 or self.clip == 0 or self.needClear or self.allRobotCount == 12):
            ftlog.debug("_isNeedCancelTimer", self.userId, self.clip, self.needClear, self.allRobotCount)
            self._clearData()
            return True
        self.updateCount += 1
        if self.updateCount % 12 == 0:
            conf = config.getRobotConf("robotScript").get(str(self.table.runConfig.fishPool), {})
            # 关闭机器人
            if conf.get("enable", 0) == 0:
                self.needClear = True
                return True

        for player in self.table.players:
            if player and player.isRobotUser is not True:
                self.allRobotCount = 0
                break
        else:
            self.allRobotCount += 1
        return False

    def _isWaitLeave(self):
        if self.waitLeaveCount > 0:
            self.waitLeaveCount -= 1
            if self.waitLeaveCount == 0:
                ftlog.debug("_isWaitLeave", self.userId)
                self._clearData()
            return True
        return False

    def _isIdle(self):
        if self.idleCount > 0:
            self.idleCount -= 1
            return True
        return False

    def _chat(self, isFace=1):
        chatMsg = random.choice(self.exp)
        mo = MsgPack()
        mo.setCmd("table_chat")
        mo.setResult("gameId", FISH_GAMEID)
        mo.setResult("userId", self.userId)
        mo.setResult("seatId", self.seatId)
        mo.setResult("isFace", isFace)
        mo.setResult("chatMsg", chatMsg)
        GameMsg.sendMsg(mo, self.table.getBroadcastUids())

    def _setFireTimer(self):
        ftlog.debug("_setFireTimer", self.userId, (self.fireTimer is not None), self.fireCount, self.fireInterval)
        if self.fireTimer is None:
            self.fireCount = random.randint(self.fireRange[0], self.fireRange[1])
            self.fireTimer = FTLoopTimer(self.fireInterval, 0, self._fire)
            self.fireTimer.start()
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/15

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
import poker.util.timestamp as pktimestamp
from newfish.entity.config import FISH_GAMEID
from newfish.entity.heartbeat import HeartbeatAble
from newfish.entity.fishgroup.superboss.superboss_fish_group import SuperBossFishGroup
from newfish.entity.msg import GameMsg


class OctopusFishGroup(SuperBossFishGroup):
    """
    远古寒龙Boss鱼群
    """
    def __init__(self, table):
        super(OctopusFishGroup, self).__init__()
        self.table = table
        self.dragon = None
        if self.table.room.roomConf.get("dragonConf"):
            self.dragon = Dragon(table)
            self.dragon.startHeart()

    def isAppear(self):
        return self.dragon and self.dragon.state > Dragon.ST_IDLE

    def triggerCatchFishEvent(self, event):
        catch = event.catch
        fIds = [catchMap["fId"] for catchMap in catch if catchMap["reason"] == 0]

    def dealEnterTable(self, userId):
        pass

    def frozen(self, fishId, fishType, frozenTime):
        pass


class Dragon(HeartbeatAble):
    """
    远古寒龙
    """
    # 冰龙状态
    ST_IDLE = 0
    ST_PREPARE = 1
    ST_APPEARING = 2
    ST_APPEARED = 3
    ST_LEAVE = 4
    ST_FINAL = 5
    def __init__(self, table):
        super(Dragon, self).__init__(1)
        self.table = table
        # 冰龙状态
        self._state = None

    @property
    def state(self):
        return self._state

    def _doHeartbeat(self):
        timestamp = pktimestamp.getCurrentTimestamp() + 1
        if self._state is None:
            self.postCall(self._doIdle)
        elif self._state == Dragon.ST_IDLE:
            if timestamp >= self.prepareTime:
                self.postCall(self._doPrepare)
        elif self._state == Dragon.ST_PREPARE:
            if timestamp >= self.appearingTime:
                self.postCall(self._doAppearing)
        elif self._state == Dragon.ST_APPEARING:
            if timestamp >= self.appearedTime:
                self.postCall(self._doAppeared)
        elif self._state == Dragon.ST_APPEARED:
            if timestamp >= self.leaveTime:
                self.postCall(self._doLeave)
        elif self._state == Dragon.ST_LEAVE:
            if timestamp >= self.finalTime:
                self.postCall(self._doFinal)
        elif self._state == Dragon.ST_FINAL:
            if timestamp >= self.nextTime:
                self.postCall(self._doNext)
        return 1


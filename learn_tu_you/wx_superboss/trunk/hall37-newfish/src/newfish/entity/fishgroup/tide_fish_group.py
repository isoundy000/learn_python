# -*- coding=utf-8 -*-
"""
Created by lichen on 2020/8/19.
"""

import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg


class TideFishGroup(object):
    """
    鱼潮
    """
    def __init__(self, table):
        self.table = table
        self._isAppear = False

    def isAppear(self):
        return self._isAppear

    def addTideFishGroup(self):
        """
        添加鱼潮接口
        """
        if self.table.runConfig.allTideGroupIds:
            self._isAppear = True
            FTLoopTimer(1, 0, self.clearWave).start()

    def clearWave(self):
        """
        清屏波浪
        """
        msg = MsgPack()
        msg.setCmd("clear_wave")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("roomId", self.table.roomId)
        msg.setResult("tableId", self.table.tableId)
        GameMsg.sendMsg(msg, self.table.getBroadcastUids())
        # 清屏波浪结束后出现鱼潮
        FTLoopTimer(2.5, 0, self._addTideFishGroup).start()

    def _addTideFishGroup(self):
        """
        添加鱼潮
        """
        tideGroupId = random.choice(self.table.runConfig.allTideGroupIds)
        group = self.table.insertFishGroup(tideGroupId)
        # 鱼潮出现后等3s出现鱼潮任务
        FTLoopTimer(3, 0, self._addTideTask, tideGroupId).start()
        # 鱼潮结束前重启鱼阵
        FTLoopTimer(group.totalTime - 6, 0, self._tideFishGroupLeave).start()

    def _addTideTask(self, tideGroupId):
        """
        添加鱼潮任务
        """
        self.table.tideTaskSystem.taskReady(tideGroupId)

    def _tideFishGroupLeave(self):
        """
        鱼潮结束，重启鱼阵
        """
        self._isAppear = False
        self.table.startFishGroup()

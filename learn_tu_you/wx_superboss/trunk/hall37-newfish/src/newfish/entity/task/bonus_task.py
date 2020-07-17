#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/16
import random
import time

import freetime.util.log as ftlog
from poker.entity.biz import bireport
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity import util
from newfish.entity.timer import FishTableTimer
from newfish.entity import change_notify
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.servers.util.rpc import user_rpc
from newfish.entity.task.table_task_base import TableMatchTask


class BonusTask(TableMatchTask):
    """
    奖金赛任务
    """
    def __init__(self, table, taskName, taskInterval):
        super(BonusTask, self).__init__(table, taskName, taskInterval)
        self._reload()

    def _reload(self):
        # 火炮效果(增加比赛分数)
        self.wpScoreScale = {12: 1.1, 16: 1.15, 18: 1.2}
        self.currentTask = {}
        self.userIds = []
        self.usersData = {}
        self.state = 0
        self.bonusPool = 0
        self.firstBonusScale = 1
        self.secondBonusScale = 0
        self.recordStartTime = 0
        self.sendInfoTime = 60
        self.catchId = 100000000
        # self.readyTimer = FishTableTimer(self.table)
        self.startTimer = FishTableTimer(self.table)
        self.endTimer = FishTableTimer(self.table)
        self.sendInfoTimer = None
        # self.readyTimer.setup(self.taskInterval, "task_ready", {"task": self.taskName})
        self.recordReloadTime = time.time()
        self.taskId = "%d-%d" % (self.table.tableId, 0)

    def clear(self):
        """
        清除所有公共数据
        """
        pass

    def taskReady(self, *args):
        pass

    def taskStart(self, *args):
        """
        任务开始
        """
        pass

    def taskEnd(self, *args, **kwargs):
        """
        任务结束
        """
        pass

    def clearTaskData(self, uid=None):
        """
        清除用户任务数据
        """

    def sendBonusTaskInfo(self):
        """
        发送奖金赛任务倒计时信息
        """
    def sendBonusTaskStartInfo(self, userId, timeLeft):
        """
        发送奖金赛开始消息
        """

    def newJoinTask(self, userId):
        """
        新加入任务
        """

    def newJoinTaskForAfterTheStart(self, userId):
        """
        任务开始后结束前新加入任务
        """

    def sendTaskInfoForReconnect(self, userId):
        """
        用户断线重连发送任务相关信息
        """

    def _sendTaskReward(self, player, chip, broadcastUserIds):
        """
        发送任务奖励
        """

    def _sendRanksInfo(self):
        """
        发送排名信息
        """

    def dealLeaveTable(self, event):
        """
        处理离开事件
        """

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """

    def _getRanks(self):
        """
        获得排名信息
        """

    def _getScores(self):
        """
        获得分数信息
        """

    def _getReward(self):
        """
        获得奖励信息
        """
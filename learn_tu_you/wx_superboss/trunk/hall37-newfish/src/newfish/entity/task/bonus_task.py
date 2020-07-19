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
        super(BonusTask, self).__init__(table, taskName, taskInterval)      # taskName: bonus
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
        self.currentTask = {}
        self.userIds = []
        self.usersData = {}
        self.state = 0
        self.bonusPool = 0
        self.recordStartTime = 0
        self.recordReloadTime = 0
        # if self.readyTimer:
        #     self.readyTimer.cancel()
        if self.startTimer:
            self.startTimer.cancel()
        if self.endTimer:
            self.endTimer.cancel()
        if self.sendInfoTimer:
            self.sendInfoTimer.cancel()

    def taskReady(self, *args):
        """
        任务准备
        """
        if self.sendInfoTimer:
            self.sendInfoTimer.cancel()
        self.state = 1
        tasks = config.getBonusTaskConf(self.table.runConfig.fishPool)
        self.bonusPool = self.table.room.lotteryPool.getBonusPoolCoin(self.table.tableId)
        if len(tasks) == 0 or len(self.table.getBroadcastUids()) == 0:
            self.state = 0
            pass
        if self.bonusPool < self.table.runConfig.minBonus:
            ftlog.debug("bonus->taskReady pool", self.bonusPool)
            if self.table.runConfig.systemBonus <= 0:
                self.state = 0
                endTimer = FishTableTimer(self.table)
                endTimer.setup(0, "task_end", {"uid": 0, "task": self.taskName})
                # ftlog.debug("bonus->BonusPool too little")
                # msg = MsgPack()
                # msg.setCmd("bonus_task")
                # msg.setResult("gameId", FISH_GAMEID)
                # msg.setResult("action", "fail")
                # msg.setResult("reason", 1)
                # GameMsg.sendMsg(msg, self.table.getBroadcastUids())
                return
            else:
                self.bonusPool = self.table.runConfig.systemBonus
        self.bonusPool = self.bonusPool if self.bonusPool < self.table.runConfig.multiple * 5000 else self.table.runConfig.multiple * 5000
        self.taskId = "%d-%d" % (self.table.tableId, int(time.time()))
        self.currentTask = random.choice(tasks)
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllRedTask(uid):
                self.userIds.append(uid)
        ftlog.debug("bonus-->taskReady userIds:", self.userIds, self.taskId)
        for uid in self.userIds:
            self.usersData[uid] = {"uid": uid, "task": self.currentTask, "score": 0, "lastCatchId": 0}
        readySeconds = self.currentTask["readySeconds"]
        msg = MsgPack()
        msg.setCmd("bonus_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "ready")
        msg.setResult("taskId", self.currentTask["taskId"])
        msg.setResult("bonusPool", self.bonusPool)
        msg.setResult("taskType", self.currentTask["taskType"])
        msg.setResult("targets", self.currentTask["targets"])
        GameMsg.sendMsg(msg, self.userIds)
        self.startTimer.setup(readySeconds, "task_start", {"task": self.taskName})

    def taskStart(self, *args):
        """
        任务开始
        """
        if not self.currentTask:
            return 0
        self.state = 2
        ftlog.debug("bonus-->taskStart", self.userIds, self.taskId)
        for userId in self.userIds:
            player = self.table.getPlayer(userId)
            if player:
                self.sendBonusTaskStartInfo(userId, self.currentTask["timeLong"])
                player.currentTask = [self.taskName, self.currentTask["taskId"], self.currentTask["taskType"], self.currentTask["targets"]]
        self.recordStartTime = int(time.time())
        self.endTimer.setup(self.currentTask["timeLong"], "task_end", {"task": self.taskName})
        self.sendBonusTaskInfo()
        return self.currentTask["taskId"]

    def taskEnd(self, *args, **kwargs):
        """
        任务结束
        """
        ftlog.debug("bonus->taskEnd")
        if self.state == 0:
            self.clear()
            return
        self.state = 0
        if self.currentTask:
            ranks = self._getRanks()
            reward = False
            rewardData = {}
            if ranks:
                reward = True
                rewardData = self._getReward()

    def clearTaskData(self, uid=None):
        """
        清除用户任务数据
        """

    def sendBonusTaskInfo(self):
        """
        发送奖金赛任务倒计时信息
        """
        pass


    def sendBonusTaskStartInfo(self, userId, timeLeft):
        """
        发送奖金赛开始消息
        """
        msg = MsgPack()
        msg.setCmd("bonus_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "start")
        msg.setResult("taskId", self.currentTask["taskId"])
        msg.setResult("desc", config.getMultiLangTextConf(str(self.currentTask["desc"]), lang=util.getLanguage(userId)))
        msg.setResult("timeLeft", timeLeft)
        msg.setResult("timeLong", self.currentTask["timeLong"])
        msg.setResult("taskType", self.currentTask["taskType"])
        msg.setResult("rewardType", 2)
        msg.setResult("targets", self.currentTask["targets"])
        msg.setResult("reward", {"name": config.CHIP_KINDID, "count": self.bonusPool})
        GameMsg.sendMsg(msg, userId)

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
        udatas = self.usersData.values()
        udatas.sort(key=lambda x: (x["score"], x["lastCatchId"]), reverse=True)
        ranks = {}
        rank1 = []
        rank2 = []
        score = 0


    def _getScores(self):
        """
        获得分数信息
        """

    def _getReward(self):
        """
        获得奖励信息
        """
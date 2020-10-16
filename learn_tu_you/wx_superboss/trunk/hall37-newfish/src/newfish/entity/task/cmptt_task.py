# -*- coding=utf-8 -*-
"""
Created by lichen on 16/11/21.
"""

import random
import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from newfish.entity.config import FISH_GAMEID, PEARL_KINDID, COUPON_KINDID
from newfish.entity.msg import GameMsg
from newfish.entity import config, util
from newfish.entity.timer import FishTableTimer
from newfish.servers.util.rpc import user_rpc
from newfish.entity import change_notify
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.entity.task.table_task_base import TableMatchTask


class CmpttTask(TableMatchTask):
    """
    竞争性任务(夺宝赛)
    """
    def __init__(self, table, taskName, taskInterval):
        super(CmpttTask, self).__init__(table, taskName, taskInterval)
        self._reload()
                
    def _reload(self):
        self.currentTask = {}
        self.userIds = []
        self.usersData = {}
        self.state = 0
        self.catchId = 100000000
        self.rewardType = 0
        self.recordStartTime = 0
        self.sendInfoTime = 60
        self.chestRewardId = 0
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
        self.state = 1
        if self.sendInfoTimer:
            self.sendInfoTimer.cancel()
        tasks = config.getCmpttTaskConf(self.table.runConfig.fishPool)
        if len(tasks) == 0 or len(self.table.getBroadcastUids()) == 0:
            endTimer = FishTableTimer(self.table)
            endTimer.setup(0, "task_end", {"uid": 0, "task": self.taskName})
            return
        self.taskId = "%d-%d" % (self.table.tableId, int(time.time()))
        randTask = random.choice(tasks)
        self.currentTask = copy.deepcopy(randTask)
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllNewbieTask(uid):
                self.userIds.append(uid)
        if len(self.userIds) <= 2:
            self.chestRewardId = self.currentTask["chestReward"][0]
        elif len(self.userIds) == 3:
            self.chestRewardId = self.currentTask["chestReward"][1]
        elif len(self.userIds) >= 4:
            self.chestRewardId = self.currentTask["chestReward"][2]
        for uid in self.userIds:
            self.usersData[uid] = {"uid": uid, "task": self.currentTask, "score": 0, "results": {}, "lastCatchId": 0}
        readySeconds = self.currentTask["readySeconds"]
        msg = MsgPack()
        msg.setCmd("cmptt_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "ready")
        msg.setResult("taskId", self.currentTask["taskId"])
        msg.setResult("taskType", self.currentTask["taskType"])
        msg.setResult("targets", self.currentTask["targets"])
        msg.setResult("reward", {"name": self.chestRewardId, "count": 1})
        GameMsg.sendMsg(msg, self.userIds)
        self.startTimer.setup(readySeconds, "task_start", {"task": self.taskName})

    def taskStart(self, *args):
        """
        任务开始
        """
        if not self.currentTask:
            return 0
        self.state = 2
        self.rewardType = 1
        # if len(self.userIds) in [1, 2]:
        #     self.rewardType = 4  # 宝箱+珍珠
        # elif len(self.userIds) == 3:
        #     self.rewardType = 3  # 宝箱+金币
        # elif len(self.userIds) == 4:
        #     self.rewardType = random.choice([3, 5])  # 宝箱+金币or宝箱+奖券
        for userId in self.userIds:
            player = self.table.getPlayer(userId)
            if player:
                self.sendCmpttTaskStartInfo(userId, self.currentTask["timeLong"])
                task = copy.deepcopy(self.currentTask)
                player.currentTask = [self.taskName, task["taskId"], task["taskType"], task["targets"]]
        self.recordStartTime = int(time.time())
        self.endTimer.setup(self.currentTask["timeLong"], "task_end", {"task": self.taskName})
        return self.currentTask["taskId"]

    def taskEnd(self, *args, **kwargs):
        """
        任务结束
        """
        if self.state == 0:
            self.clear()
            return
        self.state = 0
        _taskId = 0
        if self.currentTask:
            _taskId = self.currentTask["taskId"]
            ranks = kwargs.get("ranks")
            if not ranks:
                ranks = self._getRanks()
            reward = False
            dropItems = None
            player = None
            rewardDropId = 0
            rewardItem = 0
            if ranks:
                usersData = self.usersData.get(ranks[1]["uid"])
                if self._checkFinished(usersData):
                    reward = True
                    player = self.table.getPlayer(ranks[1]["uid"])
                    dropItems = self._sendTaskReward(player, self.chestRewardId, self.userIds)
                    # 夺宝赛获奖
                    from newfish.game import TGFish
                    from newfish.entity.event import WinCmpttTaskEvent
                    event = WinCmpttTaskEvent(player.userId, FISH_GAMEID, self.table.roomId, self.table.tableId)
                    TGFish.getEventBus().publishEvent(event)

            msg = MsgPack()
            msg.setCmd("cmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "finish")
            msg.setResult("taskId", self.currentTask["taskId"])
            msg.setResult("taskType", self.currentTask["taskType"])
            msg.setResult("ranks", ranks)
            if reward and player:
                msg.setResult("reward", dropItems)
            GameMsg.sendMsg(msg, self.userIds)
        self.clearTaskData()
        if _taskId and self.table.ttAutofillFishGroup:
            self.table.ttAutofillFishGroup.endAutofill(0, _taskId)

    def clearTaskData(self, uid=None):
        """
        清除用户任务数据
        """
        if uid:
            player = self.table.getPlayer(uid)
            if player:
                player.currentTask = None
            if uid in self.userIds:
                self.userIds.remove(uid)
            if uid in self.usersData:
                del self.usersData[uid]
        if self.state == 0 or len(self.userIds) == 0:
            for userId in self.userIds:
                player = self.table.getPlayer(userId)
                if player:
                    player.currentTask = None
            self.clear()

    def sendCmpttTaskInfo(self):
        """
        发送夺宝赛任务倒计时信息
        """
        userIds = []
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllNewbieTask(uid):
                userIds.append(uid)
        if self.sendInfoTimer:
            self.sendInfoTimer.cancel()
        if not userIds:
            return
        if self.state == 0:
            self.sendInfoTimer = FTLoopTimer(self.sendInfoTime, 0, self.sendCmpttTaskInfo)
            self.sendInfoTimer.start()
        else:
            return
        timeLeft = int(self.taskInterval) - int(time.time() - self.recordReloadTime)
        if timeLeft <= 0:
            return
        msg = MsgPack()
        msg.setCmd("cmptt_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "info")
        msg.setResult("timeLeft", timeLeft)
        GameMsg.sendMsg(msg, userIds)

    def sendCmpttTaskStartInfo(self, userId, timeLeft):
        """
        发送夺宝赛开始消息
        """
        msg = MsgPack()
        msg.setCmd("cmptt_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "start")
        msg.setResult("taskId", self.currentTask["taskId"])
        desc = config.getMultiLangTextConf(str(self.currentTask["desc"]), lang=util.getLanguage(userId))
        if desc.find("%d") >= 0:
            desc = desc % self.currentTask["targets"].get("number1", 0)
        msg.setResult("desc", desc)
        msg.setResult("timeLeft", timeLeft)
        msg.setResult("timeLong", self.currentTask["timeLong"])
        msg.setResult("taskType", self.currentTask["taskType"])
        msg.setResult("rewardType", self.rewardType)
        msg.setResult("targets", self.currentTask["targets"])
        msg.setResult("reward", {"name": self.chestRewardId, "count": 1})
        GameMsg.sendMsg(msg, userId)

    def newJoinTask(self, userId):
        """
        新加入任务
        """
        if self.state == 0:
            return
        self.userIds.append(userId)
        self.usersData[userId] = {
            "uid": userId,
            "task": copy.deepcopy(self.currentTask),
            "score": 0,
            "results": {},
            "lastCatchId": 0
        }

    def newJoinTaskForAfterTheStart(self, userId):
        """
        任务开始后结束前新加入任务
        """
        if self.state != 2:
            return
        if userId is None or len(self.userIds) == 0:
            return
        timeLeft = int(self.currentTask["timeLong"]) - int(time.time() - self.recordStartTime)
        if timeLeft <= 10:
            return
        self.newJoinTask(userId)
        # 发送开始消息，给出任务剩余时间
        self.sendCmpttTaskStartInfo(userId, timeLeft)
        # 发送排名信息
        self._sendRanksInfo()
        # 设置用户当前任务信息
        player = self.table.getPlayer(userId)
        if player:
            task = copy.deepcopy(self.currentTask)
            player.currentTask = [self.taskName, task["taskId"], task["taskType"], task["targets"]]

    def sendTaskInfoForReconnect(self, userId):
        """
        用户断线重连发送任务相关信息
        """
        if self.state != 2:
            return
        timeLeft = int(self.currentTask["timeLong"]) - int(time.time() - self.recordStartTime)
        if timeLeft <= 5:
            return
        self.sendCmpttTaskStartInfo(userId, timeLeft)
        self._sendRanksInfo()

    def _sendTaskReward(self, player, chestId, broadcastUserIds):
        """
        发送任务奖励
        """
        chestRewards = chest_system.getChestRewards(player.userId, chestId)
        util.addRewards(player.userId, chestRewards, "BI_NFISH_CMPTT_TASK_REWARDS", roomId=self.table.roomId, tableId=self.table.tableId)
        from newfish.game import TGFish
        from newfish.entity.event import GainChestEvent
        from newfish.entity.chest.chest_system import ChestFromType
        event = GainChestEvent(player.userId, FISH_GAMEID, chestId, ChestFromType.Cmptt_Ncmptt_Bonus_Task)
        TGFish.getEventBus().publishEvent(event)
        dropItems = {"chest": chestId, "chestRewards": chestRewards, "type": 0}
        return dropItems

    def _sendRanksInfo(self):
        """
        发送排名信息
        """
        if self.currentTask:
            msg = MsgPack()
            msg.setCmd("cmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "rank")
            msg.setResult("taskId", self.currentTask["taskId"])
            msg.setResult("taskType", self.currentTask["taskType"])
            msg.setResult("ranks", self._getRanks())
            GameMsg.sendMsg(msg, self.userIds)

    def dealLeaveTable(self, event):
        """
        处理离开事件
        """
        if self.state == 0:
            return
        uid = event.userId
        self.clearTaskData(uid)
        self._sendRanksInfo()

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """
        if self.state != 2:
            return 
        uid = event.userId
        fishTypes = event.fishTypes
        if uid not in self.userIds:
            return

        fpMultiple = self.getEventFpMultiple(event)
        score = 0
        player = self.table.getPlayer(uid)
        usersData = self.usersData.get(uid)
        taskType = usersData["task"]["taskType"]
        targets = usersData["task"]["targets"]
        target1 = targets.get("target1", 0)
        target2 = targets.get("target2", 0)
        multipleTarget1 = 14000 + target1 % 11000
        multipleTarget2 = 14000 + target2 % 11000
        number1 = targets.get("number1", 999)
        number2 = targets.get("number2", 999)

        if taskType != 1 and "progress" not in usersData["results"]:
            usersData["results"]["progress"] = 0
        if taskType == 1:  # 指定数量特定鱼
            if target1 not in fishTypes and target2 not in fishTypes and multipleTarget1 not in fishTypes and multipleTarget2 not in fishTypes:
                return
            if (target1 in fishTypes or multipleTarget1 in fishTypes) and target1 not in usersData["results"]:
                usersData["results"][target1] = 0
            if (target2 in fishTypes or multipleTarget2 in fishTypes) and target2 not in usersData["results"]:
                usersData["results"][target2] = 0
            if self._checkFinished(usersData):
                return
            if player and player.currentTask:
                if target1 in fishTypes or multipleTarget1 in fishTypes:
                    target1Score = fishTypes.count(target1) + fishTypes.count(multipleTarget1)
                    if usersData["results"][target1] + target1Score >= number1:
                        score += (number1 - usersData["results"][target1])
                        usersData["results"][target1] = number1
                        if player.currentTask[3].has_key("target1"):
                            player.currentTask[3].pop("target1")
                    else:
                        score += target1Score
                        usersData["results"][target1] += target1Score
                if target2 in fishTypes or multipleTarget2 in fishTypes:
                    target2Score = fishTypes.count(target2) + fishTypes.count(multipleTarget2)
                    if usersData["results"][target2] + target2Score >= number2:
                        score += (number2 - usersData["results"][target2])
                        usersData["results"][target2] = number2
                        if player.currentTask[3].has_key("target2"):
                            player.currentTask[3].pop("target2")
                    else:
                        score += target2Score
                        usersData["results"][target2] += target2Score
        elif taskType == 2:  # 指定分数
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.table.typeName, fpMultiple)
                if fishConf.get("itemId", 0) in config.BULLET_KINDIDS:
                    score += (fishConf.get("score", 0) * config.BULLET_KINDIDS[fishConf.get("itemId", 0)] / fpMultiple)
                else:
                    score += fishConf.get("score", 0)
            usersData["results"]["progress"] += score

        usersData["score"] += score
        if score == 0:
            return
        usersData["lastCatchId"] = self.catchId
        self.catchId -= 1
        self._sendRanksInfo()
        if self._checkFinished(usersData):
            self.endTimer.cancel()
            self.taskEnd(ranks=self._getRanks())
            return

    def _getRanks(self):
        """
        获得排名信息
        """
        udatas = self.usersData.values()
        if udatas:
            udatas.sort(key=lambda x: (x["score"], x["lastCatchId"]), reverse=True)
        ranks = {}
        for m in xrange(len(udatas)):
            if udatas[m]["score"] == 0:
                continue
            ranks[m + 1] = {"uid": udatas[m]["uid"], "results": udatas[m]["results"]}
        return ranks

    def _checkFinished(self, usersData):
        """
        检查是否完成任务
        """
        results = usersData["results"]
        taskType = usersData["task"]["taskType"]
        targets = usersData["task"]["targets"]
        target1 = targets.get("target1", 0)
        target2 = targets.get("target2", 0)
        number1 = targets.get("number1", 999)
        number2 = targets.get("number2", 999)
        finished = False
        if taskType == 1:
            if len(targets.keys()) == 3:    # 一个target会对应有3个字段
                if target1 in results.keys() and results[target1] >= number1:
                    finished = True
            else:
                if target1 in results.keys() and results[target1] >= number1 and \
                   target2 in results.keys() and results[target2] >= number2:
                    finished = True
        else:
            if usersData["results"].get("progress", 0) >= number1:
                finished = True
        return finished
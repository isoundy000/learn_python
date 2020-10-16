# -*- coding=utf-8 -*-
"""
Created by lichen on 16/1/12.
"""

import random
import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity import util
from newfish.entity.timer import FishTableTimer
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.entity.task.table_task_base import TableMatchTask, TaskState


class NcmpttTask(TableMatchTask):
    """
    非竞争性任务(限时任务)
    """
    def __init__(self, table, taskName, taskInterval):
        super(NcmpttTask, self).__init__(table, taskName, taskInterval)     # taskName: "ncmptt"
        self._reload()

    def _reload(self):
        """重新加载"""
        self.wpFishNumScale = {11: 0.9, 14: 0.8, 15: 0.7}   # 火炮效果(降低任务鱼数量)
        self.userIds = []                                   # 玩家uids列表
        self.usersData = {}                                 # {"uid": {"uid": uid, "task": task, "targets": targets, "state": state, "rewardType": 1, "results": {}}}
        self.userStartTimer = {}                            # 开始定时器 {"uid": startTimer}
        self.userEndTimer = {}                              # 结束定时器
        # self.readyTimer = FishTableTimer(self.table)
        # self.readyTimer.setup(self.taskInterval, "task_ready", {"task": self.taskName})
        self.recordStartTime = 0                            # 开始时间
        self.taskId = "%d-%d" % (self.table.tableId, 0)     # 任务Id

    def clear(self):
        """
        清除所有公共数据
        """
        self.userIds = []
        self.usersData = {}
        self.recordStartTime = 0
        # if self.readyTimer:
        #     self.readyTimer.cancel()

    def getTaskState(self, userId):
        """获取任务状态"""
        return 0

    def taskReady(self, *args):
        """
        任务准备
        :param args:
        """
        tasks = config.getNcmpttTaskConf(self.table.runConfig.fishPool)
        if len(tasks) == 0 or len(self.table.getBroadcastUids()) == 0:
            endTimer = FishTableTimer(self.table)
            endTimer.setup(0, "task_end", {"uid": 0, "task": self.taskName})
            return
        self.taskId = "%d-%d" % (self.table.tableId, int(time.time()))
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllRedTask(uid):                                    # 获得所有已完成的引导
                self.userIds.append(uid)
        for uid in self.userIds:
            randTask = random.choice(tasks)
            task = copy.deepcopy(randTask)
            # player = self.table.getPlayer(uid)                                # 火炮装扮减少任务鱼数量(暂时不用)
            # if player:
            # if player.gunSkinId in self.wpFishNumScale.keys():
            #     fNumScale = self.wpFishNumScale.get(player.gunSkinId, 1)
            #     for fId in task["targets"]:
            #         fNum = task["targets"][fId]["fishNum"]
            #         fNum = int(round(int(fNum) * fNumScale))
            #         fNum = fNum if fNum >= 1 else 1
            #         task["targets"][fId]["fishNum"] = fNum
            targets = task["targets"]
            readySeconds = task["readySeconds"]
            state = TaskState.TS_Ready                                          # 任务即将开始
            self.usersData[uid] = {"uid": uid, "task": task, "targets": targets, "state": state, "rewardType": 1, "results": {}}
            msg = MsgPack()
            msg.setCmd("ncmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", uid)
            msg.setResult("action", "ready")
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            GameMsg.sendMsg(msg, uid)
            startTimer = FishTableTimer(self.table)
            self.userStartTimer[uid] = startTimer
            startTimer.setup(readySeconds, "task_start", {"uid": uid, "task": self.taskName})

    def taskStart(self, uid):
        """
        任务开始
        """
        if uid and uid in self.usersData:
            task = copy.deepcopy(self.usersData[uid]["task"])
            userData = self.usersData[uid]
            userData["state"] = TaskState.TS_Start
            # if chest_system.getChestIdleOrder(uid) == -1 or self.taskName == "ncmpttA" or self.taskName == "ncmpttB":
            #     userData["rewardType"] = 2
            self.sendNcmpttTaskStartInfo(uid, task["timeLong"])
            # 设置当前任务
            player = self.table.getPlayer(uid)
            if player:
                player.currentTask = [self.taskName, task["taskId"], task["taskType"], task["targets"]]
            endTimer = FishTableTimer(self.table)
            self.userEndTimer[uid] = endTimer
            self.recordStartTime = int(time.time())
            endTimer.setup(task["timeLong"], "task_end", {"uid": uid, "task": self.taskName})
            ftlog.debug("ncmptt->taskStart userId", uid, self.taskId, task["taskId"])
            return task["taskId"]
        else:
            return 0

    def taskEnd(self, *args, **kwargs):
        """
        任务结束
        """
        if int(args[0]) in self.userIds:
            uid = int(args[0])
            ranks = self._getRanks(uid)
            reward = False
            dropItems = None
            player = None
            task = self.usersData[uid]["task"]
            _taskId = task["taskId"]
            userData = self.usersData[uid]
            userData["state"] = TaskState.TS_End
            ftlog.debug("ncmptt->taskEnd1 = ", args[0], kwargs, ranks, userData)
            if ranks and self._checkFinished(userData):
                reward = True
                player = self.table.getPlayer(uid)
                if userData["rewardType"] == 1:
                    rewardDropId = task["chestReward"]
                else:
                    rewardDropId = task["coinReward"]
                # dropType, dropItem = drop_system.getDropItem(rewardDropId)
                dropItems = self._sendTaskReward(player, 1, rewardDropId, self.userIds)
                # 限时任务获奖
                from newfish.game import TGFish
                from newfish.entity.event import WinNcmpttTaskEvent
                event = WinNcmpttTaskEvent(player.userId, FISH_GAMEID, self.table.roomId, self.table.tableId)
                TGFish.getEventBus().publishEvent(event)

            msg = MsgPack()
            msg.setCmd("ncmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", uid)
            msg.setResult("action", "finish")                   # 完成奖励
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("ranks", ranks)
            if reward:
                if player:
                    msg.setResult("reward", dropItems)
                else:
                    ftlog.warn("ncmptt->taskEnd cannot get player taskId =", self.taskId, "ranks =", ranks)
            GameMsg.sendMsg(msg, uid)
            self.clearTaskData(uid)
            if _taskId and self.table.ttAutofillFishGroup:
                self.table.ttAutofillFishGroup.endAutofill(uid, _taskId)

    def clearTaskData(self, uid=None):
        """
        清除用户任务数据
        """
        if uid in self.userIds:
            self.userIds.remove(uid)
        if uid in self.usersData:
            player = self.table.getPlayer(uid)
            if player:
                player.currentTask = None
            del self.usersData[uid]
        if uid in self.userStartTimer:
            userStartTimer = self.userStartTimer[uid]
            if userStartTimer:
                userStartTimer.cancel()
            del self.userStartTimer[uid]
        if uid in self.userEndTimer:
            userEndTimer = self.userEndTimer[uid]
            if userEndTimer:
                userEndTimer.cancel()
            del self.userEndTimer[uid]
        if len(self.userIds) == 0:
            self.clear()

    def sendNcmpttTaskStartInfo(self, userId, timeLeft):
        """
        发送限时任务开始消息
        :param userId: 玩家Id
        :param timeLeft: 剩余时间
        """
        userData = self.usersData.get(userId, {})
        task = userData.get("task")
        if userData and task:
            msg = MsgPack()
            msg.setCmd("ncmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", userId)
            msg.setResult("action", "start")
            msg.setResult("taskId", task["taskId"])
            desc = config.getMultiLangTextConf(str(task["desc"]), lang=util.getLanguage(userId))
            if desc.find("%d") >= 0:
                desc = desc % (task["targets"].get("target1") or task["targets"].get("number1", 0))
            msg.setResult("desc", desc)
            msg.setResult("timeLeft", timeLeft)
            msg.setResult("timeLong", task["timeLong"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("rewardType", userData["rewardType"])
            msg.setResult("targets", task["targets"])
            msg.setResult("reward", {"name": task["chestReward"], "count": 1})
            GameMsg.sendMsg(msg, userId)

    def newJoinTask(self, userId):
        """
        新加入任务
        """
        pass

    def newJoinTaskForAfterTheStart(self, userId):
        """
        任务开始后结束前新加入任务
        """
        pass

    def sendTaskInfoForReconnect(self, userId):
        """
        用户断线重连发送任务相关信息
        """
        userData = self.usersData.get(userId, {})
        task = userData.get("task")
        if task:
            timeLeft = int(task["timeLong"]) - int(time.time() - self.recordStartTime)
            if timeLeft <= 5:
                return
            self.sendNcmpttTaskStartInfo(userId, timeLeft)
            self._sendRanksInfo(userId)

    def _sendTaskReward(self, player, dropType, dropItem, broadcastUserIds):
        """
        发送任务奖励
        """
        dropItems = None
        if dropType == 1:       # 宝箱
            chestRewards = chest_system.getChestRewards(player.userId, dropItem)
            util.addRewards(player.userId, chestRewards, "BI_NFISH_NCMPTT_TASK_REWARDS", roomId=self.table.roomId, tableId=self.table.tableId)
            dropItems = {"chest": dropItem, "chestRewards": chestRewards, "chip": 0, "type": 0}
            from newfish.game import TGFish
            from newfish.entity.event import GainChestEvent
            from newfish.entity.chest.chest_system import ChestFromType
            event = GainChestEvent(player.userId, FISH_GAMEID, dropItem, ChestFromType.Cmptt_Ncmptt_Bonus_Task)
            TGFish.getEventBus().publishEvent(event)
            # chest_system.newChestItem(player.userId, dropItem["name"], "BI_NFISH_NCMPTT_TASK_REWARDS", self.table.roomId)
        elif dropType == 2:     # 金币
            dropItems = {"chest": 0, "chip": dropItem["count"], "type": 1}
            rewards = [{"name": "tableChip", "count": dropItem["count"]}]
            util.addRewards(player.userId, rewards, "BI_NFISH_NCMPTT_TASK_REWARDS", self.table.roomId)
        return dropItems

    def _sendRanksInfo(self, userId):
        """
        发送排名信息
        """
        userData = self.usersData.get(userId, {})
        task = userData.get("task")
        results = userData.get("results")
        if task and results:
            msg = MsgPack()
            msg.setCmd("ncmptt_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "rank")
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("ranks", self._getRanks(userId))
            GameMsg.sendMsg(msg, userId)

    def dealLeaveTable(self, event):
        """
        处理离开事件
        """
        uid = event.userId
        if uid not in self.usersData:
            return
        self.clearTaskData(uid)

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """
        fpMultiple = self.getEventFpMultiple(event)
        uid = event.userId
        fishTypes = event.fishTypes
        if uid not in self.userIds:
            return
        usersData = self.usersData.get(uid, {})
        if usersData and usersData["state"] != TaskState.TS_Start:
            return
        score = 0
        for fishType in fishTypes:
            fishConf = config.getFishConf(fishType, self.table.typeName, fpMultiple)
            if fishConf.get("itemId", 0) in config.BULLET_KINDIDS:
                score += (fishConf.get("score", 0) * config.BULLET_KINDIDS[fishConf.get("itemId", 0)] / fpMultiple)
            else:
                score += fishConf.get("score", 0)

        taskType = usersData["task"]["taskType"]
        player = self.table.getPlayer(uid)
        targets = usersData["task"]["targets"]
        target1 = targets.get("target1", 0)
        multipleTarget1 = 14000 + target1 % 11000
        target2 = targets.get("target2", 0)
        multipleTarget2 = 14000 + target2 % 11000
        number1 = targets.get("number1", 999)
        number2 = targets.get("number2", 999)

        _isUserDataUpdate = False
        if taskType != 1 and "progress" not in usersData["results"]:
            usersData["results"]["progress"] = 0
            _isUserDataUpdate = True
        if taskType == 1:  # 指定数量特定鱼
            if target1 not in fishTypes and target2 not in fishTypes and multipleTarget1 not in fishTypes and multipleTarget2 not in fishTypes:
                return
            if (target1 in fishTypes or multipleTarget1 in fishTypes) and target1 not in usersData["results"]:
                usersData["results"][target1] = 0
            if (target2 in fishTypes or multipleTarget2 in fishTypes) and target2 not in usersData["results"]:
                usersData["results"][target2] = 0
            if self._checkFinished(usersData):
                return
            if target1 in fishTypes or multipleTarget1 in fishTypes:
                score = fishTypes.count(target1) + fishTypes.count(multipleTarget1)
                usersData["results"][target1] += score
                _isUserDataUpdate = True
            if target2 in fishTypes or multipleTarget2 in fishTypes:
                score = fishTypes.count(target2) + fishTypes.count(multipleTarget2)
                usersData["results"][target2] += score
                _isUserDataUpdate = True
            if player and player.currentTask:
                if (target1 in fishTypes or multipleTarget1 in fishTypes) and usersData["results"][target1] >= number1:
                    usersData["results"][target1] = number1
                    _isUserDataUpdate = True
                    if player.currentTask[3].has_key("target1"):
                        player.currentTask[3].pop("target1")
                if (target2 in fishTypes or multipleTarget2 in fishTypes) and usersData["results"][target2] >= number2:
                    usersData["results"][target2] = number2
                    _isUserDataUpdate = True
                    if player.currentTask[3].has_key("target2"):
                        player.currentTask[3].pop("target2")
                ftlog.debug("dealCatchEvent->player.currentTask", player.currentTask)
        elif taskType == 2:  # 指定分数
            usersData["results"]["progress"] += score
            _isUserDataUpdate = True
        elif taskType == 3:  # 一炮指定分数
            if score >= usersData["targets"]["target1"]:
                usersData["results"]["progress"] += 1
                _isUserDataUpdate = True
        elif taskType == 4:  # 指定数量任意鱼
            usersData["results"]["progress"] += len(fishTypes)
            _isUserDataUpdate = True
        elif taskType == 5:  # 指定Combo数
            if player and player.combo >= target1:
                usersData["results"]["progress"] += 1
                _isUserDataUpdate = True
        if _isUserDataUpdate:
            self._sendRanksInfo(uid)

        if self._checkFinished(usersData):
            if uid not in self.userEndTimer:
                return
            userEndTimer = self.userEndTimer[uid]
            userEndTimer.cancel()
            self.taskEnd(uid)

    def _getRanks(self, uid):
        """
        获得排名信息
        """
        if uid not in self.userIds:
            return
        userData = self.usersData[uid]
        ranks = {"uid": userData["uid"], "results": userData["results"]}
        ftlog.debug("ncmptt->_getRanks =", ranks)
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
        ftlog.debug("ncmptt->_checkFinished.targets,", targets)
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
        ftlog.debug("ncmptt->checkFinished,", finished)
        return finished
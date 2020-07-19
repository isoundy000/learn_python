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
from newfish.entity import change_notify
from newfish.entity import drop_system
from newfish.entity.chest import chest_system
from newfish.entity.task.table_task_base import TaskState
from freetime.core.timer import FTLoopTimer


class TideTask(object):
    """
    非竞争性任务(鱼潮任务)
    """
    def __init__(self, table):
        self.table = table
        self.conf = config.getTideTask(self.table.runConfig.fishPool)
        self._reload()

    def _reload(self):
        self.userIds = []
        self.usersData = {}
        self.userStartTimer = {}
        self.userEndTimer = {}
        self.recordStartTime = 0
        self.taskId = 0
        self.state = 0

    def clear(self):
        """
        清除所有公共数据
        """
        self.userIds = []
        self.usersData = {}
        self.recordStartTime = 0

    def getTaskState(self):
        """获取任务状态"""
        return self.state

    def taskInit(self, *args):
        """提示消息"""
        tideId = args[0]
        task_conf = self.conf.get(tideId)
        if len(task_conf) == 0 or len(self.table.getBroadcastUids()) == 0:
            return
        self.taskId = task_conf["taskId"]
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllRedTask(uid):
                self.userIds.append(uid)
        ftlog.debug("tideTask->taskInit userIds:", self.userIds, self.taskId)
        self.state = TaskState.TS_TIP
        for uid in self.userIds:



    def taskReady(self, *args):
        """
        任务准备
        """
        tideId = args[0]
        tasks = self.conf.get(tideId)
        if len(tasks) == 0 or len(self.table.getBroadcastUids()) == 0:
            return
        self.taskId = tasks["taskId"]
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllRedTask(uid):
                self.userIds.append(uid)
        ftlog.debug("ncmptt->taskReady userIds:", self.userIds, self.taskId, self.taskName, self.taskInterval)
        for uid in self.userIds:
            randTask = random.choice(tasks)
            task = copy.deepcopy(randTask)
            ftlog.debug("taskReady->task =", task)
            targets = task["targets"]
            readySeconds = task["readySeconds"]
            state = TaskState.TS_Ready
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
            FTLoopTimer(readySeconds, "task_start", {"uid": uid, "task": self.taskName})

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
        ftlog.debug("ncmptt->taskEnd = ", args[0], kwargs, self.userIds)
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
            msg.setResult("action", "finish")
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("ranks", ranks)
            if reward:
                if player:
                    msg.setResult("reward", dropItems)
                else:
                    ftlog.warn("ncmptt->taskEnd cannot get player taskId =", self.taskId, "ranks =", ranks)
            ftlog.debug("ncmptt->taskEnd userId", uid, self.taskId, ranks, _taskId)
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
            #msg.setResult("desc", task["desc"])
            descId = task["desc"]
            desc = config.getMultiLangTextConf(str(descId), lang=util.getLanguage(userId))
            if desc.find("%d") >= 0:
                cnt = task["targets"].get("target1") or task["targets"].get("number1", 0)
                desc = desc % cnt
            msg.setResult("desc", desc)
            msg.setResult("timeLeft", timeLeft)
            msg.setResult("timeLong", task["timeLong"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("rewardType", userData["rewardType"])
            msg.setResult("targets", task["targets"])
            msg.setResult("reward", {"name":task["chestReward"], "count":1})
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
        ftlog.debug("doNcmpttTaskReward:", player.userId, dropType, dropItem)
        dropItems = None
        if dropType == 1:   # 宝箱
            chestRewards = chest_system.getChestRewards(player.userId, dropItem)
            util.addRewards(player.userId, chestRewards, "BI_NFISH_NCMPTT_TASK_REWARDS", roomId=self.table.roomId, tableId=self.table.tableId)
            dropItems = {"chest": dropItem, "chestRewards": chestRewards, "chip": 0, "type": 0}
            from newfish.game import TGFish
            from newfish.entity.event import GainChestEvent
            from newfish.entity.chest.chest_system import ChestFromType
            event = GainChestEvent(player.userId, FISH_GAMEID, dropItem, ChestFromType.Cmptt_Ncmptt_Bonus_Task)
            TGFish.getEventBus().publishEvent(event)
            # chest_system.newChestItem(player.userId, dropItem["name"], "BI_NFISH_NCMPTT_TASK_REWARDS", self.table.roomId)
        elif dropType == 2: # 金币
            dropItems = {"chest": 0, "chip": dropItem["count"], "type": 1}
            rewards = [{"name": "tableChip", "count": dropItem["count"]}]
            util.addRewards(player.userId, rewards, "BI_NFISH_NCMPTT_TASK_REWARDS", self.table.roomId)
        ftlog.debug("doNcmpttTaskReward end ...............", dropItems)
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
        ftlog.debug("ncmptt->xxootask user leave1:", event.userId, self.taskId)
        if uid not in self.usersData:
            return
        ftlog.debug("ncmptt->xxootask user leave2:", event.userId, self.taskId)
        self.clearTaskData(uid)

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """
        fpMultiple = self.getEventFpMultiple(event)
        uid = event.userId
        fishTypes = event.fishTypes
        ftlog.debug("ncmptt->dealCatchEvent:", str(event.__dict__))
        if uid not in self.userIds:
            ftlog.debug("ncmptt->invalid userId", uid, self.userIds)
            return
        usersData = self.usersData.get(uid, {})
        if usersData and usersData["state"] != TaskState.TS_Start:
            ftlog.debug("ncmptt->invalid state", usersData["state"])
            return
        ftlog.debug("ncmptt->valid event", str(event.__dict__))
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
        if taskType == 1:      # 指定数量特定鱼
            if target1 not in fishTypes and target2 not in fishTypes and \
               multipleTarget1 not in fishTypes and multipleTarget2 not in fishTypes:
                ftlog.debug("ncmptt->invalid fishTypes", fishTypes)
                return
            if (target1 in fishTypes or multipleTarget1 in fishTypes) and target1 not in usersData["results"]:
                usersData["results"][target1] = 0
            if (target2 in fishTypes or multipleTarget2 in fishTypes) and target2 not in usersData["results"]:
                usersData["results"][target2] = 0
            if self._checkFinished(usersData):
                ftlog.debug("already full", uid, target1, target2)
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

        elif taskType == 2:    # 指定分数
            usersData["results"]["progress"] += score
            _isUserDataUpdate = True
        elif taskType == 3:    # 一炮指定分数
            if score >= usersData["targets"]["target1"]:
                usersData["results"]["progress"] += 1
                _isUserDataUpdate = True
        elif taskType == 4:    # 指定数量任意鱼
            usersData["results"]["progress"] += len(fishTypes)
            _isUserDataUpdate = True
        elif taskType == 5:    # 指定Combo数
            if player and player.combo >= target1:
                usersData["results"]["progress"] += 1
                _isUserDataUpdate = True

        if _isUserDataUpdate:
            self._sendRanksInfo(uid)
        else:
            ftlog.debug("ncmptt->dealCatchEvent, task data not changed! uid =", uid)
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
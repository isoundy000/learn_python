# -*- coding=utf-8 -*-
"""
Created by lichen on 16/1/12.
"""

import time
import copy

import freetime.util.log as ftlog
from freetime.entity.msg import MsgPack
from newfish.entity.config import FISH_GAMEID
from newfish.entity.msg import GameMsg
from newfish.entity import config
from newfish.entity import util
from newfish.entity.task.table_task_base import TaskState
from freetime.core.timer import FTLoopTimer


class TideTask(object):
    """
    非竞争性任务(鱼潮任务)
    """
    def __init__(self, table):
        self.table = table
        self.fpMultiple = self.table.runConfig.multiple
        self._reload()

    def _reload(self):
        self.userIds = []
        self.usersData = {}
        self.recordStartTime = 0
        self.state = 0
        self.taskId = "%d-%d" % (self.table.tableId, 0)
        self.conf = config.getTideTaskConf()

    def clear(self):
        """
        清除所有公共数据
        """
        self._reload()

    def getTaskState(self):
        """获取任务状态"""
        return self.state

    def taskReady(self, tideId):
        """准备消息"""
        tideId = str(tideId)
        if tideId not in self.conf:
            return
        if len(self.table.getBroadcastUids()) == 0:
            return
        task = self.conf[tideId]
        if not task:
            return
        if self.state != TaskState.TS_End:
            return
        self.taskId = "%d-%d" % (self.table.tableId, int(time.time()))
        for uid in self.table.getBroadcastUids():
            if util.isFinishAllNewbieTask(uid):
                self.userIds.append(uid)
        self.state = TaskState.TS_TIP
        targets = task["targets"]
        for uid in self.userIds:
            self.usersData[uid] = {"uid": uid, "task": task, "targets": targets, "state": TaskState.TS_Ready, "rewardType": task["rewardType"], "results": {}}
        msg = MsgPack()
        msg.setCmd("tide_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "ready")
        msg.setResult("taskId", task["taskId"])
        msg.setResult("taskType", task["taskType"])
        msg.setResult("targets", targets)
        msg.setResult("rewards", task["rewards"])
        GameMsg.sendMsg(msg, self.userIds)
        FTLoopTimer(int(task["tipSeconds"]) + int(task["readySeconds"]), 0, self.taskStart, tideId).start()      # 提示秒数 准备秒数4s 3、2、1、开始比赛

    def taskStart(self, tideId):
        """
        任务开始
        """
        self.state = TaskState.TS_Start
        for uid in self.usersData:
            task = self.usersData[uid]["task"]
            userData = self.usersData[uid]
            userData["state"] = TaskState.TS_Start
            self.sendTideTaskStartInfo(uid, task["timeLong"])
            player = self.table.getPlayer(uid)
            if player:
                player.currentTask = [task["taskId"], task["taskType"], task["targets"]]        # 设置当前任务
        self.recordStartTime = int(time.time())
        FTLoopTimer(int(self.conf[tideId]["timeLong"]), 0, self.taskEnd).start()                # 记录多长时间结束任务
        return self.conf[tideId]["taskId"]

    def taskEnd(self, userId=None):
        """
        任务结束
        """
        if not userId:
            self.state = TaskState.TS_End
        tmp_userIds = copy.deepcopy(self.userIds)
        if ftlog.is_debug():
            ftlog.debug("taskEnd", tmp_userIds, self.usersData, self.recordStartTime, int(time.time()))
        for uid in tmp_userIds:
            if userId and userId != uid:
                continue
            if uid not in self.usersData:
                continue
            ranks = self._getRanks(uid)
            reward = False
            dropItems = None
            player = None
            task = self.usersData[uid]["task"]
            userData = self.usersData[uid]
            userData["state"] = TaskState.TS_End
            if ranks and self._checkFinished(userData):
                reward = True
                player = self.table.getPlayer(uid)
                rewardDropId = task["rewards"]
                dropItems = self._sendTaskReward(player, userData["rewardType"], rewardDropId)
            msg = MsgPack()
            msg.setCmd("tide_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", uid)
            msg.setResult("action", "finish")
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            if reward and player:
                msg.setResult("reward", dropItems)
            GameMsg.sendMsg(msg, uid)
            self.clearTaskData(uid)

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
        if len(self.userIds) == 0:
            self.clear()

    def sendTideTaskStartInfo(self, userId, timeLeft):
        """
        发送限时任务开始消息
        :param userId: 玩家Id
        :param timeLeft: 剩余时间
        """
        userData = self.usersData.get(userId, {})
        task = userData.get("task")
        if userData and task:
            msg = MsgPack()
            msg.setCmd("tide_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("userId", userId)
            msg.setResult("action", "start")
            msg.setResult("taskId", task["taskId"])
            desc = config.getMultiLangTextConf(str(task["desc"]), lang=util.getLanguage(userId))
            if desc.find("%d") >= 0:
                if task["taskType"] == 1:
                    desc = desc % (task["targets"].get("number", 0), task["targets"].get("target"))
                elif task["taskType"] == 2:
                    desc = desc % (task["targets"].get("number"))
                elif task["taskType"] == 3:
                    desc = desc % (task["targets"].get("number"))
            msg.setResult("desc", desc)
            msg.setResult("timeLeft", timeLeft)
            msg.setResult("timeLong", task["timeLong"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("rewardType", userData["rewardType"])
            msg.setResult("targets", task["targets"])
            msg.setResult("rewards", task["rewards"])
            GameMsg.sendMsg(msg, userId)

    def sendTaskInfoForReconnect(self, offline, userId):
        """
        用户断线重连发送任务相关信息
        """
        userData = self.usersData.get(userId, {})
        task = userData.get("task")
        if task:
            timeLeft = int(task["timeLong"]) - int(time.time() - self.recordStartTime)
            if timeLeft <= 5:
                return
            self.sendTideTaskStartInfo(userId, timeLeft)
            self._sendRanksInfo(userId)

    def _sendTaskReward(self, player, dropType, dropItem):
        """
        发送任务奖励
        """
        if dropType == 1:                   # 金币
            dropItems = {"chip": dropItem["count"]}
            rewards = [{"name": "tableChip", "count": dropItem["count"]}]
            util.addRewards(player.userId, rewards, "BI_NFISH_TIDE_TASK_REWARDS", self.table.roomId)
        else:
            util.addRewards(player.userId, [dropItem], "BI_NFISH_TIDE_TASK_REWARDS", self.table.roomId)
            dropItems = dropItem
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
            msg.setCmd("tide_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "rank")
            msg.setResult("taskId", task["taskId"])
            msg.setResult("taskType", task["taskType"])
            msg.setResult("ranks", self._getRanks(userId))
            GameMsg.sendMsg(msg, userId)

    def dealLeaveTable(self, uid):
        """
        处理离开事件
        """
        if uid not in self.usersData:
            return
        self.clearTaskData(uid)

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """
        uid = event.userId
        fishTypes = event.fishTypes
        catch = event.catch
        catchFishMultiple = event.catchFishMultiple
        if uid not in self.userIds:
            return
        usersData = self.usersData.get(uid, {})
        if not usersData:
            return
        if usersData["state"] != TaskState.TS_Start:
            return
        score = 0
        for catchMap in catch:
            fId = catchMap["fId"]
            fishType = self.table.fishMap[fId]["fishType"]
            fishConf = config.getFishConf(fishType, self.table.typeName, self.fpMultiple)
            fishMultiple = 1
            if catchFishMultiple and catchFishMultiple.get(fId):
                fishMultiple = catchFishMultiple.get(fId)
            if fishConf.get("itemId", 0) in config.BULLET_KINDIDS:
                score += (fishConf.get("score", 0) * config.BULLET_KINDIDS[fishConf.get("itemId", 0)] / self.fpMultiple)
            else:
                score += fishConf.get("score", 0) * fishMultiple

        player = self.table.getPlayer(uid)
        targets = usersData["task"]["targets"]
        target = targets.get("target", 0)
        number = targets.get("number", 999)
        _isUserDataUpdate = False
        taskType = usersData["task"]["taskType"]
        if taskType != 1 and "progress" not in usersData["results"]:
            usersData["results"]["progress"] = 0
            _isUserDataUpdate = True
        if taskType == 1:                               # 指定数量特定鱼
            if target not in fishTypes:
                return
            if target in fishTypes and target not in usersData["results"]:
                usersData["results"][target] = 0
            if self._checkFinished(usersData):
                return
            if target in fishTypes:
                num = fishTypes.count(target)
                usersData["results"][target] += num
                _isUserDataUpdate = True
            if player and player.currentTask:
                if target in fishTypes and usersData["results"][target] >= number:
                    usersData["results"][target] = number
                    _isUserDataUpdate = True
        elif taskType == 2:                             # 指定数量任意鱼
            usersData["results"]["progress"] += len(fishTypes)
            _isUserDataUpdate = True
        elif taskType == 3:                             # 指定分数
            usersData["results"]["progress"] += score
            _isUserDataUpdate = True
        if _isUserDataUpdate:
            self._sendRanksInfo(uid)
        if self._checkFinished(usersData):
            self.taskEnd(uid)

    def _getRanks(self, uid):
        """
        获得排名信息
        """
        if uid not in self.userIds:
            return {}
        userData = self.usersData[uid]
        results = copy.deepcopy(userData["results"])
        if not results:
            return {}
        if userData["task"]["taskType"] == 1:
            results["progress"] = results.values()[0]
        ranks = {"uid": userData["uid"], "results": results}
        return ranks

    def _checkFinished(self, usersData):
        """
        检查是否完成任务
        """
        results = usersData["results"]
        taskType = usersData["task"]["taskType"]
        targets = usersData["task"]["targets"]
        target = targets.get("target", 0)
        number = targets.get("number", 999)
        finished = False
        if taskType == 1 and len(targets.keys()) == 2:                                        # 一个target会对应有2个字段
            if target in results.keys() and results[target] >= number:
                finished = True
        else:
            if usersData["results"].get("progress", 0) >= number:
                finished = True
        return finished
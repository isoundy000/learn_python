# -*- coding=utf-8 -*-
"""
Created by lichen on 16/11/21.
"""

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
            if util.isFinishAllNewbieTask(uid):
                self.userIds.append(uid)
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
                bonus = self.bonusPool
                if len(rewardData.keys()) == 1:
                    bonus = self.bonusPool * self.firstBonusScale
                self.table.room.lotteryPool.deductionBonusPoolCoin(int(bonus))
                bireport.reportGameEvent("BI_NFISH_BONUS_POOL", 1, FISH_GAMEID, self.table.roomId, self.table.tableId, 0, int(bonus), 0, 0, [], "robot_3.7_-hall6-robot")
            msg = MsgPack()
            msg.setCmd("bonus_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "finish")
            msg.setResult("taskId", self.currentTask["taskId"])
            msg.setResult("taskType", self.currentTask["taskType"])
            msg.setResult("scores", self._getScores())
            msg.setResult("ranks", ranks)
            if reward:
                msg.setResult("reward", rewardData)
            GameMsg.sendMsg(msg, self.userIds)
        self.clearTaskData()

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

    def sendBonusTaskInfo(self):
        """
        发送奖金赛任务倒计时信息
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
            self.sendInfoTimer = FTLoopTimer(self.sendInfoTime, 0, self.sendBonusTaskInfo)
            self.sendInfoTimer.start()
        timeLeft = 0
        state = 0
        firstBonus = 0
        secondBonus = 0
        if self.state in [0, 1]:
            timeLeft = int(self.table.runConfig.bonusTaskInterval) - int(time.time() - self.recordReloadTime)
            timeLeft = timeLeft if timeLeft > 0 else 0
            if self.state == 0 and timeLeft == 0:
                return
        if self.state == 2:
            state = 1
            firstBonus = int(self.bonusPool * self.firstBonusScale)
            secondBonus = int(self.bonusPool * self.secondBonusScale)
        bonusPool = self.table.room.lotteryPool.getBonusPoolCoin(self.table.tableId)
        bonusPool = bonusPool if bonusPool > self.table.runConfig.minBonus else self.table.runConfig.systemBonus
        bonusPool = bonusPool if bonusPool < self.table.runConfig.multiple * 5000 else self.table.runConfig.multiple * 5000
        if self.table.runConfig.fishPool != 44001 and bonusPool <= self.table.runConfig.minBonus:
            return
        msg = MsgPack()
        msg.setCmd("bonus_task")
        msg.setResult("gameId", FISH_GAMEID)
        msg.setResult("action", "info")
        msg.setResult("state", state)
        msg.setResult("timeLeft", timeLeft)
        msg.setResult("minBonus", self.table.runConfig.minBonus)
        msg.setResult("bonusPool", bonusPool)
        msg.setResult("firstBonus", firstBonus)
        msg.setResult("secondBonus", secondBonus)
        GameMsg.sendMsg(msg, userIds)

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
        if self.state == 0:
            return
        self.userIds.append(userId)
        self.usersData[userId] = {
            "uid": userId,
            "task": self.currentTask,
            "score": 0,
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
        self.sendBonusTaskStartInfo(userId, timeLeft)
        # 发送排名信息
        self._sendRanksInfo()
        # 设置用户当前任务信息
        player = self.table.getPlayer(userId)
        if player:
            player.currentTask = [self.taskName, self.currentTask["taskId"], self.currentTask["taskType"], self.currentTask["targets"]]

    def sendTaskInfoForReconnect(self, userId):
        """
        用户断线重连发送任务相关信息
        """
        if self.state != 2:
            return
        timeLeft = int(self.currentTask["timeLong"]) - int(time.time() - self.recordStartTime)
        if timeLeft <= 5:
            return
        self.sendBonusTaskStartInfo(userId, timeLeft)
        self._sendRanksInfo()

    def _sendTaskReward(self, player, chip, broadcastUserIds):
        """
        发送任务奖励
        """
        rewardChip = [{"name": "tableChip", "count": chip}]
        ranks = self._getRanks()
        if ranks:
            userIds = ranks[1]
            if self.table.runConfig.fishPool != 44001 and player and player.userId in userIds and chip >= 150000:
                names = []
                for uid in userIds:
                    newPlayer = self.table.getPlayer(uid)
                    if newPlayer:
                        names.append(newPlayer.name)
                name = "、".join(names)
                # msg = u"恭喜玩家%s在%s的奖金争夺赛中获得冠军，赢得%d金币!" % \
                title = config.getMultiLangTextConf(self.table.runConfig.title, lang=player.lang)
                msg = config.getMultiLangTextConf("ID_LED_BONUS_TASK", lang=player.lang).format(name, title, chip)
                user_rpc.sendLed(FISH_GAMEID, msg, lang=player.lang)
        util.addRewards(player.userId, rewardChip, "BI_NFISH_BONUS_TASK_REWARDS", self.table.roomId)
        return rewardChip

    def _sendRanksInfo(self):
        """
        发送排名信息
        """
        if self.currentTask:
            msg = MsgPack()
            msg.setCmd("bonus_task")
            msg.setResult("gameId", FISH_GAMEID)
            msg.setResult("action", "rank")
            msg.setResult("taskId", self.currentTask["taskId"])
            msg.setResult("scores", self._getScores())
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
        wpId = event.wpId

        if uid not in self.userIds:
            return
        weaponConf = config.getWeaponConf(wpId, mode=event.gameMode)
        if not weaponConf:
            return
        fpMultiple = self.getEventFpMultiple(event)
        score = 0
        usersData = self.usersData.get(uid)
        taskType = usersData["task"]["taskType"]
        targets = usersData["task"]["targets"]
        target1 = targets.get("target1", 0)
        multipleTarget1 = 14000 + target1 % 11000
        target2 = targets.get("target2", 0)
        multipleTarget2 = 14000 + target2 % 11000

        if taskType == 1:  # 指定鱼算分
            if target1 not in fishTypes and target2 not in fishTypes and multipleTarget1 not in fishTypes and multipleTarget2 not in fishTypes:
                return
            if target1 in fishTypes or multipleTarget1 in fishTypes:
                fishConf = config.getFishConf(target1, self.table.typeName, fpMultiple)
                score = fishConf.get("score", 0) * fishTypes.count(target1)
                fishConf = config.getFishConf(multipleTarget1, self.table.typeName, fpMultiple)
                score += (fishConf.get("score", 0) * fishTypes.count(multipleTarget1))
            if target2 in fishTypes or multipleTarget2 in fishTypes:
                fishConf = config.getFishConf(target2, self.table.typeName, fpMultiple)
                score = fishConf.get("score", 0) * fishTypes.count(target2)
                fishConf = config.getFishConf(multipleTarget2, self.table.typeName, fpMultiple)
                score += (fishConf.get("score", 0) * fishTypes.count(multipleTarget2))
        elif taskType == 2:  # 任意鱼算分
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.table.typeName, fpMultiple)
                if fishConf.get("itemId", 0) in config.BULLET_KINDIDS:
                    score += (fishConf.get("score", 0) * config.BULLET_KINDIDS[fishConf.get("itemId", 0)] / fpMultiple)
                else:
                    score += fishConf.get("score", 0)
        elif taskType == 4:  # 任意鱼算数量
            score = len(fishTypes)

        timeLeft = int(self.currentTask["timeLong"]) - int(time.time() - self.recordStartTime)
        player = self.table.getPlayer(uid)
        if player:
            score = int(score * self.wpScoreScale.get(player.gunId, 1))
        if timeLeft <= 60:
            score *= 2
        userdata = self.usersData.get(uid)
        userdata["score"] += score
        if score == 0:
            return
        userdata["lastCatchId"] = self.catchId
        self.catchId -= 1
        self._sendRanksInfo()

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
        # for m in xrange(len(udatas)):
        #     if udatas[m]["score"] == 0:
        #         continue
        #     udata = {"uid": udatas[m]["uid"], "score": udatas[m]["score"]}
        #     if score == 0:
        #         rank1.append(udata)
        #     if score != 0 and rank1[0]["score"] == udatas[m]["score"]:
        #         rank1.append(udata)
        #     if score != 0:
        #         if not rank2 and score != udatas[m]["score"]:
        #             rank2.append(udata)
        #             score = udatas[m]["score"]
        #             continue
        #         if rank2 and rank2[0]["score"] == udatas[m]["score"]:
        #             rank2.append(udata)
        #     score = udatas[m]["score"]
        # if rank1:
        #     ranks[1] = [udata["uid"] for udata in rank1]
        # if rank2:
        #     ranks[2] = [udata["uid"] for udata in rank2]
        if udatas and udatas[0]["score"]:
            ranks[1] = [udatas[0]["uid"]]
        return ranks

    def _getScores(self):
        """
        获得分数信息
        """
        udatas = self.usersData.values()
        score = []
        for m in xrange(len(udatas)):
            udata = {}
            if udatas[m]["score"] == 0:
                continue
            udata["uid"] = udatas[m]["uid"]
            udata["score"] = udatas[m]["score"]
            score.append(udata)
        return score

    def _getReward(self):
        """
        获得奖励信息
        """
        rank1Data = []
        rank2Data = []
        rewardData = {}
        ranks = self._getRanks()
        firstChip = int(self.bonusPool * self.firstBonusScale)
        secondChip = int(self.bonusPool * self.secondBonusScale)
        from newfish.game import TGFish
        from newfish.entity.event import WinBonusTaskEvent
        if 1 in ranks.keys():
            uids = ranks[1]
            for uid in uids:
                player = self.table.getPlayer(uid)
                self._sendTaskReward(player, firstChip // len(uids), self.userIds)
                __type = 0
                # _, chestItem = drop_system.getDropItem(self.currentTask["firstChestReward"])
                # if chest_system.getChestIdleOrder(player.userId) == -1:
                #     __type = 1
                # else:
                #     chest_system.newChestItem(player.userId, chestItem["name"], "BI_NFISH_BONUS_TASK_REWARDS", self.table.roomId)
                udata = {"uid": uid, "chip": firstChip // len(uids), "type": __type}
                rank1Data.append(udata)
                event = WinBonusTaskEvent(player.userId, FISH_GAMEID, self.table.roomId, self.table.tableId, 1)
                TGFish.getEventBus().publishEvent(event)
            rewardData[1] = rank1Data
        # if 2 in ranks.keys():
        #     uids = ranks[2]
        #     for uid in uids:
        #         player = self.table.getPlayer(uid)
        #         self._sendTaskReward(player, secondChip // len(uids), self.userIds)
        #         __type = 0
        #         _, chestItem = drop_system.getDropItem(self.currentTask["secondChestReward"])
        #         if chest_system.getChestIdleOrder(player.userId) == -1:
        #             __type = 1
        #         else:
        #             chest_system.newChestItem(player.userId, chestItem["name"], "BI_NFISH_BONUS_TASK_REWARDS", self.table.roomId)
        #         udata = {"uid": uid, "chip": secondChip // len(uids), "chest": chestItem["name"], "type": __type}
        #         rank2Data.append(udata)
        #         event = WinBonusTaskEvent(player.userId, FISH_GAMEID, self.table.roomId, self.table.tableId, 2)
        #         TGFish.getEventBus().publishEvent(event)
        #     rewardData[2] = rank2Data
        return rewardData
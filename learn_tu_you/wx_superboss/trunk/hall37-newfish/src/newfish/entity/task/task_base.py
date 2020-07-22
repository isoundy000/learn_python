#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17

import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from freetime.entity.msg import MsgPack
from poker.protocol import router
from poker.entity.biz import bireport
from newfish.entity import util, config
from newfish.entity import drop_system
from newfish.entity.config import FISH_GAMEID


Task_Delay_Ready_Time = 2       # 任务延时后的准备时间
Task_Red_Ready_Time = 12        # 限时任务在新手场的准备时间
Task_Normal_Ready_Time = 9      # 限时任务在其他场的准备时间


class TaskState:
    NotOpen = 0                 # 未开始
    Start = 1                   # 开始
    Update = 2                  # 进行中
    Fail = 3                    # 失败
    Success = 4                 # 成功


# 任务模型
class TaskModel:
    Red = 0                     # 新手任务
    Main = 1                    # 主线任务
    Branch = 2                  # 支线任务
    Random = 3                  # 随机任务


class TaskType:
    CatchFishCoin = 1           # 捕获xx金币
    CatchFishNum = 2            # 捕获xx只xx鱼
    CatchBossNum = 3            # 捕获xx只BOSS
    FishNumCoinHigh = 4         # 捕获xx只xx金币以上的鱼
    BetFishNum = 5              # 捕获xx只xx倍率鱼
    ComboNum = 6                # 连击数达到xx
    UseSkillNum = 7             # 使用xx次xx技能
    UseSkillCatchFishNum = 8    # 使用技能捕获xx只xx鱼
    UseSkillCatchFishCoin = 9   # 使用技能捕获xx金币的xx鱼
    CatchFishNumByOneFire = 10  # xx网捕获xx鱼
    HoldCoin = 11               # 持有xx金币
    CatchPearlNum = 12          # 捕获xx颗珍珠
    UpgradeLevel = 13           # 升级火炮到xx级
    CatchRainbowFishNum = 14    # 捕获xx只彩虹鱼
    CatchRedPacketFishNum = 15  # 捕获多少只红包券鱼
    UserSkillItem = 16          # 使用技能道具


class TaskBase(object):

    def __init__(self, player, taskConf, taskSystem, taskData=None):
        self.player = player
        self.userId = player.userId
        self.taskId = taskConf["taskId"]
        self.taskConfig = taskConf

        self.taskSystem = taskSystem
        self.taskData = taskData or self._getInitMainData()
        self.taskInterval = taskConf["timeLong"]
        self.helpProgress = taskData.get("helpProgress", 0) if taskData else 0
        self.waitTime = taskData.get("waitTime", 0) if taskData else taskConf["waitTime"]
        self.taskActivateTimer = None       # 任务激活
        self.sendTaskInfoTimer = None       # 发送任务信息
        self.updateTaskInfoTimer = None     # 刷新任务进度
        self.userEndTaskTimer = None        # 任务结束倒计时
        self.isSendMsg = False
        self.receiveRewards = None
        self.catchBetNum = taskData.get("catchBetNum", 0) if taskData else 0
        self._reload()

    def clear(self):
        """清理定时器"""
        if self.taskActivateTimer:
            self.taskActivateTimer.cancel()
        if self.sendTaskInfoTimer:
            self.sendTaskInfoTimer.cancel()
        if self.updateTaskInfoTimer:
            self.updateTaskInfoTimer.cancel()
        if self.userEndTaskTimer:
            self.userEndTaskTimer.cancel()

    def _reload(self):
        ftlog.debug("Task_base_reload", self.player.userId)
        self.recordStartTime = 0
        if not self.isTaskOver():
            if self.taskData.get("type", 0) and self.taskData.get("type", 0) != self.taskConfig["type"]:
                self.taskData = self._getInitMainData()
                return
            if self.taskConfig["target"] != self.taskData["target"]:        # 未完成的任务任务目标发生变化后重置存档
                self.taskData = self._getInitMainData()
                return
            if self.taskConfig["targetNum"] != self.taskData["targetNum"] and self.taskData.get("type", 0) not in [0, TaskType.HoldCoin]:
                self.taskData = self._getInitMainData()
                return

    def _getInitMainData(self):
        """获取初始化主线数据"""
        targetNum = self.taskConfig["targetNum"]
        if self.taskSystem.isRedRoom() and self.taskConfig["type"] == TaskType.HoldCoin:
            targetNum += self.player.allChip // 100 * 100
        return {
            "type": self.taskConfig["type"],
            "progress": 0,
            "state": TaskState.NotOpen,
            "failTime": 0,
            "targetNum": targetNum,
            "target": self.taskConfig["target"]
        }

    def _addProgress(self, value, isMe, progress=0, isTargetAddition=False):
        """增加任务进度"""
        assert (self.taskData)
        if value == 0 or self.taskData["state"] != TaskState.Update:                            # value
            return
        if ftlog.is_debug():
            ftlog.debug("_addProgress1", "value =", value, "isMe =", isMe, "progress =", progress, "isTargetAddition =", isTargetAddition, "helpProgress =", self.helpProgress)
        if isMe:
            value *= self.taskSystem.taskExpedite
            progress_ = min(self.taskData["progress"] + value, 999999999999)
            self._updateProgress(progress_, isMe)
        else:
            if progress > 0 or isTargetAddition:
                if progress:
                    self.helpProgress += progress
                else:
                    self.helpProgress += value
                progress_ = min(self.taskData["progress"] + value, 999999999999)
                self._updateProgress(progress_, isMe)
                if ftlog.is_debug():
                    ftlog.debug("_addProgress2", "helpProgress =", self.helpProgress, "totalProgress =", progress_)

    def _updateProgress(self, value, isMe):
        """
        更新任务进度
        """
        if self.taskData["progress"] != value:
            self.taskData["progress"] = value
            self.taskData["time"] = int(time.time())
            if self._isComplete():
                self.taskEnd()
            else:
                if isMe:
                    self.sendUserTaskInfo()
                else:                               # 好友助力任务进度延迟刷新
                    self.isSendMsg = True

    def _receiveTaskReward(self):
        """领取奖励"""
        assert (self.taskData)
        if self.isTaskOver():  # 已领取
            return 1, None
        targetCount = self.taskData["targetNum"]
        if self.taskData["progress"] < targetCount:  # 未达成
            return 1, None
        _rewards = self._getDropItems()
        if not _rewards:
            _rewards = self.taskConfig["rewards"]     # 普通奖励
        if _rewards and util.isChestRewardId(_rewards[0]["name"]):      # 宝箱奖励(新手宝箱奖励固定)
            if self.taskSystem.isRedRoom():
                _rewards = [
                    {"name": 101, "count": 500},
                    {"name": 1145, "count": 1},
                    {"name": 1149, "count": 1}
                    # {"name": 1137, "count": 3}
                ]
            else:
                from newfish.entity.chest import chest_system
                _rewards = chest_system.getChestRewards(self.userId, _rewards[0]["name"])

        rewards = []
        for _, reward in enumerate(_rewards):
            if reward["name"] <= 0:
                continue
            rwDict = {}
            rwDict["name"] = reward["name"]
            rwDict["count"] = reward["count"]
            rewards.append(rwDict)

        code = 0
        ftlog.debug("_receiveTaskReward", self.userId, rewards, self.taskConfig["rewards"])
        self.taskData["state"] = TaskState.Success  # 改变状态
        if rewards:
            code = util.addRewards(self.userId, rewards, "BI_NFISH_TABLE_TASK_REWARDS", int(self.taskId))
        return code, rewards

    def _getDropItems(self):
        """获取掉落的道具"""
        realRewards = []
        rewards = self.taskConfig["rewards"]
        for reward in rewards:
            dropId = reward["name"]
            dropConf = config.getDropConf(dropId)
            if dropConf:
                _, rds = drop_system.getDropItem(dropId)
                realRewards.append(rds)
        ftlog.debug("_getDropItems===>", realRewards)
        return realRewards

    def _getCatchFishCoin(self, event, target=0):
        """获取捕鱼的金币"""
        totalCoin = 0  # 总金币数不包括招财珠
        gunSkinMul = event.gunSkinMul
        fishCoins = {}
        outCoinsNum = 0
        for gainMap in event.gain:
            fishType = int(gainMap["fishType"])
            itemId = gainMap["itemId"]
            itemCount = gainMap["count"] / gunSkinMul
            if itemId == config.CHIP_KINDID:  # 金币
                totalCoin += itemCount
                if fishType // 1000 == 14:
                    fishType = fishType % 14000 + 11000
                fishCoins[str(fishType)] = fishCoins.setdefault(str(fishType), 0) + itemCount
                if target and itemCount >= target:
                    outCoinsNum += 1
        return totalCoin, fishCoins, outCoinsNum

    def dealCatchEvent(self, event, tableMultiple, coinAddition, playersNum):
        """
        处理捕鱼事件
        :param event: 捕获事件详情
        :param tableMultiple: 房间倍率
        :param coinAddition: 当处于累计捕获金币任务时的进度加成
        :param playersNum: 当前桌内玩家数量
        :return:
        """
        if self.taskConfig["type"] in [TaskType.UseSkillNum, TaskType.ComboNum]:
           return
        ftlog.debug("taskBase_______dealCatchEvent00", self.userId, self.taskData["state"])
        if self.taskData["state"] != TaskState.Update:
            return
        isMe = event.userId == self.userId
        fishTypes = event.fishTypes  # 鱼种类
        wpId = event.wpId
        gunSkinMul = event.gunSkinMul
        target = self.taskConfig["target"]
        progress = 0
        isTargetAddition = False
        if self.taskConfig["type"] in [TaskType.CatchFishCoin, TaskType.UseSkillCatchFishCoin]:
            progress = coinAddition
        elif self.taskConfig["type"] in [TaskType.CatchFishNum, TaskType.CatchBossNum,
                                         TaskType.FishNumCoinHigh, TaskType.BetFishNum,
                                         TaskType.CatchRainbowFishNum, TaskType.CatchRedPacketFishNum]:
            friendHelpPlayerMultiple = config.getCommonValueByKey("friendHelpPlayerMultiple", {}).get(str(playersNum - 1), 0)
            probb = (friendHelpPlayerMultiple * (self.taskData["targetNum"] + 5) / self.taskData["targetNum"]) * 10000
            randInt = random.randint(1, 10000)
            if randInt <= probb:
                isTargetAddition = True
        if self.taskConfig["type"] == TaskType.CatchFishCoin:  # 1捕获xx鱼达金币数
            totalCoin, fishCoins, _ = self._getCatchFishCoin(event)
            if gunSkinMul != 1:
                ftlog.debug("taskBase_______dealCatchEvent", gunSkinMul)
            ftlog.debug("Tabletask_dealCatchEvent", totalCoin, fishCoins)
            if target:
                self._addProgress(fishCoins.get(str(target), 0), isMe, progress=progress, isTargetAddition=isTargetAddition)
            else:
                self._addProgress(totalCoin, isMe, progress=progress, isTargetAddition=isTargetAddition)

        elif self.taskConfig["type"] == TaskType.CatchFishNum:  # 2捕获鱼个数
            if target:
                betTarget = 14000 + int(target) % 11000
                fishNum = fishTypes.count(target) + fishTypes.count(betTarget)
                ftlog.debug("taskBase_______dealCatchEventCatchFishNum", betTarget, fishTypes.count(betTarget))
                self._addProgress(fishNum, isMe, progress=progress, isTargetAddition=isTargetAddition)
            else:
                self._addProgress(len(fishTypes), isMe, progress=progress, isTargetAddition=isTargetAddition)
            return
        elif self.taskConfig["type"] == TaskType.CatchBossNum:  # 3捕获boss个数
            bossNum = 0  # boss个数
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.taskSystem.table.typeName, tableMultiple)
                if fishConf["type"] in config.BOSS_FISH_TYPE:
                    bossNum += 1
            self._addProgress(bossNum, isMe, progress=progress, isTargetAddition=isTargetAddition)
            return

        elif self.taskConfig["type"] == TaskType.FishNumCoinHigh:  # 4多少金币以上的鱼
            _, _, num = self._getCatchFishCoin(event, target)
            if gunSkinMul != 1:
                ftlog.debug("taskBase_______dealCatchEvent", gunSkinMul, num)
            self._addProgress(num, isMe, progress=progress, isTargetAddition=isTargetAddition)
            return
        elif self.taskConfig["type"] == TaskType.BetFishNum: # 5--多少只倍率鱼
            betFishMap = {}
            for gainMap in event.gain:
                fishConf = config.getFishConf(gainMap["fishType"], self.taskSystem.table.typeName, tableMultiple)
                itemId = gainMap["itemId"]
                itemCount = gainMap["count"]

                if fishConf["type"] in config.MULTIPLE_FISH_TYPE:
                    if itemId == config.CHIP_KINDID:  # 金币
                        bet = itemCount / fishConf["score"] / tableMultiple / gunSkinMul
                        betFishMap[str(bet)] = betFishMap.get(str(bet), 0) + 1
            betNum = 0
            for bet in betFishMap:
                if int(bet) >= target:
                    betNum += betFishMap[bet]
            self._addProgress(betNum, isMe, progress=progress, isTargetAddition=isTargetAddition)

        elif self.taskConfig["type"] == TaskType.UseSkillCatchFishNum:  # 8 使用技能捕获鱼数
            wpType = util.getWeaponType(wpId)
            if wpType in [config.SKILL_WEAPON_TYPE,
                          config.RB_FIRE_WEAPON_TYPE,
                          config.RB_BOMB_WEAPON_TYPE]:
                if target:
                    self._addProgress(fishTypes.count(target), isMe, progress=progress, isTargetAddition=isTargetAddition)
                else:
                    self._addProgress(len(fishTypes), isMe, progress=progress, isTargetAddition=isTargetAddition)

        elif self.taskConfig["type"] == TaskType.UseSkillCatchFishCoin:  # 9 使用技能捕获XX金币类型的鱼数
            totalCoin, fishCoins, _ = self._getCatchFishCoin(event)  # 总金币数不包括招财珠
            if gunSkinMul != 1:
                ftlog.debug("taskBase_______dealCatchEvent", gunSkinMul, totalCoin, fishCoins)
            wpType = util.getWeaponType(wpId)
            if wpType in [config.SKILL_WEAPON_TYPE,
                          config.RB_FIRE_WEAPON_TYPE,
                          config.RB_BOMB_WEAPON_TYPE]:
                if target:
                    self._addProgress(fishCoins.get(str(target), 0), isMe, progress=progress, isTargetAddition=isTargetAddition)
                else:
                    self._addProgress(totalCoin, isMe, progress=progress, isTargetAddition=isTargetAddition)
        elif self.taskConfig["type"] == TaskType.CatchFishNumByOneFire:  # 10 1网捕获多少鱼
            if len(fishTypes) >= target:
                value = 1
                if not isMe:
                    return
                self._addProgress(value, isMe, progress=progress, isTargetAddition=isTargetAddition)
        elif self.taskConfig["type"] == TaskType.CatchRainbowFishNum:   # 捕获彩虹鱼
            rainbowNum = 0
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.taskSystem.table.typeName, tableMultiple)
                if fishConf["type"] in config.RAINBOW_FISH_TYPE:
                    rainbowNum += 1
            self._addProgress(rainbowNum, isMe, progress=progress, isTargetAddition=isTargetAddition)
        elif self.taskConfig["type"] == TaskType.CatchRedPacketFishNum: # 捕获红包券鱼
            redPacketNum = 0
            for fishType in fishTypes:
                fishConf = config.getFishConf(fishType, self.taskSystem.table.typeName, tableMultiple)
                if fishConf["type"] == 4:
                    redPacketNum += 1
            self._addProgress(redPacketNum, isMe, progress=progress, isTargetAddition=isTargetAddition)

    def getTaskId(self):
        """
        获取任务Id
        """
        return self.taskId

    def taskStart(self, interval=0, delay=0):
        """
        任务开始
        """
        ftlog.debug("taskBase_______taskStart", self.taskId)

        if self.taskActivateTimer:
            self.taskActivateTimer.cancel()
        if delay:
            taskActivateInterval = max(interval, Task_Delay_Ready_Time)
            self.taskActivateTimer = FTLoopTimer(taskActivateInterval, 0, self._taskActivate, delay)
            self.taskActivateTimer.start()
        elif self.taskConfig["timeLong"] > 0:
            if self.taskSystem.isRedRoom() and self.taskSystem.taskModel == TaskModel.Main:
                time_ = Task_Delay_Ready_Time
            else:
                time_ = Task_Normal_Ready_Time
            taskActivateInterval = max(interval, time_)
            taskInfoInterval = max(interval - time_, 0)
            self.delaySendUserTaskInfo(taskInfoInterval)
            self.taskActivateTimer = FTLoopTimer(taskActivateInterval, 0, self._taskActivate)
            self.taskActivateTimer.start()
        else:
            self.taskActivateTimer = FTLoopTimer(interval, 0, self._taskActivate)
            self.taskActivateTimer.start()
        from newfish.game import TGFish
        from newfish.entity.event import TableTaskStartEvent
        event = TableTaskStartEvent(self.userId, FISH_GAMEID, self.taskSystem.table.tableId, self.getTaskId())
        TGFish.getEventBus().publishEvent(event)

    def dealUseSkillEvent(self, event):
        if self.taskData["state"] != TaskState.Update:
            return
        if self.taskConfig["type"] == TaskType.UseSkillNum:
            target = self.taskConfig["target"]
            if target == 0:
                self._addProgress(1, event.userId == self.userId)
            else:
                if event.kindId == str(target):
                    self._addProgress(1, event.userId == self.userId)

    def dealUseSkillItem(self, event):
        if self.taskData["state"] != TaskState.Update:
            return
        if self.taskConfig["type"] == TaskType.UserSkillItem:
            self._addProgress(1, event.userId == self.userId)

    def dealGetPearl(self, pearl):
        if self.taskData["state"] != TaskState.Update:
            return
        ftlog.debug("task, type", self.taskConfig["type"], TaskType.CatchPearlNum, self.taskConfig["type"] == TaskType.CatchPearlNum)
        if self.taskConfig["type"] == TaskType.CatchPearlNum:
            self._addProgress(pearl, True)

    def dealCommboEvent(self, event):
        if self.taskData["state"] != TaskState.Update:
            return
        if self.taskConfig["type"] == TaskType.ComboNum:
            if event.comboNum >= self.taskConfig["target"]:
                self._addProgress(1, event.userId == self.userId)

    def refreshHoldCoin(self, coin):
        if self.taskData["state"] != TaskState.Update:
            return
        ftlog.debug("refreshHoldCoin", self.userId, coin)
        if self.taskConfig["type"] == TaskType.HoldCoin:
            self._updateProgress(coin, True)

    def refreshLevel(self, level):
        if self.taskData["state"] != TaskState.Update:
            return
        ftlog.debug("refreshLevel", self.userId, level)
        if self.taskConfig["type"] == TaskType.UpgradeLevel:
            self._updateProgress(level, True)

    def _taskActivate(self, delay=0):
        """任务激活"""
        # 未完成前3个中期目标时不触发渔场任务.
        if self.taskSystem.needCheckMidTermTargetStates:
            if not self.taskSystem.top3MidTermTargetFinished:
                self.taskSystem.top3MidTermTargetFinished = True
                for taskClass in self.player.achieveSystem.holdAssetTasks:
                    if taskClass.taskId < 1003 or (taskClass.taskId == 1003 and not taskClass.isComplete()):
                        self.taskSystem.top3MidTermTargetFinished = False
                        break
            if not self.taskSystem.top3MidTermTargetFinished:
                if self.taskActivateTimer:
                    self.taskActivateTimer.cancel()
                self.taskActivateTimer = FTLoopTimer(60, 0, self._taskActivate)
                self.taskActivateTimer.start()
                ftlog.debug("_taskActivate, need delay !", self.player.userId, self.taskId)
                return

        ftlog.debug("_taskActivate->", delay, self.waitTime)
        self.taskData["state"] = TaskState.Start
        if delay > 0:
            self.taskData["state"] = TaskState.Update
            self.taskInterval = delay
        self.recordStartTime = int(time.time())
        self.clear()
        if self.taskInterval != 0:
            self.userEndTaskTimer = FTLoopTimer(self.taskInterval, 0, self.taskEnd)
            self.userEndTaskTimer.start()
        if self.taskSystem.isFriendRoom():
            self.updateTaskInfoTimer = FTLoopTimer(1, -1, self.sendTimerUpdate)
            self.updateTaskInfoTimer.start()
        self.sendUserTaskInfo()
        self.taskData["state"] = TaskState.Update

    def getTaskFailTime(self):
        """
        当前任务已经失败多少次
        """
        return self.taskData["failTime"]

    def getTaskInfo(self):
        """
        获取返回给客户端的任务数据
        """
        progress = min(self.taskData["progress"], self.taskData["targetNum"])
        progress = int(progress) if progress - int(progress) == 0 else progress
        meProgress = progress - self.helpProgress
        meProgress = int(meProgress) if meProgress - int(meProgress) == 0 else meProgress
        taskInfo = {}
        taskInfo["taskId"] = self.taskConfig["taskId"]
        taskInfo["isLimitTime"] = self.isLimitTime()
        taskInfo["shareMode"] = 1   # 1 if not self.isLimitTime() or util.isLocationLimit(self.userId) else 0
        taskInfo["progress"] = [int(progress), int(meProgress), self.taskData["targetNum"]]
        taskInfo["state"] = self.taskData["state"]
        taskInfodescId = self.taskConfig["desc"]
        taskInfo["desc"] = config.getMultiLangTextConf(str(taskInfodescId), lang=util.getLanguage(self.userId))
        taskInfo["reward"] = self.taskConfig["rewards"]
        if self.receiveRewards:
            taskInfo["realReward"] = self.receiveRewards
        taskInfo["target"] = self.taskConfig["target"]
        taskInfo["suggestTarget"] = self.taskConfig["suggestTarget"]
        timeLeft = self.recordStartTime + self.taskInterval - int(time.time())
        taskInfo["timeLeft"] = timeLeft if timeLeft >= 0 else self.taskInterval
        taskInfo["timeLong"] = self.taskInterval
        taskInfo["failTimeConf"] = self.taskConfig["failTime"]
        taskInfo["failTime"] = self.taskData["failTime"]        # 失败次数
        taskInfo["isNextLimitTime"] = self.taskSystem.isNextLimitTime(self.getTaskId())
        taskInfo["model"] = TaskModel.Red if self.taskSystem.isRedRoom() and self.taskSystem.taskModel == TaskModel.Main else self.taskSystem.taskModel
        taskInfo["type"] = self.taskConfig["type"]
        if self.taskSystem.taskModel in [TaskModel.Red, TaskModel.Main]:
            taskInfo["index"] = self.taskSystem.allMainTaskIds.index(self.taskId)
        return taskInfo

    def getTaskData(self):
        """
        获取存储的任务数据
        """
        saveData = {}
        saveData["type"] = self.taskConfig["type"]
        saveData["taskId"] = self.taskId
        saveData["progress"] = self.taskData["progress"]
        saveData["helpProgress"] = self.helpProgress
        saveData["state"] = self.taskData["state"]
        saveData["target"] = self.taskConfig["target"]
        saveData["targetNum"] = self.taskData["targetNum"]
        saveData["failTime"] = self.taskData["failTime"]
        saveData["waitTime"] = int(self.taskActivateTimer.getTimeOut()) if self.taskActivateTimer else 0
        if self.catchBetNum:
            saveData["catchBetNum"] = self.catchBetNum
        return saveData

    def taskEnd(self):
        """
        任务结束
        """
        ftlog.debug("taskBase_______taskEnd", self.taskId, self.userId, self.taskData["state"])
        beforeState = self.taskData["state"]
        self.clear()
        if beforeState == TaskState.Update:
            isComplete = self._isComplete()
            if isComplete:
                _, rewards = self._receiveTaskReward()
                self.receiveRewards = rewards
                self.taskSystem.saveRedState()  # 保存红包
            else:
                self.taskSystem.taskExpedite = 1
                self.taskData["state"] = TaskState.Fail
                if self.isLimitTime():
                    self.taskData["failTime"] += 1
            from newfish.game import TGFish
            from newfish.entity.event import TableTaskEndEvent
            event = TableTaskEndEvent(self.userId, FISH_GAMEID, self.taskSystem.table.tableId, self.getTaskId(),
                                      isComplete,  self.isLimitTime(), self.receiveRewards)
            TGFish.getEventBus().publishEvent(event)
            # 上传当前完成任务进度
            if self.taskSystem.taskModel == TaskModel.Main and self.taskSystem.isRedRoom():
                ftlog.debug("BI_NFISH_THOUSAND_RED_TASK_PROGRESS--->000", self.getTaskId())
                bireport.reportGameEvent("BI_NFISH_GE_THOUSAND_RED_TASK", self.userId,FISH_GAMEID,
                                self.taskSystem.table.roomId, self.taskSystem.table.tableId,
                                self.getTaskId(), int(isComplete), 0,  0, [], config.CLIENTID_ROBOT)
                # 新手引导步骤完成
                if self.taskConfig["type"] == TaskType.UpgradeLevel:
                    util.addGuideStep(self.player.userId, config.NEWBIE_GUIDE_GUN_UP, self.player.clientId)
        self.sendUserTaskInfo()

    def sendTimerUpdate(self):
        """
        任务进度刷新
        """
        if self.taskConfig["type"] == TaskType.HoldCoin:
            self.taskSystem.refreshHoldCoin(self.player.holdCoin)
        elif self.taskConfig["type"] == TaskType.UpgradeLevel:
            gunLevel = self.player.gunLevel - 2100
            self.taskSystem.refreshLevel(gunLevel)
        if self.isSendMsg:
            self.sendUserTaskInfo()

    def delaySendUserTaskInfo(self, interval=0):
        """
        延时发送任务信息
        """
        if self.sendTaskInfoTimer:
            self.sendTaskInfoTimer.cancel()
        self.sendTaskInfoTimer = FTLoopTimer(interval, 0, self.sendUserTaskInfo)
        self.sendTaskInfoTimer.start()

    def sendUserTaskInfo(self):
        """
        发送任务信息
        """
        self.isSendMsg = False
        message = MsgPack()
        message.setCmd("table_task_info")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", self.userId)
        taskInfo = self.getTaskInfo()
        message.setResult("taskInfo", taskInfo)
        router.sendToUser(message, self.userId)

    def _isComplete(self):
        """
        任务是否完成
        """
        assert (self.taskData)
        targetCount = self.taskData["targetNum"]
        return self.taskData["progress"] >= targetCount

    def isTaskSuccess(self):
        """
        任务成功
        """
        return self.taskData["state"] == TaskState.Success

    def getTaskConf(self):
        assert (self.taskConfig)
        return self.taskConfig

    def isTaskOver(self):
        """任务结束"""
        return self.taskData["state"] in [TaskState.Success, TaskState.Fail]

    def getTaskState(self):
        return self.taskData["state"]

    def isLimitTime(self):
        """是否限制了时间"""
        if not self.taskConfig:
            return 0
        return 1 if self.taskConfig.get("timeLong", 0) != 0 else 0
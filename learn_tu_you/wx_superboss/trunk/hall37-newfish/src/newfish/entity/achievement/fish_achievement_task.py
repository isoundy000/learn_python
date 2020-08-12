#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/8/11
# 荣耀任务.


import json
import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from poker.entity.dao import daobase, gamedata
from poker.util import strutil
from poker.protocol import router
from newfish.entity.config import FISH_GAMEID
from newfish.entity.skill import skill_system
from newfish.entity import config, util
from newfish.entity.redis_keys import UserData, GameData


class TaskState:
    Normal = 1
    Complete = 2
    Received = 3


class AchieveType:
    CatchFishNum = 1        # 捕获多少条鱼--
    CatchBossNum = 2        # 捕获多少只boss--
    CatchBetFishNum = 3     # 捕获多少只倍率鱼--
    ReceiveWeekChest = 4    # 领取周宝箱--
    SkillUp = 5             # 技能升级类--
    CmpttWinNum = 6         # 渔场比赛获胜多少次--
    EnterRobbery = 7        # 参加招财模式多少次--
    JoinMatch = 8           # 参加比赛多少场--
    TotalRankMatch = 9      # 回馈赛榜--
    CollectStar = 10        # 渔场收集海星--
    TotalRankRobbery = 11   # 登上今日赢家榜n次--
    CompleteMainQuestSection = 12   # 完成第x章主线任务


class Task_Error_Code:
    SUCCESS = 0             # 领奖状态码
    NOTCOMPLETE = 2         # 未达成
    RECEIVE = 3             # 已领取


class FishAchievementTask(object):

    def __init__(self, userId, taskConf):
        self.userId = userId
        self.taskId = taskConf["Id"]
        self.taskConfig = taskConf
        self.lang = util.getLanguage(userId)
        self.taskData = None
        self.taskData = self._getAchievementTaskData()
        # 可循环的已领取的任务重置状态和进度.
        # if taskConf["repeat"] and self.taskData["state"] == TaskState.Received:
        #     self.taskData["state"] = TaskState.Normal
        #     self.taskData["progress"] -= taskConf["target"]["num"]
        #     self.taskData["progress"] = max(0, self.taskData["progress"])
        #     self._setAchievementTaskData()
        # 为了兼容老玩家数据.
        if self.taskConfig["type"] == AchieveType.CompleteMainQuestSection:
            finishAllMainQuest = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.finishAllMainQuest)
            curSectionIdx = gamedata.getGameAttr(self.userId, FISH_GAMEID, GameData.currSectionId) / 1000 % 640
            # 所有章节都已完成
            if finishAllMainQuest:
                self.taskData["progress"] = self.taskConfig["target"]["num"]
            else:
                self.taskData["progress"] = min(curSectionIdx - 1, self.taskConfig["target"]["num"])
            if self.taskData["state"] < TaskState.Received:
                self.taskData["state"] = TaskState.Complete if self.taskData["progress"] >= self.taskConfig["target"]["num"] else TaskState.Normal

    def getTaskInfo(self):
        """
        获取任务数据
        """
        taskInfo = {}
        self._updateState()                                         # 更新状态
        taskInfo["taskId"] = self.taskConfig["Id"]
        taskInfo["progress"] = min(int(self.taskData["progress"]), self.taskConfig["target"]["num"])
        taskInfo["state"] = self.taskData["state"]
        taskInfo["type"] = self.taskConfig["type"]
        taskInfo["target"] = self.taskConfig["target"]["num"]
        # taskInfo["desc"] = self.taskConfig["desc"]
        descId = self.taskConfig["desc"]
        desc = config.getMultiLangTextConf(str(descId), lang=self.lang)
        if taskInfo["type"] == AchieveType.SkillUp:
            if desc.find("%d") >= 0:
                taskInfo["desc"] = desc % self.taskConfig["target"].get("condition", 0)
        else:
            if desc.find("%s") >= 0:
                taskInfo["desc"] = desc % util.formatScore(taskInfo["target"], lang=self.lang)
            elif desc.find("%d") >= 0:
                taskInfo["desc"] = desc % taskInfo["target"]

        taskInfo["exp"] = self.taskConfig["exp"]
        taskInfo["time"] = self.taskData.get("time", 0)
        return taskInfo

    def addProgress(self, value=0, inTable=False):
        """
        添加任务进度
        """
        assert (self.taskData)
        if value == 0:
            return self.isComplete()
        if self.taskData["state"] == TaskState.Received or self.taskData["state"] == TaskState.Complete:
            return self.isComplete()
        progress_ = min(self.taskData["progress"] + value, 999999999999)
        return self._updateProgress(progress_, inTable)

    def getLastUpdateTime(self):
        """
        获取上次更新任务的时间戳
        """
        if self.taskData["time"] == 0:
            return int(time.time())
        return self.taskData["time"]

    def updateProgress(self, value=0, inTable=False):
        """
        更新任务进度
        """
        assert (self.taskData)
        if self.taskData["state"] == TaskState.Received or self.taskData["state"] == TaskState.Complete:
            return self.isComplete()
        return self._updateProgress(value, inTable)

    def _updateProgress(self, value, inTable):
        """更新进度"""
        beforeState = self.taskData["state"]
        self.taskData["progress"] = value
        self.taskData["time"] = int(time.time())
        self._updateState()
        if not inTable or self.taskData["state"] == TaskState.Complete:
            self._setAchievementTaskData()

        if self.isComplete():
            if beforeState != self.taskData["state"]:
                self.sendPushCompleteInfo()
            return True
        return False

    def receiveTaskReward(self, curTaskId):
        """
        领取奖励
        """
        assert (self.taskData)
        if self.taskData["state"] == TaskState.Received:    # 已领取
            return Task_Error_Code.RECEIVE, None
        targetCount = self.taskConfig["target"]["num"]
        if self.taskData["progress"] < targetCount:         # 未达成
            return Task_Error_Code.NOTCOMPLETE, None
        # # 普通奖励
        # rewards = []
        # rewards.extend(self.taskConfig["norReward"])
        # code = 0
        # # 宝箱奖励
        # chestId, chestRewards = self._getChestReward()
        # if chestId:
        #     rewards.extend(chestRewards)
        # if rewards:
        #     code = util.addRewards(self.userId, rewards, "BI_NFISH_ACHIEVEMENT_REWARDS", int(self.taskId))
        self.taskData["time"] = int(time.time())
        self.taskData["state"] = TaskState.Received         # 改变状态
        self._setAchievementTaskData()
        return Task_Error_Code.SUCCESS, self.taskConfig["exp"]


    def sendPushCompleteInfo(self):
        """
        发送任务完成消息
        """
        message = MsgPack()
        message.setCmd("fishAchievementTaskComplete")
        message.setResult("gameId", FISH_GAMEID)
        message.setResult("userId", self.userId)
        taskInfo = {}
        taskInfo["taskId"] = self.taskConfig["Id"]
        taskInfo["type"] = self.taskConfig["type"]
        taskInfo["target"] = self.taskConfig["target"]["num"]
        taskInfo["state"] = TaskState.Complete
        descId = self.taskConfig["desc"]
        desc = config.getMultiLangTextConf(descId, lang=self.lang)
        if taskInfo["type"] == AchieveType.SkillUp:
            if desc.find("%d") >= 0:
                taskInfo["desc"] = desc % self.taskConfig["target"].get("condition", 0)
        else:
            if desc.find("%s") >= 0:
                taskInfo["desc"] = desc % util.formatScore(taskInfo["target"], lang=self.lang)
            elif desc.find("%d") >= 0:
                taskInfo["desc"] = desc % taskInfo["target"]
        message.setResult("result", taskInfo)
        router.sendToUser(message, self.userId)

    def isComplete(self):
        """
        任务是否完成
        """
        assert (self.taskData)
        targetCount = self.taskConfig["target"]["num"]
        if self.taskData["state"] != TaskState.Received and self.taskData["progress"] >= targetCount:
            return True
        return False

    def getHonorId(self):
        """
        获取任务分组id
        """
        assert (self.taskId)
        return self.taskId / 100

    def getTaskConf(self):
        """
        获取任务配置
        """
        assert (self.taskConfig)
        return self.taskConfig

    def updateStateAndSave(self):
        """更新成就任务状态"""
        self._updateState()
        self._setAchievementTaskData()

    # def _getChestInfo(self):
    #     """
    #     宝箱数据
    #     """
    #     chestId = None
    #     chestInfo = None
    #     for chestInfo in self.taskConfig["chestReward"]:
    #         chestId = chestInfo["name"]
    #         chestInfo = chest_system.getChestInfo(chestId)
    #     return chestId, chestInfo
    #
    # def _getChestReward(self):
    #     chestId = None
    #     chestRewards = None
    #     for chestInfo in self.taskConfig["chestReward"]:
    #         chestId = chestInfo["name"]
    #         chestRewards = chest_system.getChestRewards(self.userId, chestId)
    #     if self.taskId == 1003:
    #         newbieMode = gamedata.getGameAttr(self.userId, FISH_GAMEID, ABTestData.newbieMode)
    #         if newbieMode in ["b", "c"]:
    #             reward = {"name": 1137, "count": 80}
    #             chestRewards.append(reward)
    #     return chestId, chestRewards

    def _setAchievementTaskData(self):
        """
        存储成就数据
        """
        assert (self.userId)
        daobase.executeUserCmd(self.userId, "HSET", getTaskKey(self.userId), self.taskId, json.dumps(self.taskData))

    def _getAchievementTaskData(self):
        """
        成就任务数据
        """
        if self.taskData:
            return self.taskData
        value = daobase.executeUserCmd(self.userId, "HGET", getTaskKey(self.userId), self.taskId)
        if value:
            value = strutil.loads(value)
        else:
            value = {"progress": 0, "state": TaskState.Normal, "time": 0}
        self.taskData = value
        return value

    def _updateState(self):
        """
        更新状态
        """
        hasRed = False
        targetCount = self.taskConfig["target"]["num"]
        if self.taskData["state"] == TaskState.Normal and self.taskData["progress"] >= targetCount:
            self.taskData["state"] = TaskState.Complete
            hasRed = True
        elif self.taskData["state"] == TaskState.Complete and self.taskData["progress"] < targetCount:
            self.taskData["state"] = TaskState.Normal
            hasRed = False
        return hasRed


def getTaskKey(userId):
    """获取任务的Key"""
    return UserData.achievement % (FISH_GAMEID, userId)


def getSkillMaxLevel(userId):
    """获取技能最大等级 等级:数量"""
    return skill_system.getHigherSkillLevelInfo(userId)
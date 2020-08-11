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
    SUCCESS = 0
    NOTCOMPLETE = 2
    RECEIVE = 3


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
        self._updateState()

        return taskInfo



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
        pass


def getTaskKey(userId):
    """获取任务的Key"""
    return UserData.achievement % (FISH_GAMEID, userId)




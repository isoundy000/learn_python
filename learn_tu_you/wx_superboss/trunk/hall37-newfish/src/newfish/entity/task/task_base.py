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

    #  增加任务进度





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
            pass


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
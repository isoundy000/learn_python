# -*- coding=utf-8 -*-
"""
Created by hhx on 18/05/10.
"""

import time

from freetime.util import log as ftlog
from freetime.entity.msg import MsgPack
from freetime.core.timer import FTLoopTimer
from poker.entity.dao import gamedata, userchip, userdata
from poker.protocol import router
from poker.util import strutil
from hall.entity import hallranking
from newfish.entity.task import task_base
from newfish.entity.task.task_base import TaskBase, TaskState, TaskModel
from newfish.entity import config, util
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData, ABTestData
from newfish.entity.event import NewbieTaskCompleteEvent
from newfish.servers.util.rpc import user_rpc


taskModelKey = "taskModel"


class RedState:
    Default = 0
    Complete = 1        # 完成新手任务
    CanReceived = 2     # 可领取女王红包奖励
    Received = 3        # 已领取女王红包奖励
    GiveUp = 4          # 放弃奖励


class TaskClass:
    Main = "mainTask"       # 主线任务
    Branch = "branchTask"   # 分支
    Random = "randomTask"   # 随机


TaskModelMap = {
    1: TaskClass.Main,
    2: TaskClass.Branch,
    3: TaskClass.Random
}


class TaskSystemUser(object):
    """
    渔场内任务管理系统(使用TableTask配置)
    """
    def __init__(self, table, player):
        self.table = table
        self.player = player
        self.userId = self.player.userId
        self.curTask = None
        if self.isNewbieRoom():
            self.saveKey = GameData.tableTask % self.table.bigRoomId
        else:
            self.saveKey = GameData.tableTask % self.table.runConfig.fishPool

        self.taskModel = None
        self.taskExpedite = 1           # 任务加速

        # 是否检测中期阶段目标完成状态
        midTermTargetMode = gamedata.getGameAttr(self.player.userId, FISH_GAMEID, ABTestData.midTermTargetMode)
        if midTermTargetMode is None or "a" == midTermTargetMode or self.isRedRoom():
            self.needCheckMidTermTargetStates = False
        else:
            self.needCheckMidTermTargetStates = True

        # 前3个中期阶段目标已完成
        self.top3MidTermTargetFinished = True
        for taskClass in self.player.achieveSystem.holdAssetTasks:
            if taskClass.taskId < 1003 or (taskClass.taskId == 1003 and not taskClass.isComplete()):
                self.top3MidTermTargetFinished = False
                break

        self._reload()
        self._initCurTask()

    def _reload(self):
        if self.isNewbieRoom():
            allRoomTaskIds = config.getAllTableTaskIds(self.table.bigRoomId)
        else:
            allRoomTaskIds = config.getAllTableTaskIds(self.table.runConfig.fishPool)
        self.allMainTaskIds = allRoomTaskIds.get(TaskClass.Main, [])
        self.allBranchTaskIds = allRoomTaskIds.get(TaskClass.Branch, [])
        self.allRandomTaskIds = allRoomTaskIds.get(TaskClass.Random, [])
        self.taskData = {}

    def _initCurTask(self):
        self.taskData = self.taskData or gamedata.getGameAttrJson(self.userId, FISH_GAMEID, self.saveKey, {})
        mainTaskData = self.taskData.get(TaskClass.Main)
        branchTaskData = self.taskData.get(TaskClass.Branch)
        randomTaskData = self.taskData.get(TaskClass.Random)
        self.taskModel = self.taskData.get(taskModelKey)

        taskData = None

        # 屏蔽随机、支线任务
        # if self.taskModel is None:
        #     if self.allMainTaskIds:
        #         curTaskId = self.allMainTaskIds[0]
        #         self.taskModel = TaskModel.Main
        #     elif self.allBranchTaskIds:
        #         curTaskId = self.allBranchTaskIds[0]
        #         self.taskModel = TaskModel.Branch
        #     else:
        #         curTaskId = self.allRandomTaskIds[0]
        #     taskConf = config.getTableTaskConfById(curTaskId)
        # else:
        #     if self.taskModel == TaskModel.Random:
        #         curTaskId = randomTaskData["taskId"] if randomTaskData["taskId"] in self.allRandomTaskIds else self.allRandomTaskIds[-1]
        #         taskData = randomTaskData
        #     elif self.taskModel == TaskModel.Branch:
        #         curTaskId = branchTaskData["taskId"] if branchTaskData["taskId"] in self.allBranchTaskIds else self.allBranchTaskIds[-1]
        #         taskData = branchTaskData
        #     else:
        #         curTaskId = mainTaskData["taskId"] if mainTaskData["taskId"] in self.allMainTaskIds else self.allMainTaskIds[-1]
        #         taskData = mainTaskData
        #     taskConf = config.getTableTaskConfById(curTaskId)

        if self.taskModel is None or self.taskModel != TaskModel.Main or not mainTaskData:
            self.taskModel = TaskModel.Main
            curTaskId = self.allMainTaskIds[0]
        else:
            self.taskModel = TaskModel.Main
            if mainTaskData.get("taskId"):
                curTaskId = mainTaskData["taskId"] if mainTaskData["taskId"] in self.allMainTaskIds else \
                self.allMainTaskIds[-1]
            else:
                curTaskId = self.allMainTaskIds[0]
        taskConf = config.getTableTaskConfById(curTaskId)

        self.curTask and self.curTask.clear()
        # 红包房间放弃红包任务 特殊处理
        # if self.isRedRoom() and self.player.redState > RedState.Default and self.taskModel == TaskModel.Main and self.allBranchTaskIds:
        #     self.taskModel = TaskModel.Branch
        #     taskConf = config.getTableTaskConfById(self.allBranchTaskIds[0])
        #     taskData = None
        self.curTask = self.getTaskClass(taskConf, taskData)
        self._gotoNextTask()

    def _taskStart(self, interval=0, delay=0):
        """
        任务开始
        """
        pass

    def isRedRoom(self):
        """
        是否为新手任务场
        """
        return self.table.typeName == config.FISH_NEWBIE
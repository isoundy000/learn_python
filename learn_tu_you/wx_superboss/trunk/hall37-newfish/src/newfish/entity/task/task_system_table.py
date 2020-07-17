#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8
import time
import random

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer
from newfish.entity.task.bonus_task import BonusTask
from newfish.entity.task.cmptt_task import CmpttTask
from newfish.entity.task.ncmptt_task import NcmpttTask
# from newfish.entity.task.guide_task import GuideTask
from newfish.entity import util
from newfish.entity.timer import FishTableTimer
from newfish.entity.event import EnterTableEvent, LeaveTableEvent
# from newfish.entity.fishactivity.world_boss_activity import WorldbossActivity


class TaskSystemTable(object):
    """
    渔场内任务管理系统(限时任务、夺宝赛、奖金赛)
    """
    def __init__(self, table):
        self.table = table
        self.readyTimer = FishTableTimer(self.table)            # 准备定时器
        self.endTimer = FishTableTimer(self.table)              # 结束定时器
        # self._guideTask = GuideTask(self.table, "guide")      # 引导任务
        self._reload()
        self._registerEvent()

    def _reload(self):
        self.showCmpttInfo = False                              # 展示夺宝赛
        self.showBonusInfo = False                              # 奖金赛
        self.openCmpttPool = True
        self.openBonusPool = True
        self.currTask = None                                    # 当前任务
        self.currTaskState = 0
        self.taskLoopInterval = self.table.runConfig.taskLoopInterval   # 循环间隔
        self.taskLoopStart()                                    # 任务结束
        self._ncmpttTask = None                                 # 限时任务
        self._cmpttTask = None                                  # 夺宝赛
        self._ncmptt2Task = None
        self._bonusTask = None                                  # 奖金赛
        self._ncmpttATask = None
        self._ncmpttBTask = None
        canTriggerTask = True
        # world boss即将出现的轮次不触发限时，奖金，夺宝赛等任务.
        # if WorldbossActivity.isOpen():
        #     ws_start_ts = self.table.world_boss.get_next_ready_timestamp()
        #     ws_end_ts = self.table.world_boss.get_next_start_timestamp() + WorldbossActivity.conf.get("info", {}).get("life_time", 300)
        #     task_start_ts = int(time.time())
        #     task_end_ts = task_start_ts + self.taskLoopInterval
        #     canTriggerTask = not (task_start_ts <= ws_start_ts <= task_end_ts or task_start_ts <= ws_end_ts <= task_end_ts)
        #     ftlog.debug("TaskSystem, _reload, canTriggerTask =", canTriggerTask, "ws_start =", ws_start_ts,
        #                 "ws_end =", ws_end_ts, "task_start =", task_start_ts, "task_end =", task_end_ts, "tableId =", self.table.tableId)
        if canTriggerTask:
            if self.table.runConfig.bonusTaskInterval > 0:
                self.readyTimer.setup(self.table.runConfig.bonusTaskInterval, "task_ready", {}, True)
                self._bonusTask = BonusTask(self.table, "bonus", self.table.runConfig.bonusTaskInterval)
                self._ncmpttTask = NcmpttTask(self.table, "ncmptt", self.table.runConfig.bonusTaskInterval)
                self._cmpttTask = CmpttTask(self.table, "cmptt", self.table.runConfig.bonusTaskInterval)
        self._funMap = {
            "ncmptt": self._ncmpttTask,
            "cmptt": self._cmpttTask,
            "bonus": self._bonusTask
        }

    def taskLoopStart(self):
        ftlog.debug("taskStart->Loop->Start", self.table.tableId)
        self.endTimer.setup(self.taskLoopInterval, "task_end", {}, True)

    def _getCurTask(self, userIds):
        """获取当前的任务"""
        if len(userIds) < 2:
            self.currTask = "ncmptt"
        else:
            self.bonusPool = self.table.room.lotteryPool.getBonusPoolCoin(self.table.tableId)   # 金币奖池
            ftlog.debug("taskReady->msg 11=", self.bonusPool, self.table.runConfig.minBonus)
            if self.bonusPool < self.table.runConfig.minBonus:
                self.currTask = "cmptt"
            else:
                self.currTask = random.choice(["cmptt", "bonus"])

    def taskReady(self, msg, userId, seatId):
        """
        任务准备
        """
        ftlog.debug("taskReady->msg =", msg, self.table.tableId)
        uid = msg.getParam("uid")

        self._taskStartCountdown(None)
        self.showBonusInfo = False
        self.showCmpttInfo = False
        if len(self.table.getBroadcastUids()) == 0:
            ftlog.debug("taskReady->msg =1", "no user", self.table.tableId)
            return
        # 竞赛活动开启期间暂停比赛.
        from newfish.entity.fishactivity import competition_activity
        if competition_activity.isActEnable():
            actState, remainTime = competition_activity._getCompStateAndRemainTime()
            ftlog.debug("taskReady->msg =12", self.table.tableId, actState, remainTime)
            if actState == competition_activity.CompActState.CAS_INPROGRESS \
                    or (actState == competition_activity.CompActState.CAS_NOTOPEN and remainTime < self.table.runConfig.bonusTaskInterval):
                ftlog.debug("taskReady->msg =2", "competition time !", self.table.tableId)
                return
        userIds = []
        for _uid in self.table.getBroadcastUids():
            if util.isFinishAllRedTask(_uid):
                userIds.append(_uid)
        self._getCurTask(userIds)                                   # 获取当前的任务

        ftlog.debug("taskReady->msg =11", self.currTask)
        if self.currTask == None:
            return
        self.showCmpttInfo = (self.currTask == "cmptt")
        self.showBonusInfo = (self.currTask == "bonus")
        self.currTaskState = 1                                      # 当前任务状态
        fun = self._funMap.get(self.currTask, None)
        if fun:
            fun.taskReady(uid)                                      # 任务准备

    def taskStart(self, msg, userId, seatId):
        """
        任务开始
        """
        ftlog.debug("taskStart->msg =", msg)
        if msg is None:
            pass
        else:
            uid = msg.getParam("uid")
            task = msg.getParam("task")
            self.currTask = task
            self.currTaskState = 2
            fun = self._funMap.get(task, None)
            if fun:
                taskId = fun.taskStart(uid)
                if taskId > 0 and self.table.ttAutofillFishGroup:
                    self.table.ttAutofillFishGroup.startAutofill(uid, taskId)

    def taskEnd(self, msg, userId, seatId):
        """
        任务结束
        """
        ftlog.debug("taskEnd->msg =", msg)
        uid = msg.getParam("uid")
        task = msg.getParam("task")
        if task is None:
            ftlog.debug("taskStart->Loop->End")
            if self._ncmpttTask:                    # 限时任务
                self._ncmpttTask.clear()
            if self._ncmptt2Task:
                self._ncmptt2Task.clear()
            if self._ncmpttATask:
                self._ncmpttATask.clear()
            if self._ncmpttBTask:
                self._ncmpttBTask.clear()
            if self._cmpttTask:                     # 夺宝赛
                self._cmpttTask.clear()
            if self._bonusTask:                     # 奖金赛
                self._bonusTask.clear()
            if self.endTimer:
                self.endTimer.cancel()
            if self.readyTimer:
                self.readyTimer.cancel()
            self._reload()
            return
        self.currTask = None
        self.currTaskState = 0
        fun = self._funMap.get(task, None)
        if fun:
            fun.taskEnd(uid)

    def getTaskState(self, userId):
        """获取任务状态"""
        if self.currTask:
            fun = self._funMap.get(self.currTask, None)
            if fun:
                return fun.getTaskState(userId)
        return 0

    def _taskStartCountdown(self, task):
        """
        任务开始倒计时
        """
        # if task == "cmptt":                                   # 竞争性任务(夺宝赛) 第一名
        # self.showCmpttInfo = True
        self.openCmpttPool = False
        self.table.room.lotteryPool.generateCmpttRatioData()
        # elif task == "bonus":
        # self.showBonusInfo = True
        self.openBonusPool = False
        self.table.room.lotteryPool.generateBonusRatioData()
        # self._sendTaskInfo()

    def _sendTaskInfo(self):
        """
        发送任务倒计时信息
        """
        ftlog.debug("sendCmpttTaskInfo =", self.showCmpttInfo)
        # 发送夺宝赛倒计时信息
        if self.showCmpttInfo and self._cmpttTask:
            cmpttTimer = FTLoopTimer(1, 0, self._cmpttTask.sendCmpttTaskInfo)
            cmpttTimer.start()

        ftlog.debug("sendBonusTaskInfo =", self.showBonusInfo)
        # 发送奖金池倒计时信息
        if self.showBonusInfo and self._bonusTask:
            bonusTimer = FTLoopTimer(1, 0, self._bonusTask.sendBonusTaskInfo)
            bonusTimer.start()

    def _sendTaskInfoForReconnect(self, userId):
        """
        用户断线重连发送任务相关信息
        """
        if util.isRedRoom(self.table.typeName):
            return
        self._sendTaskInfo()
        player = self.table.getPlayer(userId)
        if player and player.currentTask:
            task = player.currentTask[0]
            fun = self._funMap.get(task, None)
            if fun:
                timer = FTLoopTimer(1, 0, fun.sendTaskInfoForReconnect, userId)
                timer.start()

    def dealCatchEvent(self, event):
        """
        处理捕获事件
        """
        if event.tableId == self.table.tableId:
            player = self.table.getPlayer(event.userId)
            if player and player.currentTask:
                currTask = player.currentTask[0]
                fun = self._funMap.get(currTask, None)
                if fun:
                    fun.dealCatchEvent(event)
                # elif currTask == "guide":
                #     self._guideTask.dealCatchEvent(event)

    def _dealEnterTable(self, event):
        """
        处理进入事件
        """
        if event.tableId == self.table.tableId:
            ftlog.debug("_dealEnterTable->currTask =", event.userId, self.currTask, self.currTaskState)
            if event.reconnect:
                self._sendTaskInfoForReconnect(event.userId)
            else:
                self._newJoinTask(event.userId)

    def _dealLeaveTable(self, event):
        """
        处理离开事件
        """
        if event.tableId == self.table.tableId:
            for _, fun in self._funMap.iteritems():
                if fun:
                    fun.dealLeaveTable(event)
            # self._guideTask.dealLeaveTable(event)

    # def dealChooseGuideModel(self, userId):
    #     """
    #     处理选择新手引导模式
    #     """
    #     self._newJoinTask(userId)

    def _newJoinTask(self, userId):
        """
        加入任务
        """
        if not util.isFinishAllRedTask(userId):
            return
        # guideStep = util.getGuideStep(userId)
        # if guideStep:
        #     self._guideTask.newJoinTask(userId)
        #     return
        self._sendTaskInfo()
        if self.currTask:
            if self.currTaskState == 1:
                self._newJoinTaskBeforeTheStart(userId)
            # elif self.currTaskState == 2:
            #     self._newJoinTaskAfterTheStart(userId)

    def _newJoinTaskBeforeTheStart(self, userId):
        """
        任务开始前加入任务
        """
        fun = self._funMap.get(self.currTask, None)
        if fun:
            fun.newJoinTask(userId)

    def _newJoinTaskAfterTheStart(self, userId):
        """
        任务开始后加入任务
        """
        fun = self._funMap.get(self.currTask, None)
        if fun:
            timer = FTLoopTimer(1, 0, fun.newJoinTaskForAfterTheStart, userId)
            timer.start()

    def _registerEvent(self):
        """
        注册监听事件
        """
        from newfish.game import TGFish
        TGFish.getEventBus().subscribe(EnterTableEvent, self._dealEnterTable)
        TGFish.getEventBus().subscribe(LeaveTableEvent, self._dealLeaveTable)
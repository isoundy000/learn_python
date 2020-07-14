#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/13

import freetime.util.log as ftlog


class TaskState:

    TS_End = 0      # 任务结束
    TS_Ready = 1    # 任务即将开始
    TS_Start = 2    # 任务开始


class TableMatchTask(object):
    """
    牌桌比赛
    """
    def __init__(self, table, taskName, taskInterval):
        self.table = table
        self.taskName = taskName                            # 任务名称
        self.taskInterval = taskInterval                    # 任务间隔
        self.state = 0                                      # 状态
        self.currentTask = None                             # 当前任务
        self.usersData = {}

    def getTaskState(self, userId):
        """获取任务状态"""
        userData = self.usersData.get(userId, {})
        return 1 if userData else 0

    def getEventFpMultiple(self, event):
        """获取事件渔场倍率"""
        if hasattr(event, "fpMultiple"):
            fpMultiple = event.fpMultiple
        else:
            fpMultiple = self.table.runConfig.multiple
            ftlog.info(self.taskName, ", not set fpMultiple! userId =", event.userId)
        return fpMultiple
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import functools

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer


class Heartbeat(object):
    """心跳的类"""
    ST_IDLE = 0
    ST_START = 1
    ST_STOP = 2

    def __init__(self, target, interval):
        self._target = target
        self._state = Heartbeat.ST_IDLE
        self._count = 0
        self._postTaskList = []
        self._timer = None
        self._interval = interval
        self._init = False

    def start(self):
        assert (self._state == Heartbeat.ST_IDLE)
        self._state = Heartbeat.ST_START
        self._timer = FTLoopTimer(0, 0, self._onInit)
        self._timer.start()

    def stop(self):
        """停止定时器"""
        if self._state != Heartbeat.ST_STOP:
            self._state = Heartbeat.ST_STOP
            if self._timer:
                self._timer.cancel()
            self._timer = None

    @property
    def count(self):
        """次数"""
        return self._count

    def postCall(self, func, *args, **kwargs):
        """处理回调用"""
        self.postTask(functools.partial(func, *args, **kwargs))

    def postTask(self, task):
        """添加任务"""
        if self._state != Heartbeat.ST_STOP:
            self._postTaskList.append(task)
            if self._init and self._timer:
                self._timer.cancel()
                self._timer = FTLoopTimer(0, 0, self._onTimeout)
                self._timer.start()

    def _onInit(self):
        """启动定时器"""
        try:
            self._timer = None
            interval = self._target.onInit()        # 上层类函数初始化
            if interval:
                self._interval = interval           # 间隔时间
            self._scheduleTimer()
        except:
            ftlog.error("Heartbeat._onInit")

    def _onTimeout(self):
        """时间到点的定时器"""
        try:
            self._timer = None
            self._count += 1                        # 执行次数
            self._processPostTaskList()             # 处理任务集合list
            interval = self._target.onHeartbeat()   # 上层函数的心跳
            if interval is not None:
                self._interval = interval
        except:
            self._interval = 1
            ftlog.error("Heartbeat._onTimeout")
        self._scheduleTimer()

    def _scheduleTimer(self):
        """设置特定时间的定时器"""
        if self._state == Heartbeat.ST_START:
            interval = 0 if self._postTaskList else self._interval
            self._timer = FTLoopTimer(interval, 0, self._onTimeout)
            self._timer.start()

    def _processPostTaskList(self):
        """处理任务函数"""
        taskList = self._postTaskList
        self._postTaskList = []
        for task in taskList:
            try:
                task()
            except:
                ftlog.error("task=", task)


class HeartbeatAble(object):
    """心跳"""
    def __init__(self, interval):
        self._heart = Heartbeat(self, interval)

    def startHeart(self):
        """开始心跳"""
        self._heart.start()

    def stopHeart(self):
        """停止心跳"""
        self._heart.stop()

    def onInit(self):
        """初始化心跳"""
        return self._doInit()

    def onHeartbeat(self):
        """心跳的函数间隔"""
        return self._doHeartbeat()

    def postCall(self, func, *args, **kwargs):
        """传递要处理的函数"""
        self._heart.postCall(func, *args, **kwargs)

    def _doInit(self):
        """初始化"""
        return 1

    def _doHeartbeat(self):
        return 1
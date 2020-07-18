#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/17
import functools

from freetime.util import log as ftlog
from freetime.core.timer import FTLoopTimer


class Heartbeat(object):
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
        if self._state != Heartbeat.ST_STOP:
            self._state = Heartbeat.ST_STOP
            if self._timer:
                self._timer.cancel()
            self._timer = None

    @property
    def count(self):
        return self._count

    def postCall(self, func, *args, **kwargs):
        self.postTask(functools.partial(func, *args, **kwargs))

    def postTask(self, task):
        if self._state != Heartbeat.ST_STOP:
            self._postTaskList.append(task)
            if self._init and self._timer:
                self._timer.cancel()
                self._timer = FTLoopTimer(0, 0, self._onTimeout)
                self._timer.start()

    def _onInit(self):
        try:
            self._timer = None
            interval = self._target.onInit()
            if interval:
                self._interval = interval
            self._scheduleTimer()
        except:
            ftlog.error("Heartbeat._onInit")

    def _onTimeout(self):
        try:
            self._timer = None
            self._count += 1
            self._processPostTaskList()
            interval = self._target.onHeartbeat()
            if interval is not None:
                self._interval = interval
        except:
            self._interval = 1
            ftlog.error("Heartbeat._onTimeout")
        self._scheduleTimer()

    def _scheduleTimer(self):
        if self._state == Heartbeat.ST_START:
            interval = 0 if self._postTaskList else self._interval
            self._timer = FTLoopTimer(interval, 0, self._onTimeout)
            self._timer.start()

    def _processPostTaskList(self):
        taskList = self._postTaskList
        self._postTaskList = []
        for task in taskList:
            try:
                task()
            except:
                ftlog.error("task=", task)


class HeartbeatAble(object):

    def __init__(self, interval):
        self._heart = Heartbeat(self, interval)

    def startHeart(self):
        self._heart.start()

    def stopHeart(self):
        self._heart.stop()

    def onInit(self):
        return self._doInit()

    def onHeartbeat(self):
        return self._doHeartbeat()

    def postCall(self, func, *args, **kwargs):
        self._heart.postCall(func, *args, **kwargs)

    def _doInit(self):
        return 1

    def _doHeartbeat(self):
        return 1
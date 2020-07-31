#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/2

import sys
from twisted.internet import reactor
from tasklet import FTTasklet
import freetime.util.log as ftlog
import functools
from time import time


class FTTimer:
    """
    封装calllater,启动tasklet的机制...
    """
    def __init__(self, interval, task_handler, *argl, **argd):
        # self.interval = interval
        self.task_handler = task_handler
        self.argl = argl
        self.argd = argd
        self.handle = reactor.callLater(interval, self._onTime)

        if ftlog.is_debug():
            timerCaller = sys._getframe().f_back.f_code.co_name
            timerCallee = task_handler.func.func_name if isinstance(task_handler, functools.partial) else task_handler.func_name
            if "HeartBeat" not in timerCallee:
                ftlog.debug("|timerCaller, timerCallee, interval:", timerCaller, timerCallee, interval, caller=self)

    def _onTime(self):
        """准时"""
        timerCallee = self.task_handler.func.func_name if isinstance(self.task_handler, functools.partial) else self.task_handler.func_name
        if "HeartBeat" not in timerCallee:
            ftlog.debug("<<", "|timerCallee:", timerCallee, caller=self)

        self.argd["handler"] = self.task_handler
        FTTasklet.create(self.argl, self.argd)

    def cancel(self):
        """取消定时器"""
        if not self.handle:
            return False
        try:
            self.handle.cancel()
        except:
            pass
        self.handle = None
        return True

    def isActive(self):
        """是否激活了定时器"""
        if self.handle:
            return self.handle.active()
        return False

    def getTimeOut(self):
        """获取定时器的执行时间"""
        ts = self.handle
        if not ts:
            return 0.0
        try:
            return ts.getTime()
        except:
            pass
        return 0.0

    def reset(self, interval):
        """重置定时器"""
        ts = self.handle
        if ts:
            try:
                ts.reset(interval)
                return True
            except:
                pass
        return False


class FTLoopTimer():
    """
    封装calllater,启动tasklet的机制...
    loopCount 为－1时，不停止的进行timer触发调用
    loopCount 大于0时，循环触发loopCount次调用
    每次触发均使用新的tasklet进行调用 task_handler(*argl, **argd)
    必须显示调用timer.start()才能启动此timer
    """
    def __init__(self, interval, loopCount, task_handler, *argl, **argd):
        """
        定时器
        :param interval: 时间间隔 2
        :param loopCount: -1无限循环 0一次 1次数
        :param task_handler: 执行的函数
        :param argl:
        :param argd:
        """
        self.interval = interval
        self.loopCount = int(loopCount)
        self.task_handler = task_handler
        self.argl = argl if argl else []
        self.argd = argd if argd else {}
        self.handle = None

    def __repr__(self):
        return '<freetime.core.timer.FTLoopTimer instance at 0x%016x of handler %s>' % (id(self), self.task_handler)

    def start(self):
        """开启定时器"""
        if self.handle == None:
            self._start()

    def _start(self):
        self.handle = reactor.callLater(self.interval, self._onTime)

    def _onTime(self):
        targd = {}
        targd["handler"] = self._invoke
        FTTasklet.create([], targd)

    def _invoke(self):
        try:
            self.task_handler(*self.argl, **self.argd)
        except:
            ftlog.error()
            pass

        if self.loopCount == -1:
            self._start()
        elif self.loopCount > 0:
            self.loopCount -= 1
            self._start()

    def cancel(self):
        """取消定时器"""
        if self.handle:
            try:
                self.handle.cancel()
            except:
                pass
        self.loopCount = 0
        self.handle = None
        return True

    def getTimeOut(self):
        """获取还有多少秒执行函数"""
        ts = self.handle
        if not ts:
            return 0.0
        try:
            return int(ts.getTime() - time())
        except:
            ftlog.error()
            pass
        return 0.0

    def reset(self, interval):
        """重新设置执行的间隔 只能大于创建的间隔"""
        ts = self.handle
        if ts:
            try:
                ts.reset(interval)
                return True
            except:
                ftlog.error()
                pass
        return False
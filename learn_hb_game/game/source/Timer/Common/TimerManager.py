#!/usr/bin/env python
# -*- coding:utf-8 -*-

import traceback
import gevent
import gevent.event
from Source.Timer.Config.Config import PerDayHalfHourConfig, PerDayHourConfig, ExactTimerConfig, TickTimerConfig
from Source.DataBase.Common.DBEngine import DBEngine
from datetime import datetime, timedelta
from Source.Log.Write import Log
from Source.DataLock.Lock1 import Lock1


class TimerManager:
    '''
    定时器
    '''
    _timer = None

    @staticmethod
    def Init():
        TimerManager._timer = {}

    @staticmethod
    def SpawTickTimer(tick, func):
        '''
        创建一个循环时间的定时器
        :param tick: 秒数
        :param func: 函数
        :return:
        '''
        timerevent = gevent.event.Event()
        while True:
            timerevent.wait(tick)
            try:
                func()
            except Exception, e:
                Log.Write(e)
                Log.Write(traceback.format_exc())
            DBEngine.UpdateCurrentSession()
            Lock1.ClearCurrent()

    @staticmethod
    def SpawOneTimer(time, func, param):
        '''
        创建一个带参数的定时器
        :param time:
        :param func:
        :param param:
        :return:
        '''
        timerevent = gevent.event.Event()
        timerevent.wait(time)
        try:
            if param:
                func(param)
            else:
                func()
        except Exception, e:
            Log.Write(e)
            Log.Write(traceback.format_exc())
        DBEngine.UpdateCurrentSession()
        Lock1.ClearCurrent()

    @staticmethod
    def CreateTickTimer(tick, func):
        '''
        创建循环级别定时器
        :param tick:
        :param func:
        :return:
        '''
        gevent.spawn(TimerManager.SpawTickTimer, tick, func)

    @staticmethod
    def CreateOneTimer(time, func, param):
        '''
        创建一个定时器
        :param time: 固定时间
        :param func: 函数
        :param param: 参数
        :return:
        '''
        gevent.spawn(TimerManager.SpawOneTimer, time, func, param)

    @staticmethod
    def DayHourTick():
        '''
        整点定时器
        :return:
        '''
        dayhourevent = gevent.event.Event()
        nowtime = datetime.now()
        # print("[DayHour]after %d secs first call" % ((60 - nowtime.minute) * 60 - nowtime.second))
        dayhourevent.wait((60 - nowtime.minute) * 60 - nowtime.second)      # 距离整点的还差的多少数

        def DayHourTickProcess():
            '''
            检测执行函数 整点
            :return:
            '''
            Log.Write("DayHourTickProcess")
            nowtime1 = datetime.now()
            for k, v in PerDayHourConfig.items():               # 每小时运行一次
                nowhour = nowtime1.hour % 24
                k = k % 24
                if k == nowhour:
                    # print("[DayHour] Hour: %d" % (k))
                    for func in v:
                        try:
                            func()
                        except Exception, e:
                            Log.Write(e)
                            Log.Write(traceback.format_exc())

        DayHourTickProcess()                # 运行
        DBEngine.UpdateCurrentSession()     # 更新当前的session
        Lock1.ClearCurrent()
        while True:
            nowtime = datetime.now()
            dayhourevent.wait((60 - nowtime.minute) * 60 - nowtime.second)  # 等待多少秒之后
            # dayhourevent.wait(60 * 60)
            DayHourTickProcess()            # 执行
            DBEngine.UpdateCurrentSession()
            Lock1.ClearCurrent()

    @staticmethod
    def DayHalfHourTick():
        '''
        半点定时器
        :return:
        '''
        Log.Write("DayHalfHourTick")
        dayhalfhourevent = gevent.event.Event()
        nowtime = datetime.now()
        if nowtime.minute < 30:
            secs_halfhour = (30 - nowtime.minute) * 60 - nowtime.second
        else:
            secs_halfhour = (90 - nowtime.minute) * 60 - nowtime.second

        Log.Write("secs_halfhour", secs_halfhour)
        dayhalfhourevent.wait(secs_halfhour)

        def DayHalfHourTickProcess():
            '''
            检测执行函数 半点
            :return:
            '''
            Log.Write("DayHalfHourTickProcess")
            nowtime1 = datetime.now()
            for k, v in PerDayHalfHourConfig.items():
                nowhour = nowtime1.hour % 24
                k = k % 24
                if k == nowhour:
                    # print("[DayHour] Hour: %d" % (k))
                    for func in v:
                        try:
                            func()                              # 整点加30分钟 00:30 01:30 02:30
                        except Exception, e:
                            Log.Write(e)
                            Log.Write(traceback.format_exc())

        DayHalfHourTickProcess()
        DBEngine.UpdateCurrentSession()
        Lock1.ClearCurrent()
        while True:
            nowtime = datetime.now()
            if nowtime.minute < 30:     # 30分钟之后执行
                secs_halfhour = (30 - nowtime.minute) * 60 - nowtime.second
            else:                       # 90分钟之后执行
                secs_halfhour = (90 - nowtime.minute) * 60 - nowtime.second
            Log.Write("secs_halfhour", secs_halfhour)
            dayhalfhourevent.wait(secs_halfhour)
            DayHalfHourTickProcess()
            DBEngine.UpdateCurrentSession()
            Lock1.ClearCurrent()

    @staticmethod
    def SecondTick():
        '''
        秒级别定时器
        :return:
        '''
        secondevent = gevent.event.Event()

        def SecondTickProcess():
            nowtime2 = datetime.now()
            Log.Write("SecondTickProcess", nowtime2)

        while True:
            secondevent.wait(1)                         # 一秒之后执行
            SecondTickProcess()                         # 秒级别执行函数
            DBEngine.UpdateCurrentSession()
            Lock1.ClearCurrent()

    @staticmethod
    def ExactTimer():
        '''
        精确时间运行
        :return:
        '''
        Log.Write("ExactTimer")
        def ExactTimerProcess(param):
            Log.Write("ExactTimerProcess", param)
            exacttimerevent = gevent.event.Event()
            hour = param[0]                         # 小时
            minute = param[1]                       # 分钟
            second = param[2]                       # 秒数
            while True:
                nowtime3 = datetime.now()           # 当前时间
                # nowtime4 = datetime.now()
                nowtime4 = nowtime3.replace(nowtime3.year, nowtime3.month, nowtime3.day, hour, minute, second)
                timedelta1 = nowtime4 - nowtime3
                if timedelta1.days < 0:
                    nowtime4 += timedelta(days=1)
                    timedelta1 = nowtime4 - nowtime3

                waitSecond = timedelta1.days * 24 * 60 * 60 + timedelta1.seconds
                Log.Write(nowtime4, timedelta1, waitSecond)
                exacttimerevent.wait(waitSecond)
                for i in range(3, len(param)):
                    func = param[i]
                    try:
                        func()
                    except Exception, e:
                        Log.Write(e)
                        Log.Write(traceback.format_exc())
                    exacttimerevent.wait(1)
        for exact in ExactTimerConfig:
            gevent.spawn(ExactTimerProcess, exact)

    @staticmethod
    def Run():
        for v in TickTimerConfig:
            TimerManager.CreateTickTimer(v[0], v[1])
        gevent.spawn(TimerManager.DayHourTick)
        gevent.spawn(TimerManager.DayHalfHourTick)
        gevent.spawn(TimerManager.ExactTimer)
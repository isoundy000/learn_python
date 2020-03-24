#!/usr/bin/env python
# -*- coding:utf-8 -*-


from Source.Log.Write import Log
from Source.Config.ConfigManager import *
from Source.DataBase.Common.DBEngine import DBEngine
from Source.Config.ConfigManager import ConfigManager
import gevent.pool


class WorkPoolManager:

    _pool = None
    _num = 0

    def _init():
        appConfig = ConfigManager.Singleton()
        WorkPoolManager._num = int(appConfig["Server"]["Parallels"]["Workers"])
        Log.Write("[Config]Parallels Worker num: %d" % WorkPoolManager._num)
        return True

    Init = staticmethod(_init)

    def _start(worker):
        def StartFunc():
            WorkPoolManager._pool = gevent.pool.Pool(WorkPoolManager._num)      # 工作池
            def DeadCall(glet):
                Log.Write("dead greenlet", glet, "exception", glet.exception, "value", glet.value,
                          "ready", glet.ready(), "success", glet.successful())
                DBEngine.DelGreenletSession(glet)
            while True:
                WorkPoolManager._pool.spawn(worker).link(DeadCall)
        gevent.spawn(StartFunc)

    Start = staticmethod(_start)
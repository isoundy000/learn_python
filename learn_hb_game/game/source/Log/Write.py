#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'ghou'

import traceback
from datetime import datetime
from Source.Config.ConfigManager import *
from Source.DataLock.Lock2 import *
import gevent


class Log:

    LOG_PATH = None
    LOG_FILE_TIME = None
    LOG_FILE = None
    LOG_PRINT = True
    LOG_FIXTIME = False
    LOG_CACHE = []
    LOG_FIXTAG = None
    Lock = Lock1()
    FileLog = None

    @staticmethod
    def Init(fixtag=None):
        Log.LOG_FILE_TIME = datetime.now()
        if fixtag:
            Log.LOG_FIXTAG = fixtag
        appConfig = ConfigManager.Singleton()
        logConfig = appConfig["Server"]["Log"]
        if logConfig["print"] == "true":
            Log.LOG_PRINT = True
        else:
            Log.LOG_PRINT = False
        Log.LOG_PATH = logConfig["path"]
        if Log.LOG_FIXTAG:
            Log.LOG_FILE = Log.LOG_PATH + "/" + Log.LOG_FILE_TIME.strftime("%F") + Log.LOG_FIXTAG + ".log"
        else:
            Log.LOG_FILE = Log.LOG_PATH + "/" + Log.LOG_FILE_TIME.strftime("%F") + ".log"
        Log.FileLog = open(Log.LOG_FILE, "a+")

    @staticmethod
    def Fix1():
        Log.LOG_FIXTIME = True

    @staticmethod
    def Fix2():
        Log.LOG_FIXTIME = False
        def WriteToFile2():
            Lock2(Log.Lock)
            try:
                for param in Log.LOG_CACHE:
                    Log.FileLog.write(str(param) + "\r\n")
                Log.FileLog.flush()
            except Exception, e:
                print e
                traceback.print_exc()
        if Log.LOG_CACHE:
            WriteToFile2()
            Log.LOG_CACHE = []

    # @staticmethod
    # def WriteToFile(param, LOG_TIME=None):
    #     Lock2(Log.Lock)
    #     if LOG_TIME and Log.LOG_FILE_TIME.day != LOG_TIME.day:
    #         Log.LOG_FILE.close()
    #         Log.LOG_FILE_TIME = LOG_TIME
    #         Log.LOG_FILE = Log.LOG_PATH + "/" + Log.LOG_FILE_TIME.strftime("%F") + ".log"
    #         Log.FileLog = open(Log.LOG_FILE, "a+")
    #     try:
    #         Log.FileLog.write(str(param) + "\r\n")
    #         Log.FileLog.flush()
    #     except Exception, e:
    #         print e
    #         traceback.print_exc()

    @staticmethod
    def Write(*argv):
        LOG_TIME = None
        greenletaddr = id(gevent.getcurrent())
        if Log.LOG_FIXTIME:
            Log.LOG_CACHE.append((greenletaddr, argv))
            if Log.LOG_PRINT:
                print(argv)
        else:
            LOG_TIME = datetime.now()
            param = (greenletaddr, str(LOG_TIME), argv)
            if Log.LOG_PRINT:
                print(param)
            if Log.LOG_PATH:
                def WriteToFile(param):
                    Lock2(Log.Lock)
                    if LOG_TIME and Log.LOG_FILE_TIME.day != LOG_TIME.day:
                        Log.FileLog.close()
                        Log.LOG_FILE_TIME = LOG_TIME
                        if Log.LOG_FIXTAG:
                            Log.LOG_FILE = Log.LOG_PATH + "/" + Log.LOG_FILE_TIME.strftime("%F") + Log.LOG_FIXTAG + ".log"
                        else:
                            Log.LOG_FILE = Log.LOG_PATH + "/" + Log.LOG_FILE_TIME.strftime("%F") + ".log"
                        Log.FileLog = open(Log.LOG_FILE, "a+")
                    try:
                        Log.FileLog.write(str(param) + "\r\n")
                        Log.FileLog.flush()
                    except Exception, e:
                        print e
                        traceback.print_exc()
                WriteToFile(param)
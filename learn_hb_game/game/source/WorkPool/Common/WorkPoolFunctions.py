#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gevent
from Source.Protocol import error_pb2
from Source.Log.Write import Log
from Source.TaskQueue.TaskRequestQueueManager import TaskRequestQueueManager
from Source.TaskQueue.TaskResponseQueueManager import TaskResponseQueueManager
from Source.TaskQueue.TaskData import TaskData
from Source.UserData.UserDataManager import UserDataManager


class WorkPoolFunctions:

    def _excute():
        Log.Write("WorkPoolFunctions excute")




    Excute = staticmethod(_excute)

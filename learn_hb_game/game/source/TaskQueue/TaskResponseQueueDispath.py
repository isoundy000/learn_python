#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Source.Log.Write import Log
from TaskResponseQueueManager import TaskResponseQueueManager
import gevent.socket
from gevent import monkey; monkey.patch_socket()
import gevent
from Source.Net.UserSocket.UserSocketManager import UserSocketManager
from Source.Net.ServerSocket.ServerSocketManager import ServerSocketManager
from Source.Log.Write import Log

TUNNEL_TASK_DICT = {

}



class TaskResponseQueueDispath:

    def _work():
        while True:
            try:
                taskData = TaskResponseQueueManager.Pop()
                # Log.Write("TaskResponseQueueDispath", taskData)
                if taskData.From() == "user":
                    pass
            except Exception, e:
                Log.Write()


    Work = staticmethod(_work)

    def _excute(self):
        gevent.spawn(TaskResponseQueueDispath.Work)
        return True


    Start = staticmethod(_excute)
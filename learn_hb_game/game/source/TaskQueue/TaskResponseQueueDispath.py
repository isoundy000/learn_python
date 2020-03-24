#!/usr/bin/env python
# -*- coding:utf-8 -*-

from Source.Log.Write import Log
from TaskResponseQueueManager import
import gevent.socket
from gevent import monkey; monkey.patch_socket()
import gevent
from Source.Net.UserSocket.UserSocketManager import
from Source.Net.ServerSocket.ServerSocketManager import
from Source.Log.Write import Log

TUNNEL_TASK_DICT = {

}



class TaskResponseQueueDispath:

    def _work():
        pass
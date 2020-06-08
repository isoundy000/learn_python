#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import gevent.socket
from gevent import monkey; monkey.patch_socket()
from gevent.event import Event
from Source.Net.SelfSocket import SendAll
from Source.TaskQueue.TaskData import TaskData
from ServerSocketManager import ServerSocketManager
from Source.Config.ConfigManager import ConfigManager
from Source.Log.Write import Log


def ServerSocketWrite(sock, event):
    '''
    从游戏服发送数据给Acc服
    :param sock:
    :param event:
    :return:
    '''
    while True:
        taskData = ServerSocketManager.ConnectionGet()
        # Log.Write("type", taskData.Type())
        if not taskData.Result():
            taskData.setType(999999)
        if not SendAll(sock, taskData.MakeData()):
            # Log.Write("ssw f")
            event.set()
            return
        # Log.Write("ssw s")
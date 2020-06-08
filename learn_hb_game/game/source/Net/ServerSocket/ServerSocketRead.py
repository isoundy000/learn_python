#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

import gevent.socket
from gevent import monkey; monkey.patch_socket()
from gevent.event import Event
from Source.Net.SelfSocket import RecvAll
from Source.TaskQueue.TaskData import TaskData
from Source.TaskQueue.TaskRequestQueueManager import TaskRequestQueueManager
from Source.Log.Write import Log


def ServerSocketReadPack(sock):
    '''
    第一步 接收包头
    :param sock:
    :return:
    '''
    headdata = RecvAll(sock, 16)
    if headdata is None:
        Log.Write("disconnect on recv head")
        return None

    taskData = TaskData(sock)
    taskData.setFrom("gameserver")                  # 游戏服务器
    taskData.ParseHead(headdata)
    dataLen = taskData.DataLen()
    if dataLen != 0:
        data = RecvAll(sock, dataLen)
        if data is None:
            Log.Write("disconnect on recv body")
            return None
        taskData.setData(data)

    return taskData


def ServerSocketRead(sock, event):
    '''
    游戏服解析sock的数据
    :param sock:
    :param event:
    :return:
    '''
    while True:
        taskData = ServerSocketReadPack(sock)
        if taskData is None:
            event.set()
            return
        TaskRequestQueueManager.Push(taskData)
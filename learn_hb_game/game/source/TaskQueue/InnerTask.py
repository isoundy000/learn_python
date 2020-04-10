#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from TaskData import TaskData
from TaskRequestQueueManager import TaskRequestQueueManager


def InnerTask(type, data):
    '''
    设置一个内部任务
    :param type:
    :param data:
    :return:
    '''
    task = TaskData()
    task.setType(type)
    task.setData(data)
    task.setFrom("inner")
    TaskRequestQueueManager.Push(task)
#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from Source.Log.Write import Log
from gevent.queue import Queue


class TaskRequestQueueManager:

    _queue = None

    def _init():
        TaskRequestQueueManager._queue = Queue(0)

    Init = staticmethod(_init)

    def _push(task):
        TaskRequestQueueManager._queue.put(task)

    Push = staticmethod(_push)

    def _pop():
        return TaskRequestQueueManager._queue.get()

    Pop = staticmethod(_pop)
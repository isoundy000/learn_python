#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from Source.Log.Write import Log
from gevent.queue import Queue


class TaskResponseQueueManager:

    _queue = None

    def _init():
        TaskResponseQueueManager._queue = Queue(0)
        return True

    Init = staticmethod(_init)

    def _push(task):
        TaskResponseQueueManager._queue.put(task)

    Push = staticmethod(_push)

    def _pop():
        return TaskResponseQueueManager._queue.get()

    Pop = staticmethod(_pop)
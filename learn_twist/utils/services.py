# -*- encoding: utf-8 -*-
'''
Created on 2019年11月17日

@author: houguangdong
'''
import threading
from twisted.internet import defer
from twisted.internet import threads
from twisted.python import log

# typing
from typing import Set
from typing import Dict
from typing import Any


class Service(object):
    """
    attributes:
        * name - string, service name.
        * run_style
    """
    SINGLE_STYLE = 1
    PARALLEL_STYLE = 2

    def __init__(self, name, run_style=SINGLE_STYLE):
        self._name = name
        self._run_style = run_style
        self.un_display = set()  # type: Set
        self._lock = threading.RLock()
        self._targets = {}  # type: Dict[int, Any]

    @property
    def name(self):
        return self._name

    def __iter__(self):
        return self._targets.values()

    def add_ud_target(self, command):
        """Add a target unDisplay when client call it.
        @param command:
        @return:
        """
        self.un_display.add(command)

    def map_target(self, target):
        """Add a target to the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets.values():
                exist_target = self._targets.get(key)
                raise "target [%d] Already exists,\
                Conflict between the %s and %s" % (key, exist_target.__name__, target.__name__)
            self._targets[key] = target
        finally:
            self._lock.release()

    def un_map_target(self, target):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets:
                del self._targets[key]
        finally:
            self._lock.release()

    def un_map_target_by_key(self, target_key):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            del self._targets[target_key]
        finally:
            self._lock.release()

    def get_target(self, target_key: int):
        """Get a target from the service by name.
        """
        self._lock.acquire()
        try:
            target = self._targets.get(target_key, None)
        finally:
            self._lock.release()
        return target

    def call_target(self, target_key, *args, **kwargs):
        """
        call Target
        """
        if self._run_style == self.SINGLE_STYLE:
            result = self.call_target_single(target_key, *args, **kwargs)
        else:
            result = self.call_target_parallel(target_key, *args, **kwargs)
        return result

    def call_target_single(self, target_key, *args, **kwargs):
        """call Target by Single
        @param target_key: target ID
        """
        target = self.get_target(target_key)
        self._lock.acquire()
        try:
            log.msg("Services call_target_single", self._targets)
            if not target:
                log.err('the command {0} not Found on {1}'.format(target_key, self._name))
                return None
            log.msg('call method {0} on {1}[single]'.format(target_key, self._name))
            defer_data = target(*args, **kwargs)  # 执行函数
            if not defer_data:
                return None
            if isinstance(defer_data, defer.Deferred):
                return defer_data
            d = defer.Deferred()
            d.callback(defer_data)
        finally:
            self._lock.release()
        return d

    def call_target_parallel(self, target_key, *args, **kwargs):
        """call Target by Single
        @param target_key: target ID
        """
        self._lock.acquire()
        try:
            log.msg("Services call_target_parallel")
            log.msg(self._targets)
            target = self.get_target(target_key)
            if not target:
                log.err('the command {0} not Found on {1}[parallel]'.format(target_key, self._name))
                return None
            log.msg('call method {0} on {1}[parallel]'.format(target_key, self._name))
            d = threads.deferToThread(target, *args, **kwargs)
        finally:
            self._lock.release()
        return d


class CommandService(Service):
    """
    According to Command ID search target
    """

    def map_target(self, target):
        """Add a target to the service."""
        self._lock.acquire()
        try:
            key = int(target.__name__.split('_')[-1])
            if key in self._targets.values():
                exist_target = self._targets.get(key)
                raise "target [%d] Already exists,\
                Conflict between the %s and %s" % (key, exist_target.__name__, target.__name__)
            self._targets[key] = target
        finally:
            self._lock.release()

    def un_map_target(self, target):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            key = int(target.__name__.split('_')[-1])
            if key in self._targets:
                del self._targets[key]
        finally:
            self._lock.release()
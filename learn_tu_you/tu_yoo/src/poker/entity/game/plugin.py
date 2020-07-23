#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/9
'''游戏插件管理模块
'''


import importlib
import sys
import functools

import freetime.util.log as ftlog
from freetime.util.log import catchedmethod, getMethodName
from freetime.entity.msg import MsgPack

from poker.entity.configure import configure
from poker.protocol import router
from poker.entity.configure import gdata


_DEBUG = 1
def debug(*args, **kwargs):
    if _DEBUG:
        ftlog.info(*args, **kwargs)


class TYPluginUtils(object):

    @classmethod
    def updateMsg(cls, msg=None, cmd=None, params=None, result=None, **other):
        if not msg:
            msg = MsgPack()
        if cmd:
            msg.setCmd(cmd)
        if params is not None:
            msg.setKey('params', params)
        if result is not None:
            msg.setKey('result', result)

        for k, v in other.items():
            msg.setKey(k, v)

        return msg

    @classmethod
    def sendMessage(cls, gameId, targetUserIds, cmd, result, logInfo=True):
        """发送消息"""
        if isinstance(targetUserIds, int):
            targetUserIds = [targetUserIds]
        msg = cls.updateMsg(cmd=cmd, result=result)
        msg.setResult('gameId', gameId)
        if logInfo:
            debug('|to targetUserIds:', targetUserIds, '|msg:', msg, caller=cls)
        else:
            ftlog.debug('|to targetUserIds:', targetUserIds, '|msg:', msg, caller=cls)
        router.sendToUsers(msg, targetUserIds)

    @classmethod
    def mkdict(cls, **kwargs):
        return kwargs

    @classmethod
    def makeHandlers(cls, handlerClass, events):
        ''' ['EV_GAME_INIT'] => {'EV_GAME_INIT': handlerClass.EV_GAME_INIT}'''
        return dict([(ev, getattr(handlerClass, ev)) for ev in events])


class TYPlugin(object):

    def __init__(self, gameId, cfg):
        pass


class PluginExceptBreak(Exception):
    """中断事件链执行"""
    pass


class PluginExceptDelay(Exception):
    """推迟执行，直到达成一定条件"""
    pass


class TYPluginCenter:
    plugins = {}  # key: gameId, value {name: TYPluginObj}
    config_reload_flag = {}  # key: gameId, value: last reaload configure uuid(default None)
    map_events = {}  # key: gameId; value: {event1: [handler1, handler2, ...], evnet2: [handler1, handler2, ...]}

    EV_CHAIN_STOP = 'EV_CHAIN_STOP'  # handler 函数返回此值，表示中断事件链执行

    @classmethod
    def event(cls, msg, gameId):
        """ 发布事件
        发布事件，按顺序调用所有的事件处理函数。

        事件处理函数可以抛出异常来改变执行的方式：
            PluginExceptBreak: 中止此事件处理链执行；
            PluginExceptDelay: 延迟此处理函数执行（排到链尾）
            其它异常不会中断事件链
        """
        pass


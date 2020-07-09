#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
import random

from freetime.entity.msg import MsgPack
from freetime.support.tcpagent import wrapper
import freetime.util.log as ftlog
from poker.entity.configure import gdata, pokerconf, configure
from poker.protocol import oldcmd, _runenv
import stackless
from poker.util import strutil


def sendToUsers(msgpack, userIdList):
    '''
    发送消息至一组用户的客户端
    '''
    pass


def sendTableServer(msgpack, roomId):
    '''
    发送一个消息至指定的桌子处理进程
    '''
    return _communicateTableServer(0, roomId, msgpack, 'S6', 0)


def _communicateTableServer(userId, roomId, msgpack, head1, isQuery, timeout=None, notimeoutex=0):
    pass


def sendToUser(msgpack, userId):
    '''
    发送消息至用户的客户端
    '''
    if isinstance(msgpack, MsgPack):
        msgpack = msgpack.pack()


def isQuery():
    return wrapper.isQuery()


def responseQurery(msgpack, userheader1=None, userheader2=None):
    '''
    响应"查询请求"的进程内部消息命令, 即: query->response
    '''
    taskarg = stackless.getcurrent()._fttask.run_args
    if not 'responsed' in taskarg:
        taskarg['responsed'] = 1
    if isinstance(msgpack, MsgPack):
        msgpack = msgpack.pack()
    assert (isinstance(msgpack, basestring))
    wrapper.response(msgpack, userheader1, userheader2)
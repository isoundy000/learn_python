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



class _RouterServer():
    """路由器服务器"""
    def __init__(self, sids=None, srvType=None):
        if not sids:
            sids = []
        self.srvType = srvType
        self.sids = sids[:]
        self.sidlen = len(self.sids)
        if self.sidlen > 0:
            self.sididx = random.randint(0, self.sidlen - 1)
        else:
            self.sididx = 0
        self.sids.sort()
        if sids:
            ftlog.debug('ROUTER->', self.sids, self.sidlen, self.sididx, caller=self)


_connServer = _RouterServer()               # CO路由
_utilServer = _RouterServer()               # UT路由
_httpServer = _RouterServer()               # HT路由
_sdkHttpServer = _RouterServer()            # SDK HT路由
_gatewayHttpServer = _RouterServer()        # 网关HTT路由
_robotServer = _RouterServer()              # RO路由
_centerServer = _RouterServer()             # CT路由
_agentServer = _RouterServer()              # AG路由 带领路由

_cmd_route_map = {}
_cmd_notuse_map = set()
_cmd_group_match_set = set()


def _initialize():
    '''
    初始化命令路由
    '''
    ftlog.debug('router._initialize begin')
    allsrv = gdata.serverTypeMap()
    pass




def _initialize():
    '''
    初始化命令路由
    '''
    ftlog.debug('router._initialize begin')
    pass


def _initialize_udp():
    pass



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
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/4
from datetime import datetime
import socket
import zlib
import random
import struct
import hashlib
import base64
import array
import os
from twisted.internet import defer
from twisted.internet import protocol, reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.protocols.basic import LineReceiver
from twisted.python import failure
import twisted.web.http
import freetime.util.encry as ftenc
import freetime.util.log as ftlog
from tasklet import FTTasklet


class FTProtocolBase(object):
    """
    FreeTime协议的公共抽象，封装了“为每个请求派生一个tasklet”的机制

    定义了lostHandler和madeHandler接口,用于实现建立连接和连接丢失的处理逻辑
    (对于udp协议，startProtocol和stopProtocol时触发)

    定义了getTaskletFunc接口，业务逻辑层通过这个接口管理消息和消息处理函数
    的映射,框架会传入启动tasklet时的参数字典，业务逻辑层通过这些参数分配合
    适的tasklet方法，可以实现诸如消息注册等方式

    定义了parseData接口，用于实现解析网络原始包，解析后的pack后续
    可以通过ftsvr.getTaskPack()得到
    对于格式非法的数据，parseData需要返回None

    另外，还实现了请求包个数和每秒处理包速度PPS等基本统计功能
    """

    def lostHandler(self, reason):
        pass

    def madeHandler(self):
        pass

    def getTaskletFunc(self, pack):
        pass

    def parseData(self, data):
        pass

    def closeConnection(self, isabort=0):
        pass

    def _runTasklet(self, *argl, **argd):
        pass


class FTUDPQueryProtocol(DatagramProtocol, FTProtocolBase):

    QUERYID = 0

    def __init__(self, dsthost, dstport):
        pass

    def startProtocol(self):
        pass

    def stopProtocol(self):
        pass

    def datagramReceived(self, data, address):
        pass

    def query(self, data, timeout=1):
        pass

    def _clearFailed(self, deferred, mid):
        pass
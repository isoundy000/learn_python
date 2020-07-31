#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/29

import json
import time
import stackless
import struct
import random
from freetime.core.protocol import FTUDPServerProtocol
from freetime.core.timer import FTTimer
from freetime.util.cron import FTCron
import freetime.core.lock as ftlock
import freetime.entity.service as ftsvr
import freetime.support.tcpagent.wrapper as ftagent
import freetime.util.log as ftlog
import freetime.entity.config as ftcon
import freetime.aio.http as fthttp


class Interface:
    def mget(self):
        pass


class InterfaceImpl(Interface):
    def mget(self):
        return ftsvr.doRedis("user01", "HMGET", "user:11111", "name", "clientid")


"""
继承freetime提供的protocol基类，
实现getTaskletFunc方法，用于识别请求包，返回对应的tasklet入口执行方法
在这里，可以实现消息注册机制，以便更好的管理消息处理方法
"""
class MyProto(FTUDPServerProtocol):
    pass







class EchoProto(FTUDPServerProtocol):
    pass
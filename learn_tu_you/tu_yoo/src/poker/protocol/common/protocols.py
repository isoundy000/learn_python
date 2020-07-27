#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/7/21

from freetime.core.protocol import FTHttpRequest, FTHttpChannel
import freetime.entity.service as ftsvr
from freetime.support.tcpagent.protocol import S2AProtocol
import freetime.util.log as ftlog
from poker.entity.configure import gdata
from poker.protocol import runhttp, runcmd
from freetime.entity.msg import MsgPack
from freetime.core.tasklet import FTTasklet


class TYCommonHttpRequest(FTHttpRequest):
    '''
    通用的HTTP协议
    '''
    def handleRequest(self):
        taskarg = ftsvr.getTaskRunArg()
        request = taskarg['data']
        if not gdata.initializeOk():
            ftlog.info('TYCommonHttpRequest not initialize ok, ignore this request :', request.path)
            request.setResponseCode(503)
            request.finish()
            return
        runhttp.handlerHttpRequest(request)


class TYCommonHttpChannel(FTHttpChannel):
    requestFactory = TYCommonHttpRequest


class TYCommonS2AProto(S2AProtocol):
    '''
    通用的S2A协议
    '''
    def getTaskletFunc(self, argd):
        return self.doSomeLogic

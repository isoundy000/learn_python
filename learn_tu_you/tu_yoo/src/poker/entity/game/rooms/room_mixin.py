#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/18
'''房间基类Mixin
'''

import freetime.util.log as ftlog
from freetime.util.log import getMethodName
from freetime.entity.msg import MsgPack

from poker.protocol import router
from poker.entity.dao import userchip, sessiondata
from poker.entity.biz import bireport
from poker.entity.configure import gdata
from poker.util import strutil


class TYRoomMixin(object):
    '''房间Mixin基类
    '''

    def _baseLogStr(self, des="", userId=None):
        pass



    @classmethod
    def queryRoomQuickStartReq(cls, msg, roomId, tableId, **kwargs):
        '''fas快速开始的请求'''
        msg.setCmd("room")
        msg.setParam("action", "quick_start")
        msg.setParam("roomId", roomId)
        msg.setParam("tableId", tableId)
        for key in kwargs:
            msg.setParam(key, kwargs[key])
        if ftlog.is_debug():
            ftlog.debug(msg, caller=cls)
        router.queryRoomServer(msg, roomId)

    @classmethod
    def makeSitReq(cls, userId, shadowRoomId, tableId, clientId):
        """在子类中调用此方法"""
        mpSitReq = MsgPack()
        mpSitReq.setCmd("table")
        mpSitReq.setParam("action", "sit")
        mpSitReq.setParam("userId", userId)
        mpSitReq.setParam("roomId", shadowRoomId)
        mpSitReq.setParam("tableId", tableId)
        mpSitReq.setParam("clientId", clientId)
        mpSitReq.setParam("gameId", strutil.getGameIdFromInstanceRoomId(shadowRoomId))
        if ftlog.is_debug():
            ftlog.debug(str(mpSitReq), caller=cls)
        return mpSitReq
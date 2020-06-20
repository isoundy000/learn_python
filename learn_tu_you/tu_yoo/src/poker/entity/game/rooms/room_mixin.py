#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/18
'''房间基类Mixin
'''


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
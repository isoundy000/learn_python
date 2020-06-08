#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6

from poker.entity.dao import gamedata, daobase
from poker.entity.biz.message import message
from poker.protocol import router
from poker.util import strutil, timestamp


class GameMsg(object):

    @classmethod
    def sendMsg(cls, msg, uidList):
        """
        发送消息给客户端
        """
        if not isinstance(uidList, list):
            uidList = [uidList]
        router.sendToUsers(msg, uidList)
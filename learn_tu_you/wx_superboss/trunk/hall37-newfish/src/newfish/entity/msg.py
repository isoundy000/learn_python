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

    @classmethod
    def sendPrivate(cls, gameId, toUid, fromUid, text):
        """
        游戏记录（使用大厅的游戏记录功能）
        """
        ct = timestamp.formatTimeSecond()
        msg = {"gameid": gameId, "time": ct, "text": text}
        if fromUid:
            msg["from"] = fromUid

        rediskey = message.REDIS_KEY.format(message.MESSAGE_TYPE_PRIVATE, message.HALL_GAMEID, toUid)
        msglist = message._msg_load_and_expire(toUid, rediskey)
        if len(msglist) >= 100:  # 超100条删除
            lastmsgval = None
            for msgval in msglist:
                if lastmsgval:
                    if message._msg_order(lastmsgval) > message._msg_order(msgval):
                        continue
                lastmsgval = msgval
            if lastmsgval:
                daobase.executeUserCmd(toUid, "HDEL", rediskey, lastmsgval["id"])

        maxid = gamedata.incrGameAttr(toUid, message.HALL_GAMEID, "msg.id.max", 1)
        daobase.executeUserCmd(toUid, "HSET", rediskey, maxid, strutil.dumps(msg))
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/6
"""
站内消息,类似邮箱功能,可以带附件
"""
from sre_compile import isstring

import freetime.util.log as ftlog
import poker.entity.events.tyeventbus as pkeventbus
from poker.entity.biz.content import TYContentItem
from poker.entity.dao import daobase
from poker.entity.dao import gamedata
from poker.entity.events.tyevent import ModuleTipEvent
from poker.util import timestamp, strutil

MAX_SIZE = 50

MESSAGE_TYPE_PRIVATE = 1  # 游戏记录
MESSAGE_TYPE_SYSTEM = 2  # 系统通知
MESSAGE_TYPES = {
    MESSAGE_TYPE_PRIVATE: 'msg.id.private',
    MESSAGE_TYPE_SYSTEM: 'msg.id.system',
}

HALL_GAMEID = 9999
REDIS_KEY = 'message_{}:{}:{}'


def _msg_order(msg):
    """信息排序"""
    attach = msg.get('attachment')
    if not attach:
        order_pri = Attachment.ORDER_KEY
    else:
        typeid = attach['typeid']
        order_pri = MESSAGE_ATTACHMENT_CLASS[typeid].ORDER_KEY
    return order_pri, -msg['id']


def _msg_load_and_expire(userid, rediskey):
    return []
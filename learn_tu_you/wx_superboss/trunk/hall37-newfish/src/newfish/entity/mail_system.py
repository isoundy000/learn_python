#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/7
import time
import json

from freetime.entity.msg import MsgPack
from freetime.util import log as ftlog
from poker.protocol import router
from poker.entity.dao import gamedata, userdata
from newfish.entity import util, module_tip, config
from newfish.entity.config import FISH_GAMEID
from newfish.entity.redis_keys import GameData
from newfish.entity.event import SendMailEvent, ReceiveMailEvent
from newfish.servers.util.rpc import user_rpc
from newfish.entity.msg import GameMsg
from poker.entity.biz import bireport


# 邮件发送方类型
class MailSenderType:
    MT_SYS = 1      # 系统
    MT_USERS = 2    # 玩家


# 邮件奖励类型
class MailRewardType:

    GrandPrixReward = 17  # 大奖赛奖励



def addOneMail(senderUserId, receiverUserId, mailRewardType, rewards=None, message=None, title=None):
    """
    添加一封邮件
    :param senderUserId: 发件人
    :param receiverUserId: 收件人
    :param mailRewardType: 邮件类型
    :param rewards: 附件奖励
    :param message: 邮件内容
    :param title: 标题
    :return: 是否添加成功
    """

    return True

def sendSystemMail(userId, mailRewardType, rewards=None, message=None, title=None):
    """
    发送系统邮件
    """
    addOneMail(config.ROBOT_MAX_USER_ID, userId, mailRewardType, rewards, message, title)
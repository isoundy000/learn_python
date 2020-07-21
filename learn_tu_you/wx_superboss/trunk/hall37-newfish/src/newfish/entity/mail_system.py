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
    SystemReward = 0  # 系统奖励
    Present = 1  # 赠送
    StarRank = 2  # 海星榜奖励
    SystemCompensate = 3  # 系统补偿
    HonorReward = 4  # 称号奖励
    FriendReward = 5  # 渔友对战胜利奖励
    FriendUnbind = 6  # 渔友对战房间解散退还
    RobberyRank = 7  # 招财赢家榜奖励
    RobberyCompensate = 8  # 招财补偿
    ChestReward = 9  # 宝箱兑换奖励
    ShareReward = 10  # 分享奖励
    MatchReward = 11  # 比赛奖励
    InviteReward = 12  # 邀请有礼
    ActivityReward = 13  # 活动奖励
    TreasureReward = 14  # 宝藏奖励
    SystemInfo = 15  # 系统通知
    FishCanReturn = 16  # 鱼罐头返还
    GrandPrixReward = 17  # 大奖赛奖励
    PoseidonRank = 18  # 海皇赢家榜奖励
    PoseidonCompensate = 19  # 海皇补偿


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



def getAllMail(userId):
    """
    获取收件箱所有邮件
    """
    tempMail = {}
    return tempMail


def initialize():
    pass
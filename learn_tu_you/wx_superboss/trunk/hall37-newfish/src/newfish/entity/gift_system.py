#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/11




def doSendFishGift(userId, clientId):
    """
    发送礼包消息
    """
    pass


def doBuyFishGift(userId, clientId, giftId, buyType=None, itemId=0):
    """
    购买礼包
    """
    ftlog.debug("doBuyFishGift===>", userId, clientId, giftId, buyType, itemId)
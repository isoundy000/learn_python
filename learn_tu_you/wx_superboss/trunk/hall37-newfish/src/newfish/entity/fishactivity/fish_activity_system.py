#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/8

from newfish.entity import config



def countTableData(userId, betFishNum, bossFishNum, gainCoin, roomId, catchFishes):
    pass



def isActivityOpen(acType):
    """
    活动是否处于开放时间
    :param acType: 活动类型
    """
    acConfigs = config.getActivityConfig()
    for acId, acInfo in acConfigs.iteritems():
        if acInfo["type"] == acType and util.isTimeEffective(acInfo["effectiveTime"]):
            return True
    return False
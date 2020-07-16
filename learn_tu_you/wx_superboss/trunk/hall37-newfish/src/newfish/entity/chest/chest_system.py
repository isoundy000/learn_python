#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30




class ChestFromType:
    # 宝箱来源
    Share_Chest_Fish = 0            # 分享宝箱鱼
    Fly_Pig_Chest = 1               # 飞猪宝箱
    Cmptt_Ncmptt_Bonus_Task = 2     # 渔场比赛获得
    Daily_Quest_Week_Chest = 3      # 每日任务周宝箱
    Daily_Quest_Daily_Chest = 4     # 每日任务每日宝箱


def newChestItem(userId, chestId, eventId, intEventParam=0):
    """
    生成一个宝箱
    """
    return True



def getChestIdleOrder(userId):
    """
    得到空闲的宝箱栏位置
    """




    return -1


def getChestRewards(userId, chestId):
    """
    获取宝箱物品
    """
    rewards = []
    return rewards
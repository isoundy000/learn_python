#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/7


class ActivityState:
    """
    活动及其任务的状态
    """
    NotOpen = -1        # 未开启
    Normal = 0          # 已开启
    Complete = 1        # 已完成但未领奖
    Received = 2        # 已领取奖励
    NoCount = 3         # 已领完无剩余
    TodayReceived = 4   # 今日已领取
    Expired = 5         # 已过期



# 特殊活动类型
# 1、单张宣传图
# 2、一个按钮
# 3、两个按钮
# 6、海星抽奖
# 14、加群得礼包
# 18、渔友竞技
# 28、版本更新
# 32、公告图
class ActivityType:
    ExchangeBonusTask = 21      # 河马活动 兑换红利任务
    OneDayClearAc = 30          # 招财送大奖



# 活动任务类型
class TaskType:
    pass


class FishActivity(object):

    def __init__(self, userId, activityId, inTable):
        self._initData(userId, activityId, inTable)
        self.dealActivity()

    def _initData(self, userId, activityId, inTable):
        pass
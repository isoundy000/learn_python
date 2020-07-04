#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30


from newfish.entity.mail_system import MailRewardType


# 排行榜在9999/ranking/0.json配置下的index
class RankDefineIndex:
    GrandPrix = 14          # 大奖赛积分榜


# 44/rankReward/0.json文件中的key
class RankType:
    TodayStarfish = 1       # 海星收集榜
    TodayGrandPrix = 16     # 大奖赛今日榜
    LastGrandPrix = 17      # 大奖赛昨日榜
    WeekGrandPrix = 18      # 大奖赛周榜


class RankingBase(object):

    def __init__(self, userId, rankType, defineIndex, clientId=None, httpRequest=False, mailType=MailRewardType.SystemReward):
        pass









    def getTopNRankUsers(self, _timestamp, _rankDefine=None):
        """
        获取topN玩家列表
        """
        pass


